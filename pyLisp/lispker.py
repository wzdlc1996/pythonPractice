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
    return sum(x), {}


def _minus(x):
    return -x[0], {}


def _product(x):
    z = 1
    for p in x:
        z *= p
    return z, {}


def _if(x):
    if len(x) != 3:
        raise BuiltinFunctionError(x, f"If accepts 3 parameters while {len(x)} is given.")
    if x[0]:
        return x[1], {}
    else:
        return x[2], {}


# def _repeat(x):
#     return [x[0]] * x[1], {}


class builtinList(list):
    def __init__(self, x):
        super().__init__(x)
        self.x = x

    def __str__(self):
        return "(List " + " ".join([str(z) for z in self.x]) + ")"


def _list(x):
    return builtinList(x), {}


def _join(x):
    z = []
    for s in x:
        z.extend(s)
    return _list(z)


def _set(x):
    return x[1], {x[0]: x[1]}


def _equal(x):
    return int(x[0] == x[1]), {}


class lazyFunction:
    def __init__(self, param, body, known):
        self.param = param
        self.body = body
        self.known = known

    def __call__(self, rparam):
        known = {x: v for x, v in zip(self.param, rparam)}
        known.update(self.known)
        return self.body.evaluate(known)


BuiltInFunctions = {
    "Plus": _plus,
    "Minus": _minus,
    "Product": _product,
    "List": _list,
    "Join": _join,
    "Equal": _equal
}


def isNumber(x):
    return re.match("\d+$", x) is not None


def parseNumber(x):
    return int(x)


def atomParser(atom):
    if isNumber(atom):
        z = parseNumber(atom)
    else:
        z = atom
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
        if self not in self.parent.children:
            self.parent.addChild(self)

    def addChild(self, child):
        assert isinstance(child, ASTree)
        if child not in self.children:
            self.children.append(child)
            child.setParent(self)

    def addChildren(self, children):
        assert isinstance(children, list)
        for child in children:
            self.addChild(child)

    def evaluate(self, knowledge=None):
        """
        Evaluate the expression with knowledge.
        :param dict knowledge: the knowledge to use in the evaluation. Default None to use built-in functions
        :returns:
            -  result - the result of evaluation
            -  newkon - new knowledge to be updated
        """
        fs = {}
        fs.update(BuiltInFunctions)
        if knowledge is not None:
            fs.update(knowledge)
        print(fs)

        # Special operation for some built-in functions
        if isinstance(self.data, int):
            return self.data, {}
        elif self.data == "Set":
            varname = self.children[0].data
            varval, kk = self.children[1].evaluate(fs)
            res, know = _set([varname, varval])
            know.update(kk)
            return res, know
        elif self.data == "Def":
            fname = self.children[0].data
            vars = [self.children[1].data] + [x.data for x in self.children[1].children]
            expr = self.children[2]
            fbody = lazyFunction(vars, expr, fs)
            v, k = 0, {fname: fbody}
            fbody.known.update(k)
            return v, k
        elif self.data == "If":
            check, kk = self.children[0].evaluate(fs)
            ind = 1 if check else 2
            res, known = self.children[ind].evaluate(fs)
            known.update(kk)
            return res, known
        else:
            param = []
            for x in self.children:
                z, know = x.evaluate(fs)
                fs.update(know)
                param.append(z)
            if len(param) == 0:
                res, know = fs[self.data], {}
            else:
                res, know = fs[self.data](param)
            return res, know

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


class Process:
    def __init__(self):
        self.knowledge = {}
        self.knowledge.update(BuiltInFunctions)
        self.vstack = []

    def eval(self, prog):
        ast = parser(prog)
        res, newk = ast.evaluate(self.knowledge)
        self.vstack.append(res)
        self.knowledge.update(newk)

    def result(self):
        return self.vstack.pop()


def evaler(ast, knowl=None):
    assert isinstance(ast, ASTree)
    return ast.evaluate(knowl)[0]


if __name__ == "__main__":
    # Problem: special treat for the first element in the program. This makes the head should be atom. Harmful for Lisp
    # property. To overcome this, do not use ASTree, use python.list instead. The iteratively evaluation would works as
    # a tree. So we do not make a tree explicitly.
    # prog = "(Join (List (If 1 (List 1 2 3) 0)))"
    prog = "(Def f (x1 x2 x3) (Plus x1 x2))"
    ast = parser(prog)
    print(ast)
    # print(f"-\tCode:\n{prog}\n-\tAbstract Syntax Tree:\n{ast}\n-\tEval:\n{evaler(ast)}")
