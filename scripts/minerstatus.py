#! /usr/bin/python3
from PIL import Image, ImageDraw, ImageColor
import json
import subprocess
import time
import vicarioustext

configFile="/home/bitcoin/nodeyez/config/minerstatus.json"
outputFile = "/home/bitcoin/images/minerstatus.png"
mineraddress = "--put-the-ip-address-for-your-miner-in--nodeyez/config/minerstatus.json"
minerusername = "--put-the-username-for-your-miner-in--nodeyez/config/minerstatus.json"
sleepInterval=30
colorFFFFFF=ImageColor.getrgb("#ffffff")
colorHashboardLine=ImageColor.getrgb("#808080")
colorWarn=ImageColor.getrgb("#ffaa00")
tempwarning=88.0
fanwarning=3000

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

def drawicon(draw,icon,x,y,w,h,v=None):
    colorArcBorder=ImageColor.getrgb("#c0c0c0")
    colorArcBackground=ImageColor.getrgb("#000000")  # arc background/blank
    colorArcDefault=ImageColor.getrgb("#40ff40")  # green arc color (default)
    colorArcRedAlert=ImageColor.getrgb("#ff0000")  # when percent > 75
    colorArcWarn=ImageColor.getrgb("#ffff00")  # when percent > 50


    if icon == "fan":
        l = list(v.split())[0]
        p = list(v.split())[1]
        pad = 20
        draw.arc(xy=(x+pad,y+pad,x+w-pad,y+h-pad),start=120,end=420,fill=colorArcBorder,width=20)
        draw.arc(xy=(x+pad+2,y+pad+2,x+w-pad-2,y+h-pad-2),start=120+1,end=420-1,fill=colorArcBackground,width=16)
        arccolor=colorArcDefault
        if int(p) == 0:
            p = "1"
        if int(p) > 50:
            arccolor=colorArcWarn
        if int(p) > 75:
            arccolor=colorArcRedAlert
        ea=120+int((420-120)*(float(p)/100))
        draw.arc(xy=(x+pad+2,y+pad+2,x+w-pad-2,y+h-pad-2),start=120,end=ea,fill=arccolor,width=16)
        # draw percentage
        #tt = p + "%"
        #ttw,tth = draw.textsize(tt, fontDeja20)
        #ox,oy = fontDeja20.getoffset(tt)
        #ttw += ox
        #tth += oy
        # draw label (fan RPM)
        vicarioustext.drawcenteredtext(draw,l,16,x+(w/2),y+((h/8)*7))
#        tt = l
#        ttw,tth = draw.textsize(tt, fontDeja16)
#        ox,oy = fontDeja20.getoffset(tt)
#        ttw += ox
#        tth += oy
#        draw.text(xy=(x+(w/2)-(ttw/2),y+((h/8)*7)-(tth/2)),text=tt,font=fontDeja16,fill=colorFFFFFF)

def createimage(minerinfo, width=480, height=320):
    headerheight = 30
    footerheight = 15
    thheight = (height - headerheight - footerheight) * .18
    hbheight = (height - headerheight - footerheight) * .41
    fanheight = (height - headerheight - footerheight) * .41
    im = Image.new(mode="RGB", size=(width, height))
    draw = ImageDraw.Draw(im)
    # Header
    vicarioustext.drawcenteredtext(draw, "Miner Status", 24, int(width/2), int(headerheight/2),colorFFFFFF,True)
    # Get TH rate
    hashrate = gethashrate(minerinfo)
    vicarioustext.drawcenteredtext(draw, hashrate, 24, (width/4*1), (headerheight + footerheight + (thheight/2)))
    # Get Highest Temp
    hightemp = gethighesttemp(minerinfo)
    colorTemp = colorFFFFFF
    if hightemp > str(format(tempwarning,".2f"))+"°C":
        colorTemp = colorWarn
    vicarioustext.drawcenteredtext(draw, hightemp, 24, (width/4*3), (headerheight + footerheight + (thheight/2)),colorTemp)
    # Board info
    vicarioustext.drawcenteredtext(draw, "Board Temp", 16, (width/8*1), (headerheight + footerheight + thheight + (hbheight/6*3)))
    vicarioustext.drawcenteredtext(draw, "Chip Temp", 16, (width/8*1), (headerheight + footerheight + thheight + (hbheight/6*5)))
    hbcount = 0
    for temps in minerinfo["temps"]:
        for hashboard in temps["TEMPS"]:
            hbcount = hbcount + 1
            if hbcount > 3:
                break
            hashboardid = str(hashboard["ID"])
            vicarioustext.drawcenteredtext(draw, hashboardid, 16, (width/8*(1+(hbcount*2))), (headerheight + footerheight + thheight + (hbheight/6*1)))
            hashboardtemp = str(format(hashboard["Board"],".2f")) + "°C"
            colorTemp = colorFFFFFF
            if format(hashboard["Board"],".2f") > format(tempwarning,".2f"):
                colorTemp = colorWarn
            vicarioustext.drawcenteredtext(draw, hashboardtemp, 16, (width/8*(1+(hbcount*2))), (headerheight + footerheight + thheight + (hbheight/6*3)),colorTemp)
            hashboardchiptemp = str(format(hashboard["Chip"],".2f")) + "°C"
            colorTemp = colorFFFFFF
            if format(hashboard["Chip"],".2f") > format(tempwarning,".2f"):
                colorTemp = colorWarn
            vicarioustext.drawcenteredtext(draw, hashboardchiptemp, 16, (width/8*(1+(hbcount*2))), (headerheight + footerheight + thheight + (hbheight/6*5)),colorTemp)
    draw.line(xy=[0+20,headerheight+footerheight+thheight+(hbheight/3*1),width-20,headerheight+footerheight+thheight+(hbheight/3*1)],fill=colorHashboardLine,width=2)
    draw.line(xy=[0+20,headerheight+footerheight+thheight+(hbheight/3*2),width-20,headerheight+footerheight+thheight+(hbheight/3*2)],fill=colorHashboardLine,width=2)
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
    dt = "as of " + vicarioustext.getdateandtime()
    vicarioustext.drawbottomrighttext(draw, dt, 12, width, height)
    # Save to file
    im.save(outputFile)


while True:
    f = open(configFile)
    config = json.load(f)
    f.close()
    if "mineraddress" in config:
        mineraddress = config["mineraddress"]
    if "minerusername" in config:
        minerusername = config["minerusername"]
    minerinfo = getminerinfo()
    createimage(minerinfo)
    time.sleep(sleepInterval)
