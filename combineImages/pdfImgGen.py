import numpy as np
import matplotlib.pyplot as plt

X_mesh = np.linspace(0., 1., 20)

sinX_mesh = np.sin(X_mesh * np.pi * 2)
cosX_mesh = np.cos(X_mesh * np.pi * 2)

fig, ax = plt.subplots(figsize=(4, 6))
ax.plot(X_mesh, sinX_mesh)
ax.set_title("Sine Function, and a symbol: "+r"$\mu_\bot$")
ax.set_xlabel("Value of x")
ax.set_ylabel("Value of functions:"+r"$\sin x$")
fig.savefig("./fig1.pdf")
fig.savefig("./fig1.eps", format="eps")
#  fig.savefig("./fig1.png", format="png", dpi=1200)

fig, ax = plt.subplots(figsize=(3, 3))
ax.plot(X_mesh, cosX_mesh)
ax.set_title("Cosine Function")
fig.savefig("./fig2.eps")

fig, ax = plt.subplots(figsize=(8, 3))
ax.plot(X_mesh, cosX_mesh * sinX_mesh)
ax.set_title("Sine * Cosine Plot")
fig.savefig("./fig3.eps")

plt.close("all")