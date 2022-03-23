#! /usr/bin/env python3
from PIL import Image, ImageDraw, ImageColor
from os.path import exists
import json
import os
import subprocess
import sys
import time
import vicarioustext

def getMinerInfo():
    print(f"Retrieving miner info for {mineraddress}")
    emptyresponse = '{"tunerstatus":[],"tempctrl":[],"fans":[],"temps":[],"summary":[],"pools":[]}'
    cmd = "echo '{\"command\":\"fans+tempctrl+temps+tunerstatus+summary+pools\"}' | nc " + mineraddress + " 4028 | jq ."
    cmdoutput = ""
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
    except subprocess.CalledProcessError as e:
        print(f"error in getminerinfo: {e}")
        cmdoutput = emptyresponse
    if len(cmdoutput) == 0:
        cmdoutput = emptyresponse
    j = json.loads(cmdoutput)
    return j

def getPowerInfo(minerinfo):
    powerlimit = 9999
    powerused = 9999
    powerchain = 9999
    powerminer = 9999
    powerunused = 9999
    if "tunerstatus" in minerinfo:
        for tunerstatus in minerinfo["tunerstatus"]:
            for innertuner in tunerstatus["TUNERSTATUS"]:
                powerlimit = innertuner["PowerLimit"]
                powerused = innertuner["ApproximateMinerPowerConsumption"]
                powerchain = innertuner["ApproximateChainPowerConsumption"]
                powerminer = powerused - powerchain
                powerunused = powerlimit - powerused
    return powerlimit, powerused, powerchain, powerminer, powerunused

def formatHashrate(hashrate, hashdesc):
    if hashdesc == "Mh/s" and hashrate > 1000.0:
        hashrate = hashrate/1000.0
        hashdesc = "Gh/s"
    if hashdesc == "Gh/s" and hashrate > 1000.0:
        hashrate = hashrate/1000.0
        hashdesc = "Th/s"
    if hashdesc == "Th/s" and hashrate > 1000.0:
        hashrate = hashrate/1000.0
        hashdesc = "Ph/s"
    if hashdesc == "Ph/s" and hashrate > 1000.0:
        hashrate = hashrate/1000.0
        hashdesc = "Eh/s"
    hashfmt = str(format(hashrate, ".2f")) + " " + hashdesc
    return hashfmt

def getHashrate(minerinfo, historylength):
    global minerlabel
    hashrate = 0.00
    hashdesc = "Mh/s"
    if "summary" in minerinfo:
        for summary in minerinfo["summary"]:
            for innersummary in summary["SUMMARY"]:
                if innersummary["MHS 1m"] > hashrate:
                    hashrate = innersummary["MHS 1m"]
    if minerkey not in minerhashhistory:
        minerhashhistory[minerkey] = []
    hashrategh = int(hashrate/1000.0)
    minerhashhistory[minerkey].append(hashrategh)
    while len(minerhashhistory[minerkey]) > historylength:
        del minerhashhistory[minerkey][0]
    return formatHashrate(hashrate, hashdesc)

def getHighestTemp(minerinfo):
    highesttemp = 0
    if "temps" in minerinfo:
        for temp in minerinfo["temps"]:
            for innertemp in temp["TEMPS"]:
                if innertemp["Board"] > highesttemp:
                    highesttemp = innertemp["Board"]
                if innertemp["Chip"] > highesttemp:
                    highesttemp = innertemp["Chip"]
    shighesttemp = "???" if highesttemp == 0 else str(format(highesttemp, ".2f")) + "°C"
    return shighesttemp

def getTempSettings(minerinfo):
    temptarget = temphot = tempdangerous = 0
    if "tempctrl" in minerinfo:
        for tempctrl in minerinfo["tempctrl"]:
            for innertempctrl in tempctrl["TEMPCTRL"]:
                temptarget = innertempctrl["Target"]
                temphot = innertempctrl["Hot"]
                tempdangerous = innertempctrl["Dangerous"]
    stemptarget = "???" if temptarget == 0 else str(temptarget) + "°C"
    stemphot = "???" if temphot == 0 else str(temphot) + "°C"
    stempdangerous = "???" if tempdangerous == 0 else str(tempdangerous) + "°C"
    return stemptarget, stemphot, stempdangerous

