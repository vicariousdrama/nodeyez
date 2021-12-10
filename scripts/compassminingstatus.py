#! /usr/bin/python3
from datetime import datetime
from PIL import Image, ImageFilter, ImageDraw, ImageFont, ImageColor
from bs4 import BeautifulSoup
import json
import math
import subprocess
import time
import requests

# Depends on
#    pip install beautifulsoup4

outputFile="/home/bitcoin/images/compassminingstatus.png"
statusurl="https://status.compassmining.io/"
colorFFFFFF=ImageColor.getrgb("#ffffff")
colorGood=ImageColor.getrgb("#40ff40")
colorMaintenance=ImageColor.getrgb("#2020ff")
colorMajor=ImageColor.getrgb("#ff2020")
fontDeja12=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",12)
fontDeja16=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",16)
fontDeja24=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",24)

def getdateandtime():
    now = datetime.utcnow()
    return now.strftime("%Y-%m-%d %H:%M:%S")

def getfont(size):
    if size == 12:
        return fontDeja12
    if size == 16:
        return fontDeja16
    if size == 24:
        return fontDeja24

def getstatuspage():
    page = requests.get(statusurl)
    soup = BeautifulSoup(page.content, 'html.parser')
    return soup

def drawcenteredtext(draw, s, fontsize, x, y, textcolor=colorFFFFFF):
    thefont = getfont(fontsize)
    sw,sh = draw.textsize(s, thefont)
    ox,oy = thefont.getoffset(s)
    sw += ox
    sh += oy
    draw.text(xy=(x-(sw/2),y-(sh/2)), text=s, font=thefont, fill=textcolor)

def drawbottomlefttext(draw, s, fontsize, x, y, textcolor=colorFFFFFF):
    thefont = getfont(fontsize)
    sw,sh = draw.textsize(s, thefont)
    ox,oy = thefont.getoffset(s)
    sw += ox
    sh += oy
    draw.text(xy=(x,y-sh), text=s, font=thefont, fill=textcolor)

def drawbottomrighttext(draw, s, fontsize, x, y, textcolor=colorFFFFFF):
    thefont = getfont(fontsize)
    sw,sh = draw.textsize(s, thefont)
    ox,oy = thefont.getoffset(s)
    sw += ox
    sh += oy
    draw.text(xy=(x-sw,y-sh), text=s, font=thefont, fill=colorFFFFFF)

def drawtoplefttext(draw, s, fontsize, x, y, textcolor=colorFFFFFF):
    thefont = getfont(fontsize)
    sw,sh = draw.textsize(s, thefont)
    ox,oy = thefont.getoffset(s)
    sw += ox
    sh += oy
    draw.text(xy=(x,y), text=s, font=thefont, fill=textcolor)

def drawtoprighttext(draw, s, fontsize, x, y, textcolor=colorFFFFFF):
    thefont = getfont(fontsize)
    sw,sh = draw.textsize(s, thefont)
    ox,oy = thefont.getoffset(s)
    sw += ox
    sh += oy
    draw.text(xy=(x-sw,y), text=s, font=thefont, fill=textcolor)

def drawrighttext(draw, s, fontsize, x, y, textcolor=colorFFFFFF):
    thefont = getfont(fontsize)
    sw,sh = draw.textsize(s, thefont)
    ox,oy = thefont.getoffset(s)
    sw += ox
    sh += oy
    draw.text(xy=(x-sw,y-(sh/2)), text=s, font=thefont, fill=textcolor)

def drawlefttext(draw, s, fontsize, x, y, textcolor=colorFFFFFF):
    thefont = getfont(fontsize)
    sw,sh = draw.textsize(s, thefont)
    ox,oy = thefont.getoffset(s)
    sw += ox
    sh += oy
    draw.text(xy=(x,y-(sh/2)), text=s, font=thefont, fill=textcolor)

def createimage(width=480, height=320):
    soup = getstatuspage()
    headerheight = 30
    im = Image.new(mode="RGB", size=(width, height))
    draw = ImageDraw.Draw(im)
    # header
    drawcenteredtext(draw, "Compass Mining Status", 24, int(width/2), int(headerheight/2))
    # incidents
    incidentcount = 0
    incidentrowheight = 40
    # top block
    if False:
        # look for major incidents
        incidents = soup.find_all(class_="impact-major")
        for incident in incidents:
            if incident.find(class_="actual-title") is not None:
                text = incident.find(class_="actual-title").get_text()
                incidentcount = incidentcount + 1
                draw.rectangle(xy=[0,headerheight+int((incidentcount-1)*incidentrowheight)+1,width,headerheight+int((incidentcount)*incidentrowheight)-1],fill=colorMajor)
                drawcenteredtext(draw, text, 24, int(width/2), headerheight + int((incidentcount-1) * incidentrowheight) + (incidentrowheight/2))
        # look for maintenance
        incidents = soup.find_all(class_="impact-maintenance")
        for incident in incidents:
            if incident.find(class_="actual-title") is not None:
                text = incident.find(class_="actual-title").get_text()
                incidentcount = incidentcount + 1
                draw.rectangle(xy=[0,headerheight+int((incidentcount-1)*incidentrowheight)+1,width,headerheight+int((incidentcount)*incidentrowheight)-1],fill=colorMaintenance)
                drawcenteredtext(draw, text, 24, int(width/2), headerheight + int((incidentcount-1) * incidentrowheight) + (incidentrowheight/2))
    # uptime svg block
    if True:
        incidents = soup.find_all(class_="status-red")
        for incident in incidents:
            if incident.find(class_="name") is not None:
                text = incident.find(class_="name").get_text()
                incidentcount = incidentcount + 1
                draw.rectangle(xy=[0,headerheight+int((incidentcount-1)*incidentrowheight)+1,width,headerheight+int((incidentcount)*incidentrowheight)-1],fill=colorMajor)
                drawcenteredtext(draw, text, 24, int(width/2), headerheight + int((incidentcount-1) * incidentrowheight) + (incidentrowheight/2))
        incidents = soup.find_all(class_="status-blue")
        for incident in incidents:
            if incident.find(class_="name") is not None:
                text = incident.find(class_="name").get_text()
                incidentcount = incidentcount + 1
                draw.rectangle(xy=[0,headerheight+int((incidentcount-1)*incidentrowheight)+1,width,headerheight+int((incidentcount)*incidentrowheight)-1],fill=colorMaintenance)
                drawcenteredtext(draw, text, 24, int(width/2), headerheight + int((incidentcount-1) * incidentrowheight) + (incidentrowheight/2))
    # report if no incidents
    if incidentcount == 0:
        drawcenteredtext(draw, "No Known Incidents", 24, int(width/2), int(height/2), colorGood)
    # timestamp
    drawbottomrighttext(draw, "as of " + getdateandtime(), 12, width, height)
    im.save(outputFile)

while True:
    createimage()
    time.sleep(300)
