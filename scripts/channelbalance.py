#! /usr/bin/python3
from PIL import Image, ImageDraw, ImageColor
from os.path import exists
import glob
import json
import math
import os
import sys
import time
import vicariousbitcoin
import vicarioustext

def clearOldImages(pages):
    # find all images matching 
    imageMask = outputFile.replace(".png", "-*.png")
    files=glob.glob(imageMask)
    for filename in files:
        fileisgood = False
        for checkfilenumber in range(pages):
            checkfilename = outputFile.replace(".png","-" + str(checkfilenumber+1) + ".png")
            if checkfilename == filename:
                #print(f"file {filename} is ok to keep")
                fileisgood = True
        if not fileisgood:
            print(f"file {filename} is no longer needed and will be deleted")
            os.remove(filename)

def createimage(channels, firstidx, lastidx, pagenum, pageSize, width=480, height=320):
    padding=4
    outlinewidth=2
    padtop = 40
    padbottom = 40
    aliaswidth = width/3
    dataheight = int(math.floor((height - (padtop+padbottom)) / pageSize))
    im = Image.new(mode="RGB", size=(width, height))
    draw = ImageDraw.Draw(im)
    pageoutputFile = outputFile.replace(".png","-" + str(pagenum) + ".png")
    # Header
    vicarioustext.drawcenteredtext(draw, "Lightning Channel Balances", 24, int(width/2), int(padtop/2), colorTextFG, True)
    # Channel info
    linesdrawn = 0
    for channelidx in range(firstidx, (lastidx+1)):
        linesdrawn = linesdrawn + 1
        currentchannel = channels[channelidx]
        remote_pubkey = currentchannel["remote_pubkey"]
        capacity = int(currentchannel["capacity"])
        local_balance = int(currentchannel["local_balance"])
        remote_balance = int(currentchannel["remote_balance"])
        commit_fee = int(currentchannel["commit_fee"])
        alias = vicariousbitcoin.getnodealiasfrompubkey(remote_pubkey)
        datarowbottom = padtop + (linesdrawn * dataheight)
        datarowtop = datarowbottom - dataheight
        vicarioustext.drawbottomlefttext(draw, alias, 16, 0, datarowbottom, colorTextFG)
        draw.rounded_rectangle(xy=(aliaswidth,datarowtop+padding,width,datarowbottom),radius=4,fill=colorBackground,outline=colorBarOutline,width=outlinewidth)
        percentage = float(local_balance)/float(capacity)
        barwidth = int(math.floor(float(width-aliaswidth)*percentage))
        draw.rounded_rectangle(xy=(aliaswidth+outlinewidth,datarowtop+padding+outlinewidth,aliaswidth+outlinewidth+barwidth,datarowbottom-outlinewidth),radius=4,fill=colorBarFilled)
    draw.rectangle(xy=(aliaswidth-padding,padtop,aliaswidth-1,height-padbottom),fill=colorBackground)
    # Page Info
    channelcount = len(channels)
    pages = int(math.ceil(float(channelcount) / float(pageSize)))
    paging = str(pagenum) + "/" + str(pages)
    vicarioustext.drawbottomlefttext(draw, paging, 24, 0, height, colorTextFG)
    # Date and Time
    dt = "as of " + vicarioustext.getdateandtime()
    vicarioustext.drawbottomrighttext(draw, dt, 12, width, height, colorTextFG)
    # Save to file
    im.save(pageoutputFile)

if __name__ == '__main__':
    # Defaults
    configFile = "/home/bitcoin/nodeyez/config/channelbalance.json"
    outputFile = "/home/bitcoin/images/channelbalance.png"
    colorTextFG=ImageColor.getrgb("#ffffff")
    colorBackground=ImageColor.getrgb("#000000")
    colorBarOutline=ImageColor.getrgb("#770044")
    colorBarFilled=ImageColor.getrgb("#aa3377")
    sleepInterval=1800
    pageSize=8
    # Override config
    if exists(configFile):
        with open(configFile) as f:
            config = json.load(f)
        if "channelbalance" in config:
            config = config["channelbalance"]
        if "outputFile" in config:
            outputFile = config["outputFile"]
        if "colorTextFG" in config:
            colorTextFG = ImageColor.getrgb(config["colorTextFG"])
        if "colorBackground" in config:
            colorBackground = ImageColor.getrgb(config["colorBackground"])
        if "colorBarOutline" in config:
            colorBarOutline = ImageColor.getrgb(config["colorBarOutline"])
        if "colorBarFilled" in config:
            colorBarFilled = ImageColor.getrgb(config["colorBarFilled"])
        if "sleepInterval" in config:
            sleepInterval = int(config["sleepInterval"])
            sleepInterval = 300 if sleepInterval < 300 else sleepInterval # minimum 5 minutes, access others
        if "pageSize" in config:
            pageSize = int(config["pageSize"])
    # Check for single run
    if len(sys.argv) > 1:
        print(f"Generates one or more images based on the total number of lightning channels this node has.")
        print(f"A series of images depicting the balance on each side of the channel for local and remote.")
        print(f"Usage:")
        print(f"1) Call without arguments to run continuously using the configuration or defaults")
        print(f"You may specify a custom configuration file at {configFile}")
        exit(0)
    # Loop
    while True:
        channels = vicariousbitcoin.getnodechannels()
        channels = channels["channels"]
        channelcount = len(channels)
        pages = int(math.ceil(float(channelcount) / float(pageSize)))
        clearOldImages(pages)
        for pagenum in range(1, (pages+1)):
            firstidx = ((pagenum-1)*pageSize)
            lastidx = (pagenum*pageSize)-1
            if lastidx > channelcount-1:
                lastidx = channelcount-1
            createimage(channels, firstidx, lastidx, pagenum, pageSize)
        time.sleep(sleepInterval)
