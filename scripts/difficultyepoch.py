from datetime import datetime
from PIL import Image, ImageFilter, ImageDraw, ImageFont, ImageColor
import json
import math
import subprocess
import time

outputFile="/home/admin/images/difficultyepoch.png"
colorgrid=ImageColor.getrgb("#404040")
colorahead=ImageColor.getrgb("#FFFF40")
colorbehind=ImageColor.getrgb("#FF0000")
colormined=ImageColor.getrgb("#40FF40")
color000000=ImageColor.getrgb("#000000")
colorFFFFFF=ImageColor.getrgb("#ffffff")
fontDeja12=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",12)
fontDeja18=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",18)
fontDeja24=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",24)

def getdateandtime():
    now = datetime.utcnow()
    return now.strftime("%Y-%m-%d %H:%M:%S")

def getfont(size):
    if size == 12:
        return fontDeja12
    if size == 18:
        return fontDeja18
    if size == 24:
        return fontDeja24

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


def getcurrentblock():
    cmd = "bitcoin-cli getblockchaininfo"
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
        j = json.loads(cmdoutput)
        blockcurrent = int(j["blocks"])
        return blockcurrent
    except subprocess.CalledProcessError as e:
        print(e)
        return 1

def getepochnum(blocknum):
    return int(math.floor(blocknum / 2016))

def getfirstblockforepoch(blocknum):
    epochnum = getepochnum(blocknum)
    return int(epochnum * 2016) + 1

def getcurrenttimeinseconds():
    cmd = "date -u +%s"
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
        return int(cmdoutput)
    except subprocess.CalledProcessError() as e:
        print(e)
        return 1

def getblock(blocknum):
    cmd = "bitcoin-cli getblock `bitcoin-cli getblockhash " + str(blocknum) + "`"
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
        j = json.loads(cmdoutput)
        return j
    except subprocess.CalledProcessError() as e:
        print(e)
        fakejson = "{\"confirmations\": 1, \"time\": " + str(getcurrenttimeinseconds) + "\"}"
        return json.loads(fakejson)

def createimage(width=480, height=320):
    currentblock = getcurrentblock()
    j = getblock(getfirstblockforepoch(currentblock))
    blocksmined = int(j["confirmations"])
    timebegan = int(j["time"])
    timenow = getcurrenttimeinseconds()
    secondspassed = timenow - timebegan
    expectedmined = int(math.floor(secondspassed / 600))
    if blocksmined == 1:
        expectedmined = 1
    nextadjustment = "0.0"
    if float(expectedmined) > 0 and float(blocksmined) > 0:
        nextadjustment = str(float("%.2f" % (((float(blocksmined) / float(expectedmined)) - 1.0) * 100)))
    adjustcolor = colorbehind
    if "-" not in nextadjustment:
        nextadjustment = "+" + nextadjustment
        adjustcolor = colormined
    estimateepochend = timebegan + (2016*600)
    if float(blocksmined) > 0:
        estimateepochend = int(math.floor((float(secondspassed) / float(blocksmined))*2016)) + timebegan
    secondstoepochend = estimateepochend - timenow
    nextepochdesc = ""
    if blocksmined >= 10:
        if secondstoepochend > 86400:
            nextepochdays = math.floor(secondstoepochend / 86400)
            nextepochdesc = nextepochdesc + str(nextepochdays) + " day"
            if nextepochdays > 1:
                nextepochdesc = nextepochdesc + "s"
            secondstoepochend = secondstoepochend - (nextepochdays * 86400)
        if secondstoepochend > 3600:
            nextepochhours = math.floor(secondstoepochend / 3600)
            if nextepochdesc != "":
                nextepochdesc = nextepochdesc + ", "
            nextepochdesc = nextepochdesc + str(nextepochhours) + " hour"
            if nextepochhours > 1:
                nextepochdesc = nextepochdesc + "s"
            secondstoepochend = secondstoepochend - (nextepochhours * 3600)
        if (secondstoepochend > 600) and ("," not in nextepochdesc):
            nextepochminutes = math.floor(secondstoepochend / 60)
            if nextepochdesc != "":
                nextepochdesc = nextepochdesc + ", "
            nextepochdesc = nextepochdesc + str(nextepochminutes) + " minute"
            if nextepochminutes > 1:
                nextepochdesc = nextepochdesc + "s"
            secondstoepochend = secondstoepochend - (nextepochminutes * 60)
        else:
            if nextepochdesc == "":
                "a few minutes"
    else:
        nextepochdesc = "about 2 weeks"

    blockw=int(math.floor(width/63))
    padleft=int(math.floor((width-(63*blockw))/2))
    padtop=36
    im = Image.new(mode="RGB", size=(width, height))
    draw = ImageDraw.Draw(im)
    for dc in range(63):
        for dr in range(32):
            epochblocknum = ((dr*63) + dc)+1
            tlx = (padleft + (dc*blockw))
            tly = (padtop + (dr*blockw))
            brx = tlx+blockw-2
            bry = tly+blockw-2
            if epochblocknum <= blocksmined:
                fillcolor = colormined
                if epochblocknum > expectedmined:
                    fillcolor = colorahead
                draw.rectangle(xy=((tlx,tly),(brx,bry)),fill=fillcolor)
            else:
                outlinecolor = colorgrid
                if epochblocknum <= expectedmined:
                    outlinecolor = colorbehind
                draw.rectangle(xy=((tlx,tly),(brx,bry)),fill=None,outline=outlinecolor)
    drawcenteredtext(draw, "Blocks Mined This Difficulty Epoch", 24, int(width/2), int(padtop/2))
    drawtoprighttext(draw, "Expected: ", 18, int(width/4*1), height-56)
    drawtoplefttext(draw, str(expectedmined), 18, int(width/4*1), height-56)
    drawtoprighttext(draw, "Mined: ", 18, int(width/4*1), height-32)
    drawtoplefttext(draw, str(blocksmined), 18, int(width/4*1), height-32)
    drawtoprighttext(draw, "Retarget: ", 18, int(width/10*6), height-56)
    drawtoplefttext(draw, str(nextadjustment) + "%", 18, int(width/10*6), height-56, adjustcolor)
    drawtoprighttext(draw, "In: ", 18, int(width/10*6), height-32)
    drawtoplefttext(draw, str(nextepochdesc), 18, int(width/10*6), height-32)
    drawbottomrighttext(draw, "as of " + getdateandtime(), 12, width, height)
    im.save(outputFile)
    of2=outputFile.replace("/difficulty","/"+str(currentblock)+"-difficulty")
    im.save(of2)

while True:
    createimage()
    time.sleep(540)
