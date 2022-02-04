#! /usr/bin/python3
from PIL import Image, ImageDraw
import time
import vicariousbitcoin
import vicarioustext

outputFile="/home/bitcoin/images/blockheight.png"

def createimage(width=480, height=320):
    currentblock = vicariousbitcoin.getcurrentblock()
    im = Image.new(mode="RGB", size=(width, height))
    draw = ImageDraw.Draw(im)
    vicarioustext.drawcenteredtext(draw, str(currentblock), 96, int(width/2), int(height/2))
    vicarioustext.drawbottomrighttext(draw, "as of " + vicarioustext.getdateandtime(), 12, width, height)
    im.save(outputFile)

while True:
    createimage()
    time.sleep(120)