def getTunerStatus(minerinfo):
    if "tunerstatus" in minerinfo:
        if len(minerinfo["tunerstatus"]) == 0:
            return "No response from miner"
        for tunerstatus in minerinfo["tunerstatus"]:
            for innertuner in tunerstatus["TUNERSTATUS"]:
                for chainstatus in innertuner["TunerChainStatus"]:
                    status = chainstatus["Status"]
                    return status
    return "Unknown Status"

def renderPower(draw, minerinfo, left, top, width, height):
    groupFontSize = 18
    subtextFontSize = 14
    subtextPadding = 5
    powerlimit, powerused, powerchain, powerminer, powerunused = getPowerInfo(minerinfo)
    spowerlimit = "???" if powerlimit == 9999 else str(powerlimit) + "w"
    spowerused = "???" if powerused == 9999 else str(powerused) + "w"
    spowerchain = "???" if powerchain == 9999 else str(powerchain) + "w"
    spowerminer = "???" if powerminer == 9999 else str(powerminer) + "w"
    spowerunused = "???" if powerunused == 9999 else str(powerunused) + "w"
    print(f"  power used: {spowerused} (chain: {spowerchain}, miner: {spowerminer})")
    vicarioustext.drawtoplefttext(draw, "Power: ", groupFontSize, left, top, colorTextFG, True)
    vicarioustext.drawtoprighttext(draw, spowerused, groupFontSize, left+width, top, colorTextFG, True)
    vicarioustext.drawtoplefttext(draw, "~ chain power: ", subtextFontSize, left + subtextPadding, top + groupFontSize + (subtextFontSize * .5), colorTextFG)
    vicarioustext.drawtoprighttext(draw, spowerchain, subtextFontSize, left+width, top + groupFontSize + (subtextFontSize * .5), colorTextFG)
    vicarioustext.drawtoplefttext(draw, "~ miner power: ", subtextFontSize, left + subtextPadding, top + groupFontSize + (subtextFontSize * 1.5), colorTextFG)
    vicarioustext.drawtoprighttext(draw, spowerminer, subtextFontSize, left+width, top + groupFontSize + (subtextFontSize * 1.5), colorTextFG)
    vicarioustext.drawtoplefttext(draw, "unused power: ", subtextFontSize, left + subtextPadding, top + groupFontSize + (subtextFontSize * 2.5), colorTextFG)
    vicarioustext.drawtoprighttext(draw, spowerunused, subtextFontSize, left+width, top + groupFontSize + (subtextFontSize * 2.5), colorTextFG)
    vicarioustext.drawtoplefttext(draw, "allocated: ", subtextFontSize, left + subtextPadding, top + groupFontSize + (subtextFontSize * 3.5), colorTextFG)
    vicarioustext.drawtoprighttext(draw, spowerlimit, subtextFontSize, left+width, top + groupFontSize + (subtextFontSize * 3.5), colorTextFG)
    # Tuner status
    ts = getTunerStatus(minerinfo)
    colorTuner = colorTextFG
    if ts == "No response from miner":
        colorTuner = colorDangerous
    vicarioustext.drawbottomlefttext(draw, ts, 12, left, top+height, colorTuner)

