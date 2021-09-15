"""
Basic Interface for the comb
"""
import tkinter as tk
import sys
import os
from comb import artic, loadBackGround, intBackGround, A4size
from PIL import ImageTk, Image

# millimeter to pixel
millimeter2pixel_ratio = 3.7795275591  # 3.77.. pixel for 1 mm, in dpi = 96

window = tk.Tk()
window.title("test")
window.geometry("800x600")

dpi = window.winfo_fpixels('1i')  # get screen dpi
a4size_in_px = tuple(map(lambda x: int(dpi / 96 * millimeter2pixel_ratio * x), A4size))
a4w, a4h = a4size_in_px


# lab = tk.Label(window, width=100, height=100, text="hell")
# lab.pack()

canvas = tk.Canvas(window, width=400, height=600)
canvas.pack(side="right")

# Adjustable Parameters: dw, dh, x, y
relw = 0.7
relh = 0.8
dw = -5  # interval length between characters
dh = -5  # interval height between lines
x = 0.12  # left-top position-x of content relative to background
y = 0.15  # left-top position-y of content relative to background

atc = artic()
a = loadBackGround()
page = atc.makePage((int(relw * a4w), int(relh * a4h)), (dw, dh))
res = intBackGround(page, a, (x, y))
print(res.width)
res = res.resize((res.width // 2, res.height // 2))
res = ImageTk.PhotoImage(res)
imgs = canvas.create_image(0, 10, image=res, anchor="nw")
print(res.width())

window.mainloop()