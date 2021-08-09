import re

BuiltInFunctions = {
    "Plus": None,
    "Minus": None,
    "Product": None
}

class AtomParseError(Exception):
    def __init__(self, expr):
        self.expr = expr

    def __str__(self):
        return f"{self.expr} is neither built-in function nor supported data type."


def isNumber(x):
    return re.match("\d+$", x) is not None


def parseNumber(x):
    return int(x)


def atomParser(atom):
    if atom in BuiltInFunctions:
        z = atom
    elif isNumber(atom):
        z = parseNumber(atom)
    else:
        raise AtomParseError(atom)
    return tree(z)


def parser(prog):
    """
    Parse the most simple lisp program.
    :param prog: one-line program like (Plus 1 (Minus 10))
    """
    if prog[0] != "(" or prog[-1] != ")":
        return atomParser(prog)
    else:
        items = re.findall(r"[\w\d]+|\(.*\)", prog[1:-1])
        func = parser(items[0])
        node = tree(func)
        for ch in items[1:]:
            node.addChild(parser(ch))
        return node


class tree:
    def __init__(self, data):
        self.data = data
        self.children = []
        self.parent = None

    def resetData(self, newd):
        self.data = newd
        
    def setParent(self, par):
        self.parent = par

    def addChild(self, child):
        assert isinstance(child, tree)
        child.setParent(self)
        self.children.append(child)

    def __str__(self):
        chlen = len(self.children)
        if chlen == 0:
            return str(self.data)
        else:
            res = str(self.data) + "\n"
            for i, ch in enumerate(self.children):
                chres = str(ch).split("\n")
                for lin, cont in enumerate(chres):
                    if i != chlen - 1:
                        if lin == 0:
                            res += f"├───{cont}"
                        else:
                            res += f"│   {cont}"
                    else:
                        if lin == 0:
                            res += f"└───{cont}"
                        else:
                            res += f"    {cont}"
                    if lin != len(chres) - 1:
                        res += "\n"
                if i != chlen - 1:
                    res += "\n"
            return res

if __name__ == "__main__":
    print(parser("(Plus 1 2 (Minus 1))"))
