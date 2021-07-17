#!/usr/bin/python


class tree:
    def __init__(self, _dic: dict, _des: list):
        self.treeDic = _dic
        self.descrip = _des
        self.body = []
        self.root = -1
        self.treeInit()
        self.setHeight()
        self.depth = max([x["height"] for x in self.body])
    
    def treeInit(self):
        self.body = []
        for i, x in enumerate(self.descrip):
            t = {
                "value": x,
                "left": None,
                "right": None,
                "parent": None,
                "isRoot": False,
                "isLeaf": False
            }
            if i in self.treeDic:
                t["left"], t["right"] = self.treeDic[i]
            else:
                t["isLeaf"] = True
            t["isRoot"] = True
            for n, (nl, nr) in self.treeDic.items():
                if i in [nl, nr]:
                    t["isRoot"] = False
            if t["isRoot"]:
                self.root = i
            self.body.append(t)

    def _travel(self, x, func, mode="mid"):
        if x not in range(len(self.body)):
            return
        if mode == "pre":
            func(self.body[x])
        self._travel(self.body[x]["left"], func, mode)
        if mode == "mid":
            func(self.body[x])
        self._travel(self.body[x]["right"], func, mode)
        if mode == "post":
            func(self.body[x])

    def setHeight(self):
        def _set(x, h):
            if x not in range(len(self.body)):
                return
            self.body[x]["height"] = h
            _set(self.body[x]["left"], h+1)
            _set(self.body[x]["right"], h+1)          
        _set(self.root, 0)

    def vis(self, x):
        if x is None:
            return [], 0
        heig = self.depth - self.body[x]["height"]
        if self.body[x]["isLeaf"]:
            tx = [self.body[x]["value"]]
            wid = max([len(x) for x in tx])
            return tx, wid

        tl, wl = self.vis(self.body[x]["left"])
        tr, wr = self.vis(self.body[x]["right"])
        text = self.body[x]["value"]

        if len(tl) >= len(tr):
            tr += [""] * (len(tl) - len(tr))
        else:
            tl += [""] * (len(tr) - len(tl))
        
        mg = 10
        hfmg = 5
        hfwl = int(wl / 2)
        hfwr = int(wr / 2)
        newwid = mg + wl + wr
        hfw = int(newwid / 2)
        hftx = int(len(text) / 2)

        lbar = "┌" + "─" * (hfw - 1 - hfwl) if wl != 0 else " " * (hfw - hfwl)
        rbar = "─" * (hfw - 1 - hfwr) + "┐" if wr != 0 else " " * (hfw - hfwr)
        if wl == 0:
            mid = "└"
        elif wr == 0:
            mid = "┘"
        else:
            mid = "┴"
        conn = " " * hfwl + lbar + mid + rbar + " " * hfwr

        t = ["", ""] + [x + " " * mg + y for (x, y) in zip(tl, tr)]
        t[1] = conn
        t[0] = " " * (hfw - hftx) + text + " " * (hfw - hftx)
        return t, wl + wr + 2 * hfmg
        

    def plainVis(self):
        class _reap:
            def __init__(self):
                self.txt = []
            def __call__(self, node):
                self.txt.append(f"val:{node['value']}, height:{node['height']}")
        ff = _reap()
        self._travel(self.root, ff, mode="pre")
        return "\n".join(ff.txt)

    def __str__(self):
        return "\n".join(self.vis(t.root)[0])

if __name__ == "__main__":
    treeDict = {
        0: (1, 2),
        1: (3, None)
    }
    description = [
        "Grand",
        "Par: L",
        "Par: R",
        "Child"
    ]
    t = tree(treeDict, description)
    print(t.plainVis())
    print(t)



    

