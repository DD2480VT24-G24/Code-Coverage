.. _libdoc_printing:

===============================================================
:mod:`printing` -- Graph Printing and Symbolic Print Statement
===============================================================

.. module:: pytensor.printing
   :platform: Unix, Windows
   :synopsis: Provides the Print Op and graph-printing routines.
.. moduleauthor:: LISA

.. testsetup::

   import pytensor

Guide
======

Printing during execution
-------------------------

Intermediate values in a computation cannot be printed in
the normal python way with the print statement, because PyTensor has no *statements*.
Instead there is the :class:`Print` Op.

>>> from pytensor import tensor as pt, function, printing
>>> x = pt.dvector()
>>> hello_world_op = printing.Print('hello world')
>>> printed_x = hello_world_op(x)
>>> f = function([x], printed_x)
>>> r = f([1, 2, 3])
hello world __str__ = [ 1.  2.  3.]

If you print more than one thing in a function like `f`, they will not
necessarily be printed in the order that you think.  The order might even depend
on which graph rewrites are applied. Strictly speaking, the order of
printing is not completely defined by the interface --
the only hard rule is that if the input of some print output `a` is
ultimately used as an input to some other print input `b` (so that `b` depends on `a`),
then `a` will print before `b`.


Printing graphs
---------------

PyTensor provides two functions (:func:`pytensor.pp` and
:func:`pytensor.printing.debugprint`) to print a graph to the terminal before or after
compilation.  These two functions print expression graphs in different ways:
:func:`pp` is more compact and math-like, :func:`debugprint` is more verbose.
PyTensor also provides :func:`pytensor.printing.pydotprint` that creates a png image of the function.

1) The first is :func:`pytensor.pp`.

>>> from pytensor import pp, grad,
>>> from pytensor import tensor as pt
>>> x = pt.dscalar('x')
>>> y = x ** 2
>>> gy = grad(y, x)
>>> pp(gy)  # print out the gradient prior to rewriting
'((fill((x ** TensorConstant{2}), TensorConstant{1.0}) * TensorConstant{2}) * (x ** (TensorConstant{2} - TensorConstant{1})))'
>>> f = function([x], gy)
>>> pp(f.maker.fgraph.outputs[0])
'(TensorConstant{2.0} * x)'

The parameter in pt.dscalar('x') in the first line is the name of this variable
in the graph. This name is used when printing the graph to make it more readable.
If no name is provided the variable x is printed as its type as returned by
``x.type()``. In this example - ``<TensorType(float64, ())>``.

The name parameter can be any string. There are no naming restrictions:
in particular, you can have many variables with the same name.
As a convention, we generally give variables a string name that is similar to the name of the variable in local scope, but
you might want to break this convention to include an object instance, or an
iteration number or other kinds of information in the name.

.. note::

    To make graphs legible, :func:`pp` hides some Ops that are actually in the graph.  For example,
    automatic DimShuffles are not shown.


2) The second function to print a graph is :func:`pytensor.printing.debugprint`

>>> pytensor.printing.debugprint(f.maker.fgraph.outputs[0])  # doctest: +NORMALIZE_WHITESPACE
Elemwise{mul,no_inplace} [id A] ''
 |TensorConstant{2.0} [id B]
 |x [id C]

Each line printed represents a Variable in the graph.
The line ``|x [id C]`` means the variable named ``x`` with debugprint identifier
[id C] is an input of the Elemwise.  If you accidentally have two variables called ``x`` in
your graph, their different debugprint identifier will be your clue.

The line ``|TensorConstant{2.0} [id B]`` means that there is a constant 2.0
with this debugprint identifier.

The line ``Elemwise{mul,no_inplace} [id A] ''`` is indented less than
the other ones, because it means there is a variable computed by multiplying
the other (more indented) ones together.

The ``|`` symbol are just there to help read big graph. The group
together inputs to a node.

Sometimes, you'll see a Variable but not the inputs underneath.  That can
happen when that Variable has already been printed.  Where else has it been
printed?  Look for debugprint identifier using the Find feature of your text
editor.

>>> pytensor.printing.debugprint(gy)  # doctest: +NORMALIZE_WHITESPACE
Elemwise{mul} [id A] ''
 |Elemwise{mul} [id B] ''
 | |Elemwise{second,no_inplace} [id C] ''
 | | |Elemwise{pow,no_inplace} [id D] ''
 | | | |x [id E]
 | | | |TensorConstant{2} [id F]
 | | |TensorConstant{1.0} [id G]
 | |TensorConstant{2} [id F]
 |Elemwise{pow} [id H] ''
   |x [id E]
   |Elemwise{sub} [id I] ''
     |TensorConstant{2} [id F]
     |InplaceDimShuffle{} [id J] ''
       |TensorConstant{1} [id K]

>>> pytensor.printing.debugprint(gy, depth=2)  # doctest: +NORMALIZE_WHITESPACE
Elemwise{mul} [id A] ''
 |Elemwise{mul} [id B] ''
 |Elemwise{pow} [id C] ''


If the depth parameter is provided, it limits the number of levels that are
shown.



3) The function :func:`pytensor.printing.pydotprint` will print a compiled pytensor function to a png file.


In the image, Apply nodes (the applications of ops) are shown as ellipses and variables are shown as boxes.
The number at the end of each label indicates graph position.
Boxes and ovals have their own set of positions, so you can have apply #1 and also a
variable #1.
The numbers in the boxes (Apply nodes) are actually their position in the
run-time execution order of the graph.
Green ovals are inputs to the graph and blue ovals are outputs.

If your graph uses shared variables, those shared
variables will appear as inputs.  Future versions of the :func:`pydotprint`
may distinguish these implicit inputs from explicit inputs.

If you give updates arguments when creating your function, these are added as
extra inputs and outputs to the graph.
Future versions of :func:`pydotprint` may distinguish these
implicit inputs and outputs from explicit inputs and outputs.


Reference
==========


.. class:: Print(Op)

    This identity-like Op has the side effect of printing a message followed by its inputs
    when it runs. Default behaviour is to print the __str__ representation. Optionally, one
    can pass a list of the input member functions to execute, or attributes to print.


    .. method:: __init__(message="", attrs=("__str__",)

        :type message: string
        :param message: prepend this to the output
        :type attrs: list of strings
        :param attrs: list of input node attributes or member functions to print.
            Functions are
            identified through callable(), executed and their return value printed.

    .. method:: __call__(x)

        :type x: a :class:`Variable`
        :param x: any symbolic variable
        :returns: symbolic identity(x)

        When you use the return-value from this function in an PyTensor function,
        running the function will print the value that `x` takes in the graph.


.. autofunction:: pytensor.printing.debugprint

.. function:: pytensor.pp(*args)

   Just a shortcut to :func:`pytensor.printing.pp`

.. autofunction:: pytensor.printing.pp(*args)

.. autofunction:: pytensor.printing.pydotprint
