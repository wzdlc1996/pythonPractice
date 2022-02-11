import numpy as np
import matplotlib.pyplot as plt

X_mesh = np.linspace(0., 1., 20)

sinX_mesh = np.sin(X_mesh * np.pi * 2)
cosX_mesh = np.cos(X_mesh * np.pi * 2)

fig, ax = plt.subplots()
ax.plot(X_mesh, sinX_mesh)
ax.set_title("Sine Function, and a symbol: "+r"$\mu_\bot$")
ax.set_xlabel("Value of x")
ax.set_ylabel("Value of functions:"+r"$\sin x$")
fig.savefig("./fig1.pdf")
fig.savefig("./fig1.svg")

fig, ax = plt.subplots()
ax.plot(X_mesh, cosX_mesh)
ax.set_title("Cosine Function")
fig.savefig("./fig2.pdf")

plt.close("all")