.. _tutloop:

====
Loop
====


Scan
====

- A general form of *recurrence*, which can be used for looping.
- *Reduction* and *map* (loop over the leading dimensions) are special cases of ``scan``.
- You ``scan`` a function along some input sequence, producing an output at each time-step.
- The function can see the *previous K time-steps* of your function.
- ``sum()`` could be computed by scanning the *z + x(i)* function over a list, given an initial state of *z=0*.
- Often a *for* loop can be expressed as a ``scan()`` operation, and ``scan`` is the closest that PyTensor comes to looping.
- Advantages of using ``scan`` over *for* loops:

  - Number of iterations to be part of the symbolic graph.
  - Computes gradients through sequential steps.
  - Slightly faster than using a *for* loop in Python with a compiled PyTensor function.
  - Can lower the overall memory usage by detecting the actual amount of memory needed.

The full documentation can be found in the library: :ref:`Scan <lib_scan>`.

`A good ipython notebook with explanation and more examples.
<https://github.com/lamblin/ccw_tutorial/blob/master/Scan_W2016/scan_tutorial.ipynb>`_

**Scan Example: Computing tanh(x(t).dot(W) + b) elementwise**

.. testcode::

  import pytensor
  import pytensor.tensor as pt
  import numpy as np

  # defining the tensor variables
  X = pt.matrix("X")
  W = pt.matrix("W")
  b_sym = pt.vector("b_sym")

  results, updates = pytensor.scan(lambda v: pt.tanh(pt.dot(v, W) + b_sym), sequences=X)
  compute_elementwise = pytensor.function(inputs=[X, W, b_sym], outputs=results)

  # test values
  x = np.eye(2, dtype=pytensor.config.floatX)
  w = np.ones((2, 2), dtype=pytensor.config.floatX)
  b = np.ones((2), dtype=pytensor.config.floatX)
  b[1] = 2

  print(compute_elementwise(x, w, b))

  # comparison with numpy
  print(np.tanh(x.dot(w) + b))

.. testoutput::

    [[ 0.96402758  0.99505475]
     [ 0.96402758  0.99505475]]
    [[ 0.96402758  0.99505475]
     [ 0.96402758  0.99505475]]

**Scan Example: Computing the sequence x(t) = tanh(x(t - 1).dot(W) + y(t).dot(U) + p(T - t).dot(V))**

.. testcode::

  import pytensor
  import pytensor.tensor as pt
  import numpy as np

  # define tensor variables
  X = pt.vector("X")
  W = pt.matrix("W")
  b_sym = pt.vector("b_sym")
  U = pt.matrix("U")
  Y = pt.matrix("Y")
  V = pt.matrix("V")
  P = pt.matrix("P")

  results, updates = pytensor.scan(lambda y, p, x_tm1: pt.tanh(pt.dot(x_tm1, W) + pt.dot(y, U) + pt.dot(p, V)),
            sequences=[Y, P[::-1]], outputs_info=[X])
  compute_seq = pytensor.function(inputs=[X, W, Y, U, P, V], outputs=results)

  # test values
  x = np.zeros((2), dtype=pytensor.config.floatX)
  x[1] = 1
  w = np.ones((2, 2), dtype=pytensor.config.floatX)
  y = np.ones((5, 2), dtype=pytensor.config.floatX)
  y[0, :] = -3
  u = np.ones((2, 2), dtype=pytensor.config.floatX)
  p = np.ones((5, 2), dtype=pytensor.config.floatX)
  p[0, :] = 3
  v = np.ones((2, 2), dtype=pytensor.config.floatX)

  print(compute_seq(x, w, y, u, p, v))

  # comparison with numpy
  x_res = np.zeros((5, 2), dtype=pytensor.config.floatX)
  x_res[0] = np.tanh(x.dot(w) + y[0].dot(u) + p[4].dot(v))
  for i in range(1, 5):
      x_res[i] = np.tanh(x_res[i - 1].dot(w) + y[i].dot(u) + p[4-i].dot(v))
  print(x_res)

.. testoutput::

    [[-0.99505475 -0.99505475]
     [ 0.96471973  0.96471973]
     [ 0.99998585  0.99998585]
     [ 0.99998771  0.99998771]
     [ 1.          1.        ]]
    [[-0.99505475 -0.99505475]
     [ 0.96471973  0.96471973]
     [ 0.99998585  0.99998585]
     [ 0.99998771  0.99998771]
     [ 1.          1.        ]]

**Scan Example: Computing norms of lines of X**

.. testcode::

  import pytensor
  import pytensor.tensor as pt
  import numpy as np

  # define tensor variable
  X = pt.matrix("X")
  results, updates = pytensor.scan(lambda x_i: pt.sqrt((x_i ** 2).sum()), sequences=[X])
  compute_norm_lines = pytensor.function(inputs=[X], outputs=results)

  # test value
  x = np.diag(np.arange(1, 6, dtype=pytensor.config.floatX), 1)
  print(compute_norm_lines(x))

  # comparison with numpy
  print(np.sqrt((x ** 2).sum(1)))

