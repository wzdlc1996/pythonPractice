"""
See https://www.youcandothecube.com/solve-it/3x3-solution for the algorithm
"""
import sys
import os
import numpy as np
import random
import time
random.seed()

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


def readable(oper):
    """
    return readable operations.
    i.e.,
        (xyz, True) -> Anti at `xyz`
        (-xyz, True) -> Clock at `-xyz`
        (xyz, False) -> Clock at `xyz`
        (-xyz, False) -> Anti at `-xyz`
    :param oper:
    :return:
    """
    face, acl = oper
    mod = ("-" in face) != acl
    if mod:
        return f"Clock at {face}"
    else:
        return f"Anti at {face}"


def operSimplify(oper):
    def seqreduc(oper, tim):
        if tim % 4 == 0:
            return []
        elif tim % 4 == 1:
            return [oper]
        elif tim % 4 == 3:
            return [(oper[0], not oper[1])]
        else:
            return [oper] * 2
    simp = []
    temp = []
    for x in oper:
        if len(temp) == 0 or x == temp[-1]:
            temp.append(x)
        else:
            simp.extend(seqreduc(temp[0], len(temp)))
            simp.append(x)
            temp = []
    return simp


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


def _legacy_footCornerToZFace(start, end):
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
        xe, ye = -1, -1
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


# This part we handle the last -z face. The information is the pattern as a tuple as
# (
#   -z face view, (list, indexing as
#                    back
#                   0, 1, 2
#             left  3, 4, 5  right
#                   6, 7, 8
#                    front
#   side face view, (dict, as {"f": [from left to right], "r": [...], ...}. )
# )
def genPatt(cube, mod=0):
    """
    Generate the -z face pattern of cube. This function leaves cube NOT change. mod specifies the "f" face. 0 to "y", 1
    to "-x", 2 to "-y", 3 to "x". This actually make a clockwise rot on -z and look.
    :param cube:
    :param mod:
    :return:
    """
    sidemap = {"x": "y", "y": "-x", "-x": "-y", "-y": "x", "z": "z", "-z": "-z"}
    sidef = {"f": "y", "r": "x", "l": "-x", "b": "-y", "u": "-z", "d": "z"}
    pattv = cube.view("-z")
    def pattViewRot(zf):
        return {coordRot(cord, False): val for cord, val in zf.items()}
    for _ in range(mod):
        pattv = pattViewRot(pattv)
        for sd in ["l", "r", "b", "f"]:
            sidef[sd] = sidemap[sidef[sd]]
    facev = []
    for j in range(-1, 2, 1):
        for i in range(-1, 2, 1):
            facev.append(pattv[(i, j)])
    sidev = {}
    sideedge = {
        "x": [(1, 1), (1, 0), (1, -1)],
        "y": [(-1, 1), (0, 1), (1, 1)],
        "-y": [(1, -1), (0, -1), (-1, -1)],
        "-x": [(-1, -1), (-1, 0), (-1, 1)]
    }
    for relaf, realf in sidef.items():
        if relaf in ["l", "r", "f", "b"]:
            cords = sideedge[realf]
            sidev[relaf] = [cube.view(realf)[rb.adjacentCoord(("-z", x), realf)[1]] for x in cords]
    return (facev, sidev), sidef


def pattMatch(patt, refp):
    fv, sv = patt
    fvr, svr = refp
    res = True
    for x, y in zip(fv, fvr):
        res = res and ((y is None) or (x == y))
    for k in sv.keys():
        for x, y in zip(sv[k], svr[k]):
            res = res and ((y is None) or (x == y))
    return res


def zFacePatternMatch(cube, patts):
    """
    Match any -z face pattern. Note the former patts is privileged.
    :param cube:
    :param patts:
    :return:
    """
    for x in patts:
        for mod in range(4):
            pat, sidf = genPatt(cube, mod)
            if pattMatch(pat, x):
                return sidf
    return None


def zFacePatternMatchFull(cube, patts):
    sets = []
    for x in patts:
        for mod in range(4):
            pat, sidf = genPatt(cube, mod)
            if pattMatch(pat, x):
                sets.append(sidf)
    return sets


