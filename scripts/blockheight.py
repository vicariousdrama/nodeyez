#! /usr/bin/python3
from datetime import datetime
from PIL import Image, ImageFilter, ImageDraw, ImageFont, ImageColor
import json
import math
import subprocess
import time

outputFile="/home/bitcoin/images/blockheight.png"
colorFFFFFF=ImageColor.getrgb("#ffffff")
fontDeja12=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",12)
fontDeja96=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",96)

def getdateandtime():
    now = datetime.utcnow()
    return now.strftime("%Y-%m-%d %H:%M:%S")

def getfont(size):
    if size == 12:
        return fontDeja12
    if size == 96:
        return fontDeja96

def drawcenteredtext(draw, s, fontsize, x, y):
    thefont = getfont(fontsize)
    sw,sh = draw.textsize(s, thefont)
    ox,oy = thefont.getoffset(s)
    sw += ox
    sh += oy
    draw.text(xy=(x-(sw/2),y-(sh/2)), text=s, font=thefont, fill=colorFFFFFF)

def drawbottomrighttext(draw, s, fontsize, x, y):
    thefont = getfont(fontsize)
    sw,sh = draw.textsize(s, thefont)
    ox,oy = thefont.getoffset(s)
    sw += ox
    sh += oy
    draw.text(xy=(x-sw,y-sh), text=s, font=thefont, fill=colorFFFFFF)

def getcurrentblock():
    cmd = "bitcoin-cli getblockchaininfo"
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
        j = json.loads(cmdoutput)
        blockcurrent = int(j["blocks"])
        return blockcurrent
    except subprocess.CalledProcessError as e:
        print(e)
        return 1

def createimage(width=480, height=320):
    currentblock = getcurrentblock()
    im = Image.new(mode="RGB", size=(width, height))
    draw = ImageDraw.Draw(im)
    drawcenteredtext(draw, str(currentblock), 96, int(width/2), int(height/2))
    drawbottomrighttext(draw, "as of " + getdateandtime(), 12, width, height)
    im.save(outputFile)

while True:
    createimage()
    time.sleep(120)