.. testoutput::

    [ 1.  2.  3.  4.  5.  0.]
    [ 1.  2.  3.  4.  5.  0.]

**Scan Example: Computing norms of columns of X**

.. testcode::

  import pytensor
  import pytensor.tensor as pt
  import numpy as np

  # define tensor variable
  X = pt.matrix("X")
  results, updates = pytensor.scan(lambda x_i: pt.sqrt((x_i ** 2).sum()), sequences=[X.T])
  compute_norm_cols = pytensor.function(inputs=[X], outputs=results)

  # test value
  x = np.diag(np.arange(1, 6, dtype=pytensor.config.floatX), 1)
  print(compute_norm_cols(x))

  # comparison with numpy
  print(np.sqrt((x ** 2).sum(0)))

.. testoutput::

    [ 0.  1.  2.  3.  4.  5.]
    [ 0.  1.  2.  3.  4.  5.]

**Scan Example: Computing trace of X**

.. testcode::

  import pytensor
  import pytensor.tensor as pt
  import numpy as np
  floatX = "float32"

  # define tensor variable
  X = pt.matrix("X")
  results, updates = pytensor.scan(lambda i, j, t_f: pt.cast(X[i, j] + t_f, floatX),
                    sequences=[pt.arange(X.shape[0]), pt.arange(X.shape[1])],
                    outputs_info=np.asarray(0., dtype=floatX))
  result = results[-1]
  compute_trace = pytensor.function(inputs=[X], outputs=result)

  # test value
  x = np.eye(5, dtype=pytensor.config.floatX)
  x[0] = np.arange(5, dtype=pytensor.config.floatX)
  print(compute_trace(x))

  # comparison with numpy
  print(np.diagonal(x).sum())

.. testoutput::

    4.0
    4.0


**Scan Example: Computing the sequence x(t) = x(t - 2).dot(U) + x(t - 1).dot(V) +  tanh(x(t - 1).dot(W)  + b)**

.. testcode::

  import pytensor
  import pytensor.tensor as pt
  import numpy as np

  # define tensor variables
  X = pt.matrix("X")
  W = pt.matrix("W")
  b_sym = pt.vector("b_sym")
  U = pt.matrix("U")
  V = pt.matrix("V")
  n_sym = pt.iscalar("n_sym")

  results, updates = pytensor.scan(lambda x_tm2, x_tm1: pt.dot(x_tm2, U) + pt.dot(x_tm1, V) + pt.tanh(pt.dot(x_tm1, W) + b_sym),
                      n_steps=n_sym, outputs_info=[dict(initial=X, taps=[-2, -1])])
  compute_seq2 = pytensor.function(inputs=[X, U, V, W, b_sym, n_sym], outputs=results)

  # test values
  x = np.zeros((2, 2), dtype=pytensor.config.floatX) # the initial value must be able to return x[-2]
  x[1, 1] = 1
  w = 0.5 * np.ones((2, 2), dtype=pytensor.config.floatX)
  u = 0.5 * (np.ones((2, 2), dtype=pytensor.config.floatX) - np.eye(2, dtype=pytensor.config.floatX))
  v = 0.5 * np.ones((2, 2), dtype=pytensor.config.floatX)
  n = 10
  b = np.ones((2), dtype=pytensor.config.floatX)

  print(compute_seq2(x, u, v, w, b, n))

  # comparison with numpy
  x_res = np.zeros((10, 2))
  x_res[0] = x[0].dot(u) + x[1].dot(v) + np.tanh(x[1].dot(w) + b)
  x_res[1] = x[1].dot(u) + x_res[0].dot(v) + np.tanh(x_res[0].dot(w) + b)
  x_res[2] = x_res[0].dot(u) + x_res[1].dot(v) + np.tanh(x_res[1].dot(w) + b)
  for i in range(2, 10):
      x_res[i] = (x_res[i - 2].dot(u) + x_res[i - 1].dot(v) +
                  np.tanh(x_res[i - 1].dot(w) + b))
  print(x_res)

.. testoutput::

    [[  1.40514825   1.40514825]
     [  2.88898899   2.38898899]
     [  4.34018291   4.34018291]
     [  6.53463142   6.78463142]
     [  9.82972243   9.82972243]
     [ 14.22203814  14.09703814]
     [ 20.07439936  20.07439936]
     [ 28.12291843  28.18541843]
     [ 39.1913681   39.1913681 ]
     [ 54.28407732  54.25282732]]
    [[  1.40514825   1.40514825]
     [  2.88898899   2.38898899]
     [  4.34018291   4.34018291]
     [  6.53463142   6.78463142]
     [  9.82972243   9.82972243]
     [ 14.22203814  14.09703814]
     [ 20.07439936  20.07439936]
     [ 28.12291843  28.18541843]
     [ 39.1913681   39.1913681 ]
     [ 54.28407732  54.25282732]]


**Scan Example: Computing the Jacobian of y = tanh(v.dot(A)) wrt x**

