import math
import numpy as np
from PIL import Image
from matplotlib import image

charset = ["@", "%", "*", "o", "+", "-", "."]

def rgb2gray(rgb):
    rgb = np.array(rgb)
    r = rgb[:, :, 0]
    g = rgb[:, :, 1]
    b = rgb[:, :, 2]
    gamma = 2.2
    fac = 1 + 1.5 ** gamma + 0.6 ** gamma
    gray = np.power((r ** gamma + (1.5 * g) ** gamma + (0.6 * b) ** gamma) / fac, 1 / 2.2)
    return gray / np.max(gray)

def charConv(grayImg):
    img = np.int_(grayImg * (len(charset) - 1))
    shape = img.shape
    return (np.array(charset)[img.reshape((shape[0] * shape[1],))]).reshape(shape)

if __name__ == "__main__":
    img = np.asarray(Image.open("./test.png").resize((60, 20)))
    charimg = charConv(rgb2gray(img))
    for x in charimg:
        print("".join(x))
    np.savetxt("./test.txt", charimg, fmt="%s",  delimiter='')


