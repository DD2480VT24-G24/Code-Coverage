#!/usr/bin/env python
# PyTensor tutorial
# Solution to Exercise in section 'Configuration Settings and Compiling Modes'

import numpy as np
import pytensor
import pytensor.tensor as pt


pytensor.config.floatX = "float32"

rng = np.random.default_rng(428)

N = 400
feats = 784
D = (
    rng.standard_normal((N, feats)).astype(pytensor.config.floatX),
    rng.integers(size=N, low=0, high=2).astype(pytensor.config.floatX),
)
training_steps = 10000

# Declare PyTensor symbolic variables
x = pt.matrix("x")
y = pt.vector("y")
w = pytensor.shared(rng.standard_normal(feats).astype(pytensor.config.floatX), name="w")
b = pytensor.shared(np.asarray(0.0, dtype=pytensor.config.floatX), name="b")
x.tag.test_value = D[0]
y.tag.test_value = D[1]
# print "Initial model:"
# print w.get_value(), b.get_value()

# Construct PyTensor expression graph
p_1 = 1 / (1 + pt.exp(-pt.dot(x, w) - b))  # Probability of having a one
prediction = p_1 > 0.5  # The prediction that is done: 0 or 1
xent = -y * pt.log(p_1) - (1 - y) * pt.log(1 - p_1)  # Cross-entropy
cost = pt.cast(xent.mean(), "float32") + 0.01 * (w**2).sum()  # The cost to optimize
gw, gb = pt.grad(cost, [w, b])

# Compile expressions to functions
train = pytensor.function(
    inputs=[x, y],
    outputs=[prediction, xent],
    updates={w: w - 0.01 * gw, b: b - 0.01 * gb},
    name="train",
)
predict = pytensor.function(inputs=[x], outputs=prediction, name="predict")

if any(
    x.op.__class__.__name__ in ("Gemv", "CGemv", "Gemm", "CGemm")
    for x in train.maker.fgraph.toposort()
):
    print("Used the cpu")
else:
    print("ERROR, not able to tell if pytensor used the cpu or another device")
    print(train.maker.fgraph.toposort())

for i in range(training_steps):
    pred, err = train(D[0], D[1])
# print "Final model:"
# print w.get_value(), b.get_value()

print("target values for D")
print(D[1])

print("prediction on D")
print(predict(D[0]))
