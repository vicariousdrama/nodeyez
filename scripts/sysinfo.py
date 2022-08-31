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

def drawicon(draw,icon,x,y,w,h,v=None):
    if icon == "thermometer":
        tw=w/3
        draw.ellipse(xy=(x,y+((h-y)/4*3),tw,h),fill=colorThermometerOutline,outline=None,width=1)
        draw.ellipse(xy=(x+((tw-x)/4*1),y,x+((tw-x)/4*3),y+((h-y)/4*1)),fill=colorThermometerOutline,outline=None,width=1)
        draw.rectangle(xy=(x+((tw-x)/4*1),y+((h-y)/8*1),x+((tw-x)/4*3),y+((h-y)/8*7)),fill=colorThermometerOutline,outline=None,width=1)
        draw.ellipse(xy=(x+2,y+2+((h-y)/4*3),tw-2,h-2),fill=colorThermometerUnfilled,outline=None,width=1)
        draw.ellipse(xy=(x+2+((tw-x)/4*1),y+2,x-2+((tw-x)/4*3),y-2+((h-y)/4*1)),fill=colorThermometerUnfilled,outline=None,width=1)
        draw.rectangle(xy=(x+2+((tw-x)/4*1),y+2+((h-y)/8*1),x-2+((tw-x)/4*3),y-2+((h-y)/8*7)),fill=colorThermometerUnfilled,outline=None,width=1)
        barcolor=colorThermometerBar
        barpos=3
        if int(v) > 55:
            barcolor=colorThermometerBarWarn
            barpos=2
        if int(v) > 65:
            barcolor=colorThermometerBarHot
            barpos=1
        draw.ellipse(xy=(x+4,y+4+(h/4*3),tw-4,h-4),fill=barcolor,outline=None,width=1)
        draw.rectangle(xy=(x+4+((tw-x)/4*1),y+4+(h/8*barpos),x-4+((tw-x)/4*3),y-4+(h/8*7)),fill=barcolor,outline=None,width=1)
        # lines
        for j in range(8):
            draw.rectangle(xy=(x+6+((tw-x)/4*3),y+(h/4)+((h/2/8)*j),x+26+((tw-x)/4*3),y+(h/4)+((h/2/8)*j)),fill=colorThermometerOutline,outline=colorThermometerOutline,width=3)
        vicarioustext.drawtoprighttext(draw, v + "°", 48, x+w, y+(h/2), colorHeader, True)
        vicarioustext.drawcenteredtext(draw, "Temp", 24, x+(w/2), y+20, colorHeader, True)
    if icon == "piestorage":
        if list(v.split())[5] == "error":
            drawicon(draw,"pieerror",x,y,w,h)
            return
        pct = int(list(v.split())[4].replace("%",""))
        gbf = list(v.split())[3]
        pad = 30
        ox = 3
        oy = 3
        if pct == 50:
            ox = 0
        if pct > 50:
            ox = ox * -1
        sa = 0
        ea = sa + math.floor(pct*3.6)
        slicecolor = colorPieGood
        textcolor = colorPieGoodText
        if pct > 80:
            slicecolor = colorPieWarn
            textcolor = colorPieWarnText
        if pct > 90:
            slicecolor = colorPieDanger
            textcolor = colorPieDangerText
        draw.pieslice(xy=(x+pad+ox,y+pad+oy,x+w+ox-pad,y+h+oy-pad),start=sa,end=ea,fill=slicecolor,outline=colorPieOutline,width=2)
        vicarioustext.drawtoplefttext(draw, "used", 16, x+(w/2), y+(h/2)+8, textcolor)
        ox = ox * -1
        oy = oy * -1
        sa = ea
        ea = 360
        draw.pieslice(xy=(x+pad+ox,y+pad+oy,x+w+ox-pad,y+h+oy-pad),start=sa,end=ea,fill=colorPieEmpty,outline=colorPieOutline,width=2)
        vicarioustext.drawbottomlefttext(draw, "free", 16, x+(w/2), y+(h/2)-8, colorPieEmptyText)
        vicarioustext.drawcenteredtext(draw, gbf + " free", 20, x+(w/2), y+h-10, colorPieLabelText)
    if icon == "sdcard":
        drawicon(draw,"piestorage",x,y,w,h,v)
        vicarioustext.drawcenteredtext(draw, "/dev/root", 24, x+(w/2), y+20, colorHeader, True)
    if icon == "hdd":
        drawicon(draw,"piestorage",x,y,w,h,v)
        vicarioustext.drawcenteredtext(draw, "/dev/sda1", 24, x+(w/2), y+20, colorHeader, True)
    if icon == "cpuload":
        vicarioustext.drawcenteredtext(draw, "CPU Load", 24, x+(w/2), y+20, colorHeader, True)
        vicarioustext.drawlefttext(draw, "1 min", 16, x+6, y+((h/8)*3), colorCPULabelText)
        vicarioustext.drawlefttext(draw, "5 min", 16, x+6, y+((h/8)*5), colorCPULabelText)
        vicarioustext.drawlefttext(draw, "15 min", 16, x+6, y+((h/8)*7), colorCPULabelText)
        ttw = 72
        for j in range(3):
            draw.rounded_rectangle(xy=(x+ttw+3,y+((h/8)*((j*2)+2))+3,x+w,y+((h/8)*((j*2)+4))-3),radius=4,outline=colorCPUOutline,width=2)
            ld = list(v.split())[j]
            ldw = int(((x+w)-(x+ttw+3)) * (float(ld)/float(getprocessorcount())))
            barcolor=colorCPUGood
            if float(ld) > .50:
                barcolor=colorCPUWarn
            if float(ld) > .75:
                barcolor=colorCPUDanger
            draw.rounded_rectangle(xy=(x+ttw+3+1,y+((h/8)*((j*2)+2))+4,x+ttw+3+1+ldw,y+((h/8)*((j*2)+4))-3-1),radius=4,fill=barcolor,width=1)
    if icon == "memory":
        l = list(v.split())[0]
        p = list(v.split())[1]
        pad = 20
        draw.arc(xy=(x+pad,y+(pad*2),x+w-pad,y+h),start=120,end=420,fill=colorMEMOutline,width=20)
        draw.arc(xy=(x+pad+2,y+(pad*2)+2,x+w-pad-2,y+h-2),start=120+1,end=420-1,fill=colorMEMEmpty,width=16)
        arccolor=colorMEMGood
        if int(p) == 0:
            p = "1"
        if int(p) > 75:
            arccolor=colorMEMWarn
        if int(p) > 90:
            arccolor=colorMEMDanger
        ea=120+int((420-120)*(float(p)/100))
        draw.arc(xy=(x+pad+2,y+(pad*2)+2,x+w-pad-2,y+h-2),start=120,end=ea,fill=arccolor,width=16)
        vicarioustext.drawcenteredtext(draw, l, 24, x+(w/2), y+20, colorHeader, True)
        vicarioustext.drawcenteredtext(draw, p + "%", 20, x+(w/2), y+(h/2)+20, colorMEMLabelText)
    if icon == "datetime":
        vicarioustext.drawbottomrighttext(draw, "as of " + vicarioustext.getdateandtime(), 12, w, h)

