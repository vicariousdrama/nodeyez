#! /usr/bin/env python3
from PIL import Image, ImageDraw, ImageColor
from os.path import exists
import json
import subprocess
import sys
import time
import vicarioustext

def getcookiefilename():
    cmd = "echo '" + mineraddress + "' | sha256sum | awk '{print $1}'"
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
    except subprocess.CalledProcessError as e:
        cmdoutput = "tmp"
    cmdoutput = cmdoutput.replace("\n", "")
    return cookieFile + "-" + cmdoutput

def getminerinfo():
    cookiefilename = getcookiefilename()
    # login
    cmd = "curl -b " + cookiefilename + " -c " + cookiefilename
    cmd = cmd + " -F 'luci_username=" + minerusername + "' "
    if len(minerpassword) > 0:
        cmd = cmd + " -F 'luci_password=" + minerpassword + "' "
    cmd = cmd + "http://" + mineraddress + "/cgi-bin/luci/admin/miner/api_status/"
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
    colorArcBackground=colorBackground # ImageColor.getrgb("#000000")  # arc background/blank
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
        # draw label (fan RPM)
        vicarioustext.drawcenteredtext(draw,l,16,x+(w/2),y+((h/8)*7))

def createimage(minerinfo, width=480, height=320):
    headerheight = 30
    footerheight = 15
    thheight = (height - headerheight - footerheight) * .18
    hbheight = (height - headerheight - footerheight) * .41
    fanheight = (height - headerheight - footerheight) * .41
    im = Image.new(mode="RGB", size=(width, height), color=colorBackground)
    draw = ImageDraw.Draw(im)
    # Header
    headerText = "Miner"
    if len(minerlabel) > 0:
        headerText = headerText + ": " + minerlabel
    vicarioustext.drawcenteredtext(draw, headerText, 24, int(width/2), int(headerheight/2),colorTextFG,True)
    # Get TH rate
    hashrate = gethashrate(minerinfo)
    vicarioustext.drawcenteredtext(draw, hashrate, 24, (width/4*1), (headerheight + footerheight + (thheight/2)), colorTextFG)
    # Get Highest Temp
    hightemp = gethighesttemp(minerinfo)
    colorTemp = colorTextFG
    if hightemp > str(format(tempWarning,".2f"))+"°C":
        colorTemp = colorWarn
    vicarioustext.drawcenteredtext(draw, hightemp, 24, (width/4*3), (headerheight + footerheight + (thheight/2)),colorTemp)
    # Board info
    vicarioustext.drawcenteredtext(draw, "Board Temp", 16, (width/8*1), (headerheight + footerheight + thheight + (hbheight/6*3)),colorTextFG)
    vicarioustext.drawcenteredtext(draw, "Chip Temp", 16, (width/8*1), (headerheight + footerheight + thheight + (hbheight/6*5)),colorTextFG)
    hbcount = 0
    for temps in minerinfo["temps"]:
        for hashboard in temps["TEMPS"]:
            hbcount = hbcount + 1
            if hbcount > 3:
                break
            hashboardid = str(hashboard["ID"])
            vicarioustext.drawcenteredtext(draw, hashboardid, 16, (width/8*(1+(hbcount*2))), (headerheight + footerheight + thheight + (hbheight/6*1)),colorTextFG)
            hashboardtemp = str(format(hashboard["Board"],".2f")) + "°C"
            colorTemp = colorTextFG
            if format(hashboard["Board"],".2f") > format(tempWarning,".2f"):
                colorTemp = colorWarn
            vicarioustext.drawcenteredtext(draw, hashboardtemp, 16, (width/8*(1+(hbcount*2))), (headerheight + footerheight + thheight + (hbheight/6*3)),colorTemp)
            hashboardchiptemp = str(format(hashboard["Chip"],".2f")) + "°C"
            colorTemp = colorTextFG
            if format(hashboard["Chip"],".2f") > format(tempWarning,".2f"):
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
    vicarioustext.drawbottomrighttext(draw, dt, 12, width, height, colorTextFG)
    # Save to file
    outputFileMiner = outputFile
    if len(minerlabel) > 0:
        outputFileMiner = outputFileMiner.replace(".png", "-" + minerlabel + ".png")
    im.save(outputFileMiner)


