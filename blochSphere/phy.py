"""
Physics functions
"""

import numpy as np
import scipy.linalg as lg

sx = np.array(
    [[0., 1.],
     [1., 0.]], dtype=np.complex
)

sy = np.array(
    [[0., -1.j],
     [1.j, 0.]], dtype=np.complex
)

sz = np.array(
    [[1., 0.],
     [0., -1.]], dtype=np.complex
)

def ini(mode=0):
    if mode == 1:
        v = [[0], [1]]
    else:
        v = [[1], [0]]
    return np.array(v, dtype=np.complex)


def evo(state, hamil, dt):
    """
    Simulate the evolution by Trotters series

    :param state:   the initial state
    :param hamil:   the Hamiltonian, Hermitian 2x2 matrix
    :param dt:      time interval of evolution
    :return:        final state
    """
    return lg.expm(-1.j * hamil * dt).dot(state)


def toVec(state):
    """
    Map the quantum state into vector on Bloch sphere
    ref: https://en.wikipedia.org/wiki/Bloch_sphere#Plotting_pure_two-spinor_states_through_stereographic_projection

    :param state: quantum state, (2, 1) complex numpy array
    :return: (3, ) real vector
    """
    alpha, beta = np.squeeze(state)
    if np.abs(beta) == 0:
        ux, uy = 10000., 0
    else:
        ux, uy = (lambda x: (np.real(x), np.imag(x)))(alpha / beta)
    w = 1. + ux ** 2 + uy ** 2
    return np.array([2 * ux, 2 * uy, 1. - ux ** 2 - uy ** 2]) / w

def genPath(ini, h, num=20):
    path = [ini]
    ts = np.linspace(0, 1, num)
    dt = ts[1] - ts[0]
    for t in ts:
        if t == 0:
            continue
        path.append(evo(path[-1], h(t), dt))
    return np.array([toVec(x) for x in path])





