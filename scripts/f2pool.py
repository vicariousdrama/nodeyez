#! /usr/bin/python3
from datetime import datetime
from PIL import Image, ImageDraw, ImageColor
from os.path import exists
import json
import math
import subprocess
import sys
import time
import vicariousbitcoin
import vicarioustext

def getaccountinfo():
    emptyresult = '{"hashrate":0,"hashrate_history":{},"value_last_date":0.00,"value_today":0.00}'
    cmd = "curl https://api.f2pool.com/bitcoin/" + account
    cmdoutput = ""
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
    except subprocess.CalledProcessError as e:
        cmdoutput = emptyresult
    if len(cmdoutput) == 0:
        cmdoutput = emptyresult
    j = json.loads(cmdoutput)
    return j

def gethashratestring(ihashrate):
    hashrate = ihashrate
    hashdesc = "h/s"
    while (hashrate > 1000.0) and (hashdesc != "Ph/s"):
        hashrate = hashrate/1000.0
        if hashdesc == "Ph/s":
            hashdesc = "Eh/s"
        if hashdesc == "Th/s":
            hashdesc = "Ph/s"
        if hashdesc == "Gh/s":
            hashdesc = "Th/s"
        if hashdesc == "Mh/s":
            hashdesc = "Gh/s"
        if hashdesc == "Kh/s":
            hashdesc = "Mh/s"
        if hashdesc == "h/s":
            hashdesc = "Kh/s"
    hashfmt = str(format(hashrate, ".2f")) + " " + hashdesc
    return hashfmt

def getaccounthashrate(accountinfo):
    hashrate = accountinfo["hashrate"]
    return gethashratestring(hashrate)

def gethighesthashrate(accountinfo):
    highesthash = accountinfo["hashrate"]
    for key in accountinfo["hashrate_history"]:
        value = accountinfo["hashrate_history"][key]
        currentvalue = float(value)
        if currentvalue > highesthash:
            highesthash = currentvalue
    return highesthash

def getlowesthashrate(accountinfo):
    lowesthash = accountinfo["hashrate"]
    for key in accountinfo["hashrate_history"]:
        value = accountinfo["hashrate_history"][key]
        currentvalue = float(value)
        if currentvalue < lowesthash:
            lowesthash = currentvalue
    return lowesthash

