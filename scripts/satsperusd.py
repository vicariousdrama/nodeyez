#! /usr/bin/env python3
from PIL import Image, ImageDraw, ImageColor
from os.path import exists
import json
import math
import subprocess
import sys
import time
import vicarioustext
import vicariousnetwork

def drawsatssquare(draw,dc,dr,spf,satw,bpx,bpy):
    satsleft = spf
    for y in range(10):
        for x in range(10):
            if satsleft > 0:
                tlx = (bpx + (dc*11*satw) + (x*satw))
                tly = (bpy + (dr*11*satw) + (y*satw))
                brx = tlx+satw-2
                bry = tly+satw-2
                if satshape == "square":
                    draw.rectangle(xy=((tlx,tly),(brx,bry)),fill=colorSatShape)
                if satshape == "circle":
                    draw.ellipse(xy=((tlx,tly),(brx,bry)),fill=colorSatShape)
            satsleft = satsleft - 1

def createimage(width=480, height=320):
    global last
    global high
    global low
    last,high,low = vicariousnetwork.getpriceinfo(useTor, priceurl, last, high, low)
    satsperfiatunit = int(round(100000000.0 / last))
    satsperfiatunitlow = int(round(100000000.0 / low))
    satsperfiatunithigh = int(round(100000000.0 / high))
    satsleft = satsperfiatunit
    satw=int(math.floor(width/87))
    padleft=int(math.floor((width-(87*satw))/2))
    padtop=40
    im = Image.new(mode="RGBA", size=(width, height), color=colorBackground)
    draw = ImageDraw.Draw(im)
    alpha_img = Image.new(mode="RGBA", size=(width, height), color=(0,0,0,0))
    drawa = ImageDraw.Draw(alpha_img)
    if showBigText and not showBigTextOnTop:
        vicarioustext.drawcenteredtext(draw, str(satsperfiatunit), 128, int(width/2), int(height/2), colorSatAmountShadow)
        vicarioustext.drawcenteredtext(draw, str(satsperfiatunit), 128, int(width/2)-2, int(height/2)-2, colorSatAmount)
    dc = 0
    dr = 0
    while satsleft > 100:
        satsleft = satsleft - 100
        drawsatssquare(draw,dc,dr,100,satw,padleft,padtop)
        dc = dc + 1
        if dc >= 8:
            dr = dr + 1
            dc = 0
    drawsatssquare(draw,dc,dr,satsleft,satw,padleft,padtop)
    if showBigText and showBigTextOnTop:
        vicarioustext.drawcenteredtext(drawa, str(satsperfiatunit), 128, int(width/2), int(height/2), colorSatAmountShadow)
        vicarioustext.drawcenteredtext(drawa, str(satsperfiatunit), 128, int(width/2)-2, int(height/2)-2, colorSatAmount)
    vicarioustext.drawcenteredtext(draw, "Sats Per USD", 24, int(width/2), int(padtop/2), colorHeader, True)
    if not showBigText:
        vicarioustext.drawcenteredtext(draw, "Last: " + str(satsperfiatunit), 20, int(width/8*4), height-padtop)
    vicarioustext.drawcenteredtext(draw, "High: " + str(satsperfiatunitlow), 20, int(width/8*7), height-padtop)
    vicarioustext.drawcenteredtext(draw, "Low: " + str(satsperfiatunithigh), 20, int(width/8*1), height-padtop)
    vicarioustext.drawbottomlefttext(draw, "Market data by bisq", 16, 0, height, colorBisq)
    vicarioustext.drawbottomrighttext(draw, "as of " + vicarioustext.getdateandtime(), 12, width, height)
    # Combine and save
    composite = Image.alpha_composite(im, alpha_img)
    print(f"Saving file to {outputFile}")
    composite.save(outputFile)
    im.close()
    alpha_img.close()
    composite.close()

if __name__ == '__main__':
    # Defaults
    configFile="/home/nodeyez/nodeyez/config/satsperusd.json"
    outputFile="/home/nodeyez/nodeyez/imageoutput/satsperusd.png"
    priceurl="https://bisq.markets/bisq/api/markets/ticker"
    useTor=True
    satshape="square" # may be one of these: ['square','circle']
    width=480
    height=320
    sleepInterval=3600
    showBigText=True
    showBigTextOnTop=True
    colorBisq=ImageColor.getrgb("#40FF40")
    colorHeader=ImageColor.getrgb("#ffffff")
    colorSatShape=ImageColor.getrgb("#ff7f00")
    colorSatAmount=ImageColor.getrgb("#4040407f")
    colorSatAmountShadow=ImageColor.getrgb("#ffffff7f")
    colorBackground=ImageColor.getrgb("#000000")
    # Inits
    last=1
    low=1
    high=1
    # Override defaults
    if exists(configFile):
        with open(configFile) as f:
            config = json.load(f)
        if "satsperusd" in config:
            config = config["satsperusd"]
        if "outputFile" in config:
            outputFile = config["outputFile"]
        if "priceurl" in config:
            priceurl = config["priceurl"]
        if "useTor" in config:
            useTor = config["useTor"]
        if "satshape" in config:
            satshape = config["satshape"]
        if "width" in config:
            width = int(config["width"])
        if "height" in config:
            height = int(config["height"])
        if "sleepInterval" in config:
            sleepInterval = int(config["sleepInterval"])
            sleepInterval = 600 if sleepInterval < 600 else sleepInterval # minimum 10 minutes, access others
        if "showBigText" in config:
            showBigText = config["showBigText"]
        if "showBigTextOnTop" in config:
            showBigTextOnTop = config["showBigTextOnTop"]
        if "colorBisq" in config:
            colorBisq = ImageColor.getrgb(config["colorBisq"])
        if "colorHeader" in config:
            colorHeader = ImageColor.getrgb(config["colorHeader"])
        if "colorSatShape" in config:
            colorSatShape = ImageColor.getrgb(config["colorSatShape"])
        if "colorSatAmount" in config:
            colorSatAmount = ImageColor.getrgb(config["colorSatAmount"])
        if "colorSatAmountShadow" in config:
            colorSatAmountShadow = ImageColor.getrgb(config["colorSatAmountShadow"])
        if "colorBackground" in config:
            colorBackground = ImageColor.getrgb(config["colorBackground"])
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h','--help']:
            print(f"Retrieves the market rate of BTC from Bisq and renders number of Sats per dollar")
            print(f"Usage:")
            print(f"1) Call without arguments to run continuously using the configuration or defaults")
            print(f"2) Pass an argument other than -h or --help to run once and exit")
            print(f"You may specify a custom configuration file at {configFile}")
        else:
            createimage(width,height)
        exit(0)
    # Loop
    while True:
        createimage(width,height)
        time.sleep(sleepInterval)
