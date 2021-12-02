#! /usr/bin/python3
from datetime import datetime
from PIL import Image, ImageFilter, ImageDraw, ImageFont, ImageColor
import json
import math
import subprocess
import time

outputFile = "/home/bitcoin/images/slushpool.png"
authtoken = "your-auth-token-here"
# if the daily average for 30 days drops below this level, then a warning will be displayed
breakevndaily = 5000
colorminingreward=ImageColor.getrgb("#6b50ff")
colorbosreward=ImageColor.getrgb("#fb82a8")
colorreferralreward=ImageColor.getrgb("#00bac5")
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

def getaccountrewards():
    time.sleep(6)
    cmd = "curl -H \"SlushPool-Auth-Token: " + authtoken + "\" https://slushpool.com/accounts/rewards/json/btc/"
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
    except subprocess.CalledProcessError as e:
        cmdoutput = "{\"btc\":{\"daily_rewards\":[]}}"
    j = json.loads(cmdoutput)
    return j

def getaccountprofile():
    cmd = "curl -H \"SlushPool-Auth-Token: " + authtoken + "\" https://slushpool.com/accounts/profile/json/btc/"
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
    except subprocess.CalledProcessError as e:
        cmdoutput = "{\"btc\":{\"confirmed_reward\": null, \"unconfirmed_reward\": \"0.00000000\", \"estimated_reward\": \"0.00000000\", \"hash_rate_unit\": \"Gh/s\", \"hash_rate_5m\": 0.0000}}"
    j = json.loads(cmdoutput)
    return j

def getaccounthashrate(accountprofile):
    hashrate = accountprofile["btc"]["hash_rate_5m"]
    hashdesc = accountprofile["btc"]["hash_rate_unit"]
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
    hashfmt = str(format(hashrate, ".2f")) + " " + hashdesc
    return hashfmt

def gethighestreward(accountrewards):
    highestreward = 0.00
    days = 0
    for reward in accountrewards["btc"]["daily_rewards"]:
        days = days + 1
        if days > 30:
           break
        currenttotal = float(reward["total_reward"])
        if currenttotal > highestreward:
            highestreward = currenttotal
    return highestreward

def getlowestreward(accountrewards):
    lowestreward = 0.00
    days = 0
    for reward in accountrewards["btc"]["daily_rewards"]:
        days = days + 1
        if days > 30:
           break
        currenttotal = float(reward["total_reward"])
        if days == 1:
            lowestreward = currenttotal
        else:
            if currenttotal < lowestreward:
                lowestreward = currenttotal
    return lowestreward

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

def createimage(accountrewards, accountprofile, width=480, height=320):
    headerheight = 30
    footerheight = 15
    hashheight = (height - headerheight - footerheight) * .5
    rewardheight = (height - headerheight - footerheight) * .5
    im = Image.new(mode="RGB", size=(width, height))
    draw = ImageDraw.Draw(im)
    # Header
    drawcenteredtext(draw, "SlushPool Mining Summary", 24, int(width/2), int(headerheight/2))
    # Hashrate and Unconfirmed rewards
    hashrate = getaccounthashrate(accountprofile)
    drawcenteredtext(draw, "Hashrate", 16, (width/4*1), (headerheight + (hashheight/2) - 24))
    drawcenteredtext(draw, hashrate, 24, (width/4*1), (headerheight + (hashheight/2)))
    unconfirmed_reward = float(accountprofile["btc"]["unconfirmed_reward"])
#    unconfirmed_text = str(format(unconfirmed_reward, ".8f")) + " BTC"
    unconfirmed_text = str(int(math.floor(unconfirmed_reward * 100000000))) + " sats"
    drawcenteredtext(draw, "Unconfirmed Rewards", 16, (width/4*3), (headerheight + (hashheight/2) - 24))
    drawcenteredtext(draw, unconfirmed_text, 24, (width/4*3), (headerheight + (hashheight/2)))
    # 30 Days Rewards
    highestreward = gethighestreward(accountrewards)
    lowestreward = getlowestreward(accountrewards)
    labelwidth = math.floor(width / 5)
    graphedge = 3
