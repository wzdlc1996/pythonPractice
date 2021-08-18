import copy

_axis = {0: "x", 1: "y", 2: "z", 3: "-x", 4: "-y", 5: "-z"}
_iaxi = {_axis[v]: v for v in _axis}
_color = {0: "Red", 1: "Green", 2: "Yellow", 3: "Orange", 4: "Blue", 5: "White"}
_faceRotMap = {
    "x": {
        "y": [0, 1, 2],
        "z": [2, 5, 8],
        "-y": [2, 1, 0],
        "-z": [8, 5, 2]
    },
    "y": {
        "z": [0, 1, 2],
        "x": [2, 5, 8],
        "-z": [2, 1, 0],
        "-x": [8, 5, 2]
    },
    "z": {
        "x": [0, 1, 2],
        "y": [2, 5, 8],
        "-x": [2, 1, 0],
        "-y": [8, 5, 2]
    },
    "-x": {
        "y": [6, 7, 8],
        "z": [0, 3, 6],
        "-y": [8, 7, 6],
        "-z": [6, 3, 0]
    },
    "-y": {
        "z": [6, 7, 8],
        "x": [0, 3, 6],
        "-z": [8, 7, 6],
        "-x": [6, 3, 0]
    },
    "-z": {
        "x": [6, 7, 8],
        "y": [0, 3, 6],
        "-x": [8, 7, 6],
        "-y": [6, 3, 0]
    }
}


action = [
    (dire, aclo) for dire in _iaxi for aclo in [True, False]
]


def _listShift(lis: list, n: int) -> list:
    res = [0 for _ in range(len(lis))]
    for i in range(len(lis)):
        res[i] = lis[(i - n) % len(lis)]
    return res


def _shortColor(color: str) -> str:
    return color[0] + " "


def _rendColor(i: int) -> str:
    return _shortColor(_color[i])


def adjacentFaces(dir="x"):
    return list(_faceRotMap[dir].keys())


class rubik(object):
    def __init__(self):
        self.face = []
        for i in range(6):
            self.face.append([i] * 9)

    def __str__(self):
        res = ""
        for i in range(3):
            res += "  " * 3
            for ind in range(6+i, i-1, -3):
                res += _rendColor(self.face[_iaxi["z"]][ind])
            res += "  " * 6 + "\n"
        for i in range(3):
            res += "".join([_rendColor(self.face[_iaxi["-y"]][ind]) for ind in range(8-i, 1-i, -3)])
            res += "".join([_rendColor(self.face[_iaxi["x"]][ind]) for ind in range(3*i, 3*i+3)])
            res += "".join([_rendColor(self.face[_iaxi["y"]][ind]) for ind in reversed(range(8 - i, 1 - i, -3))])
            res += "".join([_rendColor(self.face[_iaxi["-x"]][ind]) for ind in reversed(range(3*i, 3*i+3))])
            res += "\n"
        for i in reversed(range(3)):
            res += "  " * 3
            for ind in range(6 + i, i - 1, -3):
                res += _rendColor(self.face[_iaxi["-z"]][ind])
            res += "  " * 6 + "\n"
        return res

    def _faceRot(self, dir=0, acl=1):
        v = [0, 1, 2, 5, 8, 7, 6, 3]
        temp = copy.copy(self.face[dir])
        for i in range(len(v)):
            self.face[dir][v[i]] = temp[v[(i + 2 * (-1) ** (acl + 1)) % len(v)]]

    def rot(self, dir="x", acl=True):
        acl = int(acl)
        edge = _faceRotMap[dir]
        dipair = list(edge.items())
        temp = [copy.copy(x) for x in self.face]  # use deepcopy would be 10 times slower
        for (d, i), (dp, ip) in zip(dipair, _listShift(dipair, (-1) ** (acl + 1))):
            for x, xp in zip(i, ip):
                self.face[_iaxi[d]][x] = temp[_iaxi[dp]][xp]

        self._faceRot(_iaxi[dir], acl)

    def view(self, dir="x"):
        res = {}
        x = 0
        # Note the relation between coordinate and index of self.face:
        # The coordinate is arranged as (coord: index)
        # (-1, 1): 0, (0, 1): 1, (1, 1): 2    | z
        # (-1, 0): 3, (0, 0): 4, (1, 0): 5    |
        # (-1,-1): 6, (0,-1): 7, (1,-1): 8    ------> y
        # In the view of x direction.
        for j in range(1, -2, -1):
            for i in range(-1, 2, 1):
                res[(i, j)] = self.face[_iaxi[dir]][x]
                x += 1
        return res

    def find(self, col: int):
        res = []
        for i, ax in _axis.items():
            if col in self.face[i]:
                res.append(ax)
        return res

    def findInEdge(self, col: int):
        res = []
        for i, ax in _axis.items():
            if col in self.face[i]:
                vw = self.view(ax)
                for x in [(-1, 0), (0, 1), (1, 0), (0, -1)]:
                    if vw[x] == col:
                        res.append((ax, x))
        return res





if __name__ == "__main__":
    rb = rubik()
    print(rb)
    rb.rot("-x", True)
    print(rb)
    print(rb.findInEdge(1))


