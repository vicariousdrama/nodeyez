#! /usr/bin/env python3
from datetime import datetime
from os.path import exists
from PIL import Image, ImageDraw, ImageColor
import json
import math
import subprocess
import sys
import time
import vicarioustext

def getdayofweek():
    now = datetime.utcnow()
    return now.strftime("%A")

def getdate():
    now = datetime.utcnow()
    return now.strftime("%d %b %Y")

def gettime():
    now = datetime.utcnow()
    return now.strftime("%H:%M:%S")

def createimage(width=480, height=320):
    im = Image.new(mode="RGB", size=(width, height))
    draw = ImageDraw.Draw(im)
    vicarioustext.drawcenteredtext(draw, getdayofweek(), 72, int(width/2), int(height/2)-120, colorTextDayOfWeek)
    vicarioustext.drawcenteredtext(draw, getdate(), 72, int(width/2), int(height/2), colorTextDate)
    vicarioustext.drawcenteredtext(draw, gettime(), 96, int(width/2), int(height/2)+120, colorTextTime)
    im.save(outputFile)

if __name__ == '__main__':
    # Defaults
    configFile="/home/bitcoin/nodeyez/config/utcclock.json"
    outputFile="/home/bitcoin/images/utcclock.png"
    sleepInterval=30
    colorTextDayOfWeek=ImageColor.getrgb("#ffffff")
    colorTextDate=ImageColor.getrgb("#ffffff")
    colorTextTime=ImageColor.getrgb("#ffffff")
    # Override defaults
    if exists(configFile):
        with open(configFile) as f:
            config = json.load(f)
        if "utcclock" in config:
            config = config["utcclock"]
        if "outputFile" in config:
            outputFile = config["outputFile"]
        if "sleepInterval" in config:
            sleepInterval = int(config["sleepInterval"])
            sleepInterval = 10 if sleepInterval < 10 else sleepInterval # minimum 10 seconds, local only
        if "colorTextDayOfWeek" in config:
            colorTextDayOfWeek = ImageColor.getrgb(config["colorTextDayOfWeek"])
        if "colorTextDate" in config:
            colorTextDate = ImageColor.getrgb(config["colorTextDate"])
        if "colorTextTime" in config:
            colorTextTime = ImageColor.getrgb(config["colorTextTime"])
    # Check for single run
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h','--help']:
            print(f"Generates a simple output of the date and time in UTC and weekday")
            print(f"Usage:")
            print(f"1) Call without arguments to run continuously using the configuration or defaults")
            print(f"2) Pass an argument other than -h or --help to run once and exit")
            print(f"You may specify a custom configuration file at {configFile}")
        else:
            createimage()
        exit(0)
    # Loop
    while True:
        createimage()
        time.sleep(sleepInterval)