def createimage(accountinfo, width=480, height=320):
    headerheight = 30
    footerheight = 15
    hashheight = (height - headerheight - footerheight) * .4
    rewardheight = (height - headerheight - footerheight) * .5
    im = Image.new(mode="RGB", size=(width, height))
    draw = ImageDraw.Draw(im)
    # Header
    vicarioustext.drawcenteredtext(draw, "F2 Pool Summary", 24, int(width/2), int(headerheight/2), colorTextFG, True)
    # Hashrate
    hashrate = getaccounthashrate(accountinfo)
    vicarioustext.drawcenteredtext(draw, "Hashrate", 16, (width/4*1), (headerheight + (hashheight/2) - 24), colorTextFG)
    vicarioustext.drawcenteredtext(draw, hashrate, 24, (width/4*1), (headerheight + (hashheight/2)), colorDataValue)
    # Yesterday and Today value
    earningspad = 24
    value_last_day = str(int(float(accountinfo["value_last_day"]) * 100000000)) + " sats"
    value_today = str(int(float(accountinfo["value_today"]) * 100000000)) + " sats"
    vicarioustext.drawcenteredtext(draw, "Earnings Yesterday", 16, (width/4*3), (headerheight + (hashheight/2) - 24 - earningspad), colorTextFG)
    vicarioustext.drawcenteredtext(draw, value_last_day, 24, (width/4*3), (headerheight + (hashheight/2) - earningspad), colorDataValue)
    vicarioustext.drawcenteredtext(draw, "Earnings Today", 16, (width/4*3), (headerheight + (hashheight/2) - 24 + earningspad), colorTextFG)
    vicarioustext.drawcenteredtext(draw, value_today, 24, (width/4*3), (headerheight + (hashheight/2) + earningspad), colorDataValue)
    # Hashrate History
    highesthashrate = gethighesthashrate(accountinfo)
    lowesthashrate = getlowesthashrate(accountinfo)
    labelwidth = math.floor(width / 5)
    graphedge = 3
    vicarioustext.drawcenteredtext(draw, "24 Hour Hashrate", 16, int(width/2), (headerheight+hashheight), colorTextFG)
    charttop = headerheight + hashheight + 12
    chartleft = labelwidth + graphedge
    chartright = width - graphedge
    chartbottom = height - footerheight - graphedge
    # - chart border
    draw.line(xy=[chartleft, charttop, chartleft, chartbottom],fill=colorGraphLineLight,width=1)
    draw.line(xy=[chartleft, chartbottom, chartright, chartbottom],fill=colorGraphLineLight,width=1)
    draw.line(xy=[chartleft, charttop, chartright, charttop],fill=colorGraphLineDark,width=1)
    draw.line(xy=[chartright, charttop, chartright, chartbottom],fill=colorGraphLineDark,width=1)
    # - dashed line background
    chart0  = int(math.floor(charttop))
    chart25 = int(math.floor(charttop + ((chartbottom - charttop)/4*1)))
    chart50 = int(math.floor(charttop + ((chartbottom - charttop)/4*2)))
    chart75 = int(math.floor(charttop + ((chartbottom - charttop)/4*3)))
    chart100  = int(math.floor(charttop + ((chartbottom - charttop))))
    for i in range(chartleft, chartright, 10):
        draw.line(xy=[i,chart25,i+1,chart25],fill=colorGraphLineDark,width=1)
        draw.line(xy=[i,chart50,i+1,chart50],fill=colorGraphLineDark,width=1)
        draw.line(xy=[i,chart75,i+1,chart75],fill=colorGraphLineDark,width=1)
    # - left labels
    hashrate25 = lowesthashrate + ((highesthashrate - lowesthashrate)/4*3)
    hashrate50 = lowesthashrate + ((highesthashrate - lowesthashrate)/4*2)
    hashrate75 = lowesthashrate + ((highesthashrate - lowesthashrate)/4*1)
    vicarioustext.drawrighttext(draw, gethashratestring(highesthashrate), 12, labelwidth, chart0, colorTextFG)
    vicarioustext.drawrighttext(draw, gethashratestring(hashrate25), 12, labelwidth, chart25, colorTextFG)
    vicarioustext.drawrighttext(draw, gethashratestring(hashrate50), 12, labelwidth, chart50, colorTextFG)
    vicarioustext.drawrighttext(draw, gethashratestring(hashrate75), 12, labelwidth, chart75, colorTextFG)
    vicarioustext.drawrighttext(draw, gethashratestring(lowesthashrate), 12, labelwidth, chart100, colorTextFG)
    # - data plot
    entrynum = 0
    plotbuf=2
    entrycount = len(accountinfo["hashrate_history"].keys())
    if entrycount > 0:
        datawidth = ((chartright - chartleft) / entrycount)
        datawidthi = int(math.floor(datawidth))
        for key in accountinfo["hashrate_history"]:
            entrynum = entrynum + 1
            datax = chartleft + int(math.floor(entrynum * datawidth))
            datapct = 0
            value = accountinfo["hashrate_history"][key]
            if highesthashrate > lowesthashrate:
                datapct = (value - lowesthashrate)/(highesthashrate - lowesthashrate)
            plottop = chartbottom - int(math.floor((chartbottom-charttop)*datapct))
            colorDotFill = colorHashDotFill
            colorDotOutline = colorHashDotOutline
            if value < hashrateLowThreshold:
                colorDotFill = colorHashDotFillLow
                colorDotOutline = colorHashDotOutlineLow
            if value == 0:
                colorDotFill = colorHashDotFillZero
                colorDotOutline = colorHashDotOutlineZero
            draw.ellipse(xy=[(datax-plotbuf,plottop-plotbuf),(datax+datawidthi+plotbuf,plottop+datawidthi+plotbuf)],fill=colorDotFill,outline=colorDotOutline,width=1)
        # moving average line
        entrynum = 0
        ma = [-1,-1,-1]
        olddatax = -1
        olddatay = -1
        for key in accountinfo["hashrate_history"]:
            entrynum = entrynum + 1
            value = accountinfo["hashrate_history"][key]
            if ma[0] == -1:
                ma[0] = value
            elif ma[1] == -1:
                ma[1] = value
            else:
                ma[2] = value
                mavg = (ma[0] + ma[1] + ma[2]) / 3
                datax = chartleft + int(math.floor(entrynum * datawidth))
                datapct = 0
                if highesthashrate > lowesthashrate:
                    datapct = (mavg - lowesthashrate)/(highesthashrate - lowesthashrate)
                datay = chartbottom - int(math.floor((chartbottom-charttop)*datapct))
                if olddatax != -1:
                    draw.line(xy=[(olddatax,olddatay),(datax,datay)],fill=colorMovingAverage,width=3)
                olddatax = datax
                olddatay = datay
                ma[0] = -1 #ma[1]
                ma[1] = -1 #ma[2]
                ma[2] = -1


    # Date and Time
    dt = "as of " + vicarioustext.getdateandtime()
    vicarioustext.drawbottomrighttext(draw, dt, 12, width, height, colorTextFG)
    # Save to file
    im.save(outputFile)


