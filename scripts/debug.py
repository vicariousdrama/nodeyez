#! /usr/bin/python3
from datetime import datetime
from PIL import Image, ImageFilter, ImageDraw, ImageFont, ImageColor
import json
import math
import subprocess
import time

outputFile="/home/bitcoin/images/debug.png"
monitorfolder="/home/bitcoin/images/"
monitorage=10
colorFFFFFF=ImageColor.getrgb("#ffffff")
colorFF0000=ImageColor.getrgb("#ff0000")
fontDeja8=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",8)
fontDeja12=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",12)
fontDeja24=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",24)
fontDeja36=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",36)
fontDeja96=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",96)

def getdateandtime():
    now = datetime.utcnow()
    return now.strftime("%Y-%m-%d %H:%M:%S")

def getfont(size):
    if size == 8:
        return fontDeja8
    if size == 12:
        return fontDeja12
    if size == 24:
        return fontDeja24
    if size == 36:
        return fontDeja36
    if size == 96:
        return fontDeja96

def drawcenteredtext(draw, s, fontsize, x, y, textcolor=colorFFFFFF):
    thefont = getfont(fontsize)
    sw,sh = draw.textsize(s, thefont)
    ox,oy = thefont.getoffset(s)
    sw += ox
    sh += oy
    draw.text(xy=(x-(sw/2),y-(sh/2)), text=s, font=thefont, fill=textcolor)

def drawbottomrighttext(draw, s, fontsize, x, y):
    thefont = getfont(fontsize)
    sw,sh = draw.textsize(s, thefont)
    ox,oy = thefont.getoffset(s)
    sw += ox
    sh += oy
    draw.text(xy=(x-sw,y-sh), text=s, font=thefont, fill=colorFFFFFF)

def checkimageage(imagename="debug.png", threshold=monitorage):
    cmd = "find " + monitorfolder + imagename + " -mmin +" + str(threshold) + " -print 2>&1"
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
        if len(cmdoutput) > 0:
            cmdoutput = cmdoutput + "\r\n"
        return cmdoutput
    except subprocess.CalledProcessError as e:
#        print(e)
        return "missing " + imagename + "\r\n"

def checkforoldimages():
    output = ""
    output = output + checkimageage("blockheight*.png", 2)
    output = output + checkimageage("channelbalance*.png", 30)
    output = output + checkimageage("compassminingstatus*.png", 5)
    output = output + checkimageage("debug*.png", 1)
    output = output + checkimageage("difficultyepoch*.png", 9)
    output = output + checkimageage("f2pool*.png", 10)
    output = output + checkimageage("ipaddress*.png", 2)
    output = output + checkimageage("mempoolblocks*.png", 5)
    output = output + checkimageage("minerstatus*.png", 1)
    output = output + checkimageage("rof*.png", 15)
    output = output + checkimageage("satsperusd*.png", 60)
    output = output + checkimageage("slushpool*.png", 10)
    output = output + checkimageage("sysinfo*.png", 1)
    output = output + checkimageage("utcclock*.png", 1)
    return output

def createimage(width=480, height=320):
    results = checkforoldimages()
    im = Image.new(mode="RGB", size=(width, height))
    draw = ImageDraw.Draw(im)
    drawcenteredtext(draw, str("Nodeyez Matured Panels"), 24, int(width/2), int(30/2))
    if len(results) > 0:
        drawcenteredtext(draw, "files with age greater than expected", 24, int(width/2), 50, colorFF0000)
        resultlines = results.splitlines()
        x = 0
        fontsize=12
        for i in resultlines:
            x = x + 1
            j = i.replace(monitorfolder, "")
            drawcenteredtext(draw, str(j), fontsize, int(width/2), 80 + (fontsize * x ), colorFF0000)
    else:
        drawcenteredtext(draw, "All panels rendering when expected", 24, int(width/2), int(height/2))
    drawbottomrighttext(draw, "as of " + getdateandtime(), 12, width, height)
    im.save(outputFile)

while True:
    createimage()
    time.sleep(30)
