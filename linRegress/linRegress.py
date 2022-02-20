import copy
import numpy as np
from typing import Any
from scipy.stats import t as tDist

class LinRegress:
    def __init__(self, X: np.ndarray, y: np.ndarray, lazy: bool=False):
        """
        Initialize the object

        :param X: array-like data
        :param y: array-like data
        """
        if len(y) != len(X):
            raise ValueError("The data length should be the same!")

        self.ydata = y
        self.dataLen = len(y)

        if len(X.shape) == 1:
            self.deg = 1
            self.xdata = np.transpose([X])
        else:
            self.deg = X.shape[1]
            self.xdata = X

        self.X = np.hstack((np.ones((self.dataLen, 1)), self.xdata))

        if lazy:
            self.coef = None
            self.residule = None
            self.sigma = None
            self.rsquare = None
            self.invCoefMat = None
            return

        self.solve()


    def solve(self):
        # Solve the Least Square Estimation
        self.coef, self.residule, self.invCoefMat = _LSESolve(self.X, self.ydata)
        self.sigma = np.sum(self.residule ** 2) / (self.dataLen - self.deg - 1)

        ymean = np.average(self.ydata)
        self.rsquare = np.sum((self.ydata + self.residule - ymean) ** 2) / np.sum((self.ydata - ymean) ** 2)

    def calStandardError(self) -> np.ndarray:
        # Calculate the standard error of regression
        se = self.sigma * np.sqrt(self.invCoefMat.diagonal())
        return se

    def report(self, pVal=0.95) -> str:
        _, r = tDist.interval(pVal, df=self.deg)
        negpad = ' '
        pospad = negpad + ' '
        intervals = [
            f"{pospad if mid > 0 else negpad}%.4f +- (%.4f)" % (mid, r * se)
            for mid, se in zip(self.coef, self.calStandardError())
        ]
        return (
                "-----------Report the Regression-----------\n" +
                ">>> The Goodness of Regression:\n" +
                f"\tR^2 =\t{pospad}{self.rsquare}\n" +
                f">>> Confidence Interval of P={pVal}:\n\t" +
                "\n\t".join([f"a_%.0d =\t{intv}" % i for intv, i in zip(intervals, range(len(intervals)))]) +
                "\n-----------     End Report     ----------"
        )



def _LSESolve(X: np.ndarray, y: np.ndarray) -> (np.ndarray, np.ndarray, Any):
    """
    Solve the least square esitimation
    :param X:
    :param y:
    :return:
    """
    mat = np.linalg.inv(X.T.dot(X))
    a = mat.dot(X.T.dot(y))
    return a, X.dot(a) - y, mat