if __name__ == '__main__':
    # Defaults
    configFile="/home/bitcoin/nodeyez/config/f2pool.json"
    outputFile = "/home/bitcoin/images/f2pool.png"
    account = "--put-your-account-name-in---nodeyez/config/f2pool.json"
    hashrateLowThreshold = 60000000000000 # 60 TH is 60,000,000,000,000 or 60 followed by 12 zeros
    sleepInterval=600
    colorDataValue=ImageColor.getrgb("#4040ff")
    colorHashDotFill=ImageColor.getrgb("#4040ff")
    colorHashDotFillZero=ImageColor.getrgb("#ff4040")
    colorHashDotFillLow=ImageColor.getrgb("#ffff40")
    colorHashDotOutline=ImageColor.getrgb("#0000ff")
    colorHashDotOutlineZero=ImageColor.getrgb("#ff0000")
    colorHashDotOutlineLow=ImageColor.getrgb("#ffff00")
    colorMovingAverage=ImageColor.getrgb("#40ff40")
    colorGraphLineLight=ImageColor.getrgb("#a0a0a0")
    colorGraphLineDark=ImageColor.getrgb("#606060")
    colorTextFG=ImageColor.getrgb("#ffffff")
    # Require config
    if not exists(configFile):
        print(f"You need to make a config file at {configFile} to set your account information")
        exit(1)
    # Override config
    if exists(configFile):
        with open(configFile) as f:
            config = json.load(f)
        if "account" in config:
            account = config["account"]
        if "outputFile" in config:
            outputFile = config["outputFile"]
        if "hashrateLowThreshold" in config:
            hashrateLowThreshold = config["hashrateLowThreshold"]
        if "sleepInterval" in config:
            sleepInterval = int(config["sleepInterval"])
            sleepInterval = 300 if sleepInterval < 300 else sleepInterval # minimum 5 minutes, access others
        if "colorDataValue" in config:
            colorDataValue = ImageColor.getrgb(config["colorDataValue"])
        if "colorHashDotFill" in config:
            colorHashDotFill = ImageColor.getrgb(config["colorHashDotFill"])
        if "colorHashDotFillZero" in config:
            colorHashDotFillZero = ImageColor.getrgb(config["colorHashDotFillZero"])
        if "colorHashDotFillLow" in config:
            colorHashDotFillLow = ImageColor.getrgb(config["colorHashDotFillLow"])
        if "colorHashDotOutline" in config:
            colorHashDotOutline = ImageColor.getrgb(config["colorHashDotOutline"])
        if "colorHashDotOutlineZero" in config:
            colorHashDotOutlineZero = ImageColor.getrgb(config["colorHashDotOutlineZero"])
        if "colorHashDotOutlineLow" in config:
            colorHashDotOutlineLow = ImageColor.getrgb(config["colorHashDotOutlineLow"])
        if "colorMovingAverage" in config:
            colorMovingAverage = ImageColor.getrgb(config["colorMovingAverage"])
        if "colorGraphLineLight" in config:
            colorGraphLineLight = ImageColor.getrgb(config["colorGraphLineLight"])
        if "colorGraphLineDark" in config:
            colorGraphLineDark = ImageColor.getrgb(config["colorGraphLineDark"])
        if "colorTextFG" in config:
            colorTextFG = ImageColor.getrgb(config["colorTextFG"])
    # Check for single run
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h','--help']:
            print(f"Prepares a summary of F2 Pool hashing and earnings for 24 hours")
            print(f"Usage:")
            print(f"1) Call without arguments to run continuously using the configuration or defaults")
            print(f"2) Passing any arguments other then -h or --help will run once and exit")
            print(f"You may specify a custom configuration file at {configFile}")
        else:
            accountinfo = getaccountinfo()
            createimage(accountinfo)
        exit(0)
    # Loop
    while True:
        accountinfo = getaccountinfo()
        createimage(accountinfo)
        time.sleep(sleepInterval)
