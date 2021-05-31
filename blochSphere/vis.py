"""
Functions for visualization, and run
"""

import matplotlib.pyplot as plt
from matplotlib import cm, colors
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import phy


def listPlot(ax, list, co="red"):
    x, y, z = np.transpose(list)
    ax.scatter(x, y, z, color=co, s=10)


if __name__ == "__main__":
    r = 1
    pi = np.pi
    cos = np.cos
    sin = np.sin
    phi, theta = np.mgrid[0.0:pi:100j, 0.0:2.0 * pi:100j]
    x = r * sin(phi) * cos(theta)
    y = r * sin(phi) * sin(theta)
    z = r * cos(phi)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")

    ax.plot_surface(
        x, y, z, rstride=1, cstride=1, color='c', alpha=0.3, linewidth=0)


    listPlot(
        ax,
        phy.genPath(phy.ini(), lambda t: phy.sx)
    )

    ax.view_init(elev=10., azim=0.)
    print(phy.genPath(phy.ini(), lambda t: phy.sx))

    fig.savefig("./temp.png")
