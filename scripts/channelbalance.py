#! /usr/bin/env python3
from datetime import datetime, timedelta
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

def createimage(node, channels, firstidx, lastidx, pagenum, pageSize, width=480, height=320):
    global outputFile, colorTextFG, colorNodeOffline, colorNodeDead, colorBackground, colorBarOutline, colorBarFilled
    global colorBarEmpty, displayBalances, sleepInterval, headerText
    utcnow = datetime.utcnow()
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
    vicarioustext.drawcenteredtext(draw, headerText, 24, int(width/2), int(padtop/2), colorTextFG, True)
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
    #print(f"channels:  \n\n{channels}")
    for channelidx in range(firstidx, (lastidx+1)):
        linesdrawn = linesdrawn + 1
        currentchannel = channels[channelidx]
        remote_pubkey = currentchannel["remote_pubkey"]
        capacity = int(currentchannel["capacity"])
        local_balance = int(currentchannel["local_balance"])
        remote_balance = int(currentchannel["remote_balance"])
        commit_fee = int(currentchannel["commit_fee"])
        isactive = currentchannel["active"]
        if isactive:
            remotealias = vicariousbitcoin.getnodealiasfrompubkeyrest(remote_pubkey, node)
            nodecolor = colorTextFG
        else:
            remoteinfo = vicariousbitcoin.getnodeinforest(remote_pubkey, node)
            nodecolor = colorNodeOffline
            remotealias = remoteinfo["node"]["alias"]
            remoteupdated = remoteinfo["node"]["last_update"]
            remoteupdateddate = datetime.fromtimestamp(remoteupdated)
            csvdelay = int(currentchannel["csv_delay"])
            daysold = utcnow - remoteupdateddate
            csvrisk = (daysold.days * 144) > csvdelay
            csvrisks = "-risk" if csvrisk else ""
            remotealias = "(" + str(daysold.days) + "d" + csvrisks + ")" + remotealias
            if daysold.days >= 5 or csvrisk:
                nodecolor = colorNodeDead
        datarowbottom = padtop + (linesdrawn * dataheight)
        datarowtop = datarowbottom - dataheight
        datarowtop = padtop + (linesdrawn * dataheight)
        datarowbottom = datarowtop + dataheight
        vicarioustext.drawlefttext(draw, remotealias, nodefontsize, 0, datarowbottom - (dataheight/2), nodecolor)
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
    print(f"saving image for page {pagenum} of {headerText}")
    im.save(pageoutputFile)
    im.close()

def overrideFromConfig(d):
    global outputFile, colorTextFG, colorNodeOffline, colorNodeDead, colorBackground, colorBarOutline, colorBarFilled
    global colorBarEmpty, displayBalances, width, height, sleepInterval, pageSize, headerText
    if "outputFile" in d:
        outputFile = d["outputFile"]
    if "colorTextFG" in d:
        colorTextFG = ImageColor.getrgb(d["colorTextFG"])
    if "colorNodeOffline" in d:
        colorNodeOffline = ImageColor.getrgb(d["colorNodeOffline"])
    if "colorNodeDead" in d:
        colorNodeDead = ImageColor.getrgb(d["colorNodeDead"])
    if "colorBackground" in d:
        colorBackground = ImageColor.getrgb(d["colorBackground"])
    if "colorBarOutline" in d:
        colorBarOutline = ImageColor.getrgb(d["colorBarOutline"])
    if "colorBarFilled" in d:
        colorBarFilled = ImageColor.getrgb(d["colorBarFilled"])
    if "colorBarEmpty" in d:
        colorBarEmpty = ImageColor.getrgb(d["colorBarEmpty"])
    if "displayBalances" in d:
        displayBalances = d["displayBalances"]
    if "width" in d:
        width = int(d["width"])
    if "height" in d:
        height = int(d["height"])
    if "sleepInterval" in d:
        sleepInterval = int(d["sleepInterval"])
        sleepInterval = 300 if sleepInterval < 300 else sleepInterval # minimum 5 minutes, access others
    if "pageSize" in d:
        pageSize = int(d["pageSize"])
    if "headerText" in d:
        headerText = d["headerText"]

def setDefaults():
    global outputFile, colorTextFG, colorNodeOffline, colorNodeDead, colorBackground, colorBarOutline, colorBarFilled
    global colorBarEmpty, displayBalances, width, height, sleepInterval, pageSize, headerText
    outputFile = "../imageoutput/channelbalance.png"
    colorTextFG=ImageColor.getrgb("#ffffff")
    colorNodeOffline=ImageColor.getrgb("#ffa500")
    colorNodeDead=ImageColor.getrgb("#ff0000")
    colorBackground=ImageColor.getrgb("#000000")
    colorBarOutline=ImageColor.getrgb("#808080")
    colorBarFilled=ImageColor.getrgb("#008000")
    colorBarEmpty=ImageColor.getrgb("#ffa500")
    displayBalances=True
    width=480
    height=320
    sleepInterval=1800
    pageSize=8
    headerText="Lightning Channel Balances"

if __name__ == '__main__':
    # Defaults
    setDefaults()
    # Override config
    configFile = "../config/channelbalance.json"
    if exists(configFile):
        with open(configFile) as f:
            config = json.load(f)
        if "channelbalance" in config:
            config = config["channelbalance"]
        overrideFromConfig(config)
    else:
        config = {}
    # Check for single run
    if len(sys.argv) > 1:
        print(f"Generates one or more images based on the total number of lightning channels this node has.")
        print(f"A series of images depicting the balance on each side of the channel for local and remote.")
        print(f"Usage:")
        print(f"1) Call without arguments to run continuously using the configuration or defaults")
        print(f"You may specify a custom configuration file at {configFile}")
    # Loop
    while True:
        if "nodes" not in config:
            config["nodes"] = [{}] # empty node definition falls back to lncli
        nodes = config["nodes"]
        for node in nodes:
            if "enabled" in node:
                if not node["enabled"]:
                    continue
            setDefaults()              # reassign defaults
            overrideFromConfig(config) # overlay configurable defaults
            overrideFromConfig(node)   # overlay node specific
            channels = vicariousbitcoin.getnodechannelsrest(node)
            if "channels" in channels:
                channels = channels["channels"]
                channelcount = len(channels)
                pages = int(math.ceil(float(channelcount) / float(pageSize)))
                clearOldImages(pages)
                for pagenum in range(1, (pages+1)):
                    firstidx = ((pagenum-1)*pageSize)
                    lastidx = (pagenum*pageSize)-1
                    if lastidx > channelcount-1:
                        lastidx = channelcount-1
                    createimage(node, channels, firstidx, lastidx, pagenum, pageSize, width, height)
            else:
                print(f"SKIPPING image creation for this node. Received unexpected response\n\nresponse: {channels}\n\nnode: {node}")
        if len(sys.argv) > 1:
            exit(0)
        print(f"sleeping for {sleepInterval} seconds")
        time.sleep(sleepInterval)
