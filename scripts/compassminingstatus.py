#! /usr/bin/env python3
from PIL import Image, ImageDraw, ImageColor
from bs4 import BeautifulSoup
from os.path import exists
import json
import sys
import time
import requests
import vicarioustext

def getstatuspage():
    page = requests.get(statusurl)
    soup = BeautifulSoup(page.content, 'html.parser')
    return soup

def createimage(width=480, height=320):
    soup = getstatuspage()
    headerheight = 30
    im = Image.new(mode="RGB", size=(width, height), color=colorBackground)
    draw = ImageDraw.Draw(im)
    # header
    vicarioustext.drawcenteredtext(draw, "Compass Mining Status", 24, int(width/2), int(headerheight/2), colorTextFG, True)
    # incidents
    incidentcount = 0
    incidentrowheight = 40
    # top block
    if True:
        # look for major incidents
        incidents = soup.find_all(class_="impact-major")
        for incident in incidents:
            if incident.find(class_="actual-title") is not None:
                text = incident.find(class_="actual-title").get_text()
                incidentcount = incidentcount + 1
                draw.rectangle(xy=[0,headerheight+int((incidentcount-1)*incidentrowheight)+1,width,headerheight+int((incidentcount)*incidentrowheight)-1],fill=colorMajor)
                vicarioustext.drawcenteredtext(draw, text, 24, int(width/2), headerheight + int((incidentcount-1) * incidentrowheight) + (incidentrowheight/2),colorMajorText)
        # look for critical incidents
        incidents = soup.find_all(class_="impact-critical")
        for incident in incidents:
            if incident.find(class_="actual-title") is not None:
                text = incident.find(class_="actual-title").get_text()
                incidentcount = incidentcount + 1
                draw.rectangle(xy=[0,headerheight+int((incidentcount-1)*incidentrowheight)+1,width,headerheight+int((incidentcount)*incidentrowheight)-1],fill=colorCritical)
                vicarioustext.drawcenteredtext(draw, text, 24, int(width/2), headerheight + int((incidentcount-1) * incidentrowheight) + (incidentrowheight/2),colorCriticalText)
        # look for maintenance
        incidents = soup.find_all(class_="impact-maintenance")
        for incident in incidents:
            if incident.find(class_="actual-title") is not None:
                text = incident.find(class_="actual-title").get_text()
                incidentcount = incidentcount + 1
                draw.rectangle(xy=[0,headerheight+int((incidentcount-1)*incidentrowheight)+1,width,headerheight+int((incidentcount)*incidentrowheight)-1],fill=colorMaintenance)
                vicarioustext.drawcenteredtext(draw, text, 24, int(width/2), headerheight + int((incidentcount-1) * incidentrowheight) + (incidentrowheight/2),colorMaintenanceText)
        # look for minor
        incidents = soup.find_all(class_="impact-minor")
        for incident in incidents:
            if incident.find(class_="actual-title") is not None:
                text = incident.find(class_="actual-title").get_text()
                incidentcount = incidentcount + 1
                draw.rectangle(xy=[0,headerheight+int((incidentcount-1)*incidentrowheight)+1,width,headerheight+int((incidentcount)*incidentrowheight)-1],fill=colorMinor)
                vicarioustext.drawcenteredtext(draw, text, 24, int(width/2), headerheight + int((incidentcount-1) * incidentrowheight) + (incidentrowheight/2),colorMinorText)
        # look for none
        incidents = soup.find_all(class_="impact-none")
        for incident in incidents:
            if incident.find(class_="actual-title") is not None:
                text = incident.find(class_="actual-title").get_text()
                incidentcount = incidentcount + 1
                draw.rectangle(xy=[0,headerheight+int((incidentcount-1)*incidentrowheight)+1,width,headerheight+int((incidentcount)*incidentrowheight)-1],fill=colorNone)
                vicarioustext.drawcenteredtext(draw, text, 24, int(width/2), headerheight + int((incidentcount-1) * incidentrowheight) + (incidentrowheight/2),colorNoneText)


    # report if no incidents
    if incidentcount == 0:
        vicarioustext.drawcenteredtext(draw, "No Known Incidents", 24, int(width/2), int(height/2), colorGoodText)
    # timestamp
    vicarioustext.drawbottomrighttext(draw, "as of " + vicarioustext.getdateandtime(), 12, width, height, colorTextFG)
    im.save(outputFile)


