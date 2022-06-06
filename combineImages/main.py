import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageOps, ImageFont

labelRelSize = 0.1
labelRelOvlp = 0.5
scaling_factor = 4


#  Pillow handle images with rasterization. Vector information would got loss with its default raster.
a = Image.open("./fig1.eps")
a.load(scale=scaling_factor)
a_wid, a_hei = a.size

b = Image.open("./fig2.eps")
b.load(scale=scaling_factor)
b_wid, b_hei = b.size

c = Image.open("./fig3.eps")
c.load(scale=scaling_factor)
c_wid, c_hei = c.size

"""
Indexing with struct [[a, b], [c]], together with padding and output
"""
figstruct = [[a, b], [c]]

#  Label width
labWidth = int(labelRelSize * a_wid)
labAddWid = int((1 - labelRelOvlp) * labWidth)

#  max width and total height
wid = 0
hei = 0
heightAtEachRow = []
for row in figstruct:
    row_wid = 0
    row_max_height = 0
    for fig in row:
        row_wid += fig.size[0] + labAddWid
        if fig.size[1] > row_max_height:
            row_max_height = fig.size[1]

    if row_wid > wid:
        wid = row_wid
    hei += row_max_height
    heightAtEachRow.append(row_max_height)


comb = Image.new("RGB", (wid, hei), color="white")

anch_x, anch_y = (0, 0)
index_chr = 97

fnt = ImageFont.truetype("./font.ttf", int(labWidth/2))
for i in range(len(figstruct)):
    # Begin the i-th row manipulate
    ihei = heightAtEachRow[i]
    for fig in figstruct[i]:
        anch_x += int((1 - labelRelOvlp) * labWidth)

        paddedfig = ImageOps.pad(fig, (fig.size[0], ihei), color=(255, 255, 255, 255), centering=(0, 0.5))

        comb.paste(paddedfig, (anch_x, anch_y))


        anch_x -= int((1 - labelRelOvlp) * labWidth)
        lab = Image.new("RGBA", (labWidth, ihei), color=(255, 255, 255, 0))
        d = ImageDraw.Draw(lab)
        d.text((0, 0), f"({chr(index_chr)})", fill=(0, 0, 0, 255), font=fnt)
        index_chr += 1

        comb.paste(lab, (anch_x, anch_y), lab)

        anch_x += fig.size[0] + int((1 - labelRelOvlp) * labWidth)

    anch_x = 0
    anch_y += ihei

comb.save("./comb.png")