def createimage(width=480, height=320):
    bw=width/3
    bh=height/2
    im = Image.new(mode="RGB", size=(width, height), color=colorBackground)
    draw = ImageDraw.Draw(im)
    drawicon(draw,"thermometer",5,5,bw-10,bh-10,v=str(gettemp()))
    drawicon(draw,"sdcard",5+bw,5,bw-10,bh-10,v=str(getdrivefree("/dev/root")))
    drawicon(draw,"hdd",5+bw+bw,5,bw-10,bh-10,v=str(getdrivefree("/dev/sda1")))
    drawicon(draw,"cpuload",5,bh+5,bw,bh-10,v=str(getloadavg()))
    drawicon(draw,"memory",5+bw,bh+5,bw,bh-10,v=str(getmemusage("Mem","RAM")))
    drawicon(draw,"memory",5+bw+bw,bh+5,bw,bh-10,v=str(getmemusage("Swap","Swap")))
    drawicon(draw,"datetime",0,0,width,height)
    im.save(outputFile)
    im.close()

def gettemp():
    cmd = "cat /sys/class/thermal/thermal_zone0/temp"
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
        temp = int(cmdoutput)
        return math.floor(temp/1000)
    except subprocess.CalledProcessError as e:
        return -1

def getdrivefree(path):
    cmd = "df -h | grep " + path
    try:
        return subprocess.check_output(cmd, shell=True).decode("utf-8")
    except subprocess.CalledProcessError as e:
        return path + " 0G 0G 0G 1% error"

