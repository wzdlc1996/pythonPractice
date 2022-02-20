# 多元线性回归

## 线性回归的最小二乘解

考虑多元线性模型
$$
y = a_0 + \sum_{i=1}^f a_i x^i + e.
$$
其中 $e$ 为误差项. 该问题在数据集合 $D = \{(x_n, y_n): n=1,\cdots,N\}$  上的最小二乘解要求最小化目标函数
$$
\begin{aligned}
L(a) &= \sum_{n=1}^N \|y_n - a_0 - \sum_{i=1}^f a_i x^i_n\|^2\\
&=(\boldsymbol{y} - \boldsymbol{X}\boldsymbol{a})^T(\boldsymbol{y} - \boldsymbol{X}\boldsymbol{a}) \\
&=\boldsymbol{a}^T\boldsymbol{X}^T \boldsymbol{X}\boldsymbol{a} - \boldsymbol{y}^T\boldsymbol{X}\boldsymbol{a} - \boldsymbol{a}^T\boldsymbol{X}^T \boldsymbol{y} + \boldsymbol{y}^T\boldsymbol{y}
\end{aligned}
$$
其中矩阵 $\boldsymbol{y} = (y_1,\cdots,y_N)^T$ , $\boldsymbol{a} = (a_0, \cdots, a_f)^T$而
$$
\boldsymbol{X} = \begin{bmatrix}
1 & x_1^1 & x_1^2 & \cdots & x_1^f \\
1 & x_2^1 & x_2^2 & \cdots & x_2^f \\
\vdots & \vdots & \vdots & \ddots & \vdots \\
1 & x_N^1 & x_N^2 & \cdots & x_N^f
\end{bmatrix}
$$
该优化问题的解为
$$
\hat {\boldsymbol{a}} = (\boldsymbol{X}^T\boldsymbol{X})^{-1} \boldsymbol{X}^T \boldsymbol{y}
$$

## 拟合方差和优度

误差方差的无偏估计为
$$
\hat \sigma^2 = \frac 1 {N-f-1} \sum_{n=1}^N (y_n - \hat y_n)^2.
$$
多元线性回归的拟合优度 (R-square) 由下式给出:
$$
R^2 = \frac {\sum_{n=1}^N (\hat y_n - \bar{y})^2} {\sum_{n=1}^N (y_n - \bar{y})^2}
$$
其中 $\bar{y} = \boldsymbol{1}^T \boldsymbol{y} / N = \frac 1 N \sum_{n=1}^N y_n$



## 置信区间

严格的最小二乘估计方差为
$$
\textrm{Var}(\hat a_j|\boldsymbol{X}) = \sigma^2 \Big(\boldsymbol{X}^T\boldsymbol{X}\Big)^{-1}_{jj}
$$
将拟合方差替换为无偏估计我们则给出系数的**standard error**, 即
$$
\textrm{se}(\hat a_j) = \frac {\frac 1 {N-f-1} \sum_{n=1}^N (y_n - \hat y_n)^2} {(\boldsymbol{X}^T\boldsymbol{X})^{-1}_{jj}}.
$$
而置信区间就来自于经典线性模型中随机变量
$$
\frac {\hat a_j - a_j} {\textrm{se}(\hat a_j)} \sim t_{N-f-1}
$$
服从t-分布的结论. 因而对于参考值 $P$ 的置信区间 $\hat a_j \pm \textrm{se}(\hat a_j) \times z$ 应当有:
$$
P = \int_{-z}^z \textrm{PDF}_{t_{N-f-1}}(s)ds
$$
