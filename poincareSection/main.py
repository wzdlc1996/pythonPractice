import numpy as np
import math

MU = -0.5


def hamil(qp: np.ndarray) -> float:
    q1, p1, q2, p2 = qp
    return -math.cos(q1) * math.sqrt(1 - p1**2) - math.cos(q2) * math.sqrt(1 - p2**2) + MU * p1 * p2


def solp2(q1, p1, q2, E) -> float:
    """
    Solve p2 of the equation: hamil(q1, p1, q2, p2) = E
    :param q1:
    :param p1:
    :param q2:
    :param E:
    :return:
    """
    A = math.cos(q2)
    x = MU * p1 / A
    R = - (E + math.cos(q1) * math.sqrt(1 - p1**2)) / A
    # To be x p2 + R == sqrt(1-p2**2)
    return (- x * R + math.sqrt(x**2 + 1 - R**2)) / (x**2 + 1)



def flow(qp: np.ndarray) -> np.ndarray:
    """
    Return the Hamiltonian flow. With the rule of dq = dH/dp, dp = - dH/dq
    :param qp:
    :return:
    """
    q1, p1, q2, p2 = qp
    dq1 = MU * p2 + math.cos(q1) * p1 / math.sqrt(1 - p1**2 + 1e-6)
    dq2 = MU * p1 + math.cos(q1) * p2 / math.sqrt(1 - p2**2 + 1e-6)
    dp1 = - math.sin(q1) * math.sqrt(1 - p1**2 + 1e-6)
    dp2 = - math.sin(q2) * math.sqrt(1 - p2**2 + 1e-6)
    return np.array([dq1, dp1, dq2, dp2])


def simDyna(iniqp: np.ndarray, t_max: float, dt: float) -> list:
    res = [(0, iniqp)]
    t = 0
    x = np.copy(iniqp)
    while t < t_max:
        k1 = flow(x)
        k2 = flow(x + dt * k1 / 2)
        k3 = flow(x + dt * k2 / 2)
        k4 = flow(x + dt * k3)
        x = x + dt * (k1 + 2 * k2 + 2 * k3 + k4) / 6
        t = t + dt
        res.append((t, x))
    return res


if __name__ == "__main__":
    E = - 1
    series = []
    for _ in range(20):
        q1, q2 = 2 * math.pi * np.random.random(2)
        p1 = 0
        try:
            p2 = solp2(q1, p1, q2, E)
            res = simDyna(np.array([q1, p1, q2, p2]), 10, 0.01)
            r = []
            for i, (t, qp) in enumerate(res[10:-1]):
                p1p = res[i+1][1][3]
                if np.abs(p1) < 1e-20 and p1p > p1:
                    r.append([qp[0], qp[2]])
            series.append(r)
        except ValueError:
            continue

    import matplotlib.pyplot as plt
    for x in series:
        X, Y = np.transpose(x)
        X = np.mod(X, 2*np.pi)
        Y = np.mod(Y, 2*np.pi)
        plt.scatter(X, Y)
    plt.show()