def getloadavg():
    cmd = "cat /proc/loadavg"
    try:
        return subprocess.check_output(cmd, shell=True).decode("utf-8")
    except subprocess.CalledProcessError as e:
        return "1.00 1.00 1.00 9 99999"

def getprocessorcount():
    cmd = "cat /proc/cpuinfo | grep processor | wc -l"
    try:
        return int(subprocess.check_output(cmd, shell=True).decode("utf-8"))
    except subprocess.CalledProcessError as e:
        return 4

def getmemusage(memtype,label):
    cmd = "free --mebi | grep " + memtype
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
        t = list(cmdoutput.split())[1]
        u = list(cmdoutput.split())[2]
        v = int((float(u)/float(t))*100)
        return label + " " + str(v)
    except subprocess.CalledProcessError as e:
        return label + " ?"

if __name__ == '__main__':
    # Defaults
    configFile="/home/nodeyez/nodeyez/config/sysinfo.json"
    outputFile="/home/nodeyez/nodeyez/imageoutput/sysinfo.png"
    width=480
    height=320
    sleepInterval=30
    colorHeader=ImageColor.getrgb("#ffffff")
    colorThermometerUnfilled=ImageColor.getrgb("#000000")
    colorThermometerOutline=ImageColor.getrgb("#c0c0c0")
    colorThermometerBar=ImageColor.getrgb("#40ff40")
    colorThermometerBarWarn=ImageColor.getrgb("#ffff00")
    colorThermometerBarHot=ImageColor.getrgb("#ff0000")
    colorPieOutline=ImageColor.getrgb("#c0c0c0")
    colorPieEmpty=ImageColor.getrgb("#000000")
    colorPieEmptyText=ImageColor.getrgb("#ffffff")
    colorPieGood=ImageColor.getrgb("#40ff40")
    colorPieGoodText=ImageColor.getrgb("#000000")
    colorPieWarn=ImageColor.getrgb("#ffff00")
    colorPieWarnText=ImageColor.getrgb("#000000")
    colorPieDanger=ImageColor.getrgb("#ff0000")
    colorPieDangerText=ImageColor.getrgb("#ffffff")
    colorPieLabelText=ImageColor.getrgb("#ffffff")
    colorCPUOutline=ImageColor.getrgb("#c0c0c0")
    colorCPUEmpty=ImageColor.getrgb("#000000")
    colorCPUGood=ImageColor.getrgb("#40ff40")
    colorCPUWarn=ImageColor.getrgb("#ffff00")
    colorCPUDanger=ImageColor.getrgb("#ff0000")
    colorCPULabelText=ImageColor.getrgb("#ffffff")
    colorMEMOutline=ImageColor.getrgb("#c0c0c0")
    colorMEMEmpty=ImageColor.getrgb("#000000")
    colorMEMGood=ImageColor.getrgb("#40ff40")
    colorMEMWarn=ImageColor.getrgb("#ffff00")
    colorMEMDanger=ImageColor.getrgb("#ff0000")
    colorMEMLabelText=ImageColor.getrgb("#ffffff")
    colorBackground=ImageColor.getrgb("#000000")
    # Override defaults
    if exists(configFile):
        with open(configFile) as f:
            config = json.load(f)
        if "sysinfo" in config:
            config = config["sysinfo"]
        if "outputFile" in config:
            outputFile = config["outputFile"]
        if "width" in config:
            width = int(config["width"])
        if "height" in config:
            height = int(config["height"])
        if "sleepInterval" in config:
            sleepInterval = int(config["sleepInterval"])
            sleepInterval = 10 if sleepInterval < 10 else sleepInterval # minimum 10 seconds, local only
        if "colorHeader" in config:
            colorHeader = ImageColor.getrgb(config["colorHeader"])
        if "colorThermometerUnfilled" in config:
            colorThermometerUnfilled = ImageColor.getrgb(config["colorThermometerUnfilled"])
        if "colorThermometerOutline" in config:
            colorThermometerOutline = ImageColor.getrgb(config["colorThermometerOutline"])
        if "colorThermometerBar" in config:
            colorThermometerBar = ImageColor.getrgb(config["colorThermometerBar"])
        if "colorThermometerBarWarn" in config:
            colorThermometerBarWarn = ImageColor.getrgb(config["colorThermometerBarWarn"])
        if "colorThermometerBarHot" in config:
            colorThermometerBarHot = ImageColor.getrgb(config["colorThermometerBarHot"])
        if "colorPieOutline" in config:
            colorPieOutline = ImageColor.getrgb(config["colorPieOutline"])
        if "colorPieEmpty" in config:
            colorPieEmpty = ImageColor.getrgb(config["colorPieEmpty"])
        if "colorPieEmptyText" in config:
            colorPieEmptyText = ImageColor.getrgb(config["colorPieEmptyText"])
        if "colorPieGood" in config:
            colorPieGood = ImageColor.getrgb(config["colorPieGood"])
        if "colorPieGoodText" in config:
            colorPieGoodText = ImageColor.getrgb(config["colorPieGoodText"])
        if "colorPieWarn" in config:
            colorPieWarn = ImageColor.getrgb(config["colorPieWarn"])
        if "colorPieWarnText" in config:
            colorPieWarnText = ImageColor.getrgb(config["colorPieWarnText"])
        if "colorPieDanger" in config:
            colorPieDanger = ImageColor.getrgb(config["colorPieDanger"])
        if "colorPieDangerText" in config:
            colorPieDangerText = ImageColor.getrgb(config["colorPieDangerText"])
        if "colorPieLabelText" in config:
            colorPieLabelText = ImageColor.getrgb(config["colorPieLabelText"])
        if "colorCPUOutline" in config:
            colorCPUOutline = ImageColor.getrgb(config["colorCPUOutline"])
        if "colorCPUEmpty" in config:
            colorCPUEmpty = ImageColor.getrgb(config["colorCPUEmpty"])
        if "colorCPUGood" in config:
            colorCPUGood = ImageColor.getrgb(config["colorCPUGood"])
        if "colorCPUWarn" in config:
            colorCPUWarn = ImageColor.getrgb(config["colorCPUWarn"])
        if "colorCPUDanger" in config:
            colorCPUDanger = ImageColor.getrgb(config["colorCPUDanger"])
        if "colorCPULabelText" in config:
            colorCPULabelText = ImageColor.getrgb(config["colorCPULabelText"])
        if "colorMEMOutline" in config:
            colorMEMOutline = ImageColor.getrgb(config["colorMEMOutline"])
        if "colorMEMEmpty" in config:
            colorMEMEmpty = ImageColor.getrgb(config["colorMEMEmpty"])
        if "colorMEMGood" in config:
            colorMEMGood = ImageColor.getrgb(config["colorMEMGood"])
        if "colorMEMWarn" in config:
            colorMEMWarn = ImageColor.getrgb(config["colorMEMWarn"])
        if "colorMEMDanger" in config:
            colorMEMDanger = ImageColor.getrgb(config["colorMEMDanger"])
        if "colorMEMLabelText" in config:
            colorMEMLabelText = ImageColor.getrgb(config["colorMEMLabelText"])
        if "colorBackground" in config:
            colorBackground = ImageColor.getrgb(config["colorBackground"])
    # Check for single run
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h','--help']:
            print(f"Generates a visual of the system running state with temp, memory, storage used")
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
