#! /usr/bin/env python3
from PIL import Image, ImageDraw, ImageColor
import glob
import json
import math
import os.path
import random
import subprocess
import sys
import time
import vicarioustext

# ===============================================================================================================================
# SPECIAL DEPENDENCY: To use this script, you should have gas price data downloaded to the the following location
#      /home/nodeyez/nodeyez/data/collectapi/gasprice/allusaprice
#      /home/nodeyez/nodeyez/data/collectapi/gasprice/canada
# You can get this data from the collectapi.com website using an API Key.  The free plan allows for making 100 requests per
# month and the gas price data is updated daily.  You can and should make use of the daily-data-retrieval.py script and service
# to retrieve this information for you so you dont waste your free api calls on testing.
#
# For configuration, copy the sample-config/gasprice.json file to config/gasprice.json and set the location of your blockclock
# ===============================================================================================================================

def getDataDirectory():
    global dataCountry
    global randomCountry
    global dataDirectory
    if randomCountry:
        countryIndex = int(random.random() * 2)
        if countryIndex == 0:
            dataCountry = "USA"
        if countryIndex == 1:
            dataCountry = "CAN"
    if dataCountry == "USA":
        return dataDirectory + "collectapi/gasprice/allusaprice/"
    if dataCountry == "CAN":
        return dataDirectory + "collectapi/gasprice/canada/"
    # default
    return dataDirectory + "collectapi/gasprice/allusaprice/"

def getNewestFile():
    gasfileDirectory = getDataDirectory()
    files = glob.glob(gasfileDirectory + "*.json")
    newestfile = max(files, key=os.path.getctime)
    return newestfile

def getItemCount(newestfile):
    with open(newestfile) as f:
        filedata = json.load(f)
        return len(filedata["result"])
    return -1

def getItemIndexForState(newestfile, name):
    with open(newestfile) as f:
        filedata = json.load(f)
        itemindex = 0
        for item in filedata["result"]:
            if item["name"] == name:
                return itemindex
            itemindex = itemindex + 1
    return -1

def getItemInfo(newestfile, itemindex):
    with open(newestfile) as f:
        filedata = json.load(f)
        name = filedata["result"][itemindex]["name"]
        currency = filedata["result"][itemindex]["currency"]
        price = filedata["result"][itemindex]["gasoline"]
        return name, currency, price
    return "Unknown", "usd", "99.99"

def createImage(name, currency, price, width=480, height=320):
    im = Image.new(mode="RGB", size=(width, height), color=colorBackground)
    draw = ImageDraw.Draw(im)
    vicarioustext.drawcenteredtext(draw, "GAS Prices", 72, int(width/2), int(height/2)-120, colorTextGas)
    vicarioustext.drawcenteredtext(draw, name, 64, int(width/2), int(height/2), colorTextLocation)
    pricelabel = "$" + price
    if dataCountry == "USA":
        pricelabel = pricelabel + "/gallon"
    else:
        pricelabel = pricelabel + "/liter"
    vicarioustext.drawcenteredtext(draw, pricelabel, 72, int(width/2), int(height/2)+120, colorTextPrice)
    im.save(outputFile)

def getUSAbbrev(name):
    abbrev = {"Alaska": "AK", "Alabama": "AL", "Arkansas": "AR", "Arizona": "AZ", "California": "CA", "Colorado": "CO", "Connecticut": "CT",
      "District of Columbia": "DC", "Delaware": "DE", "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Iowa": "IA", "Idaho": "ID",
      "Illinois": "IL", "Indiana": "IN", "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Massachusetts": "MA", "Maryland": "MD",
      "Maine": "ME", "Michigan": "MI", "Minnesota": "MN", "Missouri": "MO", "Mississippi": "MS", "Montana": "MT", "North Carolina": "NC",
      "North Dakota": "ND", "Nebraska": "NE", "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "Nevada": "NV", "New York": "NY",
      "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD",
      "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Virginia": "VA", "Vermont": "VT", "Washington": "WA", "Wisconsin": "WI",
      "West Virginia": "WV", "Wyoming": "WY"}
    return abbrev[name]

def getCANAbbrev(name):
    abbrev = {"Newfoundland and Labrador": "NL", "Prince Edward Island": "PE", "Nova Scotia": "NS", "New Brunswick": "NB", "Quebec": "QC",
      "Ontario": "ON", "Manitoba": "MB", "Saskatchewan": "SK", "Alberta": "AB", "British Columbia": "BC", "Yukon": "YT",
      "Northwest Territories": "NT", "Nunavut": "NU"}
    return abbrev[name]


def blockclockAPICall(urltocall):
    cmd = "curl -s "
    if len(blockclockPassword) > 0:
        cmd = cmd + " --digest -u :" + blockclockPassword + " "
    cmd = cmd + "\"" + urltocall + "\""
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
        print(cmdoutput)
    except subprocess.CalledProcessError as e:
        print(f"error {e}")

