#! /usr/bin/python3
from PIL import Image, ImageDraw, ImageColor
import json
import math
import subprocess
import time
import vicarioustext

outputFile="/home/bitcoin/images/satsperusd.png"
priceurl="https://bisq.markets/bisq/api/markets/ticker"
useTor=True
satshape="square" # may be one of these: ['square','circle']
sleepInterval=3600
showBigText=True
showBigTextOnTop=True
colorBisq=ImageColor.getrgb("#40FF40")
colorHeader=ImageColor.getrgb("#ffffff")
colorSatShape=ImageColor.getrgb("#ff7f00")
colorSatAmount=ImageColor.getrgb("#4040407f")
colorSatAmountShadow=ImageColor.getrgb("#ffffff7f")

last=1
low=1
high=1

def drawsatssquare(draw,dc,dr,spf,satw,bpx,bpy):
    satsleft = spf
    for y in range(10):
        for x in range(10):
            if satsleft > 0:
                tlx = (bpx + (dc*11*satw) + (x*satw))
                tly = (bpy + (dr*11*satw) + (y*satw))
                brx = tlx+satw-2
                bry = tly+satw-2
                if satshape == "square":
                    draw.rectangle(xy=((tlx,tly),(brx,bry)),fill=colorSatShape)
                if satshape == "circle":
                    draw.ellipse(xy=((tlx,tly),(brx,bry)),fill=colorSatShape)
            satsleft = satsleft - 1

def createimage(width=480, height=320):
    last,high,low = getpriceinfo()
    satsperfiatunit = int(round(100000000.0 / last))
    satsperfiatunitlow = int(round(100000000.0 / low))
    satsperfiatunithigh = int(round(100000000.0 / high))
    satsleft = satsperfiatunit
    satw=int(math.floor(width/87))
    padleft=int(math.floor((width-(87*satw))/2))
    padtop=40
    im = Image.new(mode="RGB", size=(width, height))
    draw = ImageDraw.Draw(im)
    if showBigText and not showBigTextOnTop:
        vicarioustext.drawcenteredtext(draw, str(satsperfiatunit), 128, int(width/2), int(height/2), colorSatAmountShadow)
        vicarioustext.drawcenteredtext(draw, str(satsperfiatunit), 128, int(width/2)-2, int(height/2)-2, colorSatAmount)
    dc = 0
    dr = 0
    while satsleft > 100:
        satsleft = satsleft - 100
        drawsatssquare(draw,dc,dr,100,satw,padleft,padtop)
        dc = dc + 1
        if dc >= 8:
            dr = dr + 1
            dc = 0
    drawsatssquare(draw,dc,dr,satsleft,satw,padleft,padtop)
    if showBigText and showBigTextOnTop:
        vicarioustext.drawcenteredtext(draw, str(satsperfiatunit), 128, int(width/2), int(height/2), colorSatAmountShadow)
        vicarioustext.drawcenteredtext(draw, str(satsperfiatunit), 128, int(width/2)-2, int(height/2)-2, colorSatAmount)
    vicarioustext.drawcenteredtext(draw, "Sats Per USD", 24, int(width/2), int(padtop/2), colorHeader, True)
    if not showBigText:
        vicarioustext.drawcenteredtext(draw, "Last: " + str(satsperfiatunit), 20, int(width/8*4), height-padtop)
    vicarioustext.drawcenteredtext(draw, "High: " + str(satsperfiatunitlow), 20, int(width/8*7), height-padtop)
    vicarioustext.drawcenteredtext(draw, "Low: " + str(satsperfiatunithigh), 20, int(width/8*1), height-padtop)
    vicarioustext.drawbottomlefttext(draw, "Market data by bisq", 16, 0, height, colorBisq)
    vicarioustext.drawbottomrighttext(draw, "as of " + vicarioustext.getdateandtime(), 12, width, height)
    im.save(outputFile)

def getpriceinfo():
    cmd = "curl --silent " + priceurl
    if useTor:
        cmd = "torify " + cmd
    global last
    global high
    global low
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
        if len(cmdoutput) > 0:
            j = json.loads(cmdoutput)
            last = int(math.floor(float(j["btc_usd"]["last"])))
            high = int(math.floor(float(j["btc_usd"]["high"])))
            low = int(math.floor(float(j["btc_usd"]["low"])))
    except subprocess.CalledProcessError as e:
        cmdoutput = "{\"error\":  }"
    return (last,high,low)

while True:
    createimage()
    time.sleep(sleepInterval)
