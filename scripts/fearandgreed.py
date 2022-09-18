#! /usr/bin/env python3
from datetime import datetime
from PIL import Image, ImageFilter, ImageDraw, ImageFont, ImageColor
from os.path import exists
import glob
import json
import math
import os
import subprocess
import sys
import time
import vicariousbitcoin
import vicariousnetwork
import vicarioustext

def getdatefile():
    return datetime.utcnow().strftime("%Y-%m-%d-%H") + ".json"

def makeDirIfNotExists(path):
    if not exists(path):
        print(f"Creating folder {path}")
        os.makedirs(path)

def getNewestFile(fileDirectory):
    files = glob.glob(fileDirectory + "*.json")
    newestfile = ""
    if len(files) > 0:
        newestfile = max(files, key=os.path.getctime)
    return newestfile

def getfnghistory():
    try:
        # Get reference to newest file
        fngfile = getNewestFile(fearAndGreedDataDirectory)
        if len(fngfile) == 0:
            # If dont yet have a file, download and save one
            datefile = getdatefile()
            fngfile = fearAndGreedDataDirectory + datefile
            vicariousnetwork.getandsavefile(url, fngfile)
        # Open the file
        with open(fngfile) as f:
            # Load data as JSON
            filedata = json.load(f)
            return filedata
    except Exception as e:
        print(f"Error loading Fear and Greed data: {e}")
        print(f"Using fake data")
    return {"data":[{"value":"50","value_classification":"Neutral","timestamp":"0","time_until_update":"0"}]}

def createimage(width=480, height=320):
    headerheight = 30
    footerheight = 30
    infoheight = (height - headerheight - footerheight) * .3
    chartheight = (height - headerheight - footerheight) * .7
    im = Image.new(mode="RGB", size=(width, height), color=colorBackground)
    draw = ImageDraw.Draw(im)
    # Header
    vicarioustext.drawcenteredtext(draw, "Fear and Greed Index", 24, int(width/2), int(headerheight/2), colorTextFG, True)
    # FNG History
    fnghistory = getfnghistory()
    labelwidth = 40
    graphedge = 3
    charttop = headerheight + infoheight + 12
    chartleft = labelwidth + graphedge
    chartright = width - graphedge
    chartbottom = height - footerheight - graphedge
    # - chart border
    draw.line(xy=[chartleft, charttop, chartleft, chartbottom],fill=colorGraphLineLight,width=1)
    draw.line(xy=[chartleft, chartbottom, chartright, chartbottom],fill=colorGraphLineLight,width=1)
    draw.line(xy=[chartleft, charttop, chartright, charttop],fill=colorGraphLineDark,width=1)
    draw.line(xy=[chartright, charttop, chartright, chartbottom],fill=colorGraphLineDark,width=1)
    # - dashed line background
    chart100 = int(math.floor(charttop))
    chart80  = int(math.floor(charttop + ((chartbottom - charttop)/5*1)))
    chart60  = int(math.floor(charttop + ((chartbottom - charttop)/5*2)))
    chart40  = int(math.floor(charttop + ((chartbottom - charttop)/5*3)))
    chart20  = int(math.floor(charttop + ((chartbottom - charttop)/5*4)))
    chart0   = int(math.floor(charttop + ((chartbottom - charttop))))
    for i in range(chartleft, chartright, 10):
        draw.line(xy=[i,chart20,i+1,chart20],fill=colorGraphLineDark,width=1)
        draw.line(xy=[i,chart40,i+1,chart40],fill=colorGraphLineDark,width=1)
        draw.line(xy=[i,chart60,i+1,chart60],fill=colorGraphLineDark,width=1)
        draw.line(xy=[i,chart80,i+1,chart80],fill=colorGraphLineDark,width=1)
    # - left labels
    vicarioustext.drawrighttext(draw, "100%", 12, labelwidth, chart100, colorTextFG)
    vicarioustext.drawrighttext(draw, "80%", 12, labelwidth, chart80, colorTextFG)
    vicarioustext.drawrighttext(draw, "60%", 12, labelwidth, chart60, colorTextFG)
    vicarioustext.drawrighttext(draw, "40%", 12, labelwidth, chart40, colorTextFG)
    vicarioustext.drawrighttext(draw, "20%", 12, labelwidth, chart20, colorTextFG)
    vicarioustext.drawrighttext(draw, "0%", 12, labelwidth, chart0, colorTextFG)
    # - data plot
    entrynum = 0
    plotbuf = 1
    xbuf = 0
    ybuf = 0
    fnglength = len(fnghistory["data"])
    oldmaxpos = -1
    oldmaypos = -1
    for entry in fnghistory["data"]:
        # current data point
        entrynum = entrynum + 1
        fngpct = entry["value"]
        xpos = chartright - (entrynum * plotbuf)
        ypos = chartbottom - int(math.floor((chartbottom-charttop) / 100.0 * float(fngpct)))
        #print(f"xpos: {xpos}, ypos: {ypos}")
        if ((xbuf+xpos-plotbuf) <= chartleft):
            #print(f"enough! {entrynum}")
            break
        draw.ellipse(xy=[(xbuf+xpos-plotbuf,ybuf+ypos-plotbuf),(xbuf+xpos+plotbuf,ybuf+ypos+plotbuf)],fill=colorDataValue,outline=colorDataValue,width=1)
        # moving average calculation (14 points = 7 day)
        masize = 14
        matotal = 0
        for maentry in range(masize):
            maidx = entrynum - 1 + maentry
            if (maidx >= 0) and (maidx < fnglength):
                maentryvalue = fnghistory["data"][maidx]["value"]
                maentrypct = int(maentryvalue)
                matotal = matotal + maentrypct
        mapct = float(matotal) / float(masize)
        ypos = chartbottom - int(math.floor((chartbottom-charttop) / 100.0 * mapct))
        if oldmaxpos != -1:
            draw.line(xy=[(xpos,ypos),(oldmaxpos,oldmaypos)],fill=colorMovingAverage,width=2)
        oldmaxpos = xpos
        oldmaypos = ypos
    # Info
    currentvalue = "50"
    currentlabel = "Neutral"
    if fnglength > 0:
        currentvalue = fnghistory["data"][0]["value"]
        currentlabel = fnghistory["data"][0]["value_classification"]
    vicarioustext.drawcenteredtext(draw, currentvalue, 48, int(width/2), (headerheight+32), colorDataValue, True)
    vicarioustext.drawcenteredtext(draw, currentlabel, 20, int(width/2), (headerheight+64), colorDataValue, True)
    # Attribution
    attributionLine = "Data from alternative.me"
    vicarioustext.drawbottomlefttext(draw, attributionLine, 16, 0, height, colorTextFG)
    # Date and Time
    dt = "as of " + vicarioustext.getdateandtime()
    vicarioustext.drawbottomrighttext(draw, dt, 12, width, height, colorTextFG)
    # Save to file
    im.save(outputFile)
    im.close()


