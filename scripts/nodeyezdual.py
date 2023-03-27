#! /usr/bin/env python3
from PIL import Image, ImageDraw, ImageColor
from os.path import exists
import json
import numpy as np
import sys
import time
import random
import vicariousnetwork
import vicariousstat
import vicarioustext
import sysinfo

def recolor(imInput, fromRGB, toRGB):
    im = imInput.convert('RGBA')
    data = np.array(im)
    red,green,blue,alpha = data.T
    colorset = (red==fromRGB[0]) & (green==fromRGB[1]) & (blue==fromRGB[2])
    data[...,:-1][colorset.T]=toRGB
    imOutput = Image.fromarray(data)
    return imOutput

def resizeToWidth(imInput, desiredWidth):
    w = imInput.width
    h = imInput.height
    if w == desiredWidth:
        return imInput
    else:
        r = desiredWidth / w
        nw = int(w * r)
        nh = int(h * r)
        imOutput = imInput.resize((nw,nh))
        return imOutput

def getrandomimage(list):
    found = False
    count = 10
    goodurl = ""
    while (not found) and (count > 0):
        url = random.choice(list)
        im = vicariousnetwork.getimagefromurl(False, url)
        found = im.width > 1
        count = count - 1
        goodurl = url
    if not found:
        im = im.convert('RGBA')
    else:
        print(f"using {goodurl}")
    return im

def createimage(width=480, height=800):
    ### Create canvas
    canvas = Image.new(mode="RGBA", size=(width, height), color=colorBackground)
    draw = ImageDraw.Draw(canvas)

    ### Determine Accent Color
    accentR = random.randint(48,255)
    accentG = random.randint(48,255)
    accentB = random.randint(48,255)
    accentColor3 = (accentR, accentG, accentB)
    accentColor4 = (accentR, accentG, accentB, 255)

    ### Header
    # random colorization (the foreground of the source image is #666666 = 102,102,102)
    imgHeaderC = recolor(imgHeader, (102,102,102), accentColor3)
    # resize to width
    imgHeaderC = resizeToWidth(imgHeaderC, width)
    # paste header into image
    canvas.alpha_composite(imgHeaderC)

    ### System Info Icons
    iconw = width/6
    iconh = iconw
    iconx = 0
    icony = imgHeaderC.height + 2
    sysinfo.colorHeader = accentColor4
    sysinfo.colorPieLabelText = accentColor4
    sysinfo.colorCPULabelText = accentColor4
    labelsize=int(iconh*.15)
    # CPU Temp
    cputemp = vicariousstat.getcputemp()                        # 46251 = 46.251 degrees C (as an int)
    cputempi = int(float(cputemp)/1000)
    cputemps = str(cputempi)
    sysinfo.drawicon(draw,"thermometer",iconx,icony,iconw,iconh,cputemps)
    iconx += iconw
    # Drive 1
    drive1info = vicariousstat.getdrive1info()                  # ('/', '21G', '74') = tuple of mount point, free space, free percent
    drive1infov = "X X X " + drive1info[1] + " " + str(100-int(drive1info[2])) + "% " + drive1info[0]
    sysinfo.drawicon(draw,"piestorage",iconx,icony,iconw,iconh,drive1infov)
    vicarioustext.drawcenteredtext(draw, "Root Drive", labelsize, iconx+(iconw/2), icony+(iconh*.08), accentColor4, True)
    iconx += iconw
    # Drive 2
    drive2info = vicariousstat.getdrive2info()                  # ('/mnt/hdd', '254G', '29') = tuple of mount point, free space, free percent
    if drive2info[0] != "None":
        drive2infov = "X X X " + drive2info[1] + " " + str(100-int(drive2info[2])) + "% " + drive2info[0]
        sysinfo.drawicon(draw,"piestorage",iconx,icony,iconw,iconh,drive2infov)
        vicarioustext.drawcenteredtext(draw, "2nd Drive", labelsize, iconx+(iconw/2), icony+(iconh*.08), accentColor4, True)
        iconx += iconw
    # CPU Load
    cpuload = vicariousstat.getload()                           # (0.14, 0.40, 0.52) = tuple of 1, 5, 15 minute period load on cpu (as float)
    cpuloadv = str(cpuload[0]) + " " + str(cpuload[1]) + " " + str(cpuload[2])
    sysinfo.drawicon(draw,"cpuload",iconx,icony,iconw,iconh,cpuloadv)
    iconx += iconw
    # Miscellaneous
    memoryavailable = vicariousstat.getmemoryavailable()        # 904   = 904 MB free (as an int)
    networkrx = vicariousstat.getnetworkrx()                    # 134G  = 134 GB received (as a string)
    networktx = vicariousstat.getnetworktx()                    # 289G  = 289 GB sent (as a string)
    uptime = vicariousstat.getuptime()                          # 72 days (as a string)
    iconx += 10
    vicarioustext.drawlefttext(draw, "Avail. Mem:    ", labelsize, iconx, icony+(iconh*.08), accentColor4, True)
    vicarioustext.drawlefttext(draw, "Net Data Rx:   ", labelsize, iconx, icony+(iconh*.33), accentColor4, True)
    vicarioustext.drawlefttext(draw, "Net Data Tx:   ", labelsize, iconx, icony+(iconh*.58), accentColor4, True)
    vicarioustext.drawlefttext(draw, "Uptime:        ", labelsize, iconx, icony+(iconh*.83), accentColor4, True)
    td = vicarioustext.gettextdimensions(draw, "Net Data Rx:   ", labelsize)
    iconx += td[0]
    vicarioustext.drawlefttext(draw, str(memoryavailable) + "M", labelsize, iconx, icony+(iconh*.08), accentColor4)
    vicarioustext.drawlefttext(draw, networkrx, labelsize, iconx, icony+(iconh*.33), accentColor4)
    vicarioustext.drawlefttext(draw, networktx, labelsize, iconx, icony+(iconh*.58), accentColor4)
    vicarioustext.drawlefttext(draw, uptime, labelsize, iconx, icony+(iconh*.83), accentColor4)
    td = vicarioustext.gettextdimensions(draw, uptime, labelsize)
    iconx += td[0]

    ### Stacking images from bottom to top, as many as will fit
    canvasY = height
    isFitting = True
    while isFitting:
        #### Bottom Images
        img = getrandomimage(bottomImages)
        img = resizeToWidth(img, width)
        if canvasY - img.height > 0:
            canvasY -= img.height
            canvas.paste(img, box=(0,canvasY))
        else:
            isFitting = False
        img.close()
        #### Divider
        canvasY -= dividerBuffer if dividerBuffer > 0 else 0
        if dividerHeight > 0:
            canvasY -= dividerHeight
            draw.rectangle(xy=((0,canvasY),(width,canvasY+dividerHeight)),fill=accentColor4)
        canvasY -= dividerBuffer if dividerBuffer > 0 else 0
        #### Top Images
        img = getrandomimage(topImages)
        img = resizeToWidth(img, width)
        if canvasY - img.height > 0:
            canvasY -= img.height
            canvas.paste(img, box=(0,canvasY))
        else:
            isFitting = False
        img.close()

    ### Save it
    print(f"Saving file to {outputFile}")
    canvas.save(outputFile)
    canvas.close()

