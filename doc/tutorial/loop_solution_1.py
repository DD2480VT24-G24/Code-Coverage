#!/usr/bin/env python
# PyTensor tutorial
# Solution to Exercise in section 'Loop'

import numpy as np

import pytensor
import pytensor.tensor as pt


# 1. First example

k = pt.iscalar("k")
A = pt.vector("A")


def inner_fct(prior_result, A):
    return prior_result * A

# Symbolic description of the result
result, updates = pytensor.scan(fn=inner_fct,
                              outputs_info=pt.ones_like(A),
                              non_sequences=A, n_steps=k)

# Scan has provided us with A ** 1 through A ** k.  Keep only the last
# value. Scan notices this and does not waste memory saving them.
final_result = result[-1]

power = pytensor.function(inputs=[A, k], outputs=final_result,
                        updates=updates)

print(power(list(range(10)), 2))
# [  0.   1.   4.   9.  16.  25.  36.  49.  64.  81.]


# 2. Second example

coefficients = pt.vector("coefficients")
x = pt.scalar("x")
max_coefficients_supported = 10000

# Generate the components of the polynomial
full_range = pt.arange(max_coefficients_supported)
components, updates = pytensor.scan(fn=lambda coeff, power, free_var:
                                  coeff * (free_var ** power),
                                  sequences=[coefficients, full_range],
                                  outputs_info=None,
                                  non_sequences=x)
polynomial = components.sum()
calculate_polynomial1 = pytensor.function(inputs=[coefficients, x],
                                        outputs=polynomial)

test_coeff = np.asarray([1, 0, 2], dtype=np.float32)
print(calculate_polynomial1(test_coeff, 3))
# 19.0

# 3. Reduction performed inside scan

coefficients = pt.vector("coefficients")
x = pt.scalar("x")
max_coefficients_supported = 10000

# Generate the components of the polynomial
full_range = pt.arange(max_coefficients_supported)


outputs_info = pt.as_tensor_variable(np.asarray(0, 'float64'))

components, updates = pytensor.scan(fn=lambda coeff, power, prior_value, free_var:
                                  prior_value + (coeff * (free_var ** power)),
                                  sequences=[coefficients, full_range],
                                  outputs_info=outputs_info,
                                  non_sequences=x)

polynomial = components[-1]
calculate_polynomial = pytensor.function(inputs=[coefficients, x],
                                       outputs=polynomial, updates=updates)

test_coeff = np.asarray([1, 0, 2], dtype=np.float32)
print(calculate_polynomial(test_coeff, 3))
# 19.0