#    drawtoplefttext(draw, "Rewards in last 30 days", 16, 0, (headerheight + hashheight))
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
    chart25 = int(math.floor(charttop + ((chartbottom - charttop)/4*1)))
    chart50 = int(math.floor(charttop + ((chartbottom - charttop)/4*2)))
    chart75 = int(math.floor(charttop + ((chartbottom - charttop)/4*3)))
    for i in range(chartleft, chartright, 10):
        draw.line(xy=[i,chart25,i+1,chart25],fill=colorgraphlinedark,width=1)
        draw.line(xy=[i,chart50,i+1,chart50],fill=colorgraphlinedark,width=1)
        draw.line(xy=[i,chart75,i+1,chart75],fill=colorgraphlinedark,width=1)
    # - left labels
#    reward25 = lowestreward + ((highestreward - lowestreward)/4*3)
#    reward50 = lowestreward + ((highestreward - lowestreward)/4*2)
#    reward75 = lowestreward + ((highestreward - lowestreward)/4*1)
#    drawrighttext(draw, str(format(reward25, ".5f")) + " BTC", 12, labelwidth, chart25)
#    drawrighttext(draw, str(format(reward50, ".5f")) + " BTC", 12, labelwidth, chart50)
#    drawrighttext(draw, str(format(reward75, ".5f")) + " BTC", 12, labelwidth, chart75)
    reward25 = int(math.floor((lowestreward + ((highestreward - lowestreward)/4*3)) * 100000000))
    reward50 = int(math.floor((lowestreward + ((highestreward - lowestreward)/4*2)) * 100000000))
    reward75 = int(math.floor((lowestreward + ((highestreward - lowestreward)/4*1)) * 100000000))
    drawrighttext(draw, str(reward25) + " sats", 12, labelwidth, chart25)
    drawrighttext(draw, str(reward50) + " sats", 12, labelwidth, chart50)
    drawrighttext(draw, str(reward75) + " sats", 12, labelwidth, chart75)
    # - 30 days of bars
    totaldays = 30
    days = 0
    daywidth = int(math.floor((chartright - chartleft) / totaldays))
    barwidth = daywidth - 2
    overalltotal = 0
    for reward in accountrewards["btc"]["daily_rewards"]:
        days = days + 1
        if days > totaldays:
           break
        currenttotal = float(reward["total_reward"])
        overalltotal = overalltotal + currenttotal
        dayx = chartright - (days * daywidth)
        barpct = 0
        if highestreward > lowestreward:
            barpct = (currenttotal-lowestreward)/(highestreward-lowestreward)
        bartop = chartbottom - int(math.floor((chartbottom-charttop)*barpct))
        draw.rectangle(xy=[dayx,bartop,dayx+barwidth,chartbottom-1],fill=colorminingreward)       
    overalltotal = overalltotal * 100000000
    dailyavg = (overalltotal / totaldays)
    # Chart header
    drawcenteredtext(draw, "Last 30 days (" + str(int(overalltotal)) + ") Daily Average (" + str(int(dailyavg)) + ")"  , 16, int(width/2), (headerheight + hashheight))
    if dailyavg < breakevendaily:
        drawcenteredtext(draw, "Warning: Mining at a Loss.", 16, int(width/2), (headerheight + hashheight - 40), colorFF0000)
        drawcenteredtext(draw, "Break Even is " + str(breakevendaily) + " sats Daily", 16, int(width/2), (headerheight + hashheight - 20), colorFF0000)
    # Date and Time
    dt = "as of " + getdateandtime()
    drawbottomrighttext(draw, dt, 12, width, height)
    # Save to file
    im.save(outputFile)


while True:
    accountprofile = getaccountprofile()
    accountrewards = getaccountrewards()
    createimage(accountrewards,accountprofile)
    time.sleep(300)
