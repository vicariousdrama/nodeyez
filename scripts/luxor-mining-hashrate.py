#! /usr/bin/env python3
from datetime import datetime
from PIL import Image, ImageFilter, ImageDraw, ImageFont, ImageColor
from os.path import exists
import json
import math
import subprocess
import sys
import time
import vicariousbitcoin
import vicarioustext
from luxor import API
from resolvers import RESOLVERS

def gethashratehistory():
    # full docs at https://docs.luxor.tech/docs/schema/queries/get-hashrate-score-history
    # python library at https://github.com/LuxorLabs/graphql-python-client
    LUXORAPI = API(host = 'https://api.beta.luxor.tech/graphql', method='POST', org='luxor', key=apikey)
    resp = LUXORAPI.get_hashrate_score_history(username,'BTC',100)
    return resp['data']['getHashrateScoreHistory']['nodes']

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

def gethighesthashrate(hashrate_history):
    highesthash = float(hashrate_history[0]["hashrate"])
    for entry in hashrate_history:
        value = float(entry["hashrate"])
        if value > highesthash:
            highesthash = value
    return highesthash

def getlowesthashrate(hashrate_history):
    lowesthash = float(hashrate_history[0]["hashrate"])
    for entry in hashrate_history:
        value = float(entry["hashrate"])
        if value < lowesthash:
            lowesthash = value
    return lowesthash

def leap_year(year):
    if year % 400 == 0:
        return True
    elif year % 100 == 0:
        return False
    elif year % 4 == 0:
        return True
    else:
        return False

def days_in_month(month, year):
    if month in {1,3,5,7,8,10,12}:
        return 31
    if month == 2:
        if leap_year(year):
            return 29
        return 28
    return 30

def createimage(hashrate_history, date_prefix, width=480, height=320):
    headerheight = 30
    footerheight = 30
    month = int(date_prefix[5:7])
    year = int(date_prefix[:4])
    datedOutputFile = outputFile.replace(".png","-" + date_prefix + ".png")
    infoheight = (height - headerheight - footerheight) * .3
    chartheight = (height - headerheight - footerheight) * .7
    im = Image.new(mode="RGB", size=(width, height), color=colorBackground)
    draw = ImageDraw.Draw(im)
    # Header
    vicarioustext.drawcenteredtext(draw, "Luxor Hashrate Output", 24, int(width/2), int(headerheight/2), colorTextFG, True)
    vicarioustext.drawcenteredtext(draw, subheadingText, 16, int(width/2), headerheight+8, colorTextFG, False)
    # Determine Month Label
    datetime_object = datetime.strptime(str(month), "%m")
    month_name = datetime_object.strftime("%B")
    # Hashrate History
    highesthashrate = gethighesthashrate(hashrate_history)
    lowesthashrate = 0 # getlowesthashrate(hashrate_history)
    labelwidth = math.floor(width / 5)
    graphedge = 3
    vicarioustext.drawcenteredtext(draw, "Daily Hashrate Average for " + month_name + " " + str(year), 16, int(width/2), (headerheight+infoheight), colorTextFG)
    charttop = headerheight + infoheight + 12
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
    totalvalue=0
    entrynum=0
    plotbuf=2
    xbuf=-8
    ybuf=-2
    daycount = days_in_month(month,year)
    datawidth = ((chartright - chartleft) / daycount)
    datawidthi = 3 # int(math.floor(datawidth))
    dayseen=[False]*daycount
    for entry in hashrate_history:
        if entry["date"][:7] == date_prefix:
            daynum = int(entry["date"][8:10])
            dayseen[daynum-1]=True
            datax = chartleft + int(math.floor(daynum * datawidth))
            datapct = 0
            value = float(entry["hashrate"])
            totalvalue += value
            if highesthashrate > lowesthashrate:
                datapct = (value - lowesthashrate)/(highesthashrate - lowesthashrate)
            plottop = chartbottom - int(math.floor((chartbottom-charttop)*datapct))
            colordotfill = colorHashDotFill
            colordotoutline = colorHashDotOutline
            if value < hashrateLowThreshold:
                colordotfill = colorHashDotFillLow
                colordotoutline = colorHashDotOutlineLow
            if value == 0:
                colordotfill = colorHashDotFillZero
                colordotoutline = colorHashDotOutlineZero
            draw.ellipse(xy=[(xbuf+datax-plotbuf,ybuf+plottop-plotbuf),(xbuf+datax+datawidthi+plotbuf,ybuf+plottop+datawidthi+plotbuf)],fill=colordotfill,outline=colordotoutline,width=1)
    # plot missing days
    for daynum in range(len(dayseen)):
        if dayseen[daynum] == False:
            themissingdate = datetime(year, month, daynum+1)
            if themissingdate.timestamp() < datetime.today().timestamp():
                datax = chartleft + int(math.floor((daynum+1) * datawidth))
                datapct = 0
                plottop = chartbottom - int(math.floor((chartbottom-charttop)*datapct))
                colordotfill = colorHashDotFillZero
                colordotoutline = colorHashDotOutlineZero
                draw.ellipse(xy=[(xbuf+datax-plotbuf,ybuf+plottop-plotbuf),(xbuf+datax+datawidthi+plotbuf,ybuf+plottop+datawidthi+plotbuf)],fill=colordotfill,outline=colordotoutline,width=1)
            else:
                # set daycount to today to allow average and result percent to calculate properly
                daycount = int(datetime.now().strftime("%d"))

    # Expected Total, and Percentage thereof
    totalexpected = daycount * hashrateTarget
    resultpercent = totalvalue / totalexpected
    averagehashrate = int(totalvalue / daycount)
    #print(f"{month_name} {year} expected {totalexpected} got {totalvalue}, {resultpercent}")
    hashTarget = gethashratestring(hashrateTarget)
    hashAverage = gethashratestring(averagehashrate)
    vicarioustext.drawcenteredtext(draw, "Target", 16, int(width/6), (headerheight+32), colorHashDotFill)
    vicarioustext.drawcenteredtext(draw, "Average", 16, int(width/2), (headerheight+32), colorHashDotFill)
    vicarioustext.drawcenteredtext(draw, "Uptime", 16, int(width/6)*5, (headerheight+32), colorHashDotFill)
    vicarioustext.drawcenteredtext(draw, hashTarget, 18, int(width/6), (headerheight+52), colorTextFG)
    vicarioustext.drawcenteredtext(draw, hashAverage, 18, int(width/2), (headerheight+52), colorTextFG)
    vicarioustext.drawcenteredtext(draw, str(int(resultpercent*100)) + "%", 18, int(width/6)*5, (headerheight+52), colorTextFG)


    # Date and Time
    dt = "as of " + vicarioustext.getdateandtime()
    vicarioustext.drawbottomrighttext(draw, dt, 12, width, height, colorTextFG)
    # Save to file
    im.save(datedOutputFile)
    im.close()


