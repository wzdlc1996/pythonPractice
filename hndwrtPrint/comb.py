"""
Combine the content and background
"""
import handWriting as hw
import re

gener = hw.char2imgFromFont


class artic:
    def __init__(self, filename="./content.md"):
        with open(filename, "r") as f:
            self.main = f.readlines()
        self.charNum = len(re.findall(r"[^\n]", "".join(self.main)))
        self.paraNum = len(self.main)

    def calLineNum(self, page_w, char_w):
        return int(self.charNum * char_w / page_w) + 1 + len([x for x in self.main if x == "\n"])


def artic2img(width, height, charMap=None):
    art = artic()
    if charMap is None:
        charMap = gener()
    w, h = charMap.getSize()
    linNum = art.calLineNum(width, w)
    pagNum = int(linNum * h / height) + 1
    print(linNum, pagNum)


if __name__ == "__main__":
    artic2img(1000, 1600)