def renderHashrate(draw, minerinfo, left, top, width, height):
    global minerhashhistory
    groupFontSize = 18
    subtextFontSize = 14
    tinyFontSize = 8
    subtextPadding = 15
    dataPointSize = 3
    hashrate = getHashrate(minerinfo, width)
    print(f"  hashrate: {hashrate}")
    #print(f"  hashrate history: {minerhashhistory[minerkey]}")
    vicarioustext.drawtoplefttext(draw, "Hashrate: ", groupFontSize, left, top, colorTextFG, True)
    vicarioustext.drawtoprighttext(draw, hashrate, groupFontSize, left+width, top, colorTextFG, True)
    # Visualize hashrate over time.
    hrgt = top + (groupFontSize + subtextPadding)
    hrgl = left
    hrgh = height - (groupFontSize + subtextPadding)
    hrgw = width
    hrlo = hrhi = minerhashhistory[minerkey][0]
    hrto = 0
    hrcn = 0
    for hrv in minerhashhistory[minerkey]:
        if hrv > -1:
            hrcn = hrcn + 1
            hrlo = hrv if ((hrv < hrlo) or (hrlo == -1)) else hrlo
            hrhi = hrv if ((hrv > hrhi) or (hrhi == -1)) else hrhi
            hrto = hrto + hrv
    # box
    boxfill = colorDangerous if minerhashhistory[minerkey][len(minerhashhistory[minerkey])-1] == 0 else colorBackground
    draw.rectangle(xy=[(hrgl,hrgt),(hrgl+hrgw,hrgt+hrgh)],fill=boxfill,outline=colorHashrateBox,width=2)
    # avg line
    hrav = float(hrto) / float(hrcn)
    hravp = .5
    if hrhi - hrlo > 0:
        hravp = float(hrav - hrlo)/float(hrhi - hrlo)
    hry = top + groupFontSize + subtextPadding + ((1.0 - hravp) * hrgh)
    avgliney = hry
    draw.line(xy=[(hrgl,hry),(hrgl+hrgw,hry)],fill=colorHashrateBox,width=1)
    # low line
    lowliney = 0
    lowlinev = (hrav * .80)
    if lowlinev > hrlo:
        hrp = float(lowlinev - hrlo)/float(hrhi-hrlo)
        hry = top + groupFontSize + subtextPadding + ((1.0 - hrp) * hrgh)
        lowliney = hry
        draw.line(xy=[(hrgl,hry),(hrgl+hrgw,hry)],fill=colorHot,width=1)
    hrl = len(minerhashhistory[minerkey])
    hri = hrl
    hrx = left + width - dataPointSize
    timelineBy30Mins = False
    timelineBy60Ticks = True
    if timelineBy30Mins:
        # time lines every 30 minutes
        pixelsPer30Minutes = 30 * (60 / sleepInterval)
        timeline = hrx
        timeperiod = 0
        while(timeline > left):
            timeline = timeline - pixelsPer30Minutes
            timeperiod = timeperiod + 1
            if timeline > left:
                draw.line(xy=[(timeline,hrgt-(subtextPadding/2)),(timeline,hrgt+hrgh)],fill=colorHashrateBox,width=1)
                timetext = str(timeperiod * 30) + " mins"
                vicarioustext.drawbottomlefttext(draw, timetext, tinyFontSize, timeline+2, hrgt - 1, colorTextFG)
    if timelineBy60Ticks:
        # time lines every 60 ticks
        timePeriodSize = 60
        minutesPerLine = (timePeriodSize * sleepInterval) / 60
        timeline = hrx
        timeperiod = 0
        while(timeline > left):
            timeline = timeline - timePeriodSize
            timeperiod = timeperiod + 1
            if timeline > left:
                draw.line(xy=[(timeline,hrgt-(subtextPadding/2)),(timeline,hrgt+hrgh)],fill=colorHashrateBox,width=1)
                timetext = str(int(timeperiod * minutesPerLine)) + " mins"
                vicarioustext.drawbottomlefttext(draw, timetext, tinyFontSize, timeline+2, hrgt - 1, colorTextFG)
    # data points
    while(hri > 0):
        hri = hri - 1
        hrx = hrx - 1
        if hrx <= left + dataPointSize:
            break
        hrv = minerhashhistory[minerkey][hri]
        if hrv > -1:
            hrp = .5
            if hrhi - hrlo > 0:
                hrp = float(hrv - hrlo)/float(hrhi - hrlo)
            hry = top + groupFontSize + subtextPadding + ((1.0 - hrp) * hrgh)
            colorPlot = colorHashratePlot
            if hrav > 0:
                colorPlot = colorHot if (hrv/hrav) < .80 else colorPlot
                colorPlot = colorDangerous if (hrv/hrav) < .50 else colorPlot
            else:
                colorPlot = colorDangerous
            if boxfill == colorDangerous:
                colorPlot = colorTextFG
            draw.ellipse(xy=[(hrx-1,hry-1),(hrx+1,hry+1)],fill=colorPlot,outline=colorPlot,width=dataPointSize)
    # high label
    hrmaxt = "Max: " + formatHashrate(hrhi, "Gh/s")
    tw,th,tf=vicarioustext.gettextdimensions(draw, hrmaxt, tinyFontSize, False)
    draw.rectangle(xy=[(hrgl+1,hrgt+1),(hrgl+tw+2,hrgt+th+2)],outline=colorHashrateBox,fill=colorHashrateBox,width=1)
    vicarioustext.drawtoplefttext(draw, hrmaxt, tinyFontSize, hrgl + 2, hrgt + 1, colorTextFG)
    # avg label
    hravt = "Avg: " + formatHashrate(hrav, "Gh/s")
    if hravp < .8:
        draw.rectangle(xy=[(hrgl+1,avgliney-1),(hrgl+tw+2,avgliney-th-2)],outline=colorHashrateBox,fill=colorHashrateBox,width=1)
        vicarioustext.drawbottomlefttext(draw, hravt, tinyFontSize, hrgl + 2, avgliney, colorTextFG)
    else:
        draw.rectangle(xy=[(hrgl+1,avgliney+1),(hrgl+tw+2,avgliney+th+2)],outline=colorHashrateBox,fill=colorHashrateBox,width=1)
        vicarioustext.drawtoplefttext(draw, hravt, tinyFontSize, hrgl + 2, avgliney, colorTextFG)
    # low line label
    if lowliney > 0:
        # as warning
        lowlinet = "Low: " + formatHashrate(lowlinev, "Gh/s")
        draw.rectangle(xy=[(hrgl+1,lowliney+1),(hrgl+tw+2,lowliney+th+2)],outline=colorHashrateBox,fill=colorHashrateBox,width=1)
        vicarioustext.drawtoplefttext(draw, lowlinet, tinyFontSize, hrgl + 2, lowliney + 1, colorHot)
    else:
        # as floor
        hrmint = "Min: " + formatHashrate(hrlo, "Gh/s")
        draw.rectangle(xy=[(hrgl+1,hrgt+hrgh-1),(hrgl+tw+2,hrgt+hrgh-th-2)],outline=colorHashrateBox,fill=colorHashrateBox,width=1)
        vicarioustext.drawbottomlefttext(draw, hrmint, tinyFontSize, hrgl + 2, hrgt + hrgh - 1, colorTextFG)

