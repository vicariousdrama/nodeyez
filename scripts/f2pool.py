#! /usr/bin/python3
from datetime import datetime
from PIL import Image, ImageFilter, ImageDraw, ImageFont, ImageColor
import json
import math
import subprocess
import time

outputFile = "/home/bitcoin/images/f2pool.png"
account = "--your-account-name-here--"
accountlabel = ""
hashratelowthreshold = 60000000000000

colordatavalue=ImageColor.getrgb("#4040ff")
colorhashdotfill=ImageColor.getrgb("#4040ff")
colorhashdotoutline=ImageColor.getrgb("#0000ff")
colorhashdotfillzero=ImageColor.getrgb("#ff4040")
colorhashdotoutlinezero=ImageColor.getrgb("#ff0000")
colorhashdotfilllow=ImageColor.getrgb("#ffff40")
colorhashdotoutlinelow=ImageColor.getrgb("#ffff00")

colorgraphlinelight=ImageColor.getrgb("#a0a0a0")
colorgraphlinedark=ImageColor.getrgb("#606060")

colorFFFFFF=ImageColor.getrgb("#ffffff")
color000000=ImageColor.getrgb("#000000")
colorC0C0C0=ImageColor.getrgb("#c0c0c0")
colorC0FFC0=ImageColor.getrgb("#40ff40")
colorFF0000=ImageColor.getrgb("#ff0000")
colorFFFF00=ImageColor.getrgb("#ffff00")
fontDeja12=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",12)
fontDeja16=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",16)
fontDeja20=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",20)
fontDeja24=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",24)
fontDeja48=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",48)

def getdateandtime():
    now = datetime.utcnow()
    return now.strftime("%Y-%m-%d %H:%M:%S")

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

def getfont(size):
    if size == 12:
        return fontDeja12
    if size == 16:
        return fontDeja16
    if size == 24:
        return fontDeja24
    if size == 48:
        return fontDeja48

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

def createimage(accountinfo, width=480, height=320):
    headerheight = 30
    footerheight = 15
    hashheight = (height - headerheight - footerheight) * .5
    rewardheight = (height - headerheight - footerheight) * .5
    im = Image.new(mode="RGB", size=(width, height))
    draw = ImageDraw.Draw(im)
    # Header
    drawcenteredtext(draw, "F2 Pool Summary" + accountlabel, 24, int(width/2), int(headerheight/2))
    # Hashrate
    hashrate = getaccounthashrate(accountinfo)
    drawcenteredtext(draw, "Hashrate", 16, (width/4*1), (headerheight + (hashheight/2) - 24))
    drawcenteredtext(draw, hashrate, 24, (width/4*1), (headerheight + (hashheight/2)), colordatavalue)
    # Yesterday and Today value
    earningspad = 32
    value_last_day = str(int(float(accountinfo["value_last_day"]) * 100000000)) + " sats"
    value_today = str(int(float(accountinfo["value_today"]) * 100000000)) + " sats"
    drawcenteredtext(draw, "Earnings Yesterday", 16, (width/4*3), (headerheight + (hashheight/2) - 24 - earningspad))
    drawcenteredtext(draw, value_last_day, 24, (width/4*3), (headerheight + (hashheight/2) - earningspad), colordatavalue)
    drawcenteredtext(draw, "Earnings Today", 16, (width/4*3), (headerheight + (hashheight/2) - 24 + earningspad))
    drawcenteredtext(draw, value_today, 24, (width/4*3), (headerheight + (hashheight/2) + earningspad), colordatavalue)
    # Hashrate History
    highesthashrate = gethighesthashrate(accountinfo)
    lowesthashrate = getlowesthashrate(accountinfo)
    labelwidth = math.floor(width / 5)
    graphedge = 3
    drawcenteredtext(draw, "24 Hour Hashrate", 16, int(width/2), (headerheight+hashheight))
    charttop = headerheight + hashheight + 24
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
    drawrighttext(draw, gethashratestring(highesthashrate), 12, labelwidth, chart0)
    drawrighttext(draw, gethashratestring(hashrate25), 12, labelwidth, chart25)
    drawrighttext(draw, gethashratestring(hashrate50), 12, labelwidth, chart50)
    drawrighttext(draw, gethashratestring(hashrate75), 12, labelwidth, chart75)
    drawrighttext(draw, gethashratestring(lowesthashrate), 12, labelwidth, chart100)
    # - data plot
    entrynum = 0
    plotbuf=2
    entrycount = len(accountinfo["hashrate_history"].keys())
    if entrycount > 0:
        datawidth = ((chartright - chartleft) / entrycount)
        datawidthi = int(math.floor(datawidth))
        for key in accountinfo["hashrate_history"]:
            entrynum = entrynum + 1
            dayx = chartleft + int(math.floor(entrynum * datawidth))
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
            draw.ellipse(xy=[(dayx-plotbuf,plottop-plotbuf),(dayx+datawidthi+plotbuf,plottop+datawidthi+plotbuf)],fill=colordotfill,outline=colordotoutline,width=1)
    # Date and Time
    dt = "as of " + getdateandtime()
    drawbottomrighttext(draw, dt, 12, width, height)
    # Save to file
    im.save(outputFile)


while True:
    accountinfo = getaccountinfo()
    createimage(accountinfo)
    time.sleep(600)
