"""
See https://www.youcandothecube.com/solve-it/3x3-solution for the algorithm
"""
import sys
import os
import numpy as np
import random
import time
random.seed(204)

sys.path.append(os.path.realpath(__file__ + "/../"))
import rubik as rb


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


def coordRef(cord, vert=True) -> tuple:
    """
    reflect coordinate (x, y) vertically (by vert) or not.
    If vert == True: (x, y) -> (-x, y)
    :param cord:
    :return:
    """
    (x, y) = cord
    if vert:
        return -x, y
    else:
        return x, -y


def antiClockRotAtFace(dir):
    return dir, "-" not in dir


def clockRotAtFace(dir):
    return dir, "-" in dir


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


def neg(dir):
    """
    neglect of the dir, like "x" -> "-x", "-x" -> "x"
    :param dir:
    :return:
    """
    if len(dir) == 2:
        return dir[-1]
    else:
        return "-" + dir


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
        ax = getAlong(de, (ue, ve))
        oper.extend([(ax, True)] * 2)
    else:
        dr = crs(ds, de)

        # Find rotation to make the element along `dr`.
        while getAlong(ds, (us, vs)) != dr:
            oper.append((ds, True))
            us, vs = coordRot((us, vs))

        # Rotate the target target to be along `ds`. Then the rotation of ds will not change the de face(cross)
        while getAlong(de, (ue, ve)) != ds:
            oper.append((de, True))
            ue, ve = coordRot((ue, ve))

        # Then make the `de` target be along `dr`
        while getAlong(de, (ue, ve)) != dr:
            oper.append((de, True))
            ue, ve = coordRot((ue, ve))

        # (ds, de, dr) forms a right-hand-frame, thus if `dr` is positive, the anti-clockwise rotation will move the
        # element along `dr` from `ds` to `de`; if `dr` is negative, the rotation should be clockwise.
        # This rotation is actually the anticlockwise rot AT this face.
        # oper.append((dr, "-" not in dr))
        oper.append(antiClockRotAtFace(dr))
        us, vs = [x for x in [(-1, 0), (0, 1), (1, 0), (0, -1)] if getAlong(de, x) == dr][0]

        # Rotate the final face to make the element at the target.
        while us != ue or vs != ve:
            oper.append((de, True))
            us, vs = coordRot((us, vs))
    return oper


def isFootCorner(start):
    d, (x, y) = start
    try:
        rb.adjacentCoord(start, "-z")
        res = True
    except ValueError:
        res = False
    return res


def isFootLeft(start):
    d, (x, y) = start
    footleft = {"x": (-1, -1), "y": (-1, 1), "-x": (1, -1), "-y": (-1, -1)}
    return (x, y) == footleft[d]


def footCornerToZFace(start):
    """
    Move the foot corner to z-face. for example. ("x", (-1, -1)), will be move to ("z", (1, -1)).
    The color that adjacent to -z would be moved to the start[0] face.
    This function is used to solve the top corner such that the top layer is match
    Do not affect other corner
    :param start:
    :return:
    """
    ds, (us, vs) = start
    _, (ue, ve) = rb.adjacentCoord(start, "-z")
    oper = []
    if isFootLeft((ds, (us, vs))):
        v = crs(ds, "z")
        # oper.append(("-z", True))
        # oper.append((v, "-" in v))
        # oper.append(("-z", False))
        # oper.append((v, "-" not in v))
        oper.extend([
            clockRotAtFace("-z"),
            clockRotAtFace(v),
            antiClockRotAtFace("-z"),
            antiClockRotAtFace(v)
        ])
    else:
        v = crs("z", ds)
        # oper.append(("-z", False))
        # oper.append((v, "-" not in v))
        # oper.append(("-z", True))
        # oper.append((v, "-" in v))
        oper.extend([
            antiClockRotAtFace("-z"),
            antiClockRotAtFace(v),
            clockRotAtFace("-z"),
            clockRotAtFace(v)
        ])
    return oper, ("z", (ue, ve))


def legacy_footCornerToZFace(start, end):
    ds, (us, vs) = start
    de, (ue, ve) = end

    # Rot the "-z" face till (ds, (us, vs)) corner is behind the end corner
    oper = []
    while rb.adjacentCoord((ds, (us, vs)), "-z") != ("-z", (ue, ve)):
        oper.append(("-z", True))
        ds, (us, vs) = footRot(ds, (us, vs))

    # Two case handling
    # footright = {"x": (1, -1), "y": (-1, -1), "-x": (-1, -1), "-y": (-1, 1)}
    # footleft = {"x": (-1, -1), "y": (-1, 1), "-x": (1, -1), "-y": (-1, -1)}
    if isFootLeft((ds, (us, vs))):
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
    # for op in oper:
    #     cube.rot(*op)
    return oper


