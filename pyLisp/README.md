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

### 自定义函数

Lisp 中允许我们进行自定义函数. 目前我们要求定义函数需要明确参数数量与返回值.

## 解释器的工作流程

解释器需要对输入的代码进行分析然后求值. 求值工作是我们熟悉的, 因此我们需要来考虑如何分析 Lisp 代码

通常, 解释器将读入的文本信息检查符合语法规则并转换为一个 **抽象语法树(abstract syntax tree)**. 