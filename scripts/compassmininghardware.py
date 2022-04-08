#! /usr/bin/env python3
from datetime import datetime
from PIL import Image, ImageDraw, ImageColor
from os.path import exists
import json
import math
import subprocess
import sys
import time
import requests
import vicarioustext


def getHardwareInfo():
    cmd = "curl -s " + hardwareurl
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
    except subprocess.CalledProcessError as e:
        print(f"Error retrieving compass mining hardware data from {hardwareurl}")
        print(f"{e}")
        cmdoutput = '{"ok":true,"payload":{"hardwareGrouped":[]}}'
    j = json.loads(cmdoutput)
    return j

def getHardwareGrouped(hwinfo):
    if "payload" in hwinfo:
        if "hardwareGrouped" in hwinfo["payload"]:
            hardwareGrouped = hwinfo["payload"]["hardwareGrouped"]
            if len(hardwareGrouped) > 0:
                return hardwareGrouped
    return None

def findLowestPrice(hwinfo):
    matchentry = hwinfo[0]
    for hwentry in hwinfo:
        if hwentry["algorithm"] == "SHA256":
            if int(hwentry["minCost"]) < int(matchentry["minCost"]):
                matchentry = hwentry
    return matchentry

def findHighestHashrate(hwinfo):
    matchentry = hwinfo[0]
    for hwentry in hwinfo:
        if hwentry["algorithm"] == "SHA256":
            if int(hwentry["hashrate"]) > int(matchentry["hashrate"]):
                matchentry = hwentry
    return matchentry

def findCheapestHashrate(hwinfo):
    matchentry = hwinfo[0]
    for hwentry in hwinfo:
        if hwentry["algorithm"] == "SHA256":
            if float(int(hwentry["minCost"])) / float(int(hwentry["hashrate"])) < float(int(matchentry["minCost"])) / float(int(matchentry["hashrate"])):
                matchentry = hwentry
    return matchentry

def findEfficientHashrate(hwinfo):
    matchentry = hwinfo[0]
    for hwentry in hwinfo:
        if hwentry["algorithm"] == "SHA256":
            if float(int(hwentry["power"])) / float(int(hwentry["hashrate"])) < float(int(matchentry["power"])) / float(int(matchentry["hashrate"])):
                matchentry = hwentry
    return matchentry

def renderEntry(draw, x, y, w, h, label, entry):
    name = "Miner"
    if "name" in entry:
        name = entry["name"]
    if "baseModelName" in entry:
        name = entry["baseModelName"]
    hashrate = entry["hashrate"]
    power = entry["power"]
    minCost = entry["minCost"]
    eff = round((float(power) / float(hashrate)),1)
    costPerTH = round((float(minCost) / float(hashrate)),2)
    # e.g.   Lowest Price
    vicarioustext.drawcenteredtext(draw, label, sizeEntryLabel, x + (w/2), y+20, colorEntryLabel)
    # e.g.   Whatsminer M32 66TH/s
    vicarioustext.drawcenteredtext(draw, name + " " + str(hashrate) + "TH", sizeEntryName, x + (w/2), y+40, colorEntryName)
    # e.g.   from $6999
    vicarioustext.drawcenteredtext(draw, "from $" + str(minCost), sizeEntryInfo, x + (w/2), y+60, colorEntryPrice, True)
    # e.g.   3300 watt (50.0J/TH)
    vicarioustext.drawcenteredtext(draw, str(power) + " watt (" + str(eff) + "J/TH)", sizeEntryInfo, x + (w/2), y+80, colorEntryPower)
    # e.g.   $106.05/TH
    vicarioustext.drawcenteredtext(draw, "$" + str(costPerTH) + "/TH", sizeEntryInfo, x + (w/2), y+100, colorEntryPower)

