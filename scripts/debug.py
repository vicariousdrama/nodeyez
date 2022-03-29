#! /usr/bin/env python3
from PIL import Image, ImageDraw, ImageColor
import subprocess
import time
import vicarioustext

outputFile="/home/nodeyez/nodeyez/imageoutput/debug.png"
monitorfolder="/home/nodeyez/nodeyez/imageoutput/"
monitorage=10
colorFFFFFF=ImageColor.getrgb("#ffffff")
colorFF0000=ImageColor.getrgb("#ff0000")

def checkimageage(imagename="debug.png", threshold=monitorage):
    cmd = "find " + monitorfolder + imagename + " -mmin +" + str(threshold) + " -print 2>&1"
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
        if len(cmdoutput) > 0:
            cmdoutput = cmdoutput + "\r\n"
        return cmdoutput
    except subprocess.CalledProcessError as e:
        return "missing " + imagename + "\r\n"

def checkforoldimages():
    output = ""
    output = output + checkimageage("arthashdungeon*.png", 15)
    #output = output + checkimageage("blockheight*.png", 2)
    output = output + checkimageage("channelbalance*.png", 30)
    output = output + checkimageage("compassminingstatus*.png", 5)
    output = output + checkimageage("debug*.png", 1)
    output = output + checkimageage("difficultyepoch*.png", 9)
    #output = output + checkimageage("f2pool*.png", 10)
    #output = output + checkimageage("ipaddress*.png", 2)
    output = output + checkimageage("mempoolblocks*.png", 5)
    output = output + checkimageage("minerbraiins*.png", 1)
    output = output + checkimageage("rof*.png", 15)
    output = output + checkimageage("satsperusd*.png", 60)
    output = output + checkimageage("slushpool*.png", 10)
    output = output + checkimageage("sysinfo*.png", 1)
    output = output + checkimageage("utcclock*.png", 1)
    return output

def getoldimages():
    cmd = "find " + monitorfolder + "*.png -mmin +" + str(monitorage) + " -print 2>&1"
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
        return cmdoutput
    except subprocess.CalledProcessError as e:
        print(e)
        return str(e)

def createimage(width=480, height=320):
    results = checkforoldimages()
    im = Image.new(mode="RGB", size=(width, height))
    draw = ImageDraw.Draw(im)
    vicarioustext.drawcenteredtext(draw, str("Nodeyez Matured Panels"), 24, int(width/2), int(30/2), colorFFFFFF, True)
    if len(results) > 0:
        vicarioustext.drawcenteredtext(draw, "files with age greater than expected", 24, int(width/2), 50, colorFF0000)
        resultlines = results.splitlines()
        x = 0
        fontsize=12
        for i in resultlines:
            x = x + 1
            j = i.replace(monitorfolder, "")
            vicarioustext.drawcenteredtext(draw, str(j), fontsize, int(width/2), 80 + (fontsize * x ), colorFF0000)
    else:
        vicarioustext.drawcenteredtext(draw, "All panels rendering when expected", 24, int(width/2), int(height/2))
    vicarioustext.drawbottomrighttext(draw, "as of " + vicarioustext.getdateandtime(), 12, width, height)
    im.save(outputFile)

while True:
    createimage()
    time.sleep(30)
