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

def drawcenteredtext(draw, s, fontsize, x, y):
    thefont = getfont(fontsize)
    sw,sh = draw.textsize(s, thefont)
    ox,oy = thefont.getoffset(s)
    sw += ox
    sh += oy
    draw.text(xy=(x-(sw/2),y-(sh/2)), text=s, font=thefont, fill=colorFFFFFF)

def drawbottomlefttext(draw, s, fontsize, x, y):
    thefont = getfont(fontsize)
    sw,sh = draw.textsize(s, thefont)
    ox,oy = thefont.getoffset(s)
    sw += ox
    sh += oy
    draw.text(xy=(x,y-sh), text=s, font=thefont, fill=colorFFFFFF)

def drawbottomrighttext(draw, s, fontsize, x, y):
    thefont = getfont(fontsize)
    sw,sh = draw.textsize(s, thefont)
    ox,oy = thefont.getoffset(s)
    sw += ox
    sh += oy
    draw.text(xy=(x-sw,y-sh), text=s, font=thefont, fill=colorFFFFFF)

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
    return int(epochnum * 2016)

def getcurrenttimeinseconds():
    cmd = "date +%s"
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
    nextadjustment = str(float("%.2f" % (((float(blocksmined) / float(expectedmined)) - 1.0) * 100)))
    if "-" not in nextadjustment:
        nextadjustment = "+" + nextadjustment
    blockw=int(math.floor(width/63))
    padleft=int(math.floor((width-(63*blockw))/2))
    padtop=40
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
    drawcenteredtext(draw, "Expected: " + str(expectedmined), 18, int(width/6*1), height-padtop)
    drawcenteredtext(draw, "Mined: " + str(blocksmined), 18, int(width/6*3), height-padtop)
    drawcenteredtext(draw, "Retarget: " + str(nextadjustment), 18, int(width/6*5), height-padtop)
    drawbottomrighttext(draw, "as of " + getdateandtime(), 12, width, height)
    im.save(outputFile)

while True:
    createimage()
    time.sleep(600)
