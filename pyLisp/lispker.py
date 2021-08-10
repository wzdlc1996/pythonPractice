import re


class BuiltinFunctionError(Exception):
    def __init__(self, expr, message):
        self.expr = expr
        self.mess = message

    def __str__(self):
        return f"Input {self.expr} {self.mess}"


class AtomParseError(Exception):
    def __init__(self, expr):
        self.expr = expr

    def __str__(self):
        return f"{self.expr} is neither built-in function nor supported data type."


def _plus(x):
    return sum(x), False


def _minus(x):
    return -x[0], False


def _product(x):
    z = 1
    for p in x:
        z *= p
    return z, False


def _if(x):
    if len(x) != 3:
        raise BuiltinFunctionError(x, f"If accepts 3 parameters while {len(x)} is given.")
    if x[0]:
        return x[1], False
    else:
        return x[2], False


def _repeat(x):
    return [x[1]] * x[0], False


class builtinList(list):
    def __init__(self, x):
        super().__init__(x)
        self.x = x

    def __str__(self):
        return "(List " + " ".join([str(z) for z in self.x]) + ")"


def _list(x):
    return builtinList(x), True


def _join(x):
    z = []
    for s in x:
        z.extend(s)
    return _list(z)


BuiltInFunctions = {
    "Plus": _plus,
    "Minus": _minus,
    "Product": _product,
    "If": _if,
    "Repeat": _repeat,
    "List": _list,
    "Join": _join
}


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


def bracketSubIntegrate(sub) -> str:
    x = ""
    for i, item in enumerate(sub):
        if item == "(":
            x += "("
        elif item == ")":
            x = x[:-1] + ")"
            if i != len(sub) - 1:
                x += " "
        else:
            x += item + " "
    return x


def separateByBracket(prog) -> list:
    """
    Separate the most simple lisp program by brackets
    :param prog: one-line program without outer like "Plus 1 (Minus 10)"
    :return: the list of items, like ["Plus", "1", "(Minus 10)"]
    """
    if "(" not in prog and ")" not in prog:
        return prog.split()
    else:
        splitted = prog.replace("(", " ( ").replace(")", " ) ").split()
        res = []
        meetBracket = False
        tembrck = 0
        for x in splitted:
            if x == "(":
                tembrck += 1
                if not meetBracket:
                    meetBracket = True
                    res.append(["("])
                    continue
            elif x == ")":
                tembrck -= 1
                if meetBracket and tembrck == 0:
                    meetBracket = False
                    res[-1].append(")")
                    res[-1] = bracketSubIntegrate(res[-1])
                    continue
            if not meetBracket:
                res.append(x)
            else:
                res[-1].append(x)
        return res


def parser(prog):
    """
    Parse the most simple lisp program.
    :param prog: one-line program like (Plus 1 (Minus 10))
    """
    if prog[0] != "(" or prog[-1] != ")":
        return atomParser(prog)
    else:
        items = separateByBracket(prog[1:-1])
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
            return self.data, False
        else:
            param = []
            for x in self.children:
                z, holdStruct = x.evaluate(knowledge)
                if not holdStruct and isinstance(z, list):
                    param.extend(z)
                else:
                    param.append(z)
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
    return ast.evaluate(knowl)[0]


if __name__ == "__main__":
    prog = "(Join (List 1) (List (If 1 (List 1 2 3) 0)))"
    ast = parser(prog)
    print(f"-\tCode:\n{prog}\n-\tAbstract Syntax Tree:\n{ast}\n-\tEval:\n{evaler(ast)}")
