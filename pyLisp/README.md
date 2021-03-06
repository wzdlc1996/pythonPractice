# 用python实现一个Lisp解释器

本项目旨在使用 python 来实现一个简易的 Lisp 解释器, 帮助理解 lisp 的语法, 约定 和解释机制. 同时也是使用 python 来进行一些字符串分析的练习. 

将以 [（如何（用Python）写一个（Lisp）解释器（上））, 知乎@悲路](https://zhuanlan.zhihu.com/p/28989326) 及其下篇作为参考学习, 并阅读学习 SICP 和 [Build Your Own Lisp](http://www.buildyourownlisp.com/contents) 的博文. 项目将不会很复杂, 但尽可能完备

## Lisp 的语法

我们使用 [Scheme](https://zh.wikipedia.org/wiki/Scheme) 作为实现的基础, 它是 Lisp 的一个 "方言", 并遵从极简主义的哲学. 关于 Scheme 的更详细信息可以访问 [schemers.org](https://schemers.org/) 或者 [The Scheme Programming Language Fourth Edition](https://www.scheme.com/tspl4/)

### 基本运算

Lisp 中实现基本运算的表达式是使用小括号引出的列表, 他们可以被看作一些基本的函数. 由于我们是自己进行实现的, 因此其关键字不妨沿用类似于 Mathematica 的约定来方便处理. 我们罗列一些基本运算以及它们对整数值的效果:

1.  加法: `(Plus a b c ...)`, 列表的第一个元素是函数名(我们约定首字母大写), 而这个表达式的返回值(如果它被求值)则正是其后边参数的和. `Plus` 接受任意多个参数
2.  相反数: `(Minus a)`, 它将返回 `a` 的相反数值. `Minus` 只接受一个参数
3.  乘法: `(Product a b c ...)`, 返回参数列表的连乘积, 接受任意多个参数

这些运算我们都可以通过python进行实现. 

### 自定义函数

Lisp 中允许我们进行自定义函数. 目前我们要求定义函数需要明确参数数量与返回值. 然后使用一种惰性求值机制, 即当第一次遇到自定义函数的时候, 我们先将整个表达式和参数表记录下来. 之后在此遇到时, 我们就把实际参数替换原本表达式中的参数然后进行求值. 

## 解释器的工作流程

解释器需要对输入的代码进行分析然后求值. 求值工作是我们熟悉的, 因此我们需要来考虑如何分析 Lisp 代码

通常, 解释器将读入的文本信息检查符合语法规则并转换为一个 **抽象语法树(abstract syntax tree)**. 对于 Lisp 的语法, 由于所有表达式天然地具有前缀表达式的形式, 我们直接将其实现为前缀表达式. 使用如下的 `parse` 函数:

```python{.line-numbers}
def parser(prog):
    if prog[0] != "(" or prog[-1] != ")":
        return atomParser(prog)
    else:
        items = separateByBracket(prog[1:-1])
        node = parser(items[0])
        for ch in items[1:]:
            node.addChild(parser(ch))
        return node
```

其中我们假设 `prog` 是一个一行程序的字符串, 比如 `"(Plus 1 (Minus 1))"`. `atomParser` 进行原子表达式的分析. `separateByBracket` 将字符串按照括号分隔为一个列表, 每个元素都是一个子表达式. `parser` 返回树的一个结点.

这样实现将会让每个括号分隔的表达式(列表)的第一个元素(列表头)具备特别的地位. 这带来的一个弊端是我们没有办法实现将一个返回函数的表达式作为列表头, 对lisp的语言特点有一定的损害. 但并不太会影响我们对实现一个解释器方面的理解. 为了解决这个问题也相对容易, 我们只需要一致地处理表头而不将其放在一个特别地位即可. 这可以通过不使用前缀表达式而使用列表实现, 使用 `separateByBracket` 即可, 或者为每个子表达式人为给定一个确定的表头处理.

在构造了抽象语法树后, 对它的求值便可以递归地进行. 我们再求值过程中需要明确一个存放了 函数名到函数对像 的字典作为映射, 称为 `knowledge`. 从根出发, 进行如下过程: 
1.  从已定义函数表中查找节点内容 `data`, 
2.  如果找到, 那么访问 `knowledge` 找到它得到函数对象 `f = knowledge[data]`, 否则返回错误
3.  计算该节点所有孩子节点引导子树的求值, 得到一组列表参数 `param`
4.  返回 `f(param)`

这个过程需要注意的是赋值和定义函数两个特别过程. 对于赋值, 我们需要保持它的第一个孩子为字符串(不进行计算)作为变量名, 计算第二个孩子得到值, 然后更新字典 `knowledge`. 利用递归栈的特性, 在内部的赋值过程可以将对 `knowledge` 的更新返回给外部并逐层更新, 使得外层的表达式能够使用到内层的赋值变量. 对于自定义函数, 我们的惰性求值机制就能很好地进行工作了.  