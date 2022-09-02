#! /usr/bin/env python3
from datetime import datetime, timedelta
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
    found = False
    for pool in pools["pools"]:
        if pool["poolId"] == poolid:
            found = True
            if "nbRegistered" in pool:
                nbRegistered = int(pool["nbRegistered"])
            if "nbConfirmed" in pool:
                nbConfirmed = int(pool["nbConfirmed"])
            if "elapsedTime" in pool:
                elapsedTime = int(pool["elapsedTime"])
            print(f"found pool {poolid}: premixers = {nbConfirmed}, remixers = {nbRegistered}, ms since last: {elapsedTime}")
            break
    if not found:
        print(f"did not locate pool with id: {poolid}.")
    return nbRegistered, nbConfirmed, elapsedTime

def gethumantime(timeinms, partcount=1):
    d = timedelta(milliseconds=timeinms)
    seconds = int(d.total_seconds() // 1)
    o = ""
    if partcount > 0 and (seconds // 86400) > 0:
        days = seconds // 86400
        o = o + ", " if len(o) > 0 else o
        o = o + str(days) + " day"
        o = o + "s" if days > 1 else ""
        partcount = partcount - 1
        seconds -= (days * 86400)
    if partcount > 0 and (seconds // 3600) > 0:
        hours = seconds // 3600
        o = o + ", " if len(o) > 0 else o
        o = o + str(hours) + " hour"
        o = o + "s" if hours > 1 else ""
        partcount = partcount - 1
        seconds -= (hours * 3600)
    if partcount > 0 and (seconds // 60) > 0:
        minutes = seconds // 60
        o = o + ", " if len(o) > 0 else o
        o = o + str(minutes) + " minute"
        o = o + "s" if minutes > 1 else ""
        partcount = partcount - 1
    if partcount > 0 and seconds > 0:
        o = o + ", " if len(o) > 0 else o
        o = o + str(seconds) + " second"
        o = o + "s" if seconds > 1 else ""
        partcount = partcount - 1
    if o == "":
        o = "now"
    else:
        o += " ago"
    return o

def drawpool(im, draw, pools, poolid, quadheader, topx, topy, bottomx, bottomy):
    remixers, premixers, elapsedTime = getpoolinfo(pools, poolid)
    humantime = gethumantime(elapsedTime, 1)
    headersize=18
    vicarioustext.drawcenteredtext(draw, quadheader, headersize, topx+(bottomx-topx)//2, topy + (headersize // 3 * 2), colorPoolHeader, True)
    labelsize=16
    labelbuf=4
    labelline=1.1
    whirlsize=32
    whirlpad=8
    whirllabelsize=10
    # Last Cycle
    t = "Last Cycle: " + humantime
    vicarioustext.drawcenteredtext(draw, t, labelsize, topx+(bottomx-topx)//2, topy + (headersize + (3.2 * labelsize * labelline) + labelbuf), colorElapsed, False)
    # Draw whirls for premix
    center = int( topx + (bottomx-topx)//2 + 2 )
    x = int(center - (whirlsize * 2.5) - whirlpad)
    y = int( topy + (headersize + (1 * labelsize * labelline) + labelbuf) )
    for w in range(2):
        c = "grey"
        c = "yellow" if (premixers == 1 and premixers > w) else c
        c = "green" if premixers >= 2 else c
        drawwhirl(im, x + (w * whirlsize), y-(whirlsize//2), c)
    t = str(premixers) + " premixer"
    t = t + "s" if premixers != 1 else t
    vicarioustext.drawrighttext(draw, t, whirllabelsize, x + (2 * whirlsize), topy + (headersize + (2.25 * labelsize * labelline) + labelbuf), colorPremixers, False)
    # Draw whirls for remix
    x = int(center - (whirlsize * 0.5))
    y = topy + (headersize + (1 * labelsize * labelline) + labelbuf)
    for w in range(3):
        c = "grey"
        c = "yellow" if (remixers >=1 and remixers > w) else c
        c = "green" if remixers >= 3 else c
        drawwhirl(im, x + (w * whirlsize), y-(whirlsize//2), c)
    t = str(remixers) + " remixer"
    t = t + "s" if remixers != 1 else t
    vicarioustext.drawlefttext(draw, t, whirllabelsize, x, topy + (headersize + (2.25 * labelsize * labelline) + labelbuf), colorPremixers, False)
    # Attribution
    vicarioustext.drawbottomlefttext(draw, "Data from pool.whirl.mx", 16, 0, height, colorPoolHeader)

def drawlogo(im, canvaswidth, canvasheight, targetWidth):
    if not exists(logoSamouraiFile):
        return
    logoImage=Image.open(logoSamouraiFile)
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

def drawwhirl(im, x, y, c="grey"):
    logoWhirlpoolFile = "/home/nodeyez/nodeyez/images/whirlpool-" + c + "-32.png"
    if not exists(logoWhirlpoolFile):
        return
    i = Image.open(logoWhirlpoolFile)
    l = (int(x),int(y))
    im.paste(i, l)
    i.close()

def getfileageinseconds(pathname):
    if not exists(pathname):
        return 0
    return time.time() - os.stat(pathname)[stat.ST_MTIME]

def getwhirldatafile():
    whirlfile = whirlDirectory + "whirlpoolliquidity.json"
    return whirlfile

def getorloadliquidity():
    whirlfile = getwhirldatafile()
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
        found = False
        remixers, premixers, elapsedTime = getpoolinfo(pools, "0.5btc")
        if remixers == -1 or premixers == -1:
            print("failed to retrieve valid liquidity data")
            # failed to retrieve. dont save, just return
            return pools
        with open(whirlfile, "w") as f:
            json.dump(pools, f)
    else:
        print("Loading cached whirlpool liquidity data")
        with open(whirlfile) as f:
            pools = json.load(f)
    return pools

def getfiledateandtime(pathname):
    dt = datetime.utcnow()
    if exists(pathname):
        fileage = getfileageinseconds(pathname)
        dt = dt - timedelta(seconds=fileage)
    return dt.strftime("%Y-%m-%d %H:%M:%S")

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
    quadheight = int( (height - (headerheight + footerheight)) // 2 )
    drawpool(im, draw, pools, "0.5btc", "50M Sats", 0, headerheight, quadwidth, headerheight + quadheight)
    drawpool(im, draw, pools, "0.05btc", "5M Sats", quadwidth + 1, headerheight, width, headerheight + quadheight)
    drawpool(im, draw, pools, "0.01btc", "1M Sats", 0, headerheight + quadheight + footerheight + footerheight, quadwidth, height - footerheight)
    drawpool(im, draw, pools, "0.001btc", "100K Sats", quadwidth + 1, headerheight + quadheight + footerheight + footerheight, width, height - footerheight)
    # Samourai Logo
    drawlogo(im, width, height, 80)
    # Date and Time
    vicarioustext.drawbottomrighttext(draw, "as of " + getfiledateandtime(getwhirldatafile()), 12, width, height, colorTextFG)
    # Save to file
    im.save(outputFile)
    im.close()


if __name__ == '__main__':
    # Defaults
    configFile = "/home/nodeyez/nodeyez/config/whirlpoolliquidity.json"
    outputFile = "/home/nodeyez/nodeyez/imageoutput/whirlpoolliquidity.png"
    logoSamouraiFile = "/home/nodeyez/nodeyez/images/samourai.png"
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