def isvalidminer():
    if len(mineraddress) == 0:
        return False
    if len(minerusername) == 0:
        return False
    if "miners" in config:
        if len(config["miners"]) > 1 and len(minerlabel) == 0:
            return False
    return True

if __name__ == '__main__':
    # Defaults
    configFile="/home/bitcoin/nodeyez/config/minerstatus.json"
    outputFile="/home/bitcoin/images/minerstatus.png"
    dataDirectory="/home/bitcoin/nodeyez/data/"
    minerlabel=""
    mineraddress=""
    minerusername=""
    minerpassword=""
    sleepInterval=30
    colorTextFG=ImageColor.getrgb("#ffffff")
    colorHashboardLine=ImageColor.getrgb("#808080")
    colorWarn=ImageColor.getrgb("#ffaa00")
    colorBackground=ImageColor.getrgb("#000000")
    tempWarning=88.0
    # Inits
    cookieFile=dataDirectory + "minercookiefile"
    # Require config
    if not exists(configFile):
        print(f"You need to make a config file at {configFile} to set your miner address and login information")
        exit(1)
    # Override config
    if exists(configFile):
        with open(configFile) as f:
            config = json.load(f)
        if "minerstatus" in config:
            config = config["minerstatus"]
        if "outputFile" in config:
            outputFile = config["outputFile"]
        if "dataDirectory" in config:
            dataDirectory = config["dataDirectory"]
        if "minerlabel" in config:
            minerlabel = config["minerlabel"]
        if "mineraddress" in config:
            mineraddress = config["mineraddress"]
        if "minerusername" in config:
            minerusername = config["minerusername"]
        if "minerpassword" in config:
            minerpassword = config["minerpassword"]
        if "sleepInterval" in config:
            sleepInterval = int(config["sleepInterval"])
            sleepInterval = 15 if sleepInterval < 15 else sleepInterval # 15 seconds minimum, local only
        if "colorTextFG" in config:
            colorTextFG = ImageColor.getrgb(config["colorTextFG"])
        if "colorHashboardLine" in config:
            colorHashboardLine = ImageColor.getrgb(config["colorHashboardLine"])
        if "colorWarn" in config:
            colorWarn = ImageColor.getrgb(config["colorWarn"])
        if "colorBackground" in config:
            colorBackground = ImageColor.getrgb(config["colorBackground"])
        if "tempWarning" in config:
            tempWarning = float(config["tempWarning"])
    # Data directories
    if not exists(dataDirectory):
        os.makedirs(dataDirectory)
    # Check for single run
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h','--help']:
            print(f"Creates an image reflecting the miner status with hashrate, temp and fan state")
            print(f"Usage:")
            print(f"1) Call without arguments to run continuously using the configuration or defaults")
            print(f"You may specify a custom configuration file at {configFile}")
        exit(0)
    # Loop
    while True:
        if "miners" in config:
            miners = config["miners"]
            for miner in miners:
                minerlabel=""
                mineraddress=""
                minerusername=""
                minerpassword=""
                if "minerlabel" in miner:
                    minerlabel = miner["minerlabel"]
                if "mineraddress" in miner:
                    mineraddress = miner["mineraddress"]
                if "minerusername" in miner:
                    minerusername = miner["minerusername"]
                if "minerpassword" in miner:
                    minerpassword = miner["minerpassword"]
                if isvalidminer():
                    minerinfo = getminerinfo()
                    createimage(minerinfo)
                else:
                    print(f"One or more miners is missing information in {configFile}. Skipping.")
        else:
            if isvalidminer():
                minerinfo = getminerinfo()
                createimage(minerinfo)
            else:
                print(f"Inadequate configuration for miner. Set minerlabel, mineraddress, minerusername, and minerpassword for each miner in {configFile}.")
                exit(1)
        time.sleep(sleepInterval)
