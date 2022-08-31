#! /usr/bin/env python3
from PIL import Image, ImageDraw, ImageColor
from os.path import exists
import json
import sys
import time
import vicariousbitcoin
import vicarioustext

def createimage(width=480, height=320):
    currentblock = vicariousbitcoin.getcurrentblock()
    im = Image.new(mode="RGB", size=(width, height), color=colorBackground)
    draw = ImageDraw.Draw(im)
    vicarioustext.drawcenteredtext(draw, str(currentblock), 96, int(width/2), int(height/2), colorTextFG)
    vicarioustext.drawbottomrighttext(draw, "as of " + vicarioustext.getdateandtime(), 12, width, height, colorTextFG)
    im.save(outputFile)
    im.close()

if __name__ == '__main__':
    # Defaults
    configFile="/home/nodeyez/nodeyez/config/blockheight.json"
    outputFile="/home/nodeyez/nodeyez/imageoutput/blockheight.png"
    colorTextFG=ImageColor.getrgb("#ffffff")
    colorBackground=ImageColor.getrgb("#000000")
    width=480
    height=320
    sleepInterval=120
    # Override config
    if exists(configFile):
        with open(configFile) as f:
            config = json.load(f)
        if "blockheight" in config:
            config = config["blockheight"]
        if "outputFile" in config:
            outputFile = config["outputFile"]
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
            print(f"Generates an image based on the blockheight")
            print(f"Usage:")
            print(f"1) Call without arguments to run continuously using the configuration or defaults")
            print(f"You may specify a custom configuration file at {configFile}")
        exit(0)
    # Loop
    while True:
        createimage(width,height)
        time.sleep(sleepInterval)
