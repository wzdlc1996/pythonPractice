"""
Map the chinese character to handwriting image
"""
import re
import random
from PIL import ImageFont, Image, ImageDraw


punc = {
    "。": ".", "，": ",", "、": ",", "：": ":"
}


class char2imgFromFont:
    def __init__(self, widCent=40, widRang=5, height=50, font_size=35):
        self.h = height
        self.wc = widCent
        self.wr = widRang
        self.font_size = font_size

    def genSize(self):
        return int(self.wc + self.wr * 2 * (random.random() - 0.5)), self.h

    def __call__(self, char):
        """
        Convert the character to the img with transparent background

        :param char: Character, including chinese
        :return: img object from Image.new(...)
        """
        font_size = self.font_size
        w, h = self.genSize()
        font = ImageFont.truetype("./testfont.ttf", font_size)
        img = Image.new("RGBA", [w, h])
        dr = ImageDraw.Draw(img)
        if char in punc:
            char = punc[char]
        rw, rh = font.getsize(char)
        pos = [(w - rw) / 2, (h - rh) / 2]
        dr.text(pos, char, font=font, fill="black")
        return img, (w, h)


if __name__ == "__main__":
    gen = char2imgFromFont()
    img, (w, h) = gen(",")
    img.save("./temp.png")



