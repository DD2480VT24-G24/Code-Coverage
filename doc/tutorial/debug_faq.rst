
.. _debug_faq:

===========================================
Debugging PyTensor: FAQ and Troubleshooting
===========================================

There are many kinds of bugs that might come up in a computer program.
This page is structured as a FAQ.  It provides recipes to tackle common
problems, and introduces some of the tools that we use to find problems in our
own PyTensor code, and even (it happens) in PyTensor's internals, in
:ref:`using_debugmode`.

Isolating the Problem/Testing PyTensor Compiler
-----------------------------------------------

You can run your PyTensor function in a :ref:`DebugMode<using_debugmode>`.
This tests the PyTensor rewrites and helps to find where NaN, inf and other problems come from.

Interpreting Error Messages
---------------------------

Even in its default configuration, PyTensor tries to display useful error
messages. Consider the following faulty code.

.. testcode::

    import numpy as np
    import pytensor
    import pytensor.tensor as pt

    x = pt.vector()
    y = pt.vector()
    z = x + x
    z = z + y
    f = pytensor.function([x, y], z)
    f(np.ones((2,)), np.ones((3,)))

Running the code above we see:

.. testoutput::
   :options: +ELLIPSIS

   Traceback (most recent call last):
     ...
   ValueError: Input dimension mismatch. (input[0].shape[0] = 3, input[1].shape[0] = 2)
   Apply node that caused the error: Elemwise{add,no_inplace}(<TensorType(float64, (?,))>, <TensorType(float64, (?,))>, <TensorType(float64, (?,))>)
   Inputs types: [TensorType(float64, (?,)), TensorType(float64, (?,)), TensorType(float64, (?,))]
   Inputs shapes: [(3,), (2,), (2,)]
   Inputs strides: [(8,), (8,), (8,)]
   Inputs scalar values: ['not scalar', 'not scalar', 'not scalar']

   HINT: Re-running with most PyTensor optimizations disabled could give you a back-traces when this node was created. This can be done with by setting the PyTensor flags 'optimizer=fast_compile'. If that does not work, PyTensor optimizations can be disabled with 'optimizer=None'.
   HINT: Use the PyTensor flag 'exception_verbosity=high' for a debugprint of this apply node.

