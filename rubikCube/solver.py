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


def footRot(d, coord, acl=True):
    """
    map for foot (z = -1) in x-y part by -z face rotation
    :param d:
    :param coord:
    :return:
    """
    rmap = {
        ("x", (-1, -1)): ("y", (-1, 1)),
        ("y", (-1, 1)): ("-x", (1, -1)),
        ("-x", (1, -1)): ("-y", (-1, -1)),
        ("-y", (-1, -1)): ("x", (-1, -1)),
        ("x", (1, -1)): ("y", (-1, -1)),
        ("y", (-1, -1)): ("-x", (-1, -1)),
        ("-x", (-1, -1)): ("-y", (-1, 1)),
        ("-y", (-1, 1)): ("x", (1, -1))
    }
    if not acl:
        rmap = {v: k for k, v in rmap.items()}
    return rmap[(d, coord)]


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
    Find the operation to move edge element from start to end, preserving others.
    :param start:
    :param end:
    :return:
    """
    ds, (us, vs) = start
    de, (ue, ve) = end
    oper = []
    if ds not in rb.adjacentFaces(de):
        # Will not change the de face
        while us != ue or vs != ve:
            oper.append((ds, True))
            us, vs = coordRot((us, vs))
        ax = rb.adjacentFaces(de)[0] if ve == 0 else rb.adjacentFaces(de)[1]
        oper.extend([(ax, True)] * 2)
    else:
        dr = crs(ds, de)

        # Rotate the target target to be along `ds`. Then the rotation of ds will not change the de face(cross)
        while getAlong(de, (ue, ve)) != ds:
            oper.append((de, True))
            ue, ve = coordRot((ue, ve))

        # Find rotation to make the element along `dr`.
        while getAlong(ds, (us, vs)) != dr:
            oper.append((ds, True))
            us, vs = coordRot((us, vs))

        # Then make the `de` target be along `dr`
        while getAlong(de, (ue, ve)) != dr:
            oper.append((de, True))
            ue, ve = coordRot((ue, ve))

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
        s, e = tbd[0], space[0]
        mvs = edgeMove(s, e)
        for op in mvs:
            cube.rot(*op)
        oper.extend(mvs)

    # Make this z Cross be nice, i.e., the center color of (x, y, -x, -y) match the color at the edge between them and z
    # face.
    # When the z cross is formed, there are only two possible cases, 1) it is nice automatically, and 2) it is not nice
    # but there are two disjoint faces violate the property. Then we need only find them and rot them twice, then rot z
    # twice and rot them back, at last rot z twice to make it nice.
    def isCrossNice():
        centColors = [cube.view(x)[(0, 0)] for x in ["x", "y", "-x", "-y"]]
        edgeColors = [cube.view(x)[(0, 1)] for x in ["x", "y", "-x", "-y"]]
        return centColors == edgeColors

    while cube.view("x")[(0, 0)] != cube.view("x")[(0, 1)]:
        cube.rot("z", True)
        oper.append(("z", True))

    # This check can be optimized. But would not make much progress.
    # if cube.view("y")[(0, 0)] == cube.view("y")[(0, 1)]:
    if isCrossNice():
        return oper
    else:
        ad = ([("y", True)] * 2 + [("-y", True)] * 2 + [("z", True)] * 2) * 2
        for op in ad:
            cube.rot(*op)
        oper.extend(ad)
        return oper


def isFootCorner(start):
    d, (x, y) = start
    try:
        rb.adjacentCoord(start, "-z")
        res = True
    except ValueError:
        res = False
    return res


def footCornerToZFace(start, end):
    ds, (us, vs) = start
    de, (ue, ve) = end

    # Rot the "-z" face till (ds, (us, vs)) corner is behind the end corner
    oper = []
    while rb.adjacentCoord((ds, (us, vs)), "-z") != ("-z", (ue, ve)):
        oper.append(("-z", True))
        ds, (us, vs) = footRot(ds, (us, vs))

    # Two case handling
    footright = {"x": (1, -1), "y": (-1, -1), "-x": (-1, -1), "-y": (-1, 1)}
    footleft = {"x": (-1, -1), "y": (-1, 1), "-x": (1, -1), "-y": (-1, -1)}
    if (us, vs) == footleft[ds]:
        v = crs(ds, de)
        oper.append(("-z", True))
        oper.append((v, "-" in v))
        oper.append(("-z", False))
        oper.append((v, "-" not in v))
    else:
        v = crs(de, ds)
        oper.append(("-z", False))
        oper.append((v, "-" not in v))
        oper.append(("-z", True))
        oper.append((v, "-" in v))
    for op in oper:
        cube.rot(*op)
    return oper


def headCornerToFoot(start):
    headleft = {"x": (-1, 1), "y": (1, 1), "-x": (1, 1), "-y": (1, -1)}
    d, (x, y) = start
    dp, (xp, yp) = start
    oper = []
    if (x, y) == headleft[d]:
        oper.append((d, "-" not in d))
        xp, yp = coordRot((xp, yp), True)
        oper.append(("-z", True))
        dp, (xp, yp) = footRot(dp, (xp, yp), False)
        oper.append((d, "-" in d))
    else:
        oper.append((d, "-" in d))
        xp, yp = coordRot((xp, yp), False)
        oper.append(("-z", False))
        dp, (xp, yp) = footRot(dp, (xp, yp), True)
        oper.append((d, "-" not in d))
    for op in oper:
        cube.rot(*op)
    return oper, (dp, (xp, yp))


def bottomCornerToFoot(start):
    d, (x, y) = start
    oper = []
    if (x, y) == (1, 1):
        v = "y"
        de = "-y"
        xe, ye = -1, -1
    elif (x, y) == (-1, 1):
        v = "-x"
        de = "x"
        xe, ye = -1, -1
    elif (x, y) == (-1, -1):
        v = "-y"
        de = "y"
        xe, ye = -1, 1
    else:
        v = "x"
        de = "-x"
        xe, ye = 1, -1
    oper.append((v, "-" not in v))
    oper.append(("-z", True))
    oper.append((v, "-" in v))
    for op in oper:
        cube.rot(*op)
    return oper, (de, (xe, ye))


def zFace():
    zcolor = cube.view("z")[(0, 0)]
    oper = zCross()
    def completeZFace():
        res = True
        for _, c in cube.view("z").items():
            res = res and (c == zcolor)
        return res

    while not completeZFace():
        con = cube.findInCorner(zcolor)
        spc = [("z", x) for x, c in cube.view("z").items() if c != zcolor]
        tbd = [x for x in con if x[0] != "z"]
        start = tbd[0]
        end = spc[0]
        if start[0] == "-z":
            nop, start = bottomCornerToFoot(start)
            nop += footCornerToZFace(start, end)
            oper += nop
        else:
            if isFootCorner(start):
                oper += footCornerToZFace(start, end)
            else:
                nop, start = headCornerToFoot(start)
                oper += nop + footCornerToZFace(start, end)

    return oper



    
if __name__ == '__main__':
    # print(edgeMove(("x", (-1, 0)), ("-z", (-1, 0))))
    print(zFace())
    print(cube)








