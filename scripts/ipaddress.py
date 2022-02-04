#! /usr/bin/python3
from PIL import Image, ImageDraw, ImageColor
import subprocess
import time
import vicarioustext

outputFile="/home/bitcoin/images/ipaddress.png"
colorFFFFFF=ImageColor.getrgb("#ffffff")

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
    im = Image.new(mode="RGB", size=(width, height))
    draw = ImageDraw.Draw(im)
    vicarioustext.drawcenteredtext(draw, str(currentip), 36, int(width/2), int(height/2), colorFFFFFF, True)
    vicarioustext.drawbottomrighttext(draw, "as of " + vicarioustext.getdateandtime(), 12, width, height)
    im.save(outputFile)

while True:
    createimage()
    time.sleep(120)