def blockclockReport(name, currency, price):
    if not blockclockEnabled:
        return
    baseapi="http://" + blockclockAddress + "/api/"
    # a make the value have 5 digits total pad out right side
    rprice = str(price)
    while len(rprice) < 6:
        rprice = rprice + "9"
    # send basic price info
    blockclockAPICall(baseapi + "show/number/" + rprice + "?sym=$&pair=GAS/")
    if dataCountry == "USA":
        voltype = "GAL"
        abbrev = getUSAbbrev(name)
    else:
        voltype = "LITER"
        abbrev = getCANAbbrev(name)
    # b slot 5 is currency and volume
    blockclockAPICall(baseapi + "ou_text/5/USD/" + voltype)
    # c slot 6 is location
    blockclockAPICall(baseapi + "ou_text/6/" + abbrev + "/" + dataCountry)

def processdata(width=480, height=320):
    global randomCountry
    global randomState
    #1. get newest file in folder
    newestfile = getNewestFile()
    #2. get the length of items in result
    itemcount = getItemCount(newestfile)
    if itemcount > 0:
        #3. pick a random entry or find static entry
        itemindex = getItemIndexForState(newestfile, dataState)
        if itemindex == -1 and not randomCountry and not randomState:
            print(f"Could not find state or province named {dataState} in {newestfile}. Choosing randomly")
        if randomCountry or randomState or itemindex == -1:
            itemindex = int(random.random() * itemcount)
        name, currency, price = getItemInfo(newestfile, itemindex)
        print(f"Doing gas prices for {price}, {currency}, {name}")
        #4. create the image
        createImage(name, currency, price, width, height)
        #5. send price to blockclock
        blockclockReport(name, currency, price)
    else:
        print(f"There were no entries found in {newestfile}")


if __name__ == '__main__':
    # Defaults
    configFile="/home/nodeyez/nodeyez/config/gasprice.json"
    outputFile="/home/nodeyez/nodeyez/imageoutput/gasprice.png"
    dataDirectory="/home/nodeyez/nodeyez/data/"
    dataCountry="USA"
    dataState="California"
    randomCountry=True
    randomState=True
    blockclockEnabled=False
    blockclockAddress="21.21.21.21"
    blockclockPassword=""
    width=480
    height=320
    sleepInterval=3600
    colorTextGas=ImageColor.getrgb("#e69138")
    colorTextLocation=ImageColor.getrgb("#f1c232")
    colorTextPrice=ImageColor.getrgb("#6aa84f")
    colorBackground=ImageColor.getrgb("#602060")
    # Override config
    if os.path.exists(configFile):
        with open(configFile) as f:
            config = json.load(f)
        if "gasprice" in config:
            config = config["gasprice"]
        if "outputFile" in config:
            outputFile = config["outputFile"]
        if "dataDirectory" in config:
            dataDirectory = config["dataDirectory"]
        if "dataCountry" in config:
            dataCountry = config["dataCountry"]
        if "dataState" in config:
            dataState = config["dataState"]
        if "randomCountry" in config:
            randomCountry = config["randomCountry"]
        if "randomState" in config:
            randomState = config["randomState"]
        if "blockclockEnabled" in config:
            blockclockEnabled = config["blockclockEnabled"]
        if "blockclockAddress" in config:
            blockclockAddress = config["blockclockAddress"]
        if "blockclockPassword" in config:
            blockclockPassword = config["blockclockPassword"]
        if "width" in config:
            width = int(config["width"])
        if "height" in config:
            height = int(config["height"])
        if "sleepInterval" in config:
            sleepInterval = int(config["sleepInterval"])
        if "colorTextGas" in config:
            colorTextGas = ImageColor.getrgb(config["colorTextGas"])
        if "colorTextLocation" in config:
            colorTextLocation = ImageColor.getrgb(config["colorTextLocation"])
        if "colorTextPrice" in config:
            colorTextPrice = ImageColor.getrgb(config["colorTextPrice"])
        if "colorBackground" in config:
            colorBackground = ImageColor.getrgb(config["colorBackground"])
    else:
        print(f"Config file not found. Using defaults")
    # Data directories
    if not os.path.exists(dataDirectory):
        os.makedirs(dataDirectory)
    # Check for single run
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h','--help']:
            print(f"Generates a simple output of the average price of gas for a state or privince in the US or Canada")
            print(f"Usage:")
            print(f"1) Call without arguments to run continuously using the configuration or defaults")
            print(f"2) Pass an argument other than -h or --help to run once and exit")
            print(f"You may specify a custom configuration file at {configFile}")
        else:
            processdata(width,height)
        exit(0)
    # Loop
    while True:
        processdata(width,height)
        time.sleep(sleepInterval)