.. testcode::

  import pytensor
  import pytensor.tensor as pt
  import numpy as np

  # define tensor variables
  v = pt.vector()
  A = pt.matrix()
  y = pt.tanh(pt.dot(v, A))
  results, updates = pytensor.scan(lambda i: pt.grad(y[i], v), sequences=[pt.arange(y.shape[0])])
  compute_jac_t = pytensor.function([A, v], results, allow_input_downcast=True) # shape (d_out, d_in)

  # test values
  x = np.eye(5, dtype=pytensor.config.floatX)[0]
  w = np.eye(5, 3, dtype=pytensor.config.floatX)
  w[2] = np.ones((3), dtype=pytensor.config.floatX)
  print(compute_jac_t(w, x))

  # compare with numpy
  print(((1 - np.tanh(x.dot(w)) ** 2) * w).T)

.. testoutput::

    [[ 0.41997434  0.          0.41997434  0.          0.        ]
     [ 0.          1.          1.          0.          0.        ]
     [ 0.          0.          1.          0.          0.        ]]
    [[ 0.41997434  0.          0.41997434  0.          0.        ]
     [ 0.          1.          1.          0.          0.        ]
     [ 0.          0.          1.          0.          0.        ]]

Note that we need to iterate over the indices of ``y`` and not over the elements of ``y``. The reason is that scan create a placeholder variable for its internal function and this placeholder variable does not have the same dependencies than the variables that will replace it.

**Scan Example: Accumulate number of loop during a scan**

.. testcode::

  import pytensor
  import pytensor.tensor as pt
  import numpy as np

  # define shared variables
  k = pytensor.shared(0)
  n_sym = pt.iscalar("n_sym")

  results, updates = pytensor.scan(lambda:{k:(k + 1)}, n_steps=n_sym)
  accumulator = pytensor.function([n_sym], [], updates=updates, allow_input_downcast=True)

  k.get_value()
  accumulator(5)
  k.get_value()

**Scan Example: Computing tanh(v.dot(W) + b) * d where d is binomial**

.. testcode::

  import pytensor
  import pytensor.tensor as pt
  import numpy as np

  # define tensor variables
  X = pt.matrix("X")
  W = pt.matrix("W")
  b_sym = pt.vector("b_sym")

  # define shared random stream
  trng = pytensor.tensor.random.utils.RandomStream(1234)
  d=trng.binomial(size=W[1].shape)

  results, updates = pytensor.scan(lambda v: pt.tanh(pt.dot(v, W) + b_sym) * d, sequences=X)
  compute_with_bnoise = pytensor.function(inputs=[X, W, b_sym], outputs=results,
                            updates=updates, allow_input_downcast=True)
  x = np.eye(10, 2, dtype=pytensor.config.floatX)
  w = np.ones((2, 2), dtype=pytensor.config.floatX)
  b = np.ones((2), dtype=pytensor.config.floatX)

  print(compute_with_bnoise(x, w, b))

.. testoutput::

    [[ 0.96402758  0.        ]
     [ 0.          0.96402758]
     [ 0.          0.        ]
     [ 0.76159416  0.76159416]
     [ 0.76159416  0.        ]
     [ 0.          0.76159416]
     [ 0.          0.76159416]
     [ 0.          0.76159416]
     [ 0.          0.        ]
     [ 0.76159416  0.76159416]]

Note that if you want to use a random variable ``d`` that will not be updated through scan loops, you should pass this variable as a ``non_sequences`` arguments.

**Scan Example: Computing pow(A, k)**

.. testcode::

  import pytensor
  import pytensor.tensor as pt

  k = pt.iscalar("k")
  A = pt.vector("A")

  def inner_fct(prior_result, B):
      return prior_result * B

  # Symbolic description of the result
  result, updates = pytensor.scan(fn=inner_fct,
                              outputs_info=pt.ones_like(A),
                              non_sequences=A, n_steps=k)

  # Scan has provided us with A ** 1 through A ** k.  Keep only the last
  # value. Scan notices this and does not waste memory saving them.
  final_result = result[-1]

  power = pytensor.function(inputs=[A, k], outputs=final_result,
                        updates=updates)

  print(power(range(10), 2))

.. testoutput::

    [  0.   1.   4.   9.  16.  25.  36.  49.  64.  81.]


**Scan Example: Calculating a Polynomial**

.. testcode::

  import numpy
  import pytensor
  import pytensor.tensor as pt

  coefficients = pytensor.tensor.vector("coefficients")
  x = pt.scalar("x")
  max_coefficients_supported = 10000

  # Generate the components of the polynomial
  full_range=pytensor.tensor.arange(max_coefficients_supported)
  components, updates = pytensor.scan(fn=lambda coeff, power, free_var:
                                     coeff * (free_var ** power),
                                  outputs_info=None,
                                  sequences=[coefficients, full_range],
                                  non_sequences=x)

  polynomial = components.sum()
  calculate_polynomial = pytensor.function(inputs=[coefficients, x],
                                       outputs=polynomial)

  test_coeff = numpy.asarray([1, 0, 2], dtype=numpy.float32)
  print(calculate_polynomial(test_coeff, 3))

.. testoutput::

    19.0




Exercise
========

Run both examples.

Modify and execute the polynomial example to have the reduction done by ``scan``.


:download:`Solution<loop_solution_1.py>`