if __name__ == '__main__':
    # Defaults
    configFile="/home/nodeyez/nodeyez/config/compassminingstatus.json"
    outputFile="/home/nodeyez/nodeyez/imageoutput/compassminingstatus.png"
    statusurl="https://status.compassmining.io/"
    colorTextFG=ImageColor.getrgb("#ffffff")
    colorGoodText=ImageColor.getrgb("#40ff40")
    colorMaintenance=ImageColor.getrgb("#2020ff")
    colorMaintenanceText=ImageColor.getrgb("#ffffff")
    colorCritical=ImageColor.getrgb("#ff7a00")
    colorCriticalText=ImageColor.getrgb("#ffffff")
    colorMajor=ImageColor.getrgb("#ff2020")
    colorMajorText=ImageColor.getrgb("#ffffff")
    colorNone=ImageColor.getrgb("#333333")
    colorNoneText=ImageColor.getrgb("#ffffff")
    colorMinor=ImageColor.getrgb("#2020ff")
    colorMinorText=ImageColor.getrgb("#ffffff")
    colorBackground=ImageColor.getrgb("#000000")
    sleepInterval=300
    # Override config
    if exists(configFile):
        with open(configFile) as f:
            config = json.load(f)
        if "compassminingstatus" in config:
            config = config["compassminingstatus"]
        if "outputFile" in config:
            outputFile = config["outputFile"]
        if "statusurl" in config:
            statusurl = config["statusurl"]
        if "colorTextFG" in config:
            colorTextFG = ImageColor.getrgb(config["colorTextFG"])
        if "colorGoodText" in config:
            colorGoodText = ImageColor.getrgb(config["colorGoodText"])
        if "colorMaintenance" in config:
            colorMaintenance = ImageColor.getrgb(config["colorMaintenance"])
        if "colorMaintenanceText" in config:
            colorMaintenanceText = ImageColor.getrgb(config["colorMaintenanceText"])
        if "colorCritical" in config:
            colorCritical = ImageColor.getrgb(config["colorCritical"])
        if "colorCriticalText" in config:
            colorCriticalText = ImageColor.getrgb(config["colorCriticalText"])
        if "colorMajor" in config:
            colorMajor = ImageColor.getrgb(config["colorMajor"])
        if "colorMajorText" in config:
            colorMajorText = ImageColor.getrgb(config["colorMajorText"])
        if "colorNone" in config:
            colorNone = ImageColor.getrgb(config["colorNone"])
        if "colorNoneText" in config:
            colorNoneText = ImageColor.getrgb(config["colorNoneText"])
        if "colorMinor" in config:
            colorMinor = ImageColor.getrgb(config["colorMinor"])
        if "colorMinorText" in config:
            colorMinorText = ImageColor.getrgb(config["colorMinorText"])
        if "colorBackground" in config:
            colorBackground = ImageColor.getrgb(config["colorBackground"])
        if "sleepInterval" in config:
            sleepInterval = int(config["sleepInterval"])
            sleepInterval = 300 if sleepInterval < 300 else sleepInterval # minimum 5 minutes, access others
    # Check for single run
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h','--help']:
            print(f"Retrieves the Compass Mining status page and prepares a summary image")
            print(f"Usage:")
            print(f"1) Call without arguments to run continuously using the configuration or defaults")
            print(f"You may specify a custom configuration file at {configFile}")
            print(f"Depends on Beautiful Soup package.")
            print(f"   Install via:   pip install beautifulsoup4")
        else:
            createimage()
        exit(0)
    # Loop
    while True:
        createimage()
        time.sleep(sleepInterval)