def headCornerToFoot(start):
    """
    Move the head corner (top layer) to foot. Do not affect other corner
    :param start:
    :return:
    """
    headleft = {"x": (-1, 1), "y": (1, 1), "-x": (1, 1), "-y": (1, -1)}
    d, (x, y) = start
    dp, (xp, yp) = start
    oper = []
    if (x, y) == headleft[d]:
        # oper.append((d, "-" not in d))
        # oper.append(("-z", False))
        # oper.append((d, "-" in d))
        oper.extend([
            antiClockRotAtFace(d),
            antiClockRotAtFace("-z"),
            clockRotAtFace(d)
        ])

        xp, yp = coordRot((xp, yp), "-" not in d)
        dp, (xp, yp) = footRot(dp, (xp, yp), False)
    else:
        # oper.append((d, "-" in d))
        # oper.append(("-z", True))
        # oper.append((d, "-" not in d))
        oper.extend([
            clockRotAtFace(d),
            clockRotAtFace("-z"),
            antiClockRotAtFace(d)
        ])

        xp, yp = coordRot((xp, yp), "-" in d)
        dp, (xp, yp) = footRot(dp, (xp, yp), True)
    return oper, (dp, (xp, yp))


def bottomCornerToFoot(start):
    """
    Move the bottom corner (-z face) to foot. Do not affect other corner
    :param start:
    :return:
    """
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
    # oper.append((v, "-" not in v))
    # oper.append(("-z", True))
    # oper.append((v, "-" in v))
    oper.extend([
        antiClockRotAtFace(v),
        clockRotAtFace("-z"),
        clockRotAtFace(v)
    ])
    return oper, (de, (xe, ye))


def topCornerToFoot(start):
    """
    Move the top corner (z face) to foot, to resolve the mismatch z face corner.
    Like bottomCornerToFoot, but it initially at z face. Do not affect other corner
    :param start:
    :return:
    """
    d, (x, y) = start
    oper = []
    if (x, y) == (1, 1):
        v = "y"
        de = "-y"
        xe, ye = -1, 1
    elif (x, y) == (-1, 1):
        v = "-x"
        de = "x"
        xe, ye = 1, -1
    elif (x, y) == (-1, -1):
        v = "-y"
        de = "y"
        xe, ye = -1, -1
    else:
        v = "x"
        de = "-x"
        xe, ye = 1, -1
    # oper.append((v, "-" not in v))
    # oper.append(("-z", False))
    # oper.append((v, "-" in v))
    oper.extend([
        antiClockRotAtFace(v),
        antiClockRotAtFace("-z"),
        clockRotAtFace(v)
    ])
    return oper, (de, (xe, ye))


def getMidRelFaces(front):
    """
    Get the relative face by left/right of the given face as front, and the coordinates at the front face
    :param front:
    :return:
    """
    relFace = {"u": "z", "d": "-z", "f": front, "b": neg(front), "l": crs(front, "z"), "r": crs("z", front)}
    relCoord = {}
    for dir in ["u", "d", "l", "r"]:
        adjFace = relFace[dir]
        for coord in [(-1, 0), (1, 0), (0, 1), (0, -1)]:
            if getAlong(front, coord) == adjFace:
                relCoord[dir] = coord
    return relFace, relCoord


def midMoveToRight(sface):
    """
    Move the middle to right.
    :param sface:
    :return:
    """
    relf, relc = getMidRelFaces(sface)
    return [
        antiClockRotAtFace("-z"),
        antiClockRotAtFace(relf["r"]),
        clockRotAtFace("-z"),
        clockRotAtFace(relf["r"]),
        clockRotAtFace("-z"),
        clockRotAtFace(relf["f"]),
        antiClockRotAtFace("-z"),
        antiClockRotAtFace(relf["f"])
    ]
    # oper.append(("-z", False))
    # oper.append((relf["r"], "-" not in relf["r"]))
    # oper.append(("-z", True))
    # oper.append((relf["r"], "-" in relf["r"]))
    # oper.append(("-z", True))
    # oper.append((d, "-" not in d))
    # oper.append(("-z", False))
    # oper.append((d, "-" in d))
    # return oper