if __name__ == '__main__':
    # Defaults
    configFile="/home/nodeyez/nodeyez/config/fearandgreed.json"
    outputFile = "/home/nodeyez/nodeyez/imageoutput/fearandgreed.png"
    useTor=True
    url="https://api.alternative.me/fng/?limit=0&format=json&date_format=cn"
    dataDirectory = "/home/nodeyez/nodeyez/data/"
    width=480
    height=320
    sleepInterval=43200
    colorDataValue=ImageColor.getrgb("#ff7f00")
    colorMovingAverage=ImageColor.getrgb("#40ff40")
    colorGraphLineLight=ImageColor.getrgb("#a0a0a0")
    colorGraphLineDark=ImageColor.getrgb("#606060")
    colorTextFG=ImageColor.getrgb("#ffffff")
    colorBackground=ImageColor.getrgb("#000000")
    # Override config
    if exists(configFile):
        with open(configFile) as f:
            config = json.load(f)
        if "fearandgreed" in config:
            config = config["fearandgreed"]
        if "outputFile" in config:
            outputFile = config["outputFile"]
        if "useTor" in config:
            useTor = config["useTor"]
        if "url" in config:
            url = config["url"]
        if "dataDirectory" in config:
            dataDirectory = config["dataDirectory"]
        if "width" in config:
            width = int(config["width"])
        if "height" in config:
            height = int(config["height"])
        if "sleepInterval" in config:
            sleepInterval = int(config["sleepInterval"])
            sleepInterval = 21600 if sleepInterval < 21600 else sleepInterval # minimum 6 hours, this data set changes twice a day
        if "colorDataValue" in config:
            colorDataValue = ImageColor.getrgb(config["colorDataValue"])
        if "colorMovingAverage" in config:
            colorMovingAverage = ImageColor.getrgb(config["colorMovingAverage"])
        if "colorGraphLineLight" in config:
            colorGraphLineLight = ImageColor.getrgb(config["colorGraphLineLight"])
        if "colorGraphLineDark" in config:
            colorGraphLineDark = ImageColor.getrgb(config["colorGraphLineDark"])
        if "colorTextFG" in config:
            colorTextFG = ImageColor.getrgb(config["colorTextFG"])
        if "colorBackground" in config:
            colorBackground = ImageColor.getrgb(config["colorBackground"])
    # Calculated variables
    fearAndGreedDataDirectory = dataDirectory + "fearandgreed/"
    makeDirIfNotExists(fearAndGreedDataDirectory)
    # Check for single run
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h','--help']:
            print(f"Prepares images for Fear and Greed charting")
            print(f"Usage:")
            print(f"1) Call without arguments to run continuously using the configuration or defaults")
            print(f"2) Passing any arguments other then -h or --help will run once and exit")
            print(f"You may specify a custom configuration file at {configFile}")
            exit(0)
    # Loop
    while True:
        createimage(width,height)
        # only run once if an argument was passed
        if len(sys.argv) > 1:
            break
        time.sleep(sleepInterval)
