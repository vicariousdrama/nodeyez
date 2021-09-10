#! /usr/bin/python3
from datetime import datetime
from PIL import Image, ImageFilter, ImageDraw, ImageFont, ImageColor
import json
import math
import subprocess
import time

outputFile = "/home/admin/images/channelbalance.png"
colorFFFFFF=ImageColor.getrgb("#ffffff")
colorBackground=ImageColor.getrgb("#000000")
colorBarOutline=ImageColor.getrgb("#770044")
colorBarFilled=ImageColor.getrgb("#aa3377")
fontDeja12=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",12)
fontDeja16=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",16)
fontDeja24=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",24)
fontDeja48=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",48)

def getdateandtime():
    now = datetime.utcnow()
    return now.strftime("%Y-%m-%d %H:%M:%S")

def getnodeinfo(pubkey):
    cmd = "lncli getnodeinfo --pub_key " + pubkey + " --include_channels 2>&1"
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
    except subprocess.CalledProcessError as e:
        cmdoutput = "{\"node\":{\"alias\":\"" + pubkey + "\",\"pub_key\":\"" + pubkey + "\",\"addresses\":[{\"network\":\"tcp\",\"addr\":\"0.0.0.0:65535\"}]}}"
    j = json.loads(cmdoutput)
    return j

def getnodealias(nodeinfo):
    return nodeinfo["node"]["alias"]

def getnodechannels():
    cmd = "lncli listchannels 2>&1"
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
    except subprocess.CalledProcessError as e:
        cmdoutput = '{\"channels\": []}'
    j = json.loads(cmdoutput)
    return j

def getdefaultaliasfrompubkey(pubkey):
    return pubkey[0:10]

pubkey_alias = {'pubkey':'alias'}
def getnodealiasfrompubkey(pubkey):
    alias = getdefaultaliasfrompubkey(pubkey)
    if pubkey in pubkey_alias.keys():
        alias = pubkey_alias[pubkey]
        if len(alias) < 1:
            alias = getdefaultaliasfrompubkey(pubkey)
    else:
        nodeinfo = getnodeinfo(pubkey)
        alias = getnodealias(nodeinfo)
        pubkey_alias[pubkey] = alias
    return alias

def getfont(size):
    if size == 12:
        return fontDeja12
    if size == 16:
        return fontDeja16
    if size == 24:
        return fontDeja24
    if size == 48:
        return fontDeja48

def drawcenteredtext(draw, s, fontsize, x, y, textcolor=colorFFFFFF):
    thefont = getfont(fontsize)
    sw,sh = draw.textsize(s, thefont)
    ox,oy = thefont.getoffset(s)
    sw += ox
    sh += oy
    draw.text(xy=(x-(sw/2),y-(sh/2)), text=s, font=thefont, fill=textcolor)

def drawbottomlefttext(draw, s, fontsize, x, y, textcolor=colorFFFFFF):
    thefont = getfont(fontsize)
    sw,sh = draw.textsize(s, thefont)
    ox,oy = thefont.getoffset(s)
    sw += ox
    sh += oy
    draw.text(xy=(x,y-sh), text=s, font=thefont, fill=textcolor)

def drawbottomrighttext(draw, s, fontsize, x, y, textcolor=colorFFFFFF):
    thefont = getfont(fontsize)
    sw,sh = draw.textsize(s, thefont)
    ox,oy = thefont.getoffset(s)
    sw += ox
    sh += oy
    draw.text(xy=(x-sw,y-sh), text=s, font=thefont, fill=colorFFFFFF)

def drawtoplefttext(draw, s, fontsize, x, y, textcolor=colorFFFFFF):
    thefont = getfont(fontsize)
    sw,sh = draw.textsize(s, thefont)
    ox,oy = thefont.getoffset(s)
    sw += ox
    sh += oy
    draw.text(xy=(x,y), text=s, font=thefont, fill=textcolor)

def drawtoprighttext(draw, s, fontsize, x, y, textcolor=colorFFFFFF):
    thefont = getfont(fontsize)
    sw,sh = draw.textsize(s, thefont)
    ox,oy = thefont.getoffset(s)
    sw += ox
    sh += oy
    draw.text(xy=(x-sw,y), text=s, font=thefont, fill=textcolor)

def createimage(channels, firstidx, lastidx, pagenum, pagesize, width=480, height=320):
    padding=4
    outlinewidth=2
    padtop = 40
    padbottom = 40
    aliaswidth = width/3
    dataheight = int(math.floor((height - (padtop+padbottom)) / pagesize))
    im = Image.new(mode="RGB", size=(width, height))
    draw = ImageDraw.Draw(im)
    pageoutputFile = ("-" + str(pagenum) + ".").join(outputFile.rsplit(".", 1))
    # Header
    drawcenteredtext(draw, "Lightning Channel Balances", 24, int(width/2), int(padtop/2))
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
        alias = getnodealiasfrompubkey(remote_pubkey)
        datarowbottom = padtop + (linesdrawn * dataheight)
        datarowtop = datarowbottom - dataheight
        drawbottomlefttext(draw, alias, 16, 0, datarowbottom)
        draw.rounded_rectangle(xy=(aliaswidth,datarowtop+padding,width,datarowbottom),radius=4,fill=colorBackground,outline=colorBarOutline,width=outlinewidth)
        percentage = float(local_balance)/float(capacity)
        barwidth = int(math.floor(float(width-aliaswidth)*percentage))
        draw.rounded_rectangle(xy=(aliaswidth+outlinewidth,datarowtop+padding+outlinewidth,aliaswidth+outlinewidth+barwidth,datarowbottom-outlinewidth),radius=4,fill=colorBarFilled)
    draw.rectangle(xy=(aliaswidth-padding,padtop,aliaswidth-1,height-padbottom),fill=colorBackground)
    # Page Info
    channelcount = len(channels)
    pages = int(math.ceil(float(channelcount) / float(pagesize)))
    paging = str(pagenum) + "/" + str(pages)
    drawbottomlefttext(draw, paging, 24, 0, height)
    # Date and Time
    dt = "as of " + getdateandtime()
    drawbottomrighttext(draw, dt, 12, width, height)
    # Save to file
    im.save(pageoutputFile)


while True:
    channels = getnodechannels()
    channels = channels["channels"]
    channelcount = len(channels)
    pagesize = 8
    pages = int(math.ceil(float(channelcount) / float(pagesize)))
    for pagenum in range(1, (pages+1)):
        firstidx = ((pagenum-1)*pagesize)
        lastidx = (pagenum*pagesize)-1
        if lastidx > channelcount-1:
            lastidx = channelcount-1
        createimage(channels, firstidx, lastidx, pagenum, pagesize)
    time.sleep(1800)
