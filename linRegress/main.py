from linRegress import LinRegress
import numpy as np

# Test linear model with error by norm distribution
def lin_mod(x):
    return 0.2 * x[0] + 0.5 * x[1] - 0.4 + 0.05 * np.random.randn()

# Two predictor variables
X1 = np.linspace(0., 10., 100)
X2 = np.linspace(0., 1., 100)

# X-Value by combination of the variables
X = np.array([[x1, x2] for x1 in X1 for x2 in X2])
# Y-Value
Y = np.array([lin_mod(x) for x in X])

# Calling the Linear Regression
linsq = LinRegress(X, Y)

# Print the report
print(linsq.report())