#! /usr/bin/python3
from datetime import datetime
from PIL import Image, ImageFilter, ImageDraw, ImageFont, ImageColor
import json
import math
import subprocess
import time

outputFile = "/home/bitcoin/images/minerstatus.png"
mineraddress = "69.69.69.69"
minerusername = "root"
colorFFFFFF=ImageColor.getrgb("#ffffff")
colorHasboardLine=ImageColor.getrgb("#808080")

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

def getcookiefilename():
    cmd = "echo '" + mineraddress + "' | sha256sum | awk '{print $1}'"
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
    except subprocess.CalledProcessError as e:
        cmdoutput = "tmp"
    cmdoutput = cmdoutput.replace("\n", "")
    return "~/minercookiefile-" + cmdoutput

def getminerinfo():
    cookiefilename = getcookiefilename()
    # login
    cmd = "curl -b " + cookiefilename + " -c " + cookiefilename + " -F 'luci_username=" + minerusername + "' http://" + mineraddress + "/cgi-bin/luci/admin/miner/api_status/"
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
    except subprocess.CalledProcessError as e:
        cmdoutput = ""
    # get info
    cmd = "curl -b " + cookiefilename + " -c " + cookiefilename + " http://" + mineraddress + "/cgi-bin/luci/admin/miner/api_status/"
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
    except subprocess.CalledProcessError as e:
        cmdoutput = "{\"summary\":[{\"SUMMARY\":[{\"MHS av\": 0.00}]}],\"fans\"[{\"FANS\":[{\"FAN\":0,\"ID\":0,\"Speed\":0,\"RPM\":0}]}],\"temps\"[{\"TEMPS\":[{\"TEMP\":0,\"ID\":0,\"Board\":0.00,\"Chip\":0.00}]}]}"
    j = json.loads(cmdoutput)
    return j

def gethashrate(minerinfo):
    hashrate = 0.00
    hashdesc = "Mh/s"
    for summary in minerinfo["summary"]:
        for innersummary in summary["SUMMARY"]:
            if innersummary["MHS av"] > hashrate:
                hashrate = innersummary["MHS av"]
    if hashrate > 1000.0:
        hashrate = hashrate/1000.0
        hashdesc = "Gh/s"
    if hashrate > 1000.0:
        hashrate = hashrate/1000.0
        hashdesc = "Th/s"
    if hashrate > 1000.0:
        hashrate = hashrate/1000.0
        hashdesc = "Ph/s"
    if hashrate > 1000.0:
        hashrate = hashrate/1000.0
        hashdesc = "Eh/s"
    hashfmt = str(format(hashrate, ".2f")) + " " + hashdesc
    return hashfmt

def gethighesttemp(minerinfo):
    highesttemp = 0
    for temp in minerinfo["temps"]:
        for innertemp in temp["TEMPS"]:
            if innertemp["Board"] > highesttemp:
                highesttemp = innertemp["Board"]
            if innertemp["Chip"] > highesttemp:
                highesttemp = innertemp["Chip"]
    return str(format(highesttemp, ".2f")) + "°C"

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

def drawicon(draw,icon,x,y,w,h,v=None):
    if icon == "fan":
        l = list(v.split())[0]
        p = list(v.split())[1]
        pad = 20
        draw.arc(xy=(x+pad,y+pad,x+w-pad,y+h-pad),start=120,end=420,fill=colorC0C0C0,width=20)
        draw.arc(xy=(x+pad+2,y+pad+2,x+w-pad-2,y+h-pad-2),start=120+1,end=420-1,fill=color000000,width=16)
        arccolor=colorC0FFC0
        if int(p) == 0:
            p = "1"
        if int(p) > 50:
            arccolor=colorFFFF00
        if int(p) > 75:
            arccolor=colorFF0000
        ea=120+int((420-120)*(float(p)/100))
        draw.arc(xy=(x+pad+2,y+pad+2,x+w-pad-2,y+h-pad-2),start=120,end=ea,fill=arccolor,width=16)
        # draw percentage
        tt = p + "%"
        ttw,tth = draw.textsize(tt, fontDeja20)
        ox,oy = fontDeja20.getoffset(tt)
        ttw += ox
        tth += oy
        #draw.text(xy=(x+(w/2)-(ttw/2)+1,y+((h/8)*4)-(tth/2)+1),text=tt,font=fontDeja20,fill=color000000)
        #draw.text(xy=(x+(w/2)-(ttw/2),y+((h/8)*4)-(tth/2)),text=tt,font=fontDeja20,fill=colorFFFFFF)
        # draw label (fan RPM)
        tt = l
        ttw,tth = draw.textsize(tt, fontDeja16)
        ox,oy = fontDeja20.getoffset(tt)
        ttw += ox
        tth += oy
        draw.text(xy=(x+(w/2)-(ttw/2),y+((h/8)*7)-(tth/2)),text=tt,font=fontDeja16,fill=colorFFFFFF)

