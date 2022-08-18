#! /usr/bin/env python3
from PIL import Image, ImageDraw, ImageColor, ImageOps
from os.path import exists
import json
import math
import os
import random
import subprocess
import sys
import time
import vicariousbitcoin
import vicarioustext

def getGridImage(p):
    if os.path.exists(ipfsDirectory):
        random.seed(p * 11235813)
        filegood = False
        fileattempts = 5
        while ((not filegood) and (fileattempts > 0)):
            filename = random.choice(os.listdir(ipfsDirectory))
            try:
                filepath = ipfsDirectory + "/" + filename
                filesize = os.path.getsize(filepath)
                if filesize > 50000:
                    rImage = Image.open(filepath).convert("RGBA")
                    filegood = True
            except BaseException as err:
                # not sure what
                print(f"meh error: {err}")
                fileattempts = fileattempts -1
        if filegood:
            return rImage
    # default
    return Image.open("/home/nodeyez/nodeyez/images/logo.png").convert("RGBA")


def createimage(width=480, height=320):
    rows = 35
    cols = 60
    nHeight = vicariousbitcoin.getcurrentblock()
    nSubsidyHalvingInterval = 210000
    halvings = nHeight / nSubsidyHalvingInterval
    halvingbegin = math.floor(halvings) * nSubsidyHalvingInterval
    halvingend = halvingbegin + nSubsidyHalvingInterval - 1
    halvingpct = float(nHeight - halvingbegin) / float(rows*cols)
    gridblocks = nHeight % (rows*cols)
    # start the image
    im = Image.new(mode="RGB", size=(width, height), color=colorBackground)
    draw = ImageDraw.Draw(im)
    # grid for the current percent
    blockw=int(math.floor((width-1)/cols))
    padleft=int(math.floor((width-(cols*blockw))/2))
    padtop=40
    if gridImageEnabled:
        gridw = blockw * cols
        gridh = blockw * rows
        gridratio=float(gridw)/float(gridh)
        gridsource = getGridImage(int(halvingpct))
        gridsourcew = int(gridsource.getbbox()[2])
        gridsourceh = int(gridsource.getbbox()[3])
        gridsourceratio = float(gridsourcew)/float(gridsourceh)
        if gridsourceratio > gridratio:
            newgridsourceheight=int(gridsourcew/gridratio)
            gridsourceoffset = int((newgridsourceheight-gridsourceh)/2)
            gridsourcetaller = Image.new(mode="RGBA", size=(gridsourcew, newgridsourceheight), color=colorProgress)
            gridsourcetaller.paste(gridsource, (0,gridsourceoffset))
            gridimage = gridsourcetaller.resize(size=(gridw,gridh))
        else:
            newgridsourcewidth=int(gridsourceh*gridratio)
            gridsourceoffset = int((newgridsourcewidth-gridsourcew)/2)
            gridsourcewider = Image.new(mode="RGBA", size=(newgridsourcewidth, gridsourceh), color=colorProgress)
            gridsourcewider.paste(gridsource, (gridsourceoffset,0))
            gridimage = gridsourcewider.resize(size=(gridw,gridh))
    for dc in range(cols):
        for dr in range(rows):
            gridblocknum = ((dr*cols)+dc)+1
            tlx = (padleft + (dc*blockw))
            tly = (padtop + (dr*blockw))
            brx = tlx+blockw-2
            bry = tly+blockw-2
            fillcolor = None
            outlinecolor = colorGrid
            if gridblocknum <= gridblocks:
                fillcolor = colorProgress
                outlinecolor = None
            if gridImageEnabled:
                # crop from gridimage
                gtlx = (dc*blockw)
                gtly = (dr*blockw)
                gbrx = gtlx+blockw-1
                gbry = gtly+blockw-1
                gblockimg = gridimage.crop((gtlx,gtly,gbrx,gbry))
                if fillcolor != colorProgress:
                    # convert to black and white
                    if gridImageUnminedMode == 'grayscale':
                        gblockimg = ImageOps.grayscale(gblockimg)
                    if gridImageUnminedMode == 'dither':
                        gblockimg = gblockimg.convert('1')
                    if gridImageUnminedMode == 'dither2':
                        gblockimg = gblockimg.convert('L')
                # paste the part into the right spot
                im.paste(gblockimg, (tlx, tly))
                if gridblocknum == gridblocks:
                    fillcolor = None
                    outlinecolor = colorProgress
                    draw.rectangle(xy=((tlx-1,tly-1),(brx+1,bry+1)),fill=fillcolor,outline=outlinecolor,width=2)
            else:
                draw.rectangle(xy=((tlx,tly),(brx,bry)),fill=fillcolor,outline=outlinecolor)
    # header and footer
    padtop=36
    vicarioustext.drawcenteredtext(draw, "Next Subsidy Halving", 24, int(width/2), int(padtop/2), colorTextFG, True)
    vicarioustext.drawbottomrighttext(draw, "as of " + vicarioustext.getdateandtime(), 12, width, height, colorTextFG)
    # progress bar showing major percent
    padleft=0
    barheight=32
    barwidth=(width//2)
    padtop=height-barheight
    vicarioustext.drawtoplefttext(draw, "grid represents 1 whole percent", 10, barwidth + 3, padtop, colorProgress)
    draw.rounded_rectangle(xy=(padleft,padtop,padleft+barwidth,padtop+barheight),radius=3,fill=None,outline=colorGrid,width=1)
    barwidth=int(float(barwidth)*halvingpct/100.00)
    draw.rounded_rectangle(xy=(padleft+2,padtop+2,padleft+barwidth,padtop+barheight-2),radius=3,fill=colorProgress)
    pcttxt = str(format(halvingpct, ".3f")) + "%"
    if halvingpct < 25:
        vicarioustext.drawlefttext(draw, str(nHeight) + " is " + pcttxt, 14, padleft+barwidth+4, padtop+(barheight/2), colorProgress, True)
    elif halvingpct < 75:
        vicarioustext.drawrighttext(draw, "Block\n" + str(nHeight), 14, padleft+barwidth-2, padtop+(barheight/2), colorBackground, True)
        vicarioustext.drawlefttext(draw, pcttxt, 14, padleft+barwidth+2, padtop+(barheight/2), colorProgress, True)
    else:
        vicarioustext.drawrighttext(draw, str(nHeight) + " is " + pcttxt, 14, padleft+barwidth-4, padtop+(barheight/2), colorBackground, True)
    # save
    im.save(outputFile)


if __name__ == '__main__':
    # Defaults
    configFile="/home/nodeyez/nodeyez/config/halving.json"
    outputFile="/home/nodeyez/nodeyez/imageoutput/halving.png"
    ipfsDirectory="/home/nodeyez/nodeyez/data/ipfs"
    colorGrid=ImageColor.getrgb("#404040")
    colorProgress=ImageColor.getrgb("#40FF40")
    colorTextFG=ImageColor.getrgb("#ffffff")
    colorBackground=ImageColor.getrgb("#000000")
    gridImageEnabled=True
    gridImageUnminedMode="grayscale"
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
        if "gridImageEnabled" in config:
            gridImageEnabled = config["gridImageEnabled"]
        if "gridImageUnminedMode" in config:
            gridImageUnminedMode = config["gridImageUnminedMode"]
        if "ipfsDirectory" in config:
            ipfsDirectory = config["ipfsDirectory"]
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
