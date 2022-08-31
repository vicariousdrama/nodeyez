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

def sumchannelfees(fwdinghistory, chan_id):
    match_event_count = 0
    match_total_fees = 0
    events = fwdinghistory["forwarding_events"]
    for event in events:
        chan_id_out = event["chan_id_out"]
        if str(chan_id_out) == str(chan_id):
            match_event_count = match_event_count + 1
            event_fee = int(event["fee"])
            match_total_fees = match_total_fees + event_fee
    return match_event_count, match_total_fees

def createimage(channels, firstidx, lastidx, pagenum, pageSize, fwdinghistory, width=480, height=320):
    padding=4
    outlinewidth=2
    padtop = 60
    padbottom = 40
    aliaswidth = width/3
    dataheight = int(math.floor((height - (padtop+padbottom)) / pageSize))
    im = Image.new(mode="RGB", size=(width, height), color=colorBackground)
    draw = ImageDraw.Draw(im)
    pageoutputFile = outputFile.replace(".png","-" + str(pagenum) + ".png")
    # Headers
    vicarioustext.drawcenteredtext(draw, "Channel Usage & Fees", 24, int(width/2), int(padbottom/2), colorTextFG, True)
    centery = padtop - 10
    vicarioustext.drawlefttext(draw, "Peer Alias", 14, 0, centery, colorTextFG, True)
    centerx = int(aliaswidth) + int(aliaswidth/4)
    vicarioustext.drawcenteredtext(draw, "Received", 14, centerx, centery, colorTextFG, True)
    centerx = int(aliaswidth) + int(aliaswidth/4*3)
    vicarioustext.drawcenteredtext(draw, "Sent", 14, centerx, centery, colorTextFG, True)
    centerx = int(aliaswidth*2) + int(aliaswidth/4)
    vicarioustext.drawcenteredtext(draw, "# Events", 14, centerx, centery, colorTextFG, True)
    centerx = int(aliaswidth*2) + int(aliaswidth/4*3)
    vicarioustext.drawcenteredtext(draw, "Earned", 14, centerx, centery, colorTextFG, True)
    # Channel info
    linesdrawn = 0
    for channelidx in range(firstidx, (lastidx+1)):
        linesdrawn = linesdrawn + 1
        currentchannel = channels[channelidx]
        chan_id = currentchannel["chan_id"]
        remote_pubkey = currentchannel["remote_pubkey"]
        capacity = int(currentchannel["capacity"])
        total_satoshis_sent = int(currentchannel["total_satoshis_sent"])
        total_satoshis_received = int(currentchannel["total_satoshis_received"])
        sent_ratio = str(int((float(total_satoshis_sent) / float(capacity)) * 100)) + "%"
        receive_ratio = str(int((float(total_satoshis_received) / float(capacity)) * 100)) + "%"
        event_count, fees_collected = sumchannelfees(fwdinghistory, chan_id)
        alias = vicariousbitcoin.getnodealiasfrompubkey(remote_pubkey)
        datarowbottom = padtop + (linesdrawn * dataheight)
        datarowtop = datarowbottom - dataheight
        centery = datarowtop + int(dataheight/2)
        vicarioustext.drawlefttext(draw, alias, 14, 0, centery, colorTextFG)
        draw.rectangle(xy=(aliaswidth,datarowtop,width,datarowbottom),fill=colorBackground)
        centerx = int(aliaswidth) + int(aliaswidth/4)
        vicarioustext.drawcenteredtext(draw, receive_ratio, 14, centerx, centery, colorTextFG)
        centerx = int(aliaswidth) + int(aliaswidth/4*3)
        vicarioustext.drawcenteredtext(draw, sent_ratio, 14, centerx, centery, colorTextFG)
        centerx = int(aliaswidth*2) + int(aliaswidth/4)
        vicarioustext.drawcenteredtext(draw, str(event_count), 14, centerx, centery, colorTextFG)
        centerx = int(aliaswidth*2) + int(aliaswidth/4*3)
        vicarioustext.drawcenteredtext(draw, str(fees_collected), 14, centerx, centery, colorTextFG)
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
    im.close()

if __name__ == '__main__':
    # Defaults
    configFile = "/home/nodeyez/nodeyez/config/channelfees.json"
    outputFile = "/home/nodeyez/nodeyez/imageoutput/channelfees.png"
    colorTextFG=ImageColor.getrgb("#ffffff")
    colorBackground=ImageColor.getrgb("#000000")
    width=480
    height=320
    sleepInterval=1800
    pageSize=12
    # Override config
    if exists(configFile):
        with open(configFile) as f:
            config = json.load(f)
        if "channelfees" in config:
            config = config["channelfees"]
        if "outputFile" in config:
            outputFile = config["outputFile"]
        if "colorTextFG" in config:
            colorTextFG = ImageColor.getrgb(config["colorTextFG"])
        if "colorBackground" in config:
            colorBackground = ImageColor.getrgb(config["colorBackground"])
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
        print(f"A series of images depicting the ratio of value received and sent compared to channel capacity, number of forwarding events and fees collected.")
        print(f"Usage:")
        print(f"1) Call without arguments to run continuously using the configuration or defaults")
        print(f"You may specify a custom configuration file at {configFile}")
        exit(0)
    # Loop
    while True:
        fwdinghistory = vicariousbitcoin.getfwdinghistory()
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
            createimage(channels, firstidx, lastidx, pagenum, pageSize, fwdinghistory, width, height)
        time.sleep(sleepInterval)
