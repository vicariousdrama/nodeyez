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

def sumchannelearnings(fwdinghistory, chan_id):
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

def sumchannelpayments(paymenthistory, chan_id):
    paycount = 0
    payfees = 0
    payments = paymenthistory["payments"]
    for payment in payments:
        if "status" in payment:
            if payment["status"] == "SUCCEEDED":
                if "htlcs" in payment:
                    htlcs = payment["htlcs"]
                    for htlc in htlcs:
                        if "route" in htlc:
                            route = htlc["route"]
                            if "hops" in route:
                                hops = route["hops"]
                                if len(hops) > 0:
                                    firsthop = hops[0]
                                    if "chan_id" in firsthop:
                                        hopchan_id = firsthop["chan_id"]
                                        if str(chan_id) == str(hopchan_id):
                                            paycount += 1
                                            fee = 0
                                            if "fee" in payment:
                                               fee = payment["fee"]
                                            payfees += int(fee)
#    print(f"For chan_id: {chan_id}, total payments: {paycount}, fees paid: {payfees}")
    return paycount, payfees

def createimage(channels, firstidx, lastidx, pagenum, pageSize, fwdinghistory, paymenthistory, width=480, height=320):
    utcnow = datetime.utcnow()
    padding=4
    outlinewidth=2
    padtop = 40
    padbottom = 40
    aliaswidth = width/3
    dataheight = int(math.floor((height - (padtop+padbottom)) / (pageSize + 1)))
    im = Image.new(mode="RGB", size=(width, height), color=colorBackground)
    draw = ImageDraw.Draw(im)
    pageoutputFile = outputFile.replace(".png","-" + str(pagenum) + ".png")
    # Headers
    vicarioustext.drawcenteredtext(draw, "Channel Usage, Fees and Earnings", 24, int(width/2), int(padbottom/2), colorTextFG, True)
    thfontsize = int(dataheight / 3 * 2) - 2
    thfontsize -= (thfontsize %2)
    headery = padtop + int(thfontsize/2)
    headerx = 0
    vicarioustext.drawlefttext(draw, "Peer Alias", thfontsize, headerx, headery, colorTextFG, True)
    headerx = int(width * .44)
    vicarioustext.drawcenteredtext(draw, "Ratio", thfontsize, headerx, headery, colorTextFG, True)
    headerx = int(width * .66)
    vicarioustext.drawcenteredtext(draw, "Sends", thfontsize, headerx, headery, colorTextFG, True)
    headerx = int(width * .88)
    vicarioustext.drawcenteredtext(draw, "Forwards", thfontsize, headerx, headery, colorTextFG, True)
    headery += thfontsize
    thfontsize -= 1
    headerx = int(width * .385)
    vicarioustext.drawcenteredtext(draw, "Receive", thfontsize, headerx, headery, colorTextFG, True)
    headerx = int(width * .495)
    vicarioustext.drawcenteredtext(draw, "Sent", thfontsize, headerx, headery, colorTextFG, True)
    headerx = int(width * .605)
    vicarioustext.drawcenteredtext(draw, "#", thfontsize, headerx, headery, colorTextFG, True)
    headerx = int(width * .715)
    vicarioustext.drawcenteredtext(draw, "Fees", thfontsize, headerx, headery, colorTextFG, True)
    headerx = int(width * .825)
    vicarioustext.drawcenteredtext(draw, "#", thfontsize, headerx, headery, colorTextFG, True)
    headerx = int(width * .935)
    vicarioustext.drawcenteredtext(draw, "Earned", thfontsize, headerx, headery, colorTextFG, True)
    # Channel info
    nodefontsize = thfontsize - 1
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
        earncount, earnfees = sumchannelearnings(fwdinghistory, chan_id)
        paycount, payfees = sumchannelpayments(paymenthistory, chan_id)
        datarowtop = padtop + (linesdrawn * dataheight) + 2
        datarowbottom = datarowtop + dataheight
        colorRowBG = colorRowBG1 if (linesdrawn % 2 == 0) else colorRowBG2
        colorRowFG = colorRowFG1 if (linesdrawn % 2 == 0) else colorRowFG2
        isactive = currentchannel["active"]
        if isactive:
            remotealias = vicariousbitcoin.getnodealiasfrompubkey(remote_pubkey)
            nodecolor = colorRowFG
        else:
            remoteinfo = vicariousbitcoin.getnodeinfo(remote_pubkey)
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
        # write it out
        # - node alias
        draw.rectangle(xy=(0,datarowtop,width,datarowbottom),fill=colorRowBG)
        centery = datarowtop + int(dataheight/2)
        vicarioustext.drawlefttext(draw, remotealias, nodefontsize, 0, centery, nodecolor)
        draw.rectangle(xy=(aliaswidth,datarowtop,width,datarowbottom),fill=colorRowBG) # blanks out excess to the right
        # - ratio receive
        centerx = int(width * .40)
        vicarioustext.drawrighttext(draw, receive_ratio, nodefontsize, centerx, centery, colorRowFG)
        # - ratio sent
        centerx = int(width * .50)
        vicarioustext.drawrighttext(draw, sent_ratio, nodefontsize, centerx, centery, colorRowFG)
        # - send events
        if paycount > 0:
            centerx = int(width * .605)
            vicarioustext.drawcenteredtext(draw, str(paycount), nodefontsize, centerx, centery, colorRowFG)
        # - send fees
        if payfees > 0:
            centerx = int(width * .74)
            vicarioustext.drawrighttext(draw, str(payfees), nodefontsize, centerx, centery, colorRowFG)
        # - forward events
        if earncount > 0:
            centerx = int(width * .825)
            vicarioustext.drawcenteredtext(draw, str(earncount), nodefontsize, centerx, centery, colorRowFG)
        # - forward earned
        if earnfees > 0:
            centerx = int(width * .98)
            vicarioustext.drawrighttext(draw, str(earnfees), nodefontsize, centerx, centery, colorRowFG)
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
    configFile = "/home/nodeyez/nodeyez/config/channelfees.json"
    outputFile = "/home/nodeyez/nodeyez/imageoutput/channelfees.png"
    colorTextFG=ImageColor.getrgb("#ffffff")
    colorNodeOffline=ImageColor.getrgb("#ffa500")
    colorNodeDead=ImageColor.getrgb("#ff0000")
    colorBackground=ImageColor.getrgb("#000000")
    colorRowBG1=ImageColor.getrgb("#404040")
    colorRowBG2=ImageColor.getrgb("#202020")
    colorRowFG1=ImageColor.getrgb("#ffffff")
    colorRowFG2=ImageColor.getrgb("#ffffff")
    width=480
    height=320
    sleepInterval=1800
    pageSize=8
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
        if "colorNodeOffline" in config:
            colorNodeOffline = ImageColor.getrgb(config["colorNodeOffline"])
        if "colorNodeDead" in config:
            colorNodeDead = ImageColor.getrgb(config["colorNodeDead"])
        if "colorBackground" in config:
            colorBackground = ImageColor.getrgb(config["colorBackground"])
        if "colorRowBG1" in config:
            colorRowBG1 = ImageColor.getrgb(config["colorRowBG1"])
        if "colorRowBG2" in config:
            colorRowBG2 = ImageColor.getrgb(config["colorRowBG2"])
        if "colorRowFG1" in config:
            colorRowFG1 = ImageColor.getrgb(config["colorRowFG1"])
        if "colorRowFG2" in config:
            colorRowFG2 = ImageColor.getrgb(config["colorRowFG2"])
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
    # Loop
    while True:
        fwdinghistory = vicariousbitcoin.getfwdinghistory()
        paymenthistory = vicariousbitcoin.getnodepayments()
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
            createimage(channels, firstidx, lastidx, pagenum, pageSize, fwdinghistory, paymenthistory, width, height)
        if len(sys.argv) > 1:
            exit(0)
        print(f"sleeping for {sleepInterval} seconds")
        time.sleep(sleepInterval)
