#! /usr/bin/env python3
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
    dataheight = int(math.floor((height - (padtop+padbottom)) / (pageSize+1)))
    im = Image.new(mode="RGB", size=(width, height), color=colorBackground)
    draw = ImageDraw.Draw(im)
    pageoutputFile = outputFile.replace(".png","-" + str(pagenum) + ".png")
    # Header
    vicarioustext.drawcenteredtext(draw, "Lightning Channel Balances", 24, int(width/2), int(padtop/2), colorTextFG, True)
    thfontsize = int(dataheight / 3 * 2) - 2
    thfontsize -= (thfontsize % 2)
    headery = padtop + int(thfontsize/2)
    headerx = 0
    vicarioustext.drawlefttext(draw, "Peer Alias", thfontsize, headerx, headery, colorTextFG, True)
    headerx = int(aliaswidth)
    vicarioustext.drawlefttext(draw, "Local Balance", thfontsize, headerx, headery, colorTextFG, True)
    headerx = width
    vicarioustext.drawrighttext(draw, "Remote Balance", thfontsize, headerx, headery, colorTextFG, True)
    # Channel info
    nodefontsize = thfontsize - 2
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
        datarowtop = padtop + (linesdrawn * dataheight)
        datarowbottom = datarowtop + dataheight
        vicarioustext.drawlefttext(draw, alias, nodefontsize, 0, datarowbottom - (dataheight/2), colorTextFG)
        draw.rounded_rectangle(xy=(aliaswidth,datarowtop+padding,width-outlinewidth,datarowbottom),radius=4,fill=colorBarEmpty,outline=colorBarOutline,width=outlinewidth)
        percentage = float(local_balance)/float(capacity)
        barwidth = int(math.floor(float(width-aliaswidth-outlinewidth)*percentage))
        draw.rounded_rectangle(xy=(aliaswidth+outlinewidth,datarowtop+padding+outlinewidth,aliaswidth+outlinewidth+barwidth,datarowbottom-outlinewidth),radius=3,fill=colorBarFilled)
        if displayBalances:
            vicarioustext.drawlefttext(draw, str(local_balance), nodefontsize, aliaswidth+outlinewidth+1, datarowtop + (dataheight/2) + outlinewidth + 1, colorBackground)
            vicarioustext.drawrighttext(draw, str(remote_balance), nodefontsize, width-outlinewidth-outlinewidth, datarowtop + (dataheight/2) + outlinewidth + 1, colorBackground)
            vicarioustext.drawlefttext(draw, str(local_balance), nodefontsize, aliaswidth+outlinewidth, datarowtop + (dataheight/2) + outlinewidth, colorTextFG)
            vicarioustext.drawrighttext(draw, str(remote_balance), nodefontsize, width-outlinewidth-outlinewidth-1, datarowtop + (dataheight/2) + outlinewidth, colorTextFG)
    draw.rectangle(xy=(aliaswidth-padding,padtop,aliaswidth-1,height-padbottom),fill=colorBackground)
    # Page Info
    channelcount = len(channels)
    pages = int(math.ceil(float(channelcount) / float(pageSize)))
    paging = str(pagenum) + "/" + str(pages)
    vicarioustext.drawbottomlefttext(draw, paging, 16, 0, height, colorTextFG)
    # Date and Time
    dt = "as of " + vicarioustext.getdateandtime()
    vicarioustext.drawbottomrighttext(draw, dt, 12, width, height, colorTextFG)
    # Save to file
    print(f"saving image for page {pagenum}")
    im.save(pageoutputFile)
    im.close()

if __name__ == '__main__':
    # Defaults
    configFile = "/home/nodeyez/nodeyez/config/channelbalance.json"
    outputFile = "/home/nodeyez/nodeyez/imageoutput/channelbalance.png"
    colorTextFG=ImageColor.getrgb("#ffffff")
    colorBackground=ImageColor.getrgb("#000000")
    colorBarOutline=ImageColor.getrgb("#808080")
    colorBarFilled=ImageColor.getrgb("#008000")
    colorBarEmpty=ImageColor.getrgb("#ffa500")
    displayBalances=True
    width=480
    height=320
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
        if "colorBarEmpty" in config:
            colorBarEmpty = ImageColor.getrgb(config["colorBarEmpty"])
        if "displayBalances" in config:
            displayBalances = config["displayBalances"]
        if "width" in config:
            width = int(config["width"])
        if "height" in config:
            height = int(config["height"])
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
            createimage(channels, firstidx, lastidx, pagenum, pageSize, width, height)
        if len(sys.argv) > 1:
            exit(0)
        time.sleep(sleepInterval)
