#! /usr/bin/python3
from datetime import datetime
from PIL import Image, ImageDraw, ImageColor
from bs4 import BeautifulSoup
import math
import subprocess
import time
import requests
import vicarioustext

# Depends on 
#    pip install beautifulsoup4

# https://us-central1-hashr8-compass.cloudfunctions.net/app/hardware/group?isWeb=true&sortByCost=asc

outputFile="/home/bitcoin/images/compassmininghardware.png"
infourl="https://compassmining.io/hardware"
colorFFFFFF=ImageColor.getrgb("#ffffff")

def getinfopage():
    page = requests.get(infourl)
    soup = BeautifulSoup(page.content, 'html.parser')
    return soup


def createimage(width=480, height=320):
    soup = getinfopage()
    headerheight = 30
    im = Image.new(mode="RGB", size=(width, height))
    draw = ImageDraw.Draw(im)
    # header
    vicarioustext.drawcenteredtext(draw, "Compass Mining Hardware Prices", 24, int(width/2), int(headerheight/2), colorFFFFFF, True)
    # incidents
    incidentcount = 0
    incidentrowheight = 40
    # isolate entries
    entries = soup.find_all(class_="bg-white")
    for entry in entries:
        print(entry.name)
        if entry.name.lower() == "section":
            sibling = entry.find_next_sibling()
            if sibling.name.lower() == "div":
                miner_name = entry.get_text()
                miner_price = sibling.find(class_="text-base").get_text()
                print(miner_name + " " + miner_price + "\n")



    # timestamp
    vicarioustext.drawbottomrighttext(draw, "as of " + vicarioustext.getdateandtime(), 12, width, height)
    im.save(outputFile)

#while True:
#    createimage()
#    time.sleep(86400)
createimage()