def renderTemperature(draw, minerinfo, left, top, width, height):
    groupFontSize = 16
    subtextFontSize = 12
    subtextPadding = 5
    temptarget, temphot, tempdangerous = getTempSettings(minerinfo)
    hightemp = getHighestTemp(minerinfo)
    print(f"  temperature: {hightemp}")
    colorTemp = colorTextFG
    if hightemp > temphot:
        colorTemp = colorHot
    vicarioustext.drawtoplefttext(draw, "Temp: ", groupFontSize, left, top, colorTextFG, True)
    vicarioustext.drawtoprighttext(draw, hightemp, groupFontSize, left+width, top, colorTemp, True)
    vicarioustext.drawtoplefttext(draw, "Target temp: ", subtextFontSize, left + subtextPadding, top + groupFontSize + (subtextFontSize * .5), colorTextFG)
    vicarioustext.drawtoprighttext(draw, temptarget, subtextFontSize, left+width, top + groupFontSize + (subtextFontSize * .5), colorTextFG)
    vicarioustext.drawtoplefttext(draw, "Hot temp: ", subtextFontSize, left + subtextPadding, top + groupFontSize + (subtextFontSize * 1.5), colorTextFG)
    vicarioustext.drawtoprighttext(draw, temphot, subtextFontSize, left+width, top + groupFontSize + (subtextFontSize * 1.5), colorHot)
    vicarioustext.drawtoplefttext(draw, "Danger temp: ", subtextFontSize, left + subtextPadding, top + groupFontSize + (subtextFontSize * 2.5), colorTextFG)
    vicarioustext.drawtoprighttext(draw, tempdangerous, subtextFontSize, left+width, top + groupFontSize + (subtextFontSize * 2.5), colorDangerous)

def renderFans(draw, minerinfo, left, top, width, height):
    groupFontSize = 16
    subtextFontSize = 12
    subtextPadding = 5
    fanspeed = 0
    fancount = 0
    if "fans" in minerinfo:
        for fan in minerinfo["fans"]:
            for currentfan in fan["FANS"]:
                fancount = fancount + 1
                if fancount > 4:
                    break
                fanid = str(currentfan["ID"])
                fanspeed = currentfan["Speed"]
                fanrpm = currentfan["RPM"]
                y = int(top + groupFontSize + (subtextFontSize * (float(currentfan["ID"]) + float(.5))))
                vicarioustext.drawtoplefttext(draw, "fan no. " + fanid, subtextFontSize, left + subtextPadding, y, colorTextFG)
                vicarioustext.drawtoprighttext(draw, str(fanrpm) + " RPM", subtextFontSize, left+width, y, colorTextFG)
    sfanspeed = "???" if fanspeed == 0 else str(fanspeed) + "%"
    print(f"  fan speed: {sfanspeed}")
    vicarioustext.drawtoplefttext(draw, "Fan Speed: ", groupFontSize, left, top, colorTextFG, True)
    vicarioustext.drawtoprighttext(draw, sfanspeed, groupFontSize, left+width, top, colorTextFG, True)