if __name__ == '__main__':
    # Defaults
    configFile="../config/nodeyezdual.json"
    outputFile="../imageoutput/nodeyezdual.png"
    useTor=False
    width=480
    height=800
    sleepInterval=30
    headerSVG="https://nodeyez.com/images/nodeyez.svg"
    topImages= [
        "https://nodeyez.com/images/arthash-719360.png",
        "https://nodeyez.com/images/blockhashdungeon.png",
        "https://nodeyez.com/images/blockheight.png",
        "https://nodeyez.com/images/lndchannelbalance.png",
        "https://nodeyez.com/images/lndchannelfees.png",
        "https://nodeyez.com/images/difficultyepoch.png",
        "https://nodeyez.com/images/halving.png",
        "https://nodeyez.com/images/utcclock.png",
    ]
    bottomImages= [
        "https://nodeyez.com/images/fearandgreed.png",
        "https://nodeyez.com/images/fiatprice.png",
        "https://nodeyez.com/images/mempoolblocks.png",
        "https://nodeyez.com/images/satsperusd.png",
    ]
    colorBackground=ImageColor.getrgb("#000000")
    dividerHeight=10
    dividerBuffer=5
    # referenced in sysinfo
    colorThermometerUnfilled=ImageColor.getrgb("#000000")
    colorThermometerOutline=ImageColor.getrgb("#c0c0c0")
    colorThermometerBar=ImageColor.getrgb("#40ff40")
    colorThermometerBarWarn=ImageColor.getrgb("#ffff00")
    colorThermometerBarHot=ImageColor.getrgb("#ff0000")
    # Override defaults
    if exists(configFile):
        with open(configFile) as f:
            config = json.load(f)
        if "nodeyezdual" in config:
            config = config["nodeyezdual"]
        if "outputFile" in config:
            outputFile = config["outputFile"]
        if "useTor" in config:
            useTor = config["useTor"]
        if "width" in config:
            width = int(config["width"])
        if "height" in config:
            height = int(config["height"])
        if "sleepInterval" in config:
            sleepInterval = int(config["sleepInterval"])
            sleepInterval = 5 if sleepInterval < 5 else sleepInterval # minimum 1 minutes, access others
        if "headerSVG" in config:
            headerSVG = config["headerSVG"]
        if "topImages" in config:
            topImages = config["topImages"]
        if "bottomImages" in config:
            bottomImages = config["bottomImages"]
        if "colorBackground" in config:
            colorBackground = ImageColor.getrgb(config["colorBackground"])
        if "dividerHeight" in config:
            dividerHeight = int(config["dividerHeight"])
        if "dividerBuffer" in config:
            dividerBuffer = int(config["dividerBuffer"])
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h','--help']:
            print(f"Retrieves existing images and builds a composite of 2 for Nodeyez in portrait orientation")
            print(f"Usage:")
            print(f"1) Call without arguments to run continuously using the configuration or defaults")
            print(f"2) Pass an argument other than -h or --help to run once and exit")
            print(f"You may specify a custom configuration file at {configFile}")
        else:
            imgHeader = vicariousnetwork.getimagefromurl(useTor, headerSVG)
            createimage(width,height)
        exit(0)
    # Get header file one time
    imgHeader = vicariousnetwork.getimagefromurl(useTor, headerSVG)
    # Loop
    while True:
        createimage(width,height)
        ### Wait till next run
        print(f"sleeping for {sleepInterval} seconds")
        time.sleep(sleepInterval)
