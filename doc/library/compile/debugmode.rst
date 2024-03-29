
.. _debugmode:

================
:mod:`debugmode`
================

.. module:: pytensor.compile.debugmode
   :platform: Unix, Windows
   :synopsis: defines DebugMode
.. moduleauthor:: LISA

Guide
=====


The `DebugMode` evaluation mode includes a number of self-checks and assertions
that can help to diagnose several kinds of programmer errors that can lead to
incorrect output.

It is much slower to evaluate a function or method with `DebugMode` than
it would be in ``'FAST_RUN'`` or even ``'FAST_COMPILE'``.  We recommended you use
`DebugMode` during development, but not when you launch 1000 processes on
a cluster.

`DebugMode` can be used as follows:

.. testcode::

    import pytensor
    from pytensor import tensor as pt
    from pytensor.compile.debugmode import DebugMode

    x = pt.dscalar('x')

    f = pytensor.function([x], 10*x, mode='DebugMode')

    f(5)
    f(0)
    f(7)

It can also be used by setting the configuration variable :attr:`config.mode`,
or passing a `DebugMode` instance, as in

>>> f = pytensor.function([x], 10*x, mode=DebugMode(check_c_code=False))

If any problem is detected, `DebugMode` will raise an exception according to
what went wrong, either at call time (``f(5)``) or compile time (
``f = pytensor.function(x, 10*x, mode='DebugMode')``). These exceptions
should *not* be ignored; talk to your local PyTensor guru or email the
users list if you cannot make the exception go away.

Some kinds of errors can only be detected for certain input value combinations.
In the example above, there is no way to guarantee that a future call to say,
``f(-1)`` won't cause a problem.  `DebugMode` is not a silver bullet.

If you use `DebugMode` by constructing a `DebugMode` object explicitly, rather
than using the keyword ``mode="DebugMode"``, you can configure its behaviour via
constructor arguments.

Reference
=========

.. class:: DebugMode(Mode)

    Evaluation :class:`Mode` that detects internal PyTensor errors.

    This mode catches several kinds of internal error:

    - inconsistent outputs when calling the same :class:`Op` twice with the same
      inputs, for instance if :meth:`COp.c_code` and perform implementations, are
      inconsistent, or in case of incorrect handling of output memory
      (see `BadThunkOutput`)

    - a variable replacing another when their runtime values don't match.  This is a symptom of
      an incorrect rewrite step, or faulty :class:`Op` implementation (raises `BadOptimization`)

    - stochastic rewrite ordering (raises `StochasticOrder`)

    - incomplete :attr:`Op.destroy_map` specification (raises `BadDestroyMap`)

    - an :class:`Op` that returns an illegal value not matching the output :class:`Variable`\ :class:`Type` (raises
      :class:`InvalidValueError`)

    Each of these exceptions inherits from the more generic `DebugModeError`.

    If there are no internal errors, this mode behaves like FAST_RUN or FAST_COMPILE, but takes
    a little longer and uses more memory.

    If there are internal errors, this mode will raise an `DebugModeError` exception.

    .. attribute:: stability_patience = config.DebugMode__patience

        When checking the stability of rewrites, recompile the graph this many times.
        Default 10.

    .. attribute:: check_c_code = config.DebugMode__check_c

        Should we evaluate (and check) the `c_code` implementations?

        ``True`` -> yes, ``False`` -> no.

        Default yes.

    .. attribute:: check_py_code = config.DebugMode__check_py

    Should we evaluate (and check) the `perform` implementations?

        ``True`` -> yes, ``False`` -> no.

        Default yes.

    .. attribute:: check_isfinite = config.DebugMode__check_finite

        Should we check for (and complain about) ``NaN``/``Inf`` ndarray elements?

        ``True`` -> yes, ``False`` -> no.

        Default yes.

    .. attribute:: require_matching_strides = config.DebugMode__check_strides

        Check for (and complain about) Ops whose python and C
        outputs are ndarrays with different strides. (This can catch bugs, but
        is generally overly strict.)

        0 -> no check, 1 -> warn, 2 -> err.

        Default warn.

    .. method:: __init__(self, optimizer='fast_run', stability_patience=None, check_c_code=None, check_py_code=None, check_isfinite=None, require_matching_strides=None, linker=None)

        Initialize member variables.

        If any of these arguments (except `optimizer`) is not ``None``, it overrides the class default.
        The linker arguments is not used. It is set there to allow
        :meth:`Mode.requiring` and some other functions to work with `DebugMode` too.



