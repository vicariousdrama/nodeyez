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

def createimage(width=480, height=320):
    nHeight = vicariousbitcoin.getcurrentblock()
    nSubsidyHalvingInterval = 210000
    halvings = nHeight / nSubsidyHalvingInterval
    halvingbegin = math.floor(halvings) * nSubsidyHalvingInterval
    halvingend = halvingbegin + nSubsidyHalvingInterval - 1
    halvingpct = float(nHeight - halvingbegin) / float(2100.00)
    gridblocks = nHeight % 2100
    # start the image with header and footer
    padtop=50
    im = Image.new(mode="RGB", size=(width, height), color=colorBackground)
    draw = ImageDraw.Draw(im)
    vicarioustext.drawcenteredtext(draw, "Progress to Next Subsidy Halving", 24, int(width/2), int(padtop/2), colorTextFG, True)
    vicarioustext.drawbottomrighttext(draw, "as of " + vicarioustext.getdateandtime(), 12, width, height, colorTextFG)
    # progress bar showing major percent
    padleft=50
    barheight=40
    draw.rounded_rectangle(xy=(padleft,padtop,width-padleft,padtop+barheight),radius=3,fill=None,outline=colorGrid,width=1)
    barwidth=int(math.floor(float(width-(padleft+padleft+4))*halvingpct/100.00))
    draw.rounded_rectangle(xy=(padleft+2,padtop+2,padleft+barwidth,padtop+barheight-2),radius=3,fill=colorProgress)
    pcttxt = str(format(halvingpct, ".2f")) + "%"
    if halvingpct < 75:
        vicarioustext.drawrighttext(draw, str(nHeight), 18, padleft+barwidth-2, padtop+(barheight/2), colorBackground, True)
        vicarioustext.drawlefttext(draw, pcttxt, 18, padleft+barwidth+2, padtop+(barheight/2), colorProgress, True)
    else:
        vicarioustext.drawcenteredtext(draw, str(nHeight) + " is " + pcttxt, 18, (width/2), padtop+(barheight/2), colorBackground, True)
    # grid of 70x30 (2100) for the current percent
    rows = 30
    cols = 70
    blockw=int(math.floor(width/cols))
    padleft=int(math.floor((width-(cols*blockw))/2))
    padtop=100
    for dc in range(cols):
        for dr in range(rows):
            gridblocknum = ((dr*cols)+dc)+1
            tlx = (padleft + (dc*blockw))
            tly = (padtop + (dr*blockw))
            brx = tlx+blockw-2
            bry = tly+blockw-2
            fillcolor = None
            if gridblocknum <= gridblocks:
                fillcolor = colorProgress
            draw.rectangle(xy=((tlx,tly),(brx,bry)),fill=fillcolor,outline=colorGrid)
    im.save(outputFile)


if __name__ == '__main__':
    # Defaults
    configFile="/home/nodeyez/nodeyez/config/halving.json"
    outputFile="/home/nodeyez/nodeyez/imageoutput/halving.png"
    colorGrid=ImageColor.getrgb("#404040")
    colorProgress=ImageColor.getrgb("#40FF40")
    colorTextFG=ImageColor.getrgb("#ffffff")
    colorBackground=ImageColor.getrgb("#000000")
    width=480
    height=320
    sleepInterval=540
    # Override config
    if exists(configFile):
        with open(configFile) as f:
            config = json.load(f)
        if "halving" in config:
            config = config["halving"]
        if "outputFile" in config:
            outputFile = config["outputFile"]
        if "colorGrid" in config:
            colorGrid = ImageColor.getrgb(config["colorGrid"])
        if "colorProgress" in config:
            colorProgress = ImageColor.getrgb(config["colorProgress"])
        if "colorTextFG" in config:
            colorTextFG = ImageColor.getrgb(config["colorTextFG"])
        if "colorBackground" in config:
            colorBackground = ImageColor.getrgb(config["colorBackground"])
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
            print(f"Renders a representation of progress through the current halving period")
            print(f"Usage:")
            print(f"1) Call without arguments to run continuously using the configuration or defaults")
            print(f"You may specify a custom configuration file at {configFile}")
        else:
            createimage(width, height)
        exit(0)
    # Loop
    while True:
        createimage(width, height)
        time.sleep(sleepInterval)
