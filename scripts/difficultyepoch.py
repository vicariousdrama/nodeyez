#! /usr/bin/env python3
from PIL import Image, ImageDraw, ImageColor
from os.path import exists
import json
import math
import subprocess
import sys
import time
import vicariousbitcoin
import vicarioustext
import vicariouswatermark

def getcurrenttimeinseconds():
    cmd = "date -u +%s"
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
        return int(cmdoutput)
    except subprocess.CalledProcessError() as e:
        print(e)
        return 1

def createimage(width=480, height=320):
    currentblock = vicariousbitcoin.getcurrentblock()
    j = vicariousbitcoin.getblock(vicariousbitcoin.getfirstblockforepoch(currentblock))
    blocksmined = int(j["confirmations"])
    timebegan = int(j["time"])
    timenow = getcurrenttimeinseconds()
    secondspassed = timenow - timebegan
    expectedmined = int(math.floor(secondspassed / 600))
    if blocksmined == 1:
        expectedmined = 1
    nextadjustment = "0.0"
    if float(expectedmined) > 0 and float(blocksmined) > 0:
        nextadjustment = str(float("%.2f" % (((float(blocksmined) / float(expectedmined)) - 1.0) * 100)))
    adjustcolor = colorBehind
    if "-" not in nextadjustment:
        nextadjustment = "+" + nextadjustment
        adjustcolor = colorMined
    estimateepochend = timebegan + (2016*600)
    if float(blocksmined) > 0:
        estimateepochend = int(math.floor((float(secondspassed) / float(blocksmined))*2016)) + timebegan
    secondstoepochend = estimateepochend - timenow
    nextepochdesc = ""
    if blocksmined >= 10:
        if secondstoepochend > 86400:
            nextepochdays = math.floor(secondstoepochend / 86400)
            nextepochdesc = nextepochdesc + str(nextepochdays) + " day"
            if nextepochdays > 1:
                nextepochdesc = nextepochdesc + "s"
            secondstoepochend = secondstoepochend - (nextepochdays * 86400)
        if secondstoepochend > 3600:
            nextepochhours = math.floor(secondstoepochend / 3600)
            if nextepochdesc != "":
                nextepochdesc = nextepochdesc + ", "
            nextepochdesc = nextepochdesc + str(nextepochhours) + " hour"
            if nextepochhours > 1:
                nextepochdesc = nextepochdesc + "s"
            secondstoepochend = secondstoepochend - (nextepochhours * 3600)
        if (secondstoepochend > 600) and ("," not in nextepochdesc):
            nextepochminutes = math.floor(secondstoepochend / 60)
            if nextepochdesc != "":
                nextepochdesc = nextepochdesc + ", "
            nextepochdesc = nextepochdesc + str(nextepochminutes) + " minute"
            if nextepochminutes > 1:
                nextepochdesc = nextepochdesc + "s"
            secondstoepochend = secondstoepochend - (nextepochminutes * 60)
        else:
            if nextepochdesc == "":
                "a few minutes"
    else:
        nextepochdesc = "about 2 weeks"

    blockw=int(math.floor(width/63))
    padleft=int(math.floor((width-(63*blockw))/2))
    padtop=36
    im = Image.new(mode="RGBA", size=(width, height), color=colorBackground)
    draw = ImageDraw.Draw(im)
    for dc in range(63):
        for dr in range(32):
            epochblocknum = ((dr*63) + dc)+1
            tlx = (padleft + (dc*blockw))
            tly = (padtop + (dr*blockw))
            brx = tlx+blockw-2
            bry = tly+blockw-2
            if epochblocknum <= blocksmined:
                fillcolor = colorMined
                if epochblocknum > expectedmined:
                    fillcolor = colorAhead
                draw.rectangle(xy=((tlx,tly),(brx,bry)),fill=fillcolor)
            else:
                outlinecolor = colorGrid
                if epochblocknum <= expectedmined:
                    outlinecolor = colorBehind
                draw.rectangle(xy=((tlx,tly),(brx,bry)),fill=None,outline=outlinecolor)
    vicarioustext.drawcenteredtext(draw, "Blocks Mined This Difficulty Epoch", 24, int(width/2), int(padtop/2), colorTextFG, True)
    vicarioustext.drawtoprighttext(draw, "Expected: ", 18, int(width/4*1), height-56, colorTextFG)
    vicarioustext.drawtoplefttext(draw, str(expectedmined), 18, int(width/4*1), height-56, colorTextFG)
    vicarioustext.drawtoprighttext(draw, "Mined: ", 18, int(width/4*1), height-32, colorTextFG)
    vicarioustext.drawtoplefttext(draw, str(blocksmined), 18, int(width/4*1), height-32, colorTextFG)
    vicarioustext.drawtoprighttext(draw, "Retarget: ", 18, int(width/10*6), height-56, colorTextFG)
    vicarioustext.drawtoplefttext(draw, str(nextadjustment) + "%", 18, int(width/10*6), height-56, adjustcolor)
    vicarioustext.drawtoprighttext(draw, "In: ", 18, int(width/10*6), height-32, colorTextFG)
    vicarioustext.drawtoplefttext(draw, str(nextepochdesc), 18, int(width/10*6), height-32, colorTextFG)
    vicarioustext.drawbottomrighttext(draw, "as of " + vicarioustext.getdateandtime(), 12, width, height, colorTextFG)
    vicariouswatermark.do(im,100,box=(0,height-12))
    print(f"saving imager to {outputFile}")
    im.save(outputFile)
    if saveEachBlock:
        of2=outputFile.replace(".png","-" + str(currentblock) + ".png")
        print(f"saving imager to {of2}")
        im.save(of2)
    im.close()


