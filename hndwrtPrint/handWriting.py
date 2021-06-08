"""
Map the chinese character to handwriting image
"""

from PIL import ImageFont, Image, ImageDraw

def char2img(char):
    font = ImageFont.truetype("./testfont.ttf", 35)
    strip_size = 50
    img = Image.new("L", [strip_size, strip_size], "white")
    dr = ImageDraw.Draw(img)
    w, h = font.getsize(char)
    print(w, h)
    pos = [(strip_size - w) / 2, (strip_size - h) / 2]
    dr.text(pos, char, font=font)
    return img


if __name__ == "__main__":
    img = char2img("我")
    img.save("./temp.jpeg")
