"""
See https://www.youcandothecube.com/solve-it/3x3-solution for the algorithm
"""
import sys
import os
import numpy as np
import random
random.seed(0)

sys.path.append(os.path.realpath(__file__ + "/../"))
import rubik as rb

cube = rb.rubik()

# Scrambling
for i in range(100):
    act = random.choice(rb.action)
    cube.rot(*act)

print(cube)


def coordRot(cord, acl=True):
    """
    rotate coordinate (x, y) pi/2 by acl value
    :param cord:
    :param acl:
    :return:
    """
    r = np.array([[0, -1], [1, 0]], dtype=int)
    if not acl:
        r = - r
    return tuple(r.dot(list(cord)))


def vec(dir):
    """
    vectorize the direction, like "x" or "-x" return "x"
    :param dir:
    :return:
    """
    if len(dir) == 2:
        return dir[-1]
    else:
        return dir


def cyc(dir, rev=False):
    """
    return cyc of direction, "x" -> "y" -> "z" -> "x"
    :param dir:
    :return:
    """
    cc = {"x": 0, "y": 1, "z": 2}
    ic = {cc[x]: x for x in cc}
    t = cc[dir]
    if rev:
        t = (t - 1) % 3
    else:
        t = (t + 1) % 3
    return ic[t]


def ort(d1, d2):
    """
    return the orthogonal direction of d1, d2
    :param d1:
    :param d2:
    :return:
    """
    t = [x for x in ["x", "y", "z"] if x not in [vec(d1), vec(d2)]]
    return t[0]


def crs(d1, d2):
    """
    return the cross of d1, d2 direction: (-x, -y) -> z
    :param d1:
    :param d2:
    :return:
    """
    neg = len(d1) + len(d2) - 2
    v1, v2 = vec(d1), vec(d2)
    if v2 != cyc(v1):
        neg += 1
    nd = ort(v1, v2)
    if neg % 2 != 0:
        return "-" + nd
    else:
        return nd



def getAlong(dir, coord):
    """
    Given face(dir) and coordinate, get the direction it indicates. like ("x", (0, 1)) should be "z"
    :param dir:
    :param coord:
    :return:
    """
    x, y = coord
    ndir = cyc(vec(dir), rev=(y != 0))
    if sum([x, y]) < 0:
        return "-" + ndir
    else:
        return ndir


def edgeMove(start, end):
    """
    Find the operation to move edge element from start to end, not preserving others.
    TODO: make the operation preserve the end face cross
    :param start:
    :param end:
    :return:
    """
    ds, (us, vs) = start
    de, (ue, ve) = end
    oper = []
    if ds not in rb.adjacentFaces(de):
        while us != ue or vs != ve:
            oper.append((ds, True))
            us, vs = coordRot((us, vs))
        ax = rb.adjacentFaces(de)[0] if ve == 0 else rb.adjacentFaces(de)[1]
        oper.extend([(ax, True)] * 2)
    else:
        dr = crs(ds, de)

        # Find rotation to make the element along `dr`.
        while getAlong(ds, (us, vs)) != dr:
            oper.append((ds, True))
            us, vs = coordRot((us, vs))

        # (ds, de, dr) forms a right-hand-frame, thus if `dr` is positive, the anti-clockwise rotation will move the
        # element along `dr` from `ds` to `de`; if `dr` is negative, the rotation should be clockwise.
        oper.append((dr, "-" not in dr))
        us, vs = [x for x in [(-1, 0), (0, 1), (1, 0), (0, -1)] if getAlong(de, x) == dr][0]

        # Rotate the final face to make the element at the target.
        while us != ue or vs != ve:
            oper.append((de, True))
            us, vs = coordRot((us, vs))
    return oper


def zCross():
    zcolor = cube.view("z")[(0, 0)]

    def completeCross():
        cls = [cube.view("z")[x] for x in [(-1, 0), (0, 1), (1, 0), (0, -1)]]
        x = True
        for cl in cls:
            x = x and (cl == zcolor)
        return x
    oper = []
    while not completeCross():
        zInEdge = cube.findInEdge(zcolor)
        done = [x for x in zInEdge if x[0] == "z"]
        tbd = [x for x in zInEdge if x[0] != "z"]
        space = [x for x in [("z", y) for y in [(-1, 0), (0, 1), (1, 0), (0, -1)]] if x not in done]
        pass






    
    
if __name__ == '__main__':
    print(edgeMove(("x", (-1, 0)), ("-z", (-1, 0))))







