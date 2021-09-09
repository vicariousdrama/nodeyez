#! /usr/bin/python3
from datetime import datetime
from PIL import Image, ImageFilter, ImageDraw, ImageFont, ImageColor
import json
import math
import subprocess
import time

outputFile="/home/bitcoin/images/ipaddress.png"
colorFFFFFF=ImageColor.getrgb("#ffffff")
fontDeja12=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",12)
fontDeja48=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",48)

def getdateandtime():
    now = datetime.utcnow()
    return now.strftime("%Y-%m-%d %H:%M:%S")

def getfont(size):
    if size == 12:
        return fontDeja12
    if size == 48:
        return fontDeja48

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

def getcurrentip():
    cmd = "hostname -I"
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
        iplist = cmdoutput.split()
        goodip = "IP Addresses:\n"
        for i in iplist:
            if len(i) <= 15:
                goodip = goodip + "\n" + i
        return goodip
    except subprocess.CalledProcessError as e:
        print(e)
        return "unknown"

def createimage(width=480, height=320):
    currentip = getcurrentip()
    im = Image.new(mode="RGB", size=(width, height))
    draw = ImageDraw.Draw(im)
    drawcenteredtext(draw, str(currentip), 48, int(width/2), int(height/2))
    drawbottomrighttext(draw, "as of " + getdateandtime(), 12, width, height)
    im.save(outputFile)

while True:
    createimage()
    time.sleep(120)
