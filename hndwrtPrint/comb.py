"""
Combine the content and background
"""
import handWriting as hw
import PIL
import re
import random


gener = hw.char2imgFromFont()
A4size = (210, 297)
A4hwratio = 297 / 210


def _genImgsForChars(chars, gen=gener):
    res = []
    for x in chars:
        img, (w, h) = gen(x)
        res.append({"img": img, "width": w, "height": h})
    return res


class _lag_artic:
    """
    Handle the article with homogeneous char set
    """
    def __init__(self, filename="./content.md"):
        with open(filename, "r", encoding="utf8") as f:
            """
            self.main should be text list separated by the paragraph. The title is the first element
            """
            self.main_proto = f.readlines()
            self.main_proto = [x[:-1] for x in self.main_proto if x != "\n"]

        self.main = {
            "title": self.main_proto[0],
            "paras": self.main_proto[1:]
        }
        self.chars = re.findall(r"[^\n]", "".join(self.main_proto))
        self.charNum = len(self.chars)
        self.paraNum = len(self.main["paras"])

    def splitLines(self, lineMaxCharNum, paraIndent=True):
        lines = [list(self.main["title"]), [""]]
        for x in self.main["paras"]:
            if paraIndent:
                para = "  " + x
            else:
                para = x
            lines += [list(para)[i:i+lineMaxCharNum] for i in range(0, len(para), lineMaxCharNum)]
        return lines

    def splitPages(self, lineWid: int, lineNum: int, paraIndent=True, titleCent=True) -> list:
        tit = list(self.main["title"])
        if titleCent:
            added = int((lineWid - len(tit)) / 2)
            tit = ["  "] * added + tit + ["  "] * added
        lines = [tit, [""]]
        for x in self.main["paras"]:
            if paraIndent:
                para = "  " + x
            else:
                para = x

            lines += [list(para)[i:i+lineWid] for i in range(0, len(para), lineWid)]
        lines = [lines[i:i+lineNum] for i in range(0, len(lines), lineNum)]
        return lines


class artic:
    """
    Handle the article with real-time generated char set
    """
    def __init__(self, filename="./content.md", gen=gener):
        with open(filename, "r", encoding="utf8") as f:
            """
            self.main should be text list separated by the paragraph. The title is the first element
            """
            self.main_proto = f.readlines()
            self.main_proto = [x[:-1] for x in self.main_proto if x != "\n"]

        self.gen = gen
        self.charHeight = self.gen.getHeight()
        self.charMWidth = self.gen.getWidth()

        self.main = {
            "title": self.main_proto[0],
            "paras": self.main_proto[1:]
        }
        self.char = {
            "title": _genImgsForChars(self.main["title"], self.gen),
            "paras": [_genImgsForChars(x, self.gen) for x in self.main["paras"]]
        }
        self.paraNum = len(self.main["paras"])
        self.bkpt = [0, 0]

    def make(self, boxSize, dSize, pageOffSet=None):
        res = []
        i = 0
        while self.bkpt[0] < self.paraNum and len(res) < 10:
            iniPage = i == 0
            print(self.bkpt)
            res.append(self.makePage(boxSize=boxSize, dSize=dSize, iniPage=iniPage, pageOffSet=pageOffSet))
            i += 1
        return res

    def makePage(self, boxSize, dSize, iniPage=True, pageOffSet=None):
        pw, ph = boxSize
        dw, dh = dSize

        def resetPos():
            if pageOffSet is None:
                return 0, 0
            else:
                return pageOffSet

        x, y = resetPos()

        # Gen empty image
        img = PIL.Image.new("RGBA", boxSize, None)
        if iniPage:
            self.bkpt = [0, 0]
            titleLen = (len(self.main["title"]) - 1) * dw + sum([x["width"] for x in self.char["title"]])
            x += int((pw - titleLen) / 2)
            for ch in self.char["title"]:
                chImg = ch["img"]
                img.paste(chImg, (x, y), chImg)
                x += ch["width"] + dw
            x, y = resetPos()

            # An empty line below the title
            y += (self.charHeight + dh) * 2

        np, nc = self.bkpt
        while np < self.paraNum:
            while nc < len(self.char["paras"][np]):
                if nc == 0:
                    x += 2 * self.charMWidth
                ch = self.char["paras"][np][nc]
                img.paste(ch["img"], (x, y), ch["img"])
                nc += 1

                x += ch["width"] + dw
                if x >= pw - self.charMWidth:
                    x, _ = resetPos()
                    y += self.charHeight + dh

                if y > ph - self.charHeight:
                    self.bkpt = [np, nc]
                    return img

            x, _ = resetPos()
            y += self.charHeight + dh
            nc = 0
            np += 1

        self.bkpt = [np, nc]
        return img


def loadBackGround(filename=None):
    if filename is None:
        filename = "./background/pku_background.png"
    img = PIL.Image.open(filename)
    img = img.convert("RGBA")
    # w, h = img.size
    # color = img.getpixel((0, 0))
    # for ih in range(h):
    #     for iw in range(w):
    #         dot = (iw, ih)
    #         tcol = img.getpixel(dot)
    #         if tcol == color:
    #             img.putpixel(dot, tcol[:-1] + (0,))
    return img


def intBackGround(page, bk, pos):
    size = bk.size
    abspos = (int(size[0] * pos[0]), int(size[1] * pos[1]))
    img = bk.copy()
    img.paste(page, abspos, page)
    return img


def A4sizer(wid):
    return wid, int(wid * A4hwratio)



def charNumInEachLine(page_w, char_w, dw):
    return int((page_w + dw) / (char_w + dw))


# def page2img(page, **kwargs):
#     size = (kwargs["w"], kwargs["h"])
#     dw, dh = kwargs["dw"], kwargs["dh"]
#     img = PIL.Image.new("RGBA", size, "white")
#
#     # positioning and paste char images
#     x = 0
#     y = 0
#     w, h = gener.getSize()
#     for ln in page:
#         for char in ln:
#             a = gener(char)
#             # use a as the mask to make it transparent!
#             # ref: https://stackoverflow.com/questions/5324647/how-to-merge-a-transparent-png-image-with-another-image-using-pil
#             img.paste(a, (x, y), a)
#             x += dw + w
#         x = 0
#         y += dh + h
#
#     return img


# def artic2img(artic, width, height, dw, dh):
#     art = artic()
#     w, h = gener.getSize()
#     lineMaxCharNum = charNumInEachLine(width, w, dw)
#     lines = art.splitLines(lineMaxCharNum)
#     linNum = len(lines)
#     pagNum = int(linNum * h / height) + 1
#     return lines

# def main():
#     import os
#
#     test_prefix = "./test"
#     try:
#         os.mkdir(test_prefix)
#     except FileExistsError:
#         print("Test folder exists!")
#         exit(-1)
#
#     art = artic()
#     pages = []
#     for pg in art.splitPages(16, 20):
#         pages.append(page2img(pg, w=1000, h=1600, dw=10, dh=10))
#
#     page_id = 1
#     for im in pages:
#         im.save(f"{test_prefix}/page_{page_id}.png")
#         page_id += 1



if __name__ == "__main__":
    atc = artic()
    a = loadBackGround()
    page = atc.makePage((650, 930), (-5, -5))
    res = intBackGround(page, a, (0.12, 0.15))
    res.save("./temp.png")




