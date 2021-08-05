import numpy as np
import math

MU = -0.5


def hamil(qp: np.ndarray) -> float:
    q1, p1, q2, p2 = qp
    return -math.cos(q1) * math.sqrt(1 - p1**2) - math.cos(q2) * math.sqrt(1 - p2**2) + MU * p1 * p2


def flow(qp: np.ndarray) -> np.ndarray:
    q1, p1, q2, p2 = qp
    try:
        dq1 = MU * p2 + math.cos(q1) * p1 / math.sqrt(1 - p1**2 + 1e-6)
        dq2 = MU * p1 + math.cos(q1) * p2 / math.sqrt(1 - p2**2 + 1e-6)
        dp1 = math.sin(q1) * math.sqrt(1 - p1**2 + 1e-6)
        dp2 = math.sin(q2) * math.sqrt(1 - p2**2 + 1e-6)
    except:
        print(q1, p1 ** 2, q2, p2 ** 2)
        raise ValueError("")
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
    res = simDyna(np.array([0.1, 0., 0.1, 0.]), 5, 0.005)
    import matplotlib.pyplot as plt
    x = [z[0] for z in res]
    y = [z[1][1] for z in res]
    plt.plot(x, y)
    plt.show()
