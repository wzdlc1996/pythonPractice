import re

def _plus(x):
    return sum(x)

def _minus(x):
    return -x[0]

def _product(x):
    z = 1
    for p in x:
        z *= p
    return z

BuiltInFunctions = {
    "Plus": _plus,
    "Minus": _minus,
    "Product": _product
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
    return ASTree(z)


def parser(prog):
    """
    Parse the most simple lisp program.
    :param prog: one-line program like (Plus 1 (Minus 10))
    """
    if prog[0] != "(" or prog[-1] != ")":
        return atomParser(prog)
    else:
        items = re.findall(r"[\w\d]+|\(.*?\)", prog[1:-1])
        node = parser(items[0])
        for ch in items[1:]:
            node.addChild(parser(ch))
        return node


class ASTree:
    def __init__(self, data):
        self.data = data
        self.children = []
        self.parent = None
        
    def setParent(self, par):
        self.parent = par

    def addChild(self, child):
        assert isinstance(child, ASTree)
        child.setParent(self)
        self.children.append(child)

    def evaluate(self, knowledge=None):
        fs = {}
        fs.update(BuiltInFunctions)
        if knowledge is not None:
            fs.update(knowledge)
        if len(self.children) == 0:
            return self.data
        else:
            param = [x.evaluate(knowledge) for x in self.children]
            try:
                return fs[self.data](param)
            except KeyError:
                print(fs)
                print(self.data)
                return 0

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


def evaler(ast, knowl=None):
    assert isinstance(ast, ASTree)
    return ast.evaluate(knowl)


if __name__ == "__main__":
    ast = parser("(Plus 1 3 (Minus 2) (Product 4 5 6 7))")
    print(ast)
    print(f"Eval: {evaler(ast)}")
