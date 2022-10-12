#! /usr/bin/env python3
from datetime import datetime
from os.path import exists
from PIL import Image, ImageDraw, ImageColor
import json
import locale
import math
import numpy
import random
import subprocess
import sys
import time
import vicariousbitcoin
import vicarioustext

def createimage(blocknumber=1, width=480, height=320):
    blockhash = vicariousbitcoin.getblockhash(blocknumber)
    opreturns = vicariousbitcoin.getblockopreturns(blocknumber)
    opreturncount = len(opreturns)
    if opreturncount == 0:
        print(f"No suitable OP_RETURN values in block {blocknumber}")
        return
    print(f"Found {opreturncount} OP_RETURN values in block {blocknumber}.")
    padtop=40
    im       = Image.new(mode="RGB", size=(width, height), color=colorBackground)
    draw     = ImageDraw.Draw(im)
    # Header
    vicarioustext.drawcenteredtext(draw, "OP_RETURN entries for " + str(blocknumber), 24, int(width/2), int(padtop/2), colorTextFG, True)
    # Content
    ridx = 0
    fontsize = 12
    fontsize = 20 if opreturncount <= 2 else fontsize
    fontsize = 18 if opreturncount > 2 and opreturncount < 5 else fontsize
    fontsize = 16 if opreturncount > 4 and opreturncount < 7 else fontsize
    entrysize = 16
    texty = padtop
    for r in opreturns:
        # filter out routine junk
        if "BERNSTEIN 2.0" in r:
            continue
        if r.startswith("omni"):
            continue
        if r.startswith("RSK"):
            continue
        if " " not in r:
            continue
        rbyte = bytes(r, 'utf-8')
        ridx += 1
        sw,sh,f = vicarioustext.gettextdimensions(draw, r, fontsize)
        texty += sh
        if texty > height:
            break
        textcolor = colorTextFG1 if ridx % 2 == 0 else colorTextFG2
        vicarioustext.drawbottomlefttext(draw, r, fontsize, 0, texty, textcolor, False)
    # Save
    if ridx > 0:
        print("Saving image")
        im.save(outputFile)
    else:
        print("OP_RETURN data didn't include anything interesting. Skipping")
    # cleanup resources
    im.close()

if __name__ == '__main__':
    # Defaults
    configFile="/home/nodeyez/nodeyez/config/opreturn.json"
    outputFile="/home/nodeyez/nodeyez/imageoutput/opreturn.png"
    colorTextFG=ImageColor.getrgb("#ffffff")
    colorTextFG1=ImageColor.getrgb("#ff7f00")
    colorTextFG2=ImageColor.getrgb("#dddd00")
    colorBackground=ImageColor.getrgb("#000000")
    width=480
    height=320
    sleepInterval=30
    # Override config
    if exists(configFile):
        with open(configFile) as f:
            config = json.load(f)
        if "opreturn" in config:
            config = config["opreturn"]
        if "outputFile" in config:
            outputFile = config["outputFile"]
        if "colorTextFG" in config:
            colorTextFG = ImageColor.getrgb(config["colorTextFG"])
        if "colorBackground" in config:
            colorBackground = ImageColor.getrgb(config["colorBackground"])
        if "colorTextFG1" in config:
            colorTextFG1 = ImageColor.getrgb(config["colorTextFG1"])
        if "colorTextFG2" in config:
            colorTextFG2 = ImageColor.getrgb(config["colorTextFG2"])
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
            print(f"Produces an image with OP_RETURN data")
            print(f"Usage:")
            print(f"1) Call without arguments to run continuously using the configuration or defaults")
            print(f"2) Pass the desired block number as an argument as follows")
            arg0 = sys.argv[0]
            print(f"   {arg0} 722231")
            print(f"3) Pass the desired block number, width and height as arguments")
            print(f"   {arg0} 722231 1920 1080")
            print(f"You may specify a custom configuration file at {configFile}")
            exit(0)
        blocknumber = int(sys.argv[1])
        if len(sys.argv) > 3:
            width = int(sys.argv[2])
            height = int(sys.argv[3])
        createimage(blocknumber,width,height)
        exit(0)
    # Loop
    oldblocknumber = 0
    while True:
        blocknumber = vicariousbitcoin.getcurrentblock()
        if oldblocknumber != blocknumber:
            createimage(blocknumber,width,height)
            oldblocknumber = blocknumber
        #print(f"sleeping for {sleepInterval} seconds")
        time.sleep(sleepInterval)