The keyword version of `DebugMode` (which you get by using ``mode='DebugMode``)
is quite strict, and can raise several different `Exception` types.
There following are `DebugMode` exceptions you might encounter:


.. class:: DebugModeError(Exception)

    This is a generic error.  All the other exceptions inherit from this one.
    This error is typically not raised directly.
    However, you can use ``except DebugModeError: ...`` to catch any of the more
    specific types of `Exception`\s.



.. class:: BadThunkOutput(DebugModeError)

    This exception means that different calls to the same `Op` with the same
    inputs did not compute the same thing like they were supposed to.
    For instance, it can happen if the Python (i.e. :meth:`Op.perform`) and C (i.e. :meth:`COp.c_code`)
    implementations of the `Op` are inconsistent.  The problem might be a bug in
    either :meth:`Op.perform` or :meth:`COp.c_code` (or both).  It can also happen if
    :meth:`Op.perform` or :meth:`COp.c_code` does not handle correctly output memory that
    has been preallocated (for instance, if it did not clear the memory before
    accumulating into it, or if it assumed the memory layout was C-contiguous
    even if it is not).



.. class:: BadOptimization(DebugModeError)

    This exception indicates that a rewrite replaced one variable (say ``V1``)
    with another one (say ``V2``)  but at runtime, the values for ``V1`` and ``V2`` were
    different.  This is something that rewrites are not supposed to do.

    It can be tricky to identify the one-true-cause of a rewrite error, but
    this exception provides a lot of guidance.  Most of the time, the
    exception object will indicate which rewrite was at fault.
    The exception object also contains information such as a snapshot of the
    before/after graph where the rewrite introduced the error.



.. class:: BadDestroyMap(DebugModeError)

    This happens when an :meth:`Op.perform` or :meth:`COp.c_code` modifies an
    input that it wasn't supposed to.  If either the :meth:`Op.perform` or
    :meth:`COp.c_code` implementation of an :class:`Op` might modify any input, it has
    to advertise that fact via the :attr:`Op.destroy_map` attribute.

    For detailed documentation on the :attr:`Op.destroy_map` attribute, see :ref:`inplace`.


.. class:: BadViewMap(DebugModeError)

    This happens when an :meth:`Op.perform` or :meth:`COp.c_code` creates an
    alias or alias-like dependency between an input and an output, and it didn't
    warn the rewrite system via the :attr:`Op.view_map` attribute.

    For detailed documentation on the :attr:`Op.view_map` attribute, see :ref:`views`.


.. class:: StochasticOrder(DebugModeError)

    This happens when an rewrite does not perform the same graph operations
    in the same order when run several times in a row.  This can happen if any
    steps are ordered by ``id(object)`` somehow, such as via the default object
    hash function.  A stochastic rewrite invalidates the pattern of work
    whereby we debug in `DebugMode` and then run the full-size jobs in FAST_RUN.


.. class:: InvalidValueError(DebugModeError)

    This happens when some :meth:`Op.perform` or :meth:`COp.c_code` implementation computes
    an output that is invalid with respect to the type of the corresponding output
    variable.  Like if it returned a complex-valued ndarray for a ``dscalar``
    :class:`Type`.

    This can also be triggered when floating-point values such as NaN and Inf are
    introduced into the computations.  It indicates which :class:`Op` created the first
    NaN.  These floating-point values can be allowed by passing the
    ``check_isfinite=False`` argument to `DebugMode`.
