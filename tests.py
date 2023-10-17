from rembg import remove
from PIL import Image
from os.path import abspath, splitext, basename, join


def remove_background(img: str, output="./") -> str:
    inp = Image.open(img)
    outp = remove(inp)
    path = join(output, basename(splitext(img)[0] + ".png"))
    outp.save(path)
    return abspath(path)


print(remove_background("./IMG-20210225-WA0028.jpg"))
