.. _libdoc_tensor_fft:

==============================================
:mod:`tensor.fft` -- Fast Fourier Transforms
==============================================

Performs Fast Fourier Transforms (FFT).

FFT gradients are implemented as the opposite Fourier transform of the output gradients.

.. warning ::
    The real and imaginary parts of the Fourier domain arrays are stored as a pair of float
    arrays, emulating complex. Since pytensor has limited support for complex
    number operations, care must be taken to manually implement operations such as gradients.

.. automodule:: pytensor.tensor.fft
   :members: rfft, irfft

For example, the code below performs the real input FFT of a box function,
which is a sinc function. The absolute value is plotted, since the phase
oscillates due to the box function being shifted to the middle of the array.

.. testcode::

    import numpy as np
    import pytensor
    import pytensor.tensor as pt
    from pytensor.tensor import fft

    x = pt.matrix('x', dtype='float64')

    rfft = fft.rfft(x, norm='ortho')
    f_rfft = pytensor.function([x], rfft)

    N = 1024
    box = np.zeros((1, N), dtype='float64')
    box[:, N//2-10: N//2+10] = 1

    out = f_rfft(box)
    c_out = np.asarray(out[0, :, 0] + 1j*out[0, :, 1])
    abs_out = abs(c_out)

.. image:: plot_fft.png