def midMoveToLeft(sface):
    relf, relc = getMidRelFaces(sface)
    return [
        clockRotAtFace("-z"),
        clockRotAtFace(relf["l"]),
        antiClockRotAtFace("-z"),
        antiClockRotAtFace(relf["l"]),
        antiClockRotAtFace("-z"),
        antiClockRotAtFace(relf["f"]),
        clockRotAtFace("-z"),
        clockRotAtFace(relf["f"])
    ]
    # oper = []
    # oper.append(("-z", True))
    # oper.append((relf["l"], "-" not in relf["l"]))
    # oper.append(("-z", False))
    # oper.append((relf["l"], "-" in relf["l"]))
    # oper.append(("-z", False))
    # oper.append((d, "-" not in d))
    # oper.append(("-z", True))
    # oper.append((d, "-" in d))
    # return oper


def midMoveToCorrect(start, cube: rb.rubik):
    """
    Move the middle to correct position, to solve the middle layer
    :param start:
    :return:
    """
    d, (x, y) = start
    downColor = cube.view("-z")[rb.adjacentCoord(start, "-z")[1]]
    reff, _ = getMidRelFaces(d)
    # if cube.view(reff["l"])[(0, 0)] == downColor:
    if cube.getFaceColor(reff["l"]) == downColor:
        return midMoveToLeft(d)
    elif cube.getFaceColor(reff["r"]) == downColor:
        return midMoveToRight(d)
    else:
        return []


