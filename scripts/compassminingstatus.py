#! /usr/bin/python3
from PIL import Image, ImageDraw, ImageColor
from bs4 import BeautifulSoup
import time
import requests
import vicarioustext

# Depends on 
#    pip install beautifulsoup4

outputFile="/home/bitcoin/images/compassminingstatus.png"
statusurl="https://status.compassmining.io/"
colorFFFFFF=ImageColor.getrgb("#ffffff")
colorGood=ImageColor.getrgb("#40ff40")
colorMaintenance=ImageColor.getrgb("#2020ff")
colorCritical=ImageColor.getrgb("#ff7a00")
colorMajor=ImageColor.getrgb("#ff2020")
colorNone=ImageColor.getrgb("#333333")

def getstatuspage():
    page = requests.get(statusurl)
    soup = BeautifulSoup(page.content, 'html.parser')
    return soup

def createimage(width=480, height=320):
    soup = getstatuspage()
    headerheight = 30
    im = Image.new(mode="RGB", size=(width, height))
    draw = ImageDraw.Draw(im)
    # header
    vicarioustext.drawcenteredtext(draw, "Compass Mining Status", 24, int(width/2), int(headerheight/2), colorFFFFFF, True)
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
                vicarioustext.drawcenteredtext(draw, text, 24, int(width/2), headerheight + int((incidentcount-1) * incidentrowheight) + (incidentrowheight/2))
        # look for critical incidents
        incidents = soup.find_all(class_="impact-critical")
        for incident in incidents:
            if incident.find(class_="actual-title") is not None:
                text = incident.find(class_="actual-title").get_text()
                incidentcount = incidentcount + 1
                draw.rectangle(xy=[0,headerheight+int((incidentcount-1)*incidentrowheight)+1,width,headerheight+int((incidentcount)*incidentrowheight)-1],fill=colorCritical)
                vicarioustext.drawcenteredtext(draw, text, 24, int(width/2), headerheight + int((incidentcount-1) * incidentrowheight) + (incidentrowheight/2))
        # look for maintenance
        incidents = soup.find_all(class_="impact-maintenance")
        for incident in incidents:
            if incident.find(class_="actual-title") is not None:
                text = incident.find(class_="actual-title").get_text()
                incidentcount = incidentcount + 1
                draw.rectangle(xy=[0,headerheight+int((incidentcount-1)*incidentrowheight)+1,width,headerheight+int((incidentcount)*incidentrowheight)-1],fill=colorMaintenance)
                vicarioustext.drawcenteredtext(draw, text, 24, int(width/2), headerheight + int((incidentcount-1) * incidentrowheight) + (incidentrowheight/2))
        # look for none
        incidents = soup.find_all(class_="impact-none")
        for incident in incidents:
            if incident.find(class_="actual-title") is not None:
                text = incident.find(class_="actual-title").get_text()
                incidentcount = incidentcount + 1
                draw.rectangle(xy=[0,headerheight+int((incidentcount-1)*incidentrowheight)+1,width,headerheight+int((incidentcount)*incidentrowheight)-1],fill=colorNone)
                vicarioustext.drawcenteredtext(draw, text, 24, int(width/2), headerheight + int((incidentcount-1) * incidentrowheight) + (incidentrowheight/2))


    # report if no incidents
    if incidentcount == 0:
        vicarioustext.drawcenteredtext(draw, "No Known Incidents", 24, int(width/2), int(height/2), colorGood)
    # timestamp
    vicarioustext.drawbottomrighttext(draw, "as of " + vicarioustext.getdateandtime(), 12, width, height)
    im.save(outputFile)

while True:
    createimage()
    time.sleep(300)