Arguably the most useful information is approximately half-way through
the error message, where the kind of error is displayed along with its
cause (e.g. ``ValueError: Input dimension mismatch. (input[0].shape[0] = 3, input[1].shape[0] = 2``).
Below it, some other information is given, such as the `Apply` node that
caused the error, as well as the input types, shapes, strides and
scalar values.

The two hints can also be helpful when debugging. Using the PyTensor flag
``optimizer=fast_compile`` or ``optimizer=None`` can often tell you
the faulty line, while ``exception_verbosity=high`` will display a
debug print of the apply node. Using these hints, the end of the error
message becomes :

.. code-block:: none

    Backtrace when the node is created:
      File "test0.py", line 8, in <module>
        z = z + y

    Debugprint of the apply node:
    Elemwise{add,no_inplace} [id A] <TensorType(float64, (?,))> ''
     |Elemwise{add,no_inplace} [id B] <TensorType(float64, (?,))> ''
     | |<TensorType(float64, (?,))> [id C] <TensorType(float64, (?,))>
     | |<TensorType(float64, (?,))> [id C] <TensorType(float64, (?,))>
     |<TensorType(float64, (?,))> [id D] <TensorType(float64, (?,))>

We can here see that the error can be traced back to the line ``z = z + y``.
For this example, using ``optimizer=fast_compile`` worked. If it did not,
you could set ``optimizer=None`` or use test values.

.. _test_values:

Using Test Values
-----------------

As of v.0.4.0, PyTensor has a new mechanism by which graphs are executed
on-the-fly, before a :func:`pytensor.function` is ever compiled. Since optimizations
haven't been applied at this stage, it is easier for the user to locate the
source of some bug. This functionality is enabled through the config flag
`pytensor.config.compute_test_value`. Its use is best shown through the
following example. Here, we use ``exception_verbosity=high`` and
``optimizer=fast_compile``, which would not tell you the line at fault.
``optimizer=None`` would and it could therefore be used instead of test values.


.. testcode:: testvalue

    import numpy as np
    import pytensor
    import pytensor.tensor as pt

    # compute_test_value is 'off' by default, meaning this feature is inactive
    pytensor.config.compute_test_value = 'off' # Use 'warn' to activate this feature

    # configure shared variables
    W1val = np.random.random((2, 10, 10)).astype(pytensor.config.floatX)
    W1 = pytensor.shared(W1val, 'W1')
    W2val = np.random.random((15, 20)).astype(pytensor.config.floatX)
    W2 = pytensor.shared(W2val, 'W2')

    # input which will be of shape (5,10)
    x  = pt.matrix('x')
    # provide PyTensor with a default test-value
    #x.tag.test_value = np.random.random((5, 10))

    # transform the shared variable in some way. PyTensor does not
    # know off hand that the matrix func_of_W1 has shape (20, 10)
    func_of_W1 = W1.dimshuffle(2, 0, 1).flatten(2).T

    # source of error: dot product of 5x10 with 20x10
    h1 = pt.dot(x, func_of_W1)

    # do more stuff
    h2 = pt.dot(h1, W2.T)

    # compile and call the actual function
    f = pytensor.function([x], h2)
    f(np.random.random((5, 10)))

Running the above code generates the following error message:

.. testoutput:: testvalue

    Traceback (most recent call last):
      File "test1.py", line 31, in <module>
        f(np.random.random((5, 10)))
      File "PATH_TO_PYTENSOR/pytensor/compile/function/types.py", line 605, in __call__
        self.vm.thunks[self.vm.position_of_error])
      File "PATH_TO_PYTENSOR/pytensor/compile/function/types.py", line 595, in __call__
        outputs = self.vm()
    ValueError: Shape mismatch: x has 10 cols (and 5 rows) but y has 20 rows (and 10 cols)
    Apply node that caused the error: Dot22(x, DimShuffle{1,0}.0)
    Inputs types: [TensorType(float64, (?, ?)), TensorType(float64, (?, ?))]
    Inputs shapes: [(5, 10), (20, 10)]
    Inputs strides: [(80, 8), (8, 160)]
    Inputs scalar values: ['not scalar', 'not scalar']

    Debugprint of the apply node:
    Dot22 [id A] <TensorType(float64, (?, ?))> ''
     |x [id B] <TensorType(float64, (?, ?))>
     |DimShuffle{1,0} [id C] <TensorType(float64, (?, ?))> ''
       |Flatten{2} [id D] <TensorType(float64, (?, ?))> ''
         |DimShuffle{2,0,1} [id E] <TensorType(float64, (?, ?, ?))> ''
           |W1 [id F] <TensorType(float64, (?, ?, ?))>

    HINT: Re-running with most PyTensor optimization disabled could give you a back-traces when this node was created. This can be done with by setting the PyTensor flags 'optimizer=fast_compile'. If that does not work, PyTensor optimization can be disabled with 'optimizer=None'.

If the above is not informative enough, by instrumenting the code ever
so slightly, we can get PyTensor to reveal the exact source of the error.

.. code-block:: python

    # enable on-the-fly graph computations
    pytensor.config.compute_test_value = 'warn'

    ...

    # Input which will have the shape (5, 10)
    x  = pt.matrix('x')
    # Provide PyTensor with a default test-value
    x.tag.test_value = np.random.random((5, 10))

In the above, we are tagging the symbolic matrix *x* with a special test
value. This allows PyTensor to evaluate symbolic expressions on-the-fly (by
calling the ``perform`` method of each op), as they are being defined. Sources
of error can thus be identified with much more precision and much earlier in
the compilation pipeline. For example, running the above code yields the
following error message, which properly identifies *line 24* as the culprit.

.. code-block:: none

    Traceback (most recent call last):
      File "test2.py", line 24, in <module>
        h1 = pt.dot(x, func_of_W1)
      File "PATH_TO_PYTENSOR/pytensor/tensor/basic.py", line 4734, in dot
        return _dot(a, b)
      File "PATH_TO_PYTENSOR/pytensor/graph/op.py", line 545, in __call__
        required = thunk()
      File "PATH_TO_PYTENSOR/pytensor/graph/op.py", line 752, in rval
        r = p(n, [x[0] for x in i], o)
      File "PATH_TO_PYTENSOR/pytensor/tensor/basic.py", line 4554, in perform
        z[0] = np.asarray(np.dot(x, y))
    ValueError: matrices are not aligned

The ``compute_test_value`` mechanism works as follows:

* PyTensor ``constants`` and ``shared`` variables are used as is. No need to instrument them.
* A PyTensor *variable* (i.e. ``dmatrix``, ``vector``, etc.) should be
  given a special test value through the attribute ``tag.test_value``.
* PyTensor automatically instruments intermediate results. As such, any quantity
  derived from *x* will be given a ``tag.test_value`` automatically.

``compute_test_value`` can take the following values:

* ``off``: Default behavior. This debugging mechanism is inactive.
* ``raise``: Compute test values on the fly. Any variable for which a test
  value is required, but not provided by the user, is treated as an error. An
  exception is raised accordingly.
* ``warn``: Idem, but a warning is issued instead of an *Exception*.
* ``ignore``: Silently ignore the computation of intermediate test values, if a
  variable is missing a test value.

.. note::
  This feature is currently incompatible with ``Scan`` and also with ops
  which do not implement a ``perform`` method.

It is also possible to override variables ``__repr__`` method to have them return tag.test_value.

.. testsetup:: printtestvalue

   import pytensor
   import pytensor.tensor as pt


.. testcode:: printtestvalue

   x = pt.scalar('x')
   # Assigning test value
   x.tag.test_value = 42

   # Enable test value printing
   pytensor.config.print_test_value = True
   print(x.__repr__())

   # Disable test value printing
   pytensor.config.print_test_value = False
   print(x.__repr__())

Running the code above returns the following output:

.. testoutput:: printtestvalue

   x
   array(42.0)
   x


"How do I print an intermediate value in a function?"
-----------------------------------------------------

PyTensor provides a :class:`Print`\ :class:`Op` to do this.

.. testcode::

    import numpy as np
    import pytensor

    x = pytensor.tensor.dvector('x')

    x_printed = pytensor.printing.Print('this is a very important value')(x)

    f = pytensor.function([x], x * 5)
    f_with_print = pytensor.function([x], x_printed * 5)

    # This runs the graph without any printing
    assert np.array_equal(f([1, 2, 3]), [5, 10, 15])

    # This runs the graph with the message, and value printed
    assert np.array_equal(f_with_print([1, 2, 3]), [5, 10, 15])

.. testoutput::

    this is a very important value __str__ = [ 1.  2.  3.]

Since PyTensor runs your program in a topological order, you won't have precise
control over the order in which multiple :class:`Print`\ `Op`\s are evaluated.  For a more
precise inspection of what's being computed where, when, and how, see the discussion
:ref:`faq_monitormode`.

.. warning::

    Using this :class:`Print`\ `Op` can prevent some PyTensor rewrites from being
    applied.  So, if you use `Print` and the graph now returns NaNs for example,
    try removing the `Print`\s to see if they're the cause or not.


"How do I print a graph (before or after compilation)?"
-------------------------------------------------------

.. TODO: dead links in the next paragraph

PyTensor provides two functions, :func:`pytensor.pp` and
:func:`pytensor.printing.debugprint`, to print a graph to the terminal before or after
compilation.  These two functions print expression graphs in different ways:
:func:`pp` is more compact and somewhat math-like, and :func:`debugprint` is more verbose and true to
the underlying graph objects being printed.
PyTensor also provides :func:`pytensor.printing.pydotprint` that creates a PNG image of the graph.

You can read about them in :ref:`libdoc_printing`.

"The function I compiled is too slow; what's up?"
-------------------------------------------------

First, make sure you're running in ``FAST_RUN`` mode. Even though
``FAST_RUN`` is the default mode, insist by passing ``mode='FAST_RUN'``
to `pytensor.function`  or by setting :attr:`config.mode`
to ``FAST_RUN``.

Second, try the PyTensor :ref:`profiling <tut_profiling>`.  This will tell you which
:class:`Apply` nodes, and which :class:`Op`\s are eating up your CPU cycles.

Tips:

* Use the flags ``floatX=float32`` to require type float32 instead of float64.
  Use the PyTensor constructors `matrix`, `vector`, etc., instead of `dmatrix`, `dvector`, etc.,
  since the latter use the default detected precision and the former use only float64.
* Check in the ``profile`` mode that there is no `Dot`\ `Op` in the post-compilation
  graph while you are multiplying two matrices of the same type. `Dot` should be
  optimized to ``dot22`` when the inputs are matrices and of the same type. This can
  still happen when using ``floatX=float32`` when one of the inputs of the graph is
  of type float64.


.. _faq_monitormode:

"How do I step through a compiled function?"
--------------------------------------------

You can use `MonitorMode` to inspect the inputs and outputs of each
node being executed when the function is called. The code snipped below
shows how to print all inputs and outputs:

.. testcode::

    import pytensor

    def inspect_inputs(fgraph, i, node, fn):
        print(i, node, "input(s) value(s):", [input[0] for input in fn.inputs],
              end='')

    def inspect_outputs(fgraph, i, node, fn):
        print(" output(s) value(s):", [output[0] for output in fn.outputs])

    x = pytensor.tensor.dscalar('x')
    f = pytensor.function([x], [5 * x],
                        mode=pytensor.compile.MonitorMode(
                            pre_func=inspect_inputs,
                            post_func=inspect_outputs))
    f(3)

