#! /usr/bin/env python3
from datetime import datetime
from os.path import exists
from PIL import Image, ImageDraw, ImageColor
import json
import math
import os
import stat
import subprocess
import sys
import time
import vicarioustext
import vicariousnetwork


def getpoolinfo(pools, poolid):
    nbRegistered = -1
    nbConfirmed = -1
    elapsedTime = -1
    for pool in pools["pools"]:
        if pool["poolId"] == poolid:
            nbRegistered = pool["nbRegistered"]
            nbConfirmed = pool["nbConfirmed"]
            elapsedTime = pool["elapsedTime"]
            break
    return nbRegistered, nbConfirmed, elapsedTime

def drawpool(draw, pools, poolid, quadheader, topx, topy, bottomx, bottomy):
    remixers, premixers, elapsedTime = getpoolinfo(pools, poolid)
    headersize=18
    vicarioustext.drawcenteredtext(draw, quadheader, headersize, topx+(bottomx-topx)//2, topy + (headersize // 3 * 2), colorPoolHeader, False)
    labelsize=16
    labelbuf=4
    labelline=1.1
    vicarioustext.drawrighttext(draw, "Premixers: ", labelsize, topx+(bottomx-topx)//2, topy + (headersize + (1 * labelsize * labelline) + labelbuf), colorPremixers, False)
    vicarioustext.drawrighttext(draw, "Remixers: ", labelsize, topx+(bottomx-topx)//2, topy + (headersize + (2 * labelsize * labelline) + labelbuf), colorRemixers, False)
    vicarioustext.drawrighttext(draw, "Elapsed: ", labelsize, topx+(bottomx-topx)//2, topy + (headersize + (3 * labelsize * labelline) + labelbuf), colorElapsed, False)
    vicarioustext.drawlefttext(draw, str(premixers), labelsize, topx+(bottomx-topx)//2 + 2, topy + (headersize + (1 * labelsize * labelline) + labelbuf), colorTextFG, False)
    vicarioustext.drawlefttext(draw, str(remixers), labelsize, topx+(bottomx-topx)//2 + 2, topy + (headersize + (2 * labelsize * labelline) + labelbuf), colorTextFG, False)
    vicarioustext.drawlefttext(draw, str(elapsedTime), labelsize, topx+(bottomx-topx)//2 + 2, topy + (headersize + (3 * labelsize * labelline) + labelbuf), colorTextFG, False)

def drawlogo(im, canvaswidth, canvasheight, targetWidth):
    if not exists(logoFile):
        return
    logoImage=Image.open(logoFile)
    logoWidth=int(logoImage.getbbox()[2])
    logoHeight=int(logoImage.getbbox()[3])
    logoRatio=float(logoWidth)/float(logoHeight)
    newWidth=int(targetWidth)
    newHeight=int(newWidth * logoRatio)
    newLogo = logoImage.resize(size=(newWidth,newHeight))
    logoImage.close()
    logoX = (canvaswidth // 2) - (newWidth // 2)
    logoY = (canvasheight // 2) - (newHeight // 2)
    logoPos = (logoX, logoY)
    im.paste(newLogo, logoPos)
    newLogo.close()

def getfileageinseconds(pathname):
    return time.time() - os.stat(pathname)[stat.ST_MTIME]

def getorloadliquidity():
    whirlfile = whirlDirectory + "whirlpoolliquidity.json"
    refreshData = False
    if not exists(whirlfile):
        refreshData = True
    else:
        fileage = getfileageinseconds(whirlfile)
        if fileage > sleepInterval:
            refreshData = True
    if refreshData:
        print("Refreshing whirlpool liquidity data")
        pools = vicariousnetwork.getwhirlpoolliquidity()
        with open(whirlfile, "w") as f:
            json.dump(pools, f)
    else:
        print("Loading cached whirlpool liquidity data")
        with open(whirlfile) as f:
            pools = json.load(f)
    return pools

# ---------------------------------------

def createimage(width=480, height=320):
    headerheight = 30
    footerheight = 15
    pools = getorloadliquidity()
    im = Image.new(mode="RGB", size=(width, height), color=colorBackground)
    draw = ImageDraw.Draw(im)
    # Header
    vicarioustext.drawcenteredtext(draw, "Whirlpool Liquidity", 24, int(width/2), int(headerheight/2), colorHeader, True)
    # Pools
    quadwidth = width // 2
    print(f"quadwidth: {quadwidth}, width: {width}")
    quadheight = (height - (headerheight + footerheight)) // 2
    drawpool(draw, pools, "0.5btc", "50M Sats", 0, headerheight, quadwidth, headerheight + quadheight)
    drawpool(draw, pools, "0.05btc", "5M Sats", quadwidth + 1, headerheight, width, headerheight + quadheight)
    drawpool(draw, pools, "0.01btc", "1M Sats", 0, headerheight + quadheight + footerheight, quadwidth, height - footerheight)
    drawpool(draw, pools, "0.001btc", "100K Sats", quadwidth + 1, headerheight + quadheight + footerheight, width, height - footerheight)
    # Samourai Logo
    drawlogo(im, width, height, 80)
    # Date and Time
    vicarioustext.drawbottomrighttext(draw, "as of " + vicarioustext.getdateandtime(), 12, width, height, colorTextFG)
    # Save to file
    im.save(outputFile)
    im.close()


if __name__ == '__main__':
    # Defaults
    configFile = "/home/nodeyez/nodeyez/config/whirlpool.json"
    outputFile = "/home/nodeyez/nodeyez/imageoutput/whirlpoolliquidity.png"
    logoFile = "/home/nodeyez/nodeyez/images/samourai.png"
    dataDirectory = "/home/nodeyez/nodeyez/data/"
    useTor=True
    width=480
    height=320
    sleepInterval = 3600                              # controls how often this display panel is updated. 3600 is once every hour
    colorHeader=ImageColor.getrgb("#ffffff")          # The header text color. Need to pass to also specify bolding
    colorPoolHeader=ImageColor.getrgb("#aa2222")      # Pool Header for each quad
    colorRemixers=ImageColor.getrgb("#aaaaaa")        # Label for Remixers (nbRegistered)
    colorPremixers=ImageColor.getrgb("#aaaaaa")       # Label for Premixers (nbConfirmed)
    colorElapsed=ImageColor.getrgb("#aaaaaa")         # Label for Elapsed Time (since last mix?)
    colorTextFG=ImageColor.getrgb("#ffffff")          # General text color other than header and data values
    colorBackground=ImageColor.getrgb("#000000")      # Background color
    # Overide defaults
    if exists(configFile):
        with open(configFile) as f:
            config = json.load(f)
        if "whirlpool" in config:
            config = config["whirlpool"]
        if "outputFile" in config:
            outputFile = config["outputFile"]
        if "useTor" in config:
            useTor = config["useTor"]
        if "width" in config:
            width = int(config["width"])
        if "height" in config:
            height = int(config["height"])
        if "sleepInterval" in config:
            sleepInterval = int(config["sleepInterval"])
            sleepInterval = 600 if sleepInterval < 600 else sleepInterval # minimum 10 minutes, access others
        if "colorHeader" in config:
            colorHeader = ImageColor.getrgb(config["colorHeader"])
        if "colorPoolHeader" in config:
            colorPoolHeader = ImageColor.getrgb(config["colorPoolHeader"])
        if "colorRemixers" in config:
            colorRemixers = ImageColor.getrgb(config["colorRemixers"])
        if "colorPremixers" in config:
            colorPremixers = ImageColor.getrgb(config["colorPremixers"])
        if "colorElapsed" in config:
            colorElapsed = ImageColor.getrgb(config["colorElapsed"])
        if "colorTextFG" in config:
            colorTextFG = ImageColor.getrgb(config["colorTextFG"])
        if "colorBackground" in config:
            colorBackground = ImageColor.getrgb(config["colorBackground"])
    # Data directories
    if not os.path.exists(dataDirectory):
        os.makedirs(dataDirectory)
    whirlDirectory = dataDirectory + "whirlpool/"
    if not os.path.exists(whirlDirectory):
        os.makedirs(whirlDirectory)
    # Check for single run
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h','--help']:
            print(f"Creates a summary image of Whirlpool Liquidity.")
            print(f"Usage:")
            print(f"1) Call without arguments to run continuously using the configuration or defaults")
            print(f"2) Pass with an argument other than -h or --help to run once and exit.")
            print(f"You must specify a custom configuration file at {configFile}")
            exit(0)
        else:
            print(f"Running once and exiting")
    # Loop
    while True:
        print("Creating image")
        createimage(width,height)
        print("Image created")
        if len(sys.argv) > 1:
            exit(0)
        time.sleep(sleepInterval)