if __name__ == '__main__':
    # Defaults
    configFile="/home/nodeyez/nodeyez/config/luxor.json"
    outputFile = "/home/nodeyez/nodeyez/imageoutput/luxor-mining-hashrate.png"
    apikey = "--configure-in--nodeyez/config/luxor.json"
    username = "--configure-in--nodeyez/config/luxor.json"
    subheadingText = "S19 Pro 110TH"
    hashrateTarget = 110000000000000
    hashrateLowThreshold = 90000000000000
    width=480
    height=320
    sleepInterval=86400
    colorDataValue=ImageColor.getrgb("#4040ff")
    colorHashDotFill=ImageColor.getrgb("#4040ff")
    colorHashDotOutline=ImageColor.getrgb("#0000ff")
    colorHashDotFillZero=ImageColor.getrgb("#ff4040")
    colorHashDotOutlineZero=ImageColor.getrgb("#ff0000")
    colorHashDotFillLow=ImageColor.getrgb("#ffff40")
    colorHashDotOutlineLow=ImageColor.getrgb("#ffff00")
    colorMovingAverage=ImageColor.getrgb("#40ff40")
    colorGraphLineLight=ImageColor.getrgb("#a0a0a0")
    colorGraphLineDark=ImageColor.getrgb("#606060")
    colorTextFG=ImageColor.getrgb("#ffffff")
    colorBackground=ImageColor.getrgb("#000000")
    # Require config
    if not exists(configFile):
        print(f"You need to make a config file at {configFile} to set your apikey and username information")
        exit(1)
    # Override config
    if exists(configFile):
        with open(configFile) as f:
            config = json.load(f)
        if "outputFile" in config:
            outputFile = config["outputFile"]
        if "apikey" in config:
            apikey = config["apikey"]
        else:
            print(f"You need to make a config file at {configFile} to set your apikey and username information")
            exit(1)
        if "username" in config:
            username = config["username"]
        else:
            print(f"You need to make a config file at {configFile} to set your apikey and username information")
            exit(1)
        if "subheadingText" in config:
            subheadingText = config["subheadingText"]
        if "hashrateTarget" in config:
            hashrateTarget = config["hashrateTarget"]
        if "hashrateLowThreshold" in config:
            hashrateLowThreshold = config["hashrateLowThreshold"]
        if "width" in config:
            width = int(config["width"])
        if "height" in config:
            height = int(config["height"])
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
        if "colorBackground" in config:
            colorBackground = ImageColor.getrgb(config["colorBackground"])
    # Check for single run
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h','--help']:
            print(f"Prepares images for Luxor Mining Hashrate for each month in the dataset")
            print(f"Usage:")
            print(f"1) Call without arguments to run continuously using the configuration or defaults")
            print(f"2) Passing any arguments other then -h or --help will run once and exit")
            print(f"You may specify a custom configuration file at {configFile}")
            exit(0)
    # Loop
    while True:
        hashrate_history = gethashratehistory()
        date_prefix = ""
        for entry in hashrate_history:
            if entry["date"][:7] != date_prefix:
                date_prefix = entry["date"][:7]
                print(f"Creating image for {date_prefix}")
                createimage(hashrate_history, date_prefix,width,height)
        # only run once if an argument was passed
        if len(sys.argv) > 1:
            break
        time.sleep(sleepInterval)
