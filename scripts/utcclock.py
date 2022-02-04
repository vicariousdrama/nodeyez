#! /usr/bin/python3
from datetime import datetime
from PIL import Image, ImageDraw, ImageColor
import json
import math
import subprocess
import time
import vicarioustext

outputFile="/home/bitcoin/images/utcclock.png"
sleepInterval=30

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
    vicarioustext.drawcenteredtext(draw, getdayofweek(), 72, int(width/2), int(height/2)-120)
    vicarioustext.drawcenteredtext(draw, getdate(), 72, int(width/2), int(height/2))
    vicarioustext.drawcenteredtext(draw, gettime(), 96, int(width/2), int(height/2)+120)
    im.save(outputFile)

while True:
    createimage()
    time.sleep(sleepInterval)