if __name__ == '__main__':
    # Defaults
    configFile="/home/nodeyez/nodeyez/config/difficultyepoch.json"
    outputFile="/home/nodeyez/nodeyez/imageoutput/difficultyepoch.png"
    colorGrid=ImageColor.getrgb("#404040")
    colorAhead=ImageColor.getrgb("#FFFF40")
    colorBehind=ImageColor.getrgb("#FF0000")
    colorMined=ImageColor.getrgb("#40FF40")
    colorTextFG=ImageColor.getrgb("#ffffff")
    colorBackground=ImageColor.getrgb("#000000")
    saveEachBlock=False
    width=480
    height=320
    sleepInterval=540
    # Override config
    if exists(configFile):
        with open(configFile) as f:
            config = json.load(f)
        if "difficultyepoch" in config:
            config = config["difficultyepoch"]
        if "outputFile" in config:
            outputFile = config["outputFile"]
        if "colorGrid" in config:
            colorGrid = ImageColor.getrgb(config["colorGrid"])
        if "colorAhead" in config:
            colorAhead = ImageColor.getrgb(config["colorAhead"])
        if "colorBehind" in config:
            colorBehind = ImageColor.getrgb(config["colorBehind"])
        if "colorMined" in config:
            colorMined = ImageColor.getrgb(config["colorMined"])
        if "colorTextFG" in config:
            colorTextFG = ImageColor.getrgb(config["colorTextFG"])
        if "colorBackground" in config:
            colorBackground = ImageColor.getrgb(config["colorBackground"])
        if "saveEachBlock" in config:
            saveEachBlock = config["saveEachBlock"]
        if "width" in config:
            width = int(config["width"])
        if "height" in config:
            height = int(config["height"])
        if "sleepInterval" in config:
            sleepInterval = int(config["sleepInterval"])
            sleepInterval = 30 if sleepInterval < 30 else sleepInterval # minimum 30 seconds, local only
    # Check for single run
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h','--help']:
            print(f"Renders a representation of progress through the current difficulty epoch")
            print(f"Usage:")
            print(f"1) Call without arguments to run continuously using the configuration or defaults")
            print(f"You may specify a custom configuration file at {configFile}")
        else:
            createimage(width, height)
        exit(0)
    # Loop
    while True:
        createimage(width, height)
        print(f"sleeping for {sleepInterval} seconds")
        time.sleep(sleepInterval)