class RubikSolver:
    def __init__(self):
        self.cube = rb.rubik()
        self.oper = []

    def _scrambling(self):
        for i in range(100):
            act = random.choice(rb.action)
            self.cube.rot(*act)

    def __str__(self):
        return self.cube.__str__()

    def solve(self):
        self._zCross()
        self._zFace()
        self._midLay()
        return self.oper

    def _actSingleOper(self, op):
        self.oper.append(op)
        self.cube.rot(*op)

    def _actOpers(self, oper):
        for op in oper:
            self._actSingleOper(op)

    def _zCross(self):
        cube = self.cube
        zcolor = cube.getFaceColor("z")

        def completeCross():
            cls = [cube.view("z")[x] for x in [(-1, 0), (0, 1), (1, 0), (0, -1)]]
            x = True
            for cl in cls:
                x = x and (cl == zcolor)
            return x

        while not completeCross():
            zInEdge = cube.findInEdge(zcolor)
            done = [x for x in zInEdge if x[0] == "z"]
            tbd = [x for x in zInEdge if x[0] != "z"]
            space = [x for x in [("z", y) for y in [(-1, 0), (0, 1), (1, 0), (0, -1)]] if x not in done]
            s, e = tbd[0], space[0]
            mvs = edgeMove(s, e)
            self._actOpers(mvs)

        # Make this z Cross be nice, i.e., the center color of (x, y, -x, -y) match the color at the edge between them
        # and z face.
        # To achieve this, we make the zCross to -z with center color not right. Then rot -z face to make side face
        # corresponding, then rot the corresponding side face to resolve the zCross

        # Make the cross to -z face
        for f in ["x", "y", "-x", "-y"]:
            self._actOpers([(f, True)] * 2)

        # Match the side face
        for f in ["x", "y", "-x", "-y"]:
            _, refc = getMidRelFaces(f)
            _, adjc = rb.adjacentCoord((f, refc["d"]), "-z")
            while cube.getFaceColor(f) != cube.view(f)[refc["d"]] or cube.view("-z")[adjc] != zcolor:
                self._actSingleOper(("-z", True))
            self._actOpers([(f, True)] * 2)


    def _zFace(self):
        """
        Complete the z face and top layer
        :return:
        """
        cube = self.cube
        zcolor = cube.getFaceColor("z")

        # z face is made up with the same color then completeZFace() returns True
        def completeZFace():
            res = True
            for _, c in cube.view("z").items():
                res = res and (c == zcolor)
            return res

        # The adjacent color of solved corner should match the color of side face
        def isZCornerSolved(start):
            d, (x, y) = start
            if (x, y) == (-1, -1):
                u, v = "-x", "-y"
            elif (x, y) == (1, -1):
                u, v = "-y", "x"
            elif (x, y) == (1, 1):
                u, v = "x", "y"
            else:
                u, v = "y", "-x"
            _, uc = rb.adjacentCoord(start, u)
            _, vc = rb.adjacentCoord(start, v)
            return (cube.getFaceColor(u) == cube.view(u)[uc]) and (cube.getFaceColor(v) == cube.view(v)[vc])

        while not completeZFace():

            # Find the start as unsolved corner
            start = [x for x in cube.findInCorner(zcolor) if x[0] != "z" or not isZCornerSolved(x)][0]

            # Move it to foot
            if start[0] == "z":
                nop, start = topCornerToFoot(start)
            elif start[0] == "-z":
                nop, start = bottomCornerToFoot(start)
            elif not isFootCorner(start):
                nop, start = headCornerToFoot(start)
            else:
                nop, start = [], start
            self._actOpers(nop)

            print(self)
            input("aa  ")
            # Rot the (-z face) to make the start at the right place to implement footCornerToZFace.
            print(cube.getFaceColor(start[0]))
            print(cube.view("-z")[rb.adjacentCoord(start, "-z")[1]])
            print(cube.view(start[0])[start[1]])
            print(zcolor)
            while cube.view("-z")[rb.adjacentCoord(start, "-z")[1]] != cube.getFaceColor(start[0]):
                start = footRot(*start)
                self._actSingleOper(("-z", True))

            _, ce = rb.adjacentCoord(start, "-z")
            nop, _ = footCornerToZFace(start)
            self._actOpers(nop)

    def _midLay(self):
        """
        solve the middle layer
        :return:
        """
        cube = self.cube

        def findMismatchMidLay():
            # find the mismatch face, i.e., the box has no -z face color and mismatch the edge
            mismatchFace = []
            dcolor = cube.getFaceColor("-z")
            for f in ["x", "y", "-x", "-y"]:
                reff, refc = getMidRelFaces(f)
                fcolor = cube.getFaceColor(f)
                leftSqColor = cube.view(f)[refc["l"]]
                leftAdjSqColor = cube.view(reff["l"])[rb.adjacentCoord((f, refc["l"]), reff["l"])[1]]
                if leftSqColor != fcolor and (dcolor not in [leftSqColor, leftAdjSqColor]):
                    mismatchFace.append(f)
            return mismatchFace

        def findMidOptional():
            # find the optional vertical like pattern to move left or right
            opt = []
            dcolor = cube.getFaceColor("-z")
            for f in ["x", "y", "-x", "-y"]:
                reff, refc = getMidRelFaces(f)
                fcolor = cube.getFaceColor(f)
                downSqColor = cube.view(f)[refc["d"]]
                downAdjSqColor = cube.view(reff["d"])[rb.adjacentCoord((f, refc["d"]), reff["d"])[1]]
                if downSqColor == fcolor and downAdjSqColor != dcolor:
                    opt.append((f, refc["d"]))
            return opt

        def complete():
            # return whether the middle layer is solved or not
            res = True
            for f in ["x", "y", "-x", "-y"]:
                _, refc = getMidRelFaces(f)
                fcolor = cube.getFaceColor(f)
                lcolor = cube.view(f)[refc["l"]]
                rcolor = cube.view(f)[refc["r"]]
                res = res and (fcolor == lcolor) and (fcolor == rcolor)
            return res

        while not complete():
            opt = findMidOptional()
            while len(opt) == 0:
                for _ in range(4):
                    if len(opt) == 0:
                        self._actSingleOper(("-z", True))
                        opt = findMidOptional()
                if len(opt) == 0:
                    f = findMismatchMidLay()
                    self._actOpers(midMoveToLeft(f[0]))

            self._actOpers(midMoveToCorrect(opt[0], cube))



    
if __name__ == '__main__':
    # print(edgeMove(("x", (-1, 0)), ("-z", (-1, 0))))
    prob = RubikSolver()
    prob.cube.face = [[2, 0, 3, 4, 0, 4, 2, 1, 4], [2, 3, 1, 4, 1, 1, 5, 5, 4], [0, 2, 5, 2, 2, 2, 4, 2, 1], [3, 3, 5, 0, 3, 3, 2, 0, 0], [3, 5, 3, 5, 4, 4, 1, 1, 5], [1, 0, 0, 5, 5, 3, 0, 1, 4]]
    prob._zFace()
    print(prob)
    # for i in range(63, 64):
    #     random.seed(i)
    #     prob._scrambling()
    #     prob._zCross()
    #     prob._zFace()
    #
    # print(prob)
    # random.seed(64)
    # prob._scrambling()
    # prob._zCross()
    # print(prob)
    # print(prob.cube.face)