def zFacePatternMatchPartial(cube, patts):
    sets = {}
    for x, prev in patts:
        for mod in range(4):
            pat, sidf = genPatt(cube, mod)
            if pattMatch(pat, x):
                if prev not in sets:
                    sets[prev] = []
                sets[prev].append(sidf)
    return sets[max(sets.keys())]



class RubikSolver:
    """
    TODO: rearrange private functions and readin interface
    """
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

    def _rewind(self, operlen):
        for _ in range(operlen):
            op = self.oper.pop()
            op = (op[0], not op[1])
            self.cube.rot(*op)

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

        def complete():
            zf = completeZFace()
            return zf and all([isZCornerSolved(("z", (x, y))) for x, y in [(-1, -1), (-1, 1), (1, -1), (1, 1)]])

        while not complete():

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

            # Rot the (-z face) to make the start at the right place to implement footCornerToZFace.
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

    def _finlay_simp_tree_search(self, refgen, opergen, complete):
        """
        Possibly optimization, use a smarter way to handle the search.
        Naive tree search is quite slow with a lot of useless steps
        :param refgen:
        :param opergen:
        :param complete:
        :return:
        """
        opers = []  # operation stack
        forbid = []  # forbid configuration
        path = []  # is the list of configuration
        def looptrap(path):
            """
            Check whether the path is trapped in a loop
            :param path:
            :return:
            """
            return path[-1] in path[:-1]
            # return path[-1][0] in [x[0] for x in path[:-1]]

        while not complete():

            # Begin the traverse of all possible operations (with respect to possible rel-faces (pattMatchFull))
            refs = refgen(self.cube)
            for (i, ref) in enumerate(refs):

                # If the configuration should be forbid, skip this ref
                if len(path) != 0 and (self.cube.__str__(), i) in forbid:

                    # If all refs should be skip, then this means the current state is bad. We should rewind the
                    # procedure and add the last configuration to forbid
                    if i == len(refs) - 1:
                        self._rewind(len(opers.pop()))  # rewind by pop the operation stack
                        forbid.append(path.pop())  # add the bad configuration to forbid
                        break  # quit the travers
                    continue  # skip the current ref

                # If the ref is available, do this next and push the operation to operation stack
                oper = opergen(ref)
                path.append((self.cube.__str__(), i))  # update path
                opers.append(oper)  # add to stack
                self._actOpers(oper)  # implement the operation

                # Check whether the current path is loop or not. If it is a loop, pop and add to forbid
                if looptrap(path):
                    # Forbid the entire loop chain, will significantly shorten the operation length.
                    for i in range(len(path) - 1):
                        if path[-1] == path[-2-i]:
                            break
                    for _ in range(i):
                        self._rewind(len(opers.pop()))
                        forbid.append(path.pop())
                    continue
                else:
                    break


    def _finlay_cross(self):
        """
        Subroutine for finlay solving. Make a cross first by FURU'R'F'
        :param self:
        :return:
        """
        mzColor = self.cube.getFaceColor("-z")
        def complete():
            res = self.cube.view("-z")
            return all([res[x] == mzColor for x in [(-1, 0), (1, 0), (0, 1), (0, -1)]])

        def genFaceOnlyPattRef(ind):
            return (
                [(None if i not in ind else mzColor) for i in range(9)],
                {
                    "f": [None] * 3,
                    "b": [None] * 3,
                    "r": [None] * 3,
                    "l": [None] * 3
                }
            )
        self._finlay_simp_tree_search(
            lambda x: zFacePatternMatchFull(self.cube, [
                genFaceOnlyPattRef([1, 3, 4]),
                genFaceOnlyPattRef([3, 4, 5]),
                genFaceOnlyPattRef([4])
            ]),
            lambda rel: [
                clockRotAtFace(rel["f"]),
                clockRotAtFace(rel["u"]),
                clockRotAtFace(rel["r"]),
                antiClockRotAtFace(rel["u"]),
                antiClockRotAtFace(rel["r"]),
                antiClockRotAtFace(rel["f"])
            ],
            complete
        )
        # while not complete():
        #     rel = zFacePatternMatch(self.cube, [
        #         genFaceOnlyPattRef([1, 3, 4]),
        #         genFaceOnlyPattRef([3, 4, 5]),
        #         genFaceOnlyPattRef([4])
        #     ])
        #     assert rel is not None
        #     self._actOpers([
        #         clockRotAtFace(rel["f"]),
        #         clockRotAtFace(rel["u"]),
        #         clockRotAtFace(rel["r"]),
        #         antiClockRotAtFace(rel["u"]),
        #         antiClockRotAtFace(rel["r"]),
        #         antiClockRotAtFace(rel["f"])
        #     ])

    def _finlay_face(self):
        mzColor = self.cube.getFaceColor("-z")
        def complete():
            res = self.cube.view("-z")
            return all([x == mzColor for x in res.values()])

        def genSparsePatt(faceind, serfsp):
            base = (
                [(None if i not in faceind else mzColor) for i in range(9)],
                {
                    "f": [None] * 3,
                    "b": [None] * 3,
                    "r": [None] * 3,
                    "l": [None] * 3
                }
            )
            for x, v in serfsp.items():
                for ind in v:
                    base[1][x][ind] = mzColor
            return base

        self._finlay_simp_tree_search(
            # lambda x: zFacePatternMatchFull(x, [
            #     genSparsePatt(
            #         [0, 1, 2, 3, 4, 5, 7],
            #         {"f": [0]}
            #     ),
            #     genSparsePatt(
            #         [0, 1, 3, 4, 5, 7, 8],
            #         {"f": [0]}
            #     ),
            #     genSparsePatt(
            #         [1, 2, 3, 4, 5, 7, 8],
            #         {"f": [0]}
            #     ),
            #     genSparsePatt(
            #         [1, 3, 4, 5, 7],
            #         {"l": [2]}
            #     ),
            #     genSparsePatt(
            #         [1, 3, 4, 5, 6, 7],
            #         {}
            #     )
            # ]),
            lambda x: zFacePatternMatchPartial(x, [
                (genSparsePatt(
                    [0, 1, 2, 3, 4, 5, 7],
                    {"f": [0]}
                ), 2),
                (genSparsePatt(
                    [0, 1, 3, 4, 5, 7, 8],
                    {"f": [0]}
                ), 2),
                (genSparsePatt(
                    [1, 2, 3, 4, 5, 7, 8],
                    {"f": [0]}
                ), 2),
                (genSparsePatt(
                    [1, 3, 4, 5, 7],
                    {"l": [2]}
                ), 2),
                (genSparsePatt(
                    [1, 3, 4, 5, 6, 7],
                    {}
                ), 2)
            ]),
            lambda rel: [
                clockRotAtFace(rel["r"]),
                clockRotAtFace(rel["u"]),
                antiClockRotAtFace(rel["r"]),
                clockRotAtFace(rel["u"]),
                clockRotAtFace(rel["r"]),
                clockRotAtFace(rel["u"]),
                clockRotAtFace(rel["u"]),
                antiClockRotAtFace(rel["r"])
            ],
            complete
        )

    def _finlay_corner(self):
        def corner_match():
            """
            find the matched face for corners, i.e., the element in the "-z" edge's corners whose color is the same as
            the color of ["x", "y", "-x", "-y"]
            :return???matchs: matched position, list of (face, coord)
            :return matchf: matched faces, list of "x..."
            """
            matchs = []
            matchf = []
            for adjf, coord in zip([("-x", "-y"), ("x", "y"), ("x", "-y"), ("-x", "y")], [(-1, -1), (1, 1), (1, -1), (-1, 1)]):
                temp = []
                for f in adjf:
                    fcol = self.cube.getFaceColor(f)
                    corn = rb.adjacentCoord(("-z", coord), f)
                    acol = self.cube.view(f)[corn[1]]
                    if fcol == acol:
                        matchs.append(corn)
                        temp.append(f)
                # matchf stores the pair or single face notations by the matching. If match f contains all possible
                # adjf (with length 4, all elements length 2), then corner solved. If len(matchf) is 2 and the matched
                # faces are overlapped, i.e., adjacent corners. Else it should be diagonal corner.
                if temp != []:
                    matchf.append(temp)
            return matchs, matchf
        def genRelFaces():
            while True:
                cor, fac = corner_match()
                if len(cor) >= 4:
                    break
                self._actSingleOper(("-z", True))
            if len(fac) == 4 and min([len(x) for x in fac]) == 2:
                return None
            else:
                if len(fac) == 2:
                    a, b = fac
                    inters = [x for x in a if x in b]
                    if len(inters) != 0:
                        return {
                            "u": "-z",
                            "d": "z",
                            "l": crs("-z", inters[0]),
                            "r": crs("z", inters[0]),
                            "f": neg(inters[0]),
                            "b": inters[0]
                        }
            # Then it should be diagonal case
            while True:
                cor, fac = corner_match()
                if ["x", "-y"] in fac or (["x"] in fac and ["-y"] in fac):
                    return {"u": "-z", "d": "z", "l": "y", "r": "-y", "f": "x", "b": "-x"}
                self._actSingleOper(("-z", True))

        while genRelFaces() is not None:
            relf = genRelFaces()
            self._actOpers([
                antiClockRotAtFace(relf["r"]),
                clockRotAtFace(relf["f"]),
                antiClockRotAtFace(relf["r"]),
                clockRotAtFace(relf["b"]),
                clockRotAtFace(relf["b"]),
                clockRotAtFace(relf["r"]),
                antiClockRotAtFace(relf["f"]),
                antiClockRotAtFace(relf["r"]),
                clockRotAtFace(relf["b"]),
                clockRotAtFace(relf["b"]),
                clockRotAtFace(relf["r"]),
                clockRotAtFace(relf["r"]),
                antiClockRotAtFace(relf["u"])
            ])

    def _finlay_edge(self):
        def findSolved():
            for f in ["x", "y", "-x", "-y"]:
                fcol = self.cube.getFaceColor(f)
                if all([x == fcol for x in self.cube.view(f).values()]):
                    return f

        def complete():
            res = True
            for f in ["x", "y", "-x", "-y"]:
                fcol = self.cube.getFaceColor(f)
                res = res and all([x == fcol for x in self.cube.view(f).values()])
            return res

        while not complete():

            back = findSolved()
            if back is None:
                back = "-x"
            relf = {
                "u": "-z",
                "d": "z",
                "f": neg(back),
                "b": back,
                "l": crs(back, "z"),
                "r": crs(back, "-z")
            }
            # Get the front edge color
            col = None
            for x in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                if getAlong(relf["f"], x) == relf["u"]:
                    col = self.cube.view(relf["f"])[x]
            if col == self.cube.getFaceColor(relf["l"]):
                # If it is the same to left face
                fu = clockRotAtFace
            else:
                fu = antiClockRotAtFace
            self._actOpers([
                clockRotAtFace(relf["f"]),
                clockRotAtFace(relf["f"]),
                fu(relf["u"]),
                clockRotAtFace(relf["l"]),
                antiClockRotAtFace(relf["r"]),
                clockRotAtFace(relf["f"]),
                clockRotAtFace(relf["f"]),
                antiClockRotAtFace(relf["l"]),
                clockRotAtFace(relf["r"]),
                fu(relf["u"]),
                clockRotAtFace(relf["f"]),
                clockRotAtFace(relf["f"])
            ])

    def _finlay(self):
        self._finlay_cross()
        self._finlay_face()
        self._finlay_corner()
        self._finlay_edge()











    
if __name__ == '__main__':
    # print(edgeMove(("x", (-1, 0)), ("-z", (-1, 0))))

    prob = RubikSolver()
    prob._scrambling()
    print(prob)
    # a = prob.solve()
    # print(f"solve in {len(a)} opers")
    # print(f"solve in {len(operSimplify(a))} opers (reduced)")
    # print(prob)
    # for x in reversed(operSimplify(a)):
    #     prob.cube.rot(x[0], not x[1])
    prob.solve()

    prob._finlay_cross()
    prob._finlay_face()
    prob._finlay_corner()
    prob._finlay_edge()
    print(prob)
    print(f"solved in {len(prob.oper)} rots")

    # print(prob._finlay_corner())


    # print(zFacePatternMatch(prob.cube, [([3, 3] + [None] * 7, {x: [None]*3 for x in ["l", "r", "f", "b"]})]))
    # print(f, s)








