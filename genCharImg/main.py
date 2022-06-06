import numpy as np
from PIL import Image

charset = ["@", "%", "*", "o", "+", "-", "."]

def rgb2gray(rgb):
    """
    Convert the RGB array into normalized gray array

    :param rgb: the rgb array of size (weight, height, 3)
    :return: gray array of size (weight, height). the values are normalized in [0, 1]
    """
    rgb = np.array(rgb)
    r = rgb[:, :, 0]
    g = rgb[:, :, 1]
    b = rgb[:, :, 2]
    gamma = 2.2
    fac = 1 + 1.5 ** gamma + 0.6 ** gamma
    gray = np.power((r ** gamma + (1.5 * g) ** gamma + (0.6 * b) ** gamma) / fac, 1 / 2.2)
    return gray / np.max(gray)

def charConv(grayImg):
    """
    Convert the gray array into char array, generate the char image

    :param grayImg: normalized gray array of the image
    :return: char array
    """
    img = np.int_(grayImg * (len(charset) - 1))
    shape = img.shape
    return (np.array(charset)[img.reshape((shape[0] * shape[1],))]).reshape(shape)

if __name__ == "__main__":
    img = np.asarray(Image.open("./test.png").resize((60, 20))) # read the png file as rgb array and resize, by PIL
    charimg = charConv(rgb2gray(img))
    for x in charimg:
        print("".join(x))
    np.savetxt("./test.txt", charimg, fmt="%s",  delimiter='')