def createimage(width=480, height=320):
    hardwareinfo = getHardwareInfo()
    hwGrouped = getHardwareGrouped(hardwareinfo)
    headerheight = 50
    footerheight = 18
    im = Image.new(mode="RGB", size=(width, height), color=colorBackground)
    draw = ImageDraw.Draw(im)
    # header
    vicarioustext.drawcenteredtext(draw, "Compass Mining Hardware Prices", 24, int(width/2), 15, colorTextFG, True)
    vicarioustext.drawcenteredtext(draw, "Certified Reseller ASICs", 16, int(width/2), 40, colorTextFG)

    if hwGrouped is not None:
        # find the machines we want
        entryLowestPrice = findLowestPrice(hwGrouped)
        entryHighestHashrate = findHighestHashrate(hwGrouped)
        entryCheapestHashrate = findCheapestHashrate(hwGrouped)
        entryEfficientHashrate = findEfficientHashrate(hwGrouped)
        # render
        internalHeight = height-(headerheight+footerheight)
        halfInternalHeight = int(internalHeight/2)
        renderEntry(draw, 0, headerheight, int(width/2), halfInternalHeight, "Lowest Price", entryLowestPrice)
        renderEntry(draw, int(width/2), headerheight, int(width/2), halfInternalHeight, "Highest Hashrate", entryHighestHashrate)
        renderEntry(draw, 0, headerheight + halfInternalHeight, int(width/2), halfInternalHeight, "Cheapest Hashrate", entryCheapestHashrate)
        renderEntry(draw, int(width/2), headerheight + halfInternalHeight, int(width/2), halfInternalHeight, "Energy Efficient", entryEfficientHashrate)
    else:
        vicarioustext.drawcenteredtext(draw, "Unable to get hardware information", 20, width, height, colorTextWarn)

    # timestamp
    vicarioustext.drawbottomrighttext(draw, "as of " + vicarioustext.getdateandtime(), 12, width, height, colorTextFG)
    im.save(outputFile)

if __name__ == '__main__':
    # Defaults
    configFile="/home/nodeyez/nodeyez/config/compassmininghardware.json"
    outputFile="/home/nodeyez/nodeyez/imageoutput/compassmininghardware.png"
    hardwareurl="https://us-central1-hashr8-compass.cloudfunctions.net/app/hardware/group?isWeb=true&sortByCost=asc"
    colorTextFG=ImageColor.getrgb("#ffffff")
    colorTextWarn=ImageColor.getrgb("#ff0000")
    colorBackground=ImageColor.getrgb("#000000")
    colorEntryLabel=ImageColor.getrgb("#8080ff")
    colorEntryName=ImageColor.getrgb("#ff8000")
    colorEntryPrice=ImageColor.getrgb("#ffffff")
    colorEntryPower=ImageColor.getrgb("#808080")
    sizeEntryLabel=20
    sizeEntryName=18
    sizeEntryInfo=14
    sleepInterval=3600
    # Override defaults
    if exists(configFile):
        with open(configFile) as f:
            config = json.load(f)
        if "compassmininghardware" in config:
            config = config["compassmininghardware"]
        if "outputFile" in config:
            outputFile = config["outputFile"]
        if "hardwareurl" in config:
            hardwareurl = config["hardwareurl"]
        if "colorTextFG" in config:
            colorTextFG = ImageColor.getrgb(config["colorTextFG"])
        if "colorTextWarn" in config:
            colorTextWarn = ImageColor.getrgb(config["colorTextWarn"])
        if "colorBackground" in config:
            colorBackground = ImageColor.getrgb(config["colorBackground"])
        if "colorEntryLabel" in config:
            colorEntryLabel = ImageColor.getrgb(config["colorEntryLabel"])
        if "colorEntryName" in config:
            colorEntryName = ImageColor.getrgb(config["colorEntryName"])
        if "colorEntryPrice" in config:
            colorEntryPrice = ImageColor.getrgb(config["colorEntryPrice"])
        if "colorEntryPower" in config:
            colorEntryPower = ImageColor.getrgb(config["colorEntryPower"])
        if "sizeEntryLabel" in config:
            sizeEntryLabel = int(config["sizeEntryLabel"])
        if "sizeEntryName" in config:
            sizeEntryName = int(config["sizeEntryName"])
        if "sizeEntryInfo" in config:
            sizeEntryInfo = int(config["sizeEntryInfo"])
        if "sleepInterval" in config:
            sleepInterval = int(config["sleepInterval"])
            sleepInterval = 300 if sleepInterval < 300 else sleepInterval # minimum 5 minutes, access other
    # Check for single run
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h','--help']:
            print(f"Retrieves the Compass Mining Hardware from reseller market and summarizes")
            print(f"Usage:")
            print(f"1) Call without arguments to run continuously using the configuration or defaults")
            print(f"You may specify a custom configuration file at {configFile}")
        else:
            createimage()
        exit(0)
    # Loop
    while True:
        createimage()
        time.sleep(sleepInterval)