.. testoutput::

    0 Elemwise{mul,no_inplace}(TensorConstant{5.0}, x) input(s) value(s): [array(5.0), array(3.0)] output(s) value(s): [array(15.0)]

When using these ``inspect_inputs`` and ``inspect_outputs`` functions
with `MonitorMode`, you should see (potentially a lot of) printed output.
Every `Apply` node will be printed out, along with its position in the graph,
the arguments to the functions `Op.perform` or `COp.c_code` and the output it
computed.
Admittedly, this may be a huge amount of output to read through if you are using
large tensors, but you can choose to add logic that would, for instance, print
something out only if a certain kind of op were used, at a certain program
position, or only if a particular value showed up in one of the inputs or
outputs.  A typical example is to detect when NaN values are added into
computations, which can be achieved as follows:

.. testcode:: compiled

    import numpy

    import pytensor

    # This is the current suggested detect_nan implementation to
    # show you how it work.  That way, you can modify it for your
    # need.  If you want exactly this method, you can use
    # `pytensor.compile.monitormode.detect_nan` that will always
    # contain the current suggested version.

    def detect_nan(fgraph, i, node, fn):
        for output in fn.outputs:
            if (not isinstance(output[0], np.ndarray) and
                np.isnan(output[0]).any()):
                print('*** NaN detected ***')
                pytensor.printing.debugprint(node)
                print('Inputs : %s' % [input[0] for input in fn.inputs])
                print('Outputs: %s' % [output[0] for output in fn.outputs])
                break

    x = pytensor.tensor.dscalar('x')
    f = pytensor.function(
        [x], [pytensor.tensor.log(x) * x],
        mode=pytensor.compile.MonitorMode(
        post_func=detect_nan)
    )
    f(0)  # log(0) * 0 = -inf * 0 = NaN

.. testoutput:: compiled
   :options: +NORMALIZE_WHITESPACE

   *** NaN detected ***
   Elemwise{Composite{(log(i0) * i0)}} [id A] ''
    |x [id B]
   Inputs : [array(0.0)]
   Outputs: [array(nan)]

To help understand what is happening in your graph, you can
disable the `local_elemwise_fusion` and all in-place
rewrites. The first is a speed optimization that merges elemwise
operations together. This makes it harder to know which particular
elemwise causes the problem. The second makes some `Op`\s'
outputs overwrite their inputs. So, if an `Op` creates a bad output, you
will not be able to see the input that was overwritten in the ``post_func``
function. To disable those rewrites, define the `MonitorMode` like this:

.. testcode:: compiled

   mode = pytensor.compile.MonitorMode(post_func=detect_nan).excluding(
       'local_elemwise_fusion', 'inplace')
   f = pytensor.function([x], [pytensor.tensor.log(x) * x],
                       mode=mode)

.. note::

    The PyTensor flags ``optimizer_including``, ``optimizer_excluding``
    and ``optimizer_requiring`` aren't used by the `MonitorMode`, they
    are used only by the ``default`` mode. You can't use the ``default``
    mode with `MonitorMode`, as you need to define what you monitor.

To be sure all inputs of the node are available during the call to
``post_func``, you must also disable the garbage collector. Otherwise,
the execution of the node can garbage collect its inputs that aren't
needed anymore by the PyTensor function. This can be done with the PyTensor
flag:

.. code-block:: python

   allow_gc=False


.. TODO: documentation for link.WrapLinkerMany


How to Use ``pdb``
------------------

In the majority of cases, you won't be executing from the interactive shell
but from a set of Python scripts. In such cases, the use of the Python
debugger can come in handy, especially as your models become more complex.
Intermediate results don't necessarily have a clear name and you can get
exceptions which are hard to decipher, due to the "compiled" nature of the
functions.

Consider this example script (``ex.py``):

.. testcode::

   import numpy as np
   import pytensor
   import pytensor.tensor as pt

   a = pt.dmatrix('a')
   b = pt.dmatrix('b')

   f = pytensor.function([a, b], [a * b])

   # Matrices chosen so dimensions are unsuitable for multiplication
   mat1 = np.arange(12).reshape((3, 4))
   mat2 = np.arange(25).reshape((5, 5))

   f(mat1, mat2)

