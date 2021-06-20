"""
Combine the content and background
"""
import handWriting as hw
import PIL
import re

gener = hw.char2imgFromFont()


class artic:
    def __init__(self, filename="./content.md"):
        with open(filename, "r") as f:
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
        self.charDict = set(self.chars)

    def splitLines(self, lineMaxCharNum, paraIndent=True):
        lines = [list(self.main["title"]), [""]]
        for x in self.main["paras"]:
            if paraIndent:
                para = "  " + x
            else:
                para = x
            lines += [list(para)[i:i+lineMaxCharNum] for i in range(0, len(para), lineMaxCharNum)]
        return lines


def charNumInEachLine(page_w, char_w, dw):
    return int((page_w + dw) / (char_w + dw))


def genPage(lines, width, height, dw, dh, pool):
    # generate the background
    size = (width, height)
    img = PIL.Image.new("RGBA", size, "white")

    # positioning and paste char images
    x = 0
    y = 0
    w, h = gener.getSize()
    for ln in lines:
        for char in ln:
            a = gener(char)
            # use a as the mask to make it transparent!
            # ref: https://stackoverflow.com/questions/5324647/how-to-merge-a-transparent-png-image-with-another-image-using-pil
            img.paste(a, (x, y), a)
            x += dw + w
        x = 0
        y += dh + h

    img.save("page.png")





def artic2img(width, height, dw, dh):
    art = artic()
    w, h = gener.getSize()
    lineMaxCharNum = charNumInEachLine(width, w, dw)
    lines = art.splitLines(lineMaxCharNum)
    linNum = len(lines)
    pagNum = int(linNum * h / height) + 1
    return lines


if __name__ == "__main__":
    lines = artic2img(1000, 1600, 10, 10)
    genPage(lines[:20], 1000, 1600, 10, 10, {})
