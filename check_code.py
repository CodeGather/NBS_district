import json
import datetime
import os
import pytesseract
from PIL import Image


if __name__ == '__main__':
    im = Image.open("/Users/yau/work/3.Github/NBS_district/demo.jpeg")
    text = pytesseract.image_to_string(im)
    print(text)