def createimage(minerinfo, width=480, height=320):
    headerheight = 30
    footerheight = 15
    thheight = (height - headerheight - footerheight) * .18
    hbheight = (height - headerheight - footerheight) * .41
    fanheight = (height - headerheight - footerheight) * .41
    im = Image.new(mode="RGB", size=(width, height))
    draw = ImageDraw.Draw(im)
    # Header
    drawcenteredtext(draw, "Miner Status", 24, int(width/2), int(headerheight/2))
    # Get TH rate
    hashrate = gethashrate(minerinfo)
    drawcenteredtext(draw, hashrate, 24, (width/4*1), (headerheight + footerheight + (thheight/2)))
    # Get Highest Temp
    hightemp = gethighesttemp(minerinfo)
    drawcenteredtext(draw, hightemp, 24, (width/4*3), (headerheight + footerheight + (thheight/2)))
    # Board info
    drawcenteredtext(draw, "Board Temp", 16, (width/8*1), (headerheight + footerheight + thheight + (hbheight/6*3)))
    drawcenteredtext(draw, "Chip Temp", 16, (width/8*1), (headerheight + footerheight + thheight + (hbheight/6*5)))
    hbcount = 0
    for temps in minerinfo["temps"]:
        for hashboard in temps["TEMPS"]:
            hbcount = hbcount + 1
            if hbcount > 3:
                break
            hashboardid = str(hashboard["ID"])
            hashboardtemp = str(format(hashboard["Board"],".2f")) + "°C"
            hashboardchiptemp = str(format(hashboard["Chip"],".2f")) + "°C"
            drawcenteredtext(draw, hashboardid, 16, (width/8*(1+(hbcount*2))), (headerheight + footerheight + thheight + (hbheight/6*1)))
            drawcenteredtext(draw, hashboardtemp, 16, (width/8*(1+(hbcount*2))), (headerheight + footerheight + thheight + (hbheight/6*3)))
            drawcenteredtext(draw, hashboardchiptemp, 16, (width/8*(1+(hbcount*2))), (headerheight + footerheight + thheight + (hbheight/6*5)))
    draw.line(xy=[0+20,headerheight+footerheight+thheight+(hbheight/3*1),width-20,headerheight+footerheight+thheight+(hbheight/3*1)],fill=colorHasboardLine,width=2)
    draw.line(xy=[0+20,headerheight+footerheight+thheight+(hbheight/3*2),width-20,headerheight+footerheight+thheight+(hbheight/3*2)],fill=colorHasboardLine,width=2)
    # Fan info
    fancount = 0
    for fan in minerinfo["fans"]:
        for currentfan in fan["FANS"]:
            fancount = fancount + 1
            if fancount > 4:
                break
            fanid = str(currentfan["ID"])
            fanspeed = currentfan["Speed"]
            fanrpm = currentfan["RPM"]
            fanx = (fancount-1)*(width/4)
            fany = headerheight+footerheight+thheight+hbheight-10
            fanw = width/4
            fanh = fanheight
            drawicon(draw, "fan", fanx, fany, fanw, fanh, str(fanrpm) + "RPM " + str(fanspeed))
    # Date and Time
    dt = "as of " + getdateandtime()
    drawbottomrighttext(draw, dt, 12, width, height)
    # Save to file
    im.save(outputFile)


while True:
    minerinfo = getminerinfo()
    createimage(minerinfo)
    time.sleep(30)
