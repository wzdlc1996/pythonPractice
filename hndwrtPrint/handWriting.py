"""
Map the chinese character to handwriting image
"""

from PIL import ImageFont, Image, ImageDraw


class char2imgFromFont:
    def __init__(self, strip_size=50, font_size=35):
        self.strip_size = strip_size
        self.font_size = font_size

    def __call__(self, char):
        """
        Convert the character to the img with transparent background

        :param char: Character, including chinese
        :return: img object from Image.new(...)
        """
        font_size = self.font_size
        strip_size = self.strip_size
        font = ImageFont.truetype("./testfont.ttf", font_size)
        img = Image.new("RGBA", [strip_size, strip_size])
        dr = ImageDraw.Draw(img)
        w, h = font.getsize(char)
        pos = [(strip_size - w) / 2, (strip_size - h) / 2]
        dr.text(pos, char, font=font, fill="black")
        return img

    def getSize(self):
        return self.strip_size, self.strip_size


if __name__ == "__main__":
    gen = char2imgFromFont()
    img = gen("啊")
    img.save("./temp.png")

