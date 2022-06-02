#! /usr/bin/env python3
from PIL import Image, ImageDraw, ImageColor
from os.path import exists
import json
import subprocess
import sys
import time
import vicarioustext


def getcurrentip():
    cmd = "hostname -I"
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
        iplist = cmdoutput.split()
        goodip = "IP Addresses:\n"
        for i in iplist:
            if len(i) <= 15:
                goodip = goodip + "\n" + i
        return goodip
    except subprocess.CalledProcessError as e:
        print(e)
        return "unknown"

def createimage(width=480, height=320):
    currentip = getcurrentip()
    im = Image.new(mode="RGB", size=(width, height), color=colorBackground)
    draw = ImageDraw.Draw(im)
    vicarioustext.drawcenteredtext(draw, str(currentip), 36, int(width/2), int(height/2), colorTextFG, True)
    vicarioustext.drawbottomrighttext(draw, "as of " + vicarioustext.getdateandtime(), 12, width, height, colorTextFG)
    im.save(outputFile)

if __name__ == '__main__':
    # Defaults
    configFile="/home/nodeyez/nodeyez/config/ipaddress.json"
    outputFile="/home/nodeyez/nodeyez/imageoutput/ipaddress.png"
    colorTextFG=ImageColor.getrgb("#ffffff")
    colorBackground=ImageColor.getrgb("#000000")
    width=480
    height=320
    sleepInterval=120
    # Override config
    if exists(configFile):
        with open(configFile) as f:
            config = json.load(f)
        if "ipaddress" in config:
            config = config["ipaddress"]
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
            print(f"Prepares an image with all the IP addresses used by this host")
            print(f"Usage:")
            print(f"1) Call without arguments to run continuously using the configuration or defaults")
            print(f"2) Call with an argument other then -h or --help to run once and exit")
            print(f"You may specify a custom configuration file at {configFile}")
        else:
            createimage(width,height)
        exit(0)
    # Loop
    while True:
        createimage(width,height)
        time.sleep(sleepInterval)
