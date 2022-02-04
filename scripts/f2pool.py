#! /usr/bin/python3
from datetime import datetime
from PIL import Image, ImageFilter, ImageDraw, ImageFont, ImageColor
import json
import math
import subprocess
import time
import vicariousbitcoin
import vicarioustext

configFile="/home/bitcoin/nodeyez/config/f2pool.json"
outputFile = "/home/bitcoin/images/f2pool.png"
account = "--put-your-account-name-in---nodeyez/config/f2pool.json"
accountlabel = ""
hashratelowthreshold = 60000000000000
sleepInterval=600
colordatavalue=ImageColor.getrgb("#4040ff")
colorhashdotfill=ImageColor.getrgb("#4040ff")
colorhashdotoutline=ImageColor.getrgb("#0000ff")
colorhashdotfillzero=ImageColor.getrgb("#ff4040")
colorhashdotoutlinezero=ImageColor.getrgb("#ff0000")
colorhashdotfilllow=ImageColor.getrgb("#ffff40")
colorhashdotoutlinelow=ImageColor.getrgb("#ffff00")
colorma=ImageColor.getrgb("#40ff40")
colorgraphlinelight=ImageColor.getrgb("#a0a0a0")
colorgraphlinedark=ImageColor.getrgb("#606060")

colorFFFFFF=ImageColor.getrgb("#ffffff")
color000000=ImageColor.getrgb("#000000")
colorC0C0C0=ImageColor.getrgb("#c0c0c0")
colorC0FFC0=ImageColor.getrgb("#40ff40")
colorFF0000=ImageColor.getrgb("#ff0000")
colorFFFF00=ImageColor.getrgb("#ffff00")

def getaccountinfo():
    cmd = "curl https://api.f2pool.com/bitcoin/" + account
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
    except subprocess.CalledProcessError as e:
        cmdoutput = "{\"hashrate\":0,\"hashrate_history\":{},\"value_last_day\":0.00,\"value_today\":0.00}"
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
    vicarioustext.drawcenteredtext(draw, "F2 Pool Summary" + accountlabel, 24, int(width/2), int(headerheight/2), colorFFFFFF, True)
    # Hashrate
    hashrate = getaccounthashrate(accountinfo)
    vicarioustext.drawcenteredtext(draw, "Hashrate", 16, (width/4*1), (headerheight + (hashheight/2) - 24))
    vicarioustext.drawcenteredtext(draw, hashrate, 24, (width/4*1), (headerheight + (hashheight/2)), colordatavalue)
    # Yesterday and Today value
    earningspad = 24
    value_last_day = str(int(float(accountinfo["value_last_day"]) * 100000000)) + " sats"
    value_today = str(int(float(accountinfo["value_today"]) * 100000000)) + " sats"
    vicarioustext.drawcenteredtext(draw, "Earnings Yesterday", 16, (width/4*3), (headerheight + (hashheight/2) - 24 - earningspad))
    vicarioustext.drawcenteredtext(draw, value_last_day, 24, (width/4*3), (headerheight + (hashheight/2) - earningspad), colordatavalue)
    vicarioustext.drawcenteredtext(draw, "Earnings Today", 16, (width/4*3), (headerheight + (hashheight/2) - 24 + earningspad))
    vicarioustext.drawcenteredtext(draw, value_today, 24, (width/4*3), (headerheight + (hashheight/2) + earningspad), colordatavalue)
    # Hashrate History
    highesthashrate = gethighesthashrate(accountinfo)
    lowesthashrate = getlowesthashrate(accountinfo)
    labelwidth = math.floor(width / 5)
    graphedge = 3
    vicarioustext.drawcenteredtext(draw, "24 Hour Hashrate", 16, int(width/2), (headerheight+hashheight))
    charttop = headerheight + hashheight + 12
    chartleft = labelwidth + graphedge
    chartright = width - graphedge
    chartbottom = height - footerheight - graphedge
    # - chart border
    draw.line(xy=[chartleft, charttop, chartleft, chartbottom],fill=colorgraphlinelight,width=1)
    draw.line(xy=[chartleft, chartbottom, chartright, chartbottom],fill=colorgraphlinelight,width=1)
    draw.line(xy=[chartleft, charttop, chartright, charttop],fill=colorgraphlinedark,width=1)
    draw.line(xy=[chartright, charttop, chartright, chartbottom],fill=colorgraphlinedark,width=1)
    # - dashed line background
    chart0  = int(math.floor(charttop))
    chart25 = int(math.floor(charttop + ((chartbottom - charttop)/4*1)))
    chart50 = int(math.floor(charttop + ((chartbottom - charttop)/4*2)))
    chart75 = int(math.floor(charttop + ((chartbottom - charttop)/4*3)))
    chart100  = int(math.floor(charttop + ((chartbottom - charttop))))
    for i in range(chartleft, chartright, 10):
        draw.line(xy=[i,chart25,i+1,chart25],fill=colorgraphlinedark,width=1)
        draw.line(xy=[i,chart50,i+1,chart50],fill=colorgraphlinedark,width=1)
        draw.line(xy=[i,chart75,i+1,chart75],fill=colorgraphlinedark,width=1)
    # - left labels
    hashrate25 = lowesthashrate + ((highesthashrate - lowesthashrate)/4*3)
    hashrate50 = lowesthashrate + ((highesthashrate - lowesthashrate)/4*2)
    hashrate75 = lowesthashrate + ((highesthashrate - lowesthashrate)/4*1)
    vicarioustext.drawrighttext(draw, gethashratestring(highesthashrate), 12, labelwidth, chart0)
    vicarioustext.drawrighttext(draw, gethashratestring(hashrate25), 12, labelwidth, chart25)
    vicarioustext.drawrighttext(draw, gethashratestring(hashrate50), 12, labelwidth, chart50)
    vicarioustext.drawrighttext(draw, gethashratestring(hashrate75), 12, labelwidth, chart75)
    vicarioustext.drawrighttext(draw, gethashratestring(lowesthashrate), 12, labelwidth, chart100)
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
            colordotfill = colorhashdotfill
            colordotoutline = colorhashdotoutline
            if value < hashratelowthreshold:
                colordotfill = colorhashdotfilllow
                colordotoutline = colorhashdotoutlinelow
            if value == 0:
                colordotfill = colorhashdotfillzero
                colordotoutline = colorhashdotoutlinezero
            draw.ellipse(xy=[(datax-plotbuf,plottop-plotbuf),(datax+datawidthi+plotbuf,plottop+datawidthi+plotbuf)],fill=colordotfill,outline=colordotoutline,width=1)
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
                    draw.line(xy=[(olddatax,olddatay),(datax,datay)],fill=colorma,width=3)
                olddatax = datax
                olddatay = datay
                ma[0] = -1 #ma[1]
                ma[1] = -1 #ma[2]
                ma[2] = -1


    # Date and Time
    dt = "as of " + vicarioustext.getdateandtime()
    vicarioustext.drawbottomrighttext(draw, dt, 12, width, height)
    # Save to file
    im.save(outputFile)


while True:
    f = open(configFile)
    config = json.load(f)
    f.close()
    if "account" in config:
        account = config["account"]
    accountinfo = getaccountinfo()
    createimage(accountinfo)
    time.sleep(sleepInterval)