.. testoutput::
   :hide:
   :options: +ELLIPSIS

   Traceback (most recent call last):
     ...
   ValueError: Input dimension mismatch. (input[0].shape[0] = 3, input[1].shape[0] = 5)
   Apply node that caused the error: Elemwise{mul,no_inplace}(a, b)
   Toposort index: 0
   Inputs types: [TensorType(float64, (?, ?)), TensorType(float64, (?, ?))]
   Inputs shapes: [(3, 4), (5, 5)]
   Inputs strides: [(32, 8), (40, 8)]
   Inputs values: ['not shown', 'not shown']
   Outputs clients: [['output']]

   Backtrace when the node is created:
     File "<doctest default[0]>", line 8, in <module>
       f = pytensor.function([a, b], [a * b])

   HINT: Use the PyTensor flag 'exception_verbosity=high' for a debugprint and storage map footprint of this apply node.

This is actually so simple the debugging could be done easily, but it's for
illustrative purposes. As the matrices can't be multiplied element-wise
(unsuitable shapes), we get the following exception:

.. code-block:: none

    File "ex.py", line 14, in <module>
      f(mat1, mat2)
    File "/u/username/PyTensor/pytensor/compile/function/types.py", line 451, in __call__
    File "/u/username/PyTensor/pytensor/graph/link.py", line 271, in streamline_default_f
    File "/u/username/PyTensor/pytensor/graph/link.py", line 267, in streamline_default_f
    File "/u/username/PyTensor/pytensor/graph/cc.py", line 1049, in execute ValueError: ('Input dimension mismatch. (input[0].shape[0] = 3, input[1].shape[0] = 5)', Elemwise{mul,no_inplace}(a, b), Elemwise{mul,no_inplace}(a, b))

The call stack contains some useful information to trace back the source
of the error. There's the script where the compiled function was called --
but if you're using (improperly parameterized) prebuilt modules, the error
might originate from `Op`\s in these modules, not this script. The last line
tells us about the `Op` that caused the exception. In this case it's a ``mul``
involving variables with names ``a`` and ``b``. But suppose we instead had an
intermediate result to which we hadn't given a name.

After learning a few things about the graph structure in PyTensor, we can use
the Python debugger to explore the graph, and then we can get runtime
information about the error. Matrix dimensions, especially, are useful to
pinpoint the source of the error. In the printout, there are also two of the
four dimensions of the matrices involved, but for the sake of example say we'd
need the other dimensions to pinpoint the error. First, we re-launch with the
debugger module and run the program with ``c``:

.. code-block:: text

    python -m pdb ex.py
    > /u/username/experiments/doctmp1/ex.py(1)<module>()
    -> import pytensor
    (Pdb) c

Then we get back the above error printout, but the interpreter breaks in
that state. Useful commands here are

* ``up`` and ``down`` (to move up and down the call stack),
* ``l`` (to print code around the line in the current stack position),
* ``p variable_name`` (to print the string representation of ``variable_name``),
* ``p dir(object_name)``, using the Python :func:`dir` function to print the list of an object's members

Here, for example, I do ``up``, and a simple ``l`` shows me there's a local
variable ``node``. This is the ``node`` from the computation graph, so by
following the ``node.inputs``, ``node.owner`` and ``node.outputs`` links I can
explore around the graph.

That graph is purely symbolic (no data, just symbols to manipulate it
abstractly). To get information about the actual parameters, you explore the
"thunk" objects, which bind the storage for the inputs (and outputs) with the
function itself (a "thunk" is a concept related to closures). Here, to get the
current node's first input's shape, you'd therefore do
``p thunk.inputs[0][0].shape``, which prints out ``(3, 4)``.

.. _faq_dump_fct:

Dumping a Function to help debug
--------------------------------

If you are reading this, there is high chance that you emailed our
mailing list and we asked you to read this section. This section
explain how to dump all the parameter passed to
:func:`pytensor.function`. This is useful to help us reproduce a problem
during compilation and it doesn't request you to make a self contained
example.

For this to work, we need to be able to import the code for all `Op` in
the graph. So if you create your own `Op`, we will need this
code; otherwise, we won't be able to unpickle it.

.. code-block:: python

    # Replace this line:
    pytensor.function(...)
    # with
    pytensor.function_dump(filename, ...)
    # Where `filename` is a string to a file that we will write to.

Then send us ``filename``.


Breakpoint during PyTensor function execution
---------------------------------------------

You can set a breakpoint during the execution of an PyTensor function with
:class:`PdbBreakpoint <pytensor.breakpoint.PdbBreakpoint>`.
:class:`PdbBreakpoint <pytensor.breakpoint.PdbBreakpoint>` automatically
detects available debuggers and uses the first available in the following order:
`pudb`, `ipdb`, or `pdb`.
