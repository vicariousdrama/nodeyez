#! /usr/bin/python3
from datetime import datetime
from PIL import Image, ImageFilter, ImageDraw, ImageFont, ImageColor
import json
import math
import subprocess
import time
import vicariousbitcoin
import vicarioustext
from luxor import API
from resolvers import RESOLVERS

configFile="/home/bitcoin/nodeyez/config/luxor.json"
outputFile = "/home/bitcoin/images/luxor-mining-hashrate.png"
apikey = "--configure-in--nodeyez/config/luxor.json"
username = "--configure-in--nodeyez/config/luxor.json"
subheadingtext = "S19 Pro 110TH / Compass Mining in Quebec"
accountlabel = ""
hashratetarget = 110000000000000
hashratelowthreshold = 90000000000000
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
    im = Image.new(mode="RGB", size=(width, height))
    draw = ImageDraw.Draw(im)
    # Header
    vicarioustext.drawcenteredtext(draw, "Luxor Hashrate Output", 24, int(width/2), int(headerheight/2), colorFFFFFF, True)
    vicarioustext.drawcenteredtext(draw, subheadingtext, 16, int(width/2), headerheight+8, colorFFFFFF, False)
    # Determine Month Label
    datetime_object = datetime.strptime(str(month), "%m")
    month_name = datetime_object.strftime("%B")
    # Hashrate History
    highesthashrate = gethighesthashrate(hashrate_history)
    lowesthashrate = 0 # getlowesthashrate(hashrate_history)
    labelwidth = math.floor(width / 5)
    graphedge = 3
    vicarioustext.drawcenteredtext(draw, "Daily Hashrate Average for " + month_name + " " + str(year), 16, int(width/2), (headerheight+infoheight))
    charttop = headerheight + infoheight + 12
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
            colordotfill = colorhashdotfill
            colordotoutline = colorhashdotoutline
            if value < hashratelowthreshold:
                colordotfill = colorhashdotfilllow
                colordotoutline = colorhashdotoutlinelow
            if value == 0:
                colordotfill = colorhashdotfillzero
                colordotoutline = colorhashdotoutlinezero
            draw.ellipse(xy=[(xbuf+datax-plotbuf,ybuf+plottop-plotbuf),(xbuf+datax+datawidthi+plotbuf,ybuf+plottop+datawidthi+plotbuf)],fill=colordotfill,outline=colordotoutline,width=1)
    # plot missing days
    for daynum in range(len(dayseen)):
        if dayseen[daynum] == False:
            datax = chartleft + int(math.floor((daynum+1) * datawidth))
            datapct = 0
            plottop = chartbottom - int(math.floor((chartbottom-charttop)*datapct))
            colordotfill = colorhashdotfillzero
            colordotoutline = colorhashdotoutlinezero
            draw.ellipse(xy=[(xbuf+datax-plotbuf,ybuf+plottop-plotbuf),(xbuf+datax+datawidthi+plotbuf,ybuf+plottop+datawidthi+plotbuf)],fill=colordotfill,outline=colordotoutline,width=1)

    # Expected Total, and Percentage thereof
    totalexpected = daycount * hashratetarget
    resultpercent = totalvalue / totalexpected
    averagehashrate = int(totalvalue / daycount)
    #print(f"{month_name} {year} expected {totalexpected} got {totalvalue}, {resultpercent}")
    hashTarget = gethashratestring(hashratetarget)
    hashAverage = gethashratestring(averagehashrate)
    vicarioustext.drawcenteredtext(draw, "Target", 16, int(width/6), (headerheight+32), colorhashdotfill)
    vicarioustext.drawcenteredtext(draw, "Average", 16, int(width/2), (headerheight+32), colorhashdotfill)
    vicarioustext.drawcenteredtext(draw, "Uptime", 16, int(width/6)*5, (headerheight+32), colorhashdotfill)
    vicarioustext.drawcenteredtext(draw, hashTarget, 18, int(width/6), (headerheight+52))
    vicarioustext.drawcenteredtext(draw, hashAverage, 18, int(width/2), (headerheight+52))
    vicarioustext.drawcenteredtext(draw, str(int(resultpercent*100)) + "%", 18, int(width/6)*5, (headerheight+52))


    # Date and Time
    dt = "as of " + vicarioustext.getdateandtime()
    vicarioustext.drawbottomrighttext(draw, dt, 12, width, height)
    # Save to file
    im.save(datedOutputFile)


#while True:
with open(configFile) as f:
    config = json.load(f)
apikey = config["apikey"]
username = config["username"]
hashrate_history = gethashratehistory()
date_prefix = ""
for entry in hashrate_history:
    if entry["date"][:7] != date_prefix:
        date_prefix = entry["date"][:7]
        createimage(hashrate_history, date_prefix)


#print(gethashratestring(gethighesthashrate(hashrate_history)))
#print(gethashratestring(getlowesthashrate(hashrate_history)))
#    createimage(hashrate_history)
#    time.sleep(sleepInterval)
