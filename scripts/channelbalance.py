#! /usr/bin/python3
from PIL import Image, ImageDraw, ImageColor
import glob
import math
import os
import time
import vicariousbitcoin
import vicarioustext

outputFile = "/home/bitcoin/images/channelbalance.png"
colorFFFFFF=ImageColor.getrgb("#ffffff")
colorBackground=ImageColor.getrgb("#000000")
colorBarOutline=ImageColor.getrgb("#770044")
colorBarFilled=ImageColor.getrgb("#aa3377")

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

def createimage(channels, firstidx, lastidx, pagenum, pagesize, width=480, height=320):
    padding=4
    outlinewidth=2
    padtop = 40
    padbottom = 40
    aliaswidth = width/3
    dataheight = int(math.floor((height - (padtop+padbottom)) / pagesize))
    im = Image.new(mode="RGB", size=(width, height))
    draw = ImageDraw.Draw(im)
    pageoutputFile = outputFile.replace(".png","-" + str(pagenum) + ".png")
    # Header
    vicarioustext.drawcenteredtext(draw, "Lightning Channel Balances", 24, int(width/2), int(padtop/2), colorFFFFFF, True)
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
        vicarioustext.drawbottomlefttext(draw, alias, 16, 0, datarowbottom)
        draw.rounded_rectangle(xy=(aliaswidth,datarowtop+padding,width,datarowbottom),radius=4,fill=colorBackground,outline=colorBarOutline,width=outlinewidth)
        percentage = float(local_balance)/float(capacity)
        barwidth = int(math.floor(float(width-aliaswidth)*percentage))
        draw.rounded_rectangle(xy=(aliaswidth+outlinewidth,datarowtop+padding+outlinewidth,aliaswidth+outlinewidth+barwidth,datarowbottom-outlinewidth),radius=4,fill=colorBarFilled)
    draw.rectangle(xy=(aliaswidth-padding,padtop,aliaswidth-1,height-padbottom),fill=colorBackground)
    # Page Info
    channelcount = len(channels)
    pages = int(math.ceil(float(channelcount) / float(pagesize)))
    paging = str(pagenum) + "/" + str(pages)
    vicarioustext.drawbottomlefttext(draw, paging, 24, 0, height)
    # Date and Time
    dt = "as of " + vicarioustext.getdateandtime()
    vicarioustext.drawbottomrighttext(draw, dt, 12, width, height)
    # Save to file
    im.save(pageoutputFile)


while True:
    channels = vicariousbitcoin.getnodechannels()
    channels = channels["channels"]
    channelcount = len(channels)
    pagesize = 8
    pages = int(math.ceil(float(channelcount) / float(pagesize)))
    clearOldImages(pages)
    for pagenum in range(1, (pages+1)):
        firstidx = ((pagenum-1)*pagesize)
        lastidx = (pagenum*pagesize)-1
        if lastidx > channelcount-1:
            lastidx = channelcount-1
        createimage(channels, firstidx, lastidx, pagenum, pagesize)
    time.sleep(1800)
