"""
Basic Interface for the comb
"""
import tkinter as tk
import sys
import os
from comb import artic, loadBackGround, intBackGround
from PIL import ImageTk, Image

window = tk.Tk()
window.title("test")
window.geometry("800x1200")

# lab = tk.Label(window, width=100, height=100, text="hell")
# lab.pack()

canvas = tk.Canvas(window, width=900, height=1200)
canvas.pack()

atc = artic()
a = loadBackGround()
page = atc.makePage((650, 930), (-5, -5))
res = intBackGround(page, a, (0.12, 0.15))
res = res.resize((res.width // 2, res.height // 2))
res = ImageTk.PhotoImage(res)
imgs = canvas.create_image(300, 100, image=res, anchor="nw")

window.mainloop()