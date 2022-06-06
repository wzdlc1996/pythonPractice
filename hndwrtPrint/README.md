# 手写体文章打印工具

一堆思想汇报要求手写, 为什么不试试手写体文章打印呢!

## 解决思路

本项目将实现一个简单的功能, 通过读一个信纸的pdf文件并把它置为背景, 通过都markdown文件来获得文本内容, 将文本内容映射为图片资源的手写体汉字之后, 搭建一个交互性的ui界面来调节文本的诸如大小, 间距, 行数等数据, 来实现将文本图片覆盖在信纸上, 生成一个手写体的文稿用于打印.

## 项目结构

1.  `handWriting.py`: 一个封装好的 `char -> img` 的接口. 它将用于将汉字(标点符号)字符转换为透明背景图片进而用于整合. 接口应当返回图片对象, 图片尺寸 `(w, h)` 的信息. 
    1.  在其内部, 我们应当作出如下的约定: 
    字符图片的高度是确定的, 字符图片的宽度不确定. 允许存在一定的随机浮动来模拟实际手写.
    对标点符号的处理是特别的, 它应当保证标点符号显示在图片的下方, 并且标点的宽度比通常字符更小.
2.  `comb.py`: 将文本内容进行处理的接口, 计算字符图片的排布规则, 返回整合的图片对像
    1.  在读入文章的文本内容之后, 就应当调用 `handWriting` 接口生成所有要用到的字符, 然后根据不同的传参 `(pagewidth, pageheight, dw, dh, position)` 等来计算字符图片的排布

## 有用的参考

1.  [github.com/Gsllchb/Handright](https://github.com/Gsllchb/Handright)
2.  [pyqt get start](https://lovesoo.org/2020/03/14/pyqt-getting-started/)
3.  [pyqt canvas](https://stackoverflow.com/questions/34519639/what-is-pyqts-equivalent-to-tkinters-canvas/34520076)
4.  [python word](https://www.cnblogs.com/fengfenggirl/p/python_worddb.html)
5.  [CASIA dataset for handwriting](http://www.nlpr.ia.ac.cn/databases/handwriting/Offline_database.html)
6.  [GAN for handwriting](https://cloud.tencent.com/developer/article/1729739)
7.  [知乎/汉字生成的那些坑](https://zhuanlan.zhihu.com/p/24805121)