def renderPoolInfo(draw, minerinfo, left, top, width, height):
    groupFontSize = 16
    subtextFontSize = 12
    subtextPadding = 5
    linecount = 0
    if "pools" in minerinfo:
        for pool in minerinfo["pools"]:
            for currentpool in pool["POOLS"]:
                linecount = linecount + 1
                if linecount > 4:
                    break
                poolurl = currentpool["URL"]
                poolurlpos = poolurl[:poolurl.rfind(".")].rfind(".") + 1
                poolurl = poolurl[poolurlpos:]
                poolstatus = currentpool["Status"]
                print(f"  pool: {poolurl} ({poolstatus})")
                y = int(top + groupFontSize + (subtextFontSize * (float(linecount-1) + float(.5))))
                vicarioustext.drawtoplefttext(draw, poolurl, subtextFontSize, left + subtextPadding, y, colorTextFG)
                linecount = linecount + 1
                if linecount > 4:
                    break
                y = int(top + groupFontSize + (subtextFontSize * (float(linecount-1) + float(.5))))
                vicarioustext.drawtoprighttext(draw, poolstatus, subtextFontSize, left+width, y, colorTextFG)
    vicarioustext.drawtoplefttext(draw, "Pool Info: ", groupFontSize, left, top, colorTextFG, True)

def createimage(minerinfo, width=480, height=320):
    headerheight = 30
    footerheight = 15
    thheight = (height - headerheight - footerheight) * .18
    hbheight = (height - headerheight - footerheight) * .41
    fanheight = (height - headerheight - footerheight) * .41
    quadheight = int((height - headerheight - footerheight) * .5)
    quadwidth = int(width/2)
    quadpad = 5
    innerquadwidth = quadwidth-(quadpad*2)
    innerquadheight = quadheight-(quadpad*2)
    leftquadwidth = int(width * .40)
    rightquadwidth = int(width * .60)
    topquadheight = int((height - headerheight - footerheight) * .60)
    bottomquadheight = int((height - headerheight - footerheight) * .40)
    im = Image.new(mode="RGB", size=(width, height), color=colorBackground)
    draw = ImageDraw.Draw(im)
    # Header
    headerText = "Miner Status"
    if len(minerlabel) > 0:
        headerText = minerlabel
    vicarioustext.drawcenteredtext(draw, headerText, 24, int(width/2), int(headerheight/2),colorTextFG,True)
    # Input Power
    renderPower(draw, minerinfo, 0+quadpad, headerheight+quadpad, leftquadwidth-(quadpad*2), topquadheight-(quadpad*2))
    # Output Hashrate
    renderHashrate(draw, minerinfo, leftquadwidth+quadpad, headerheight+quadpad, rightquadwidth-(quadpad*2), topquadheight-(quadpad*2))
    # Input Temperature
    renderTemperature(draw, minerinfo, 0+quadpad, headerheight+topquadheight+quadpad, leftquadwidth-(quadpad*2), bottomquadheight-(quadpad*2))
    # Output Fans
    renderFans(draw, minerinfo, leftquadwidth+quadpad, headerheight+topquadheight+quadpad, int((rightquadwidth-(quadpad*2))*.50), bottomquadheight-(quadpad*2))
    # Output Pool
    renderPoolInfo(draw, minerinfo, leftquadwidth+quadpad+int((rightquadwidth-(quadpad))*.50)+quadpad, headerheight+topquadheight+quadpad, int((rightquadwidth-(quadpad*3))*.50), bottomquadheight-(quadpad*2))
    # Date and Time
    dt = "as of " + vicarioustext.getdateandtime()
    vicarioustext.drawbottomrighttext(draw, dt, 12, width, height, colorTextFG)
    # Braiins
    vicarioustext.drawbottomlefttext(draw, "Powered by Braiins", 14, 0, height, colorBraiins)
    # Save to file
    outputFileMiner = outputFile
    outputFileMiner = outputFileMiner.replace(".png", "-" + mineraddress + ".png")
    im.save(outputFileMiner)

def getMinerHashHistoryFilename():
    return dataDirectory + "minerbraiins/minerhashhistory.json"

def loadMinerHashHistory():
    filename = getMinerHashHistoryFilename()
    if not exists(filename):
        return {}
    mtime = int(os.path.getmtime(filename))
    currenttime = int(time.time())
    diff = currenttime - mtime
    emptyTicks = int(diff / sleepInterval)
    print(f"Loading existing hash history")
    with open(filename) as f:
        minerhashhistory = json.load(f)
    if emptyTicks > 0:
        print(f"Adding {emptyTicks} entries of empty hash history to demarcate time since last run.")
        for key in minerhashhistory:
            for k in range(emptyTicks):
                minerhashhistory[key].append(-1)
    return minerhashhistory

def saveMinerHashHistory(minerhashhistory):
    with open(getMinerHashHistoryFilename(), "w") as f:
        json.dump(minerhashhistory,f)

def isValidMiner():
    if len(mineraddress) == 0:
        return False
    if "miners" in config:
        for miner in config["miners"]:
            if len(miner["mineraddress"]) == 0:
                return False
    return True

if __name__ == '__main__':
    # Defaults
    configFile="/home/bitcoin/nodeyez/config/minerbraiins.json"
    outputFile="/home/bitcoin/images/minerbraiins.png"
    dataDirectory="/home/bitcoin/nodeyez/data/"
    minerlabel=""
    mineraddress=""
    sleepInterval=30
    colorBraiins=ImageColor.getrgb("#2f3fc5")
    colorTextFG=ImageColor.getrgb("#ffffff")
    colorHot=ImageColor.getrgb("#ffaa00")
    colorDangerous=ImageColor.getrgb("#ff0000")
    colorBackground=ImageColor.getrgb("#000000")
    colorHashrateBox=ImageColor.getrgb("#404040")
    colorHashratePlot=ImageColor.getrgb("#00ff00")
    # Inits
    lastSaved = 0
    saveInterval = 600
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
        if "sleepInterval" in config:
            sleepInterval = int(config["sleepInterval"])
            sleepInterval = 5 if sleepInterval < 5 else sleepInterval # 5 seconds minimum, local only
        if "colorTextFG" in config:
            colorTextFG = ImageColor.getrgb(config["colorTextFG"])
        if "colorHot" in config:
            colorHot = ImageColor.getrgb(config["colorHot"])
        if "colorDangerous" in config:
            colorDangerous = ImageColor.getrgb(config["colorDangerous"])
        if "colorBackground" in config:
            colorBackground = ImageColor.getrgb(config["colorBackground"])
        if "colorHashrateBox" in config:
            colorHashrateBox = ImageColor.getrgb(config["colorHashrateBox"])
        if "colorHashratePlot" in config:
            colorHashratePlot = ImageColor.getrgb(config["colorHashratePlot"])
    # Data directories
    if not exists(dataDirectory):
        os.makedirs(dataDirectory)
    if not exists(dataDirectory + "minerbraiins/"):
        os.makedirs(dataDirectory + "minerbraiins/")
    # Check for single run
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h','--help']:
            print(f"Creates an image summarizing miner status with power, hashrate, temp, fan and pool info")
            print(f"Usage:")
            print(f"1) Call without arguments to run continuously using the configuration or defaults")
            print(f"You may specify a custom configuration file at {configFile}")
        exit(0)
    # Load any existing hashrate history
    minerhashhistory = loadMinerHashHistory()
    # Loop
    while True:
        if "miners" in config:
            miners = config["miners"]
            for miner in miners:
                minerlabel=""
                mineraddress=""
                if "mineraddress" in miner:
                    mineraddress = miner["mineraddress"]
                if "minerlabel" in miner:
                    minerlabel = miner["minerlabel"]
                else:
                    minerlabel = "Miner: " + mineraddress
                if isValidMiner():
                    minerkey = mineraddress
                    minerinfo = getMinerInfo()
                    createimage(minerinfo)
                else:
                    print(f"One or more miners is missing information in {configFile}. Skipping.")
        else:
            if isValidMiner():
                minerkey = mineraddress
                minerinfo = getMinerInfo()
                createimage(minerinfo)
            else:
                print(f"Inadequate configuration for miner. Set minerlabel and mineraddress for each miner in {configFile}.")
                exit(1)
        if int(time.time()) > lastSaved + saveInterval:
            saveMinerHashHistory(minerhashhistory)
            lastSaved = int(time.time())
        time.sleep(sleepInterval)
