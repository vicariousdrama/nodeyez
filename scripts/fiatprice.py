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

def createimage(width=480, height=320):
    global last
    global high
    global low
    global priceofbitcoin
    last,high,low = vicariousnetwork.getpriceinfo(useTor, priceurl, last, high, low)
    priceofbitcoin=last
    padtop=40
    im = Image.new(mode="RGBA", size=(width, height), color=colorBackground)
    draw = ImageDraw.Draw(im)
    alpha_img = Image.new(mode="RGBA", size=(width, height), color=(0,0,0,0))
    drawa = ImageDraw.Draw(alpha_img)
    # header
    vicarioustext.drawcenteredtext(draw, "Price of Bitcoin", 24, int(width/2), int(padtop/2), colorHeader, True)
    # mid
    bpt = "$" + str(priceofbitcoin)
    if showBigText:
        #fsize = 128 #vicarioustext.getmaxfontsize(draw, bpt, False, 128, 10)
        fsize = vicarioustext.getmaxfontsize(draw, bpt, width, height)
        x = int(width/2)
        y = int(height/2)
        colorPrice = colorPriceDown if last < priceofbitcoin else colorPriceUp
        vicarioustext.drawcenteredtext((draw if showBigTextOnTop else drawa), bpt, fsize, x, y, colorPriceShadow)
        vicarioustext.drawcenteredtext((draw if showBigTextOnTop else drawa), bpt, fsize, x-2, y-2, colorPrice)
    # footer
    if not showBigText:
        vicarioustext.drawcenteredtext(draw, "Price: " + bpt, 20, int(width/8*4), height-padtop)
    vicarioustext.drawbottomlefttext(draw, "Data from bisq", 16, 0, height, colorBisq)
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
    configFile="/home/nodeyez/nodeyez/config/fiatprice.json"
    outputFile="/home/nodeyez/nodeyez/imageoutput/fiatprice.png"
    priceurl="https://bisq.markets/bisq/api/markets/ticker"
    useTor=True
    width=480
    height=320
    sleepInterval=300
    showBigText=True
    showBigTextOnTop=True
    colorBisq=ImageColor.getrgb("#40FF40")
    colorHeader=ImageColor.getrgb("#ffffff")
    colorPriceUp=ImageColor.getrgb("#40FF40")
    colorPriceDown=ImageColor.getrgb("#FF4040")
    colorPriceShadow=ImageColor.getrgb("#ffffff7f")
    colorBackground=ImageColor.getrgb("#000000")
    # Inits
    last=0
    low=0
    high=0
    priceofbitcoin=0
    colorPrice=colorPriceUp
    # Override defaults
    if exists(configFile):
        with open(configFile) as f:
            config = json.load(f)
        if "fiatprice" in config:
            config = config["fiatprice"]
        if "outputFile" in config:
            outputFile = config["outputFile"]
        if "priceurl" in config:
            priceurl = config["priceurl"]
        if "useTor" in config:
            useTor = config["useTor"]
        if "width" in config:
            width = int(config["width"])
        if "height" in config:
            height = int(config["height"])
        if "sleepInterval" in config:
            sleepInterval = int(config["sleepInterval"])
            sleepInterval = 60 if sleepInterval < 600 else sleepInterval # minimum 1 minutes, access others
        if "showBigText" in config:
            showBigText = config["showBigText"]
        if "showBigTextOnTop" in config:
            showBigTextOnTop = config["showBigTextOnTop"]
        if "colorBisq" in config:
            colorBisq = ImageColor.getrgb(config["colorBisq"])
        if "colorHeader" in config:
            colorHeader = ImageColor.getrgb(config["colorHeader"])
        if "colorPriceUp" in config:
            colorPriceUp = ImageColor.getrgb(config["colorPriceUp"])
        if "colorPriceDown" in config:
            colorPriceDown = ImageColor.getrgb(config["colorPriceDown"])
        if "colorPriceShadow" in config:
            colorPriceShadow = ImageColor.getrgb(config["colorPriceShadow"])
        if "colorBackground" in config:
            colorBackground = ImageColor.getrgb(config["colorBackground"])
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h','--help']:
            print(f"Retrieves the market rate of BTC from Bisq and renders the price in dollars")
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
