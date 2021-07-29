from datetime import datetime
from PIL import Image, ImageFilter, ImageDraw, ImageFont, ImageColor
import json
import math
import subprocess
import time

priceurl="https://bisq.markets/bisq/api/markets/ticker"
outputFile="/home/admin/images/satsperusd.png"
color40FF40=ImageColor.getrgb("#40FF40")
color000000=ImageColor.getrgb("#000000")
colorFFFFFF=ImageColor.getrgb("#ffffff")
fontDeja12=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",12)
fontDeja16=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",16)
fontDeja20=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",20)
fontDeja24=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",24)

def drawsatssquare(draw,dc,dr,spf,satw,bpx,bpy):
    satsleft = spf
    for y in range(10):
        for x in range(10):
            if satsleft > 0:
                tlx = (bpx + (dc*11*satw) + (x*satw))
                tly = (bpy + (dr*11*satw) + (y*satw))
                brx = tlx+satw-2
                bry = tly+satw-2
                draw.rectangle(xy=((tlx,tly),(brx,bry)),fill=color40FF40)
            satsleft = satsleft - 1

def getdateandtime():
    now = datetime.utcnow()
    return now.strftime("%Y-%m-%d %H:%M:%S")
def getfont(size):
    if size == 12:
        return fontDeja12
    if size == 16:
        return fontDeja16
    if size == 20:
        return fontDeja20
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
    draw.text(xy=(x-sw,y-sh), text=s, font=thefont, fill=textcolor)

def createimage(width=480, height=320):
    last,high,low = getpriceinfo()
    satsperfiatunit = int(round(100000000.0 / last))
    satw=int(math.floor(width/87))
    padleft=int(math.floor((width-(87*satw))/2))
    padtop=40
    im = Image.new(mode="RGB", size=(width, height))
    draw = ImageDraw.Draw(im)
    dc = 0
    dr = 0
    while satsperfiatunit > 100:
        satsperfiatunit = satsperfiatunit - 100
        drawsatssquare(draw,dc,dr,100,satw,padleft,padtop)
        dc = dc + 1
        if dc >= 8:
            dr = dr + 1
            dc = 0
    drawsatssquare(draw,dc,dr,satsperfiatunit,satw,padleft,padtop)
    drawcenteredtext(draw, "Sats Per USD", 24, int(width/2), int(padtop/2))
    satsperfiatunit = int(round(100000000.0 / last))
    drawcenteredtext(draw, "Last: " + str(satsperfiatunit), 20, int(width/8*4), height-padtop)
    satsperfiatunit = int(round(100000000.0 / low))
    drawcenteredtext(draw, "High: " + str(satsperfiatunit), 20, int(width/8*7), height-padtop)
    satsperfiatunit = int(round(100000000.0 / high))
    drawcenteredtext(draw, "Low: " + str(satsperfiatunit), 20, int(width/8*1), height-padtop)
    drawbottomlefttext(draw, "Market data by bisq", 16, 0, height, color40FF40)
    drawbottomrighttext(draw, "as of " + getdateandtime(), 12, width, height)
    im.save(outputFile)

def getpriceinfo():
    cmd = "torify curl --silent " + priceurl
    last = 1
    high = 1
    low = 1
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
        j = json.loads(cmdoutput)
        last = int(math.floor(float(j["btc_usd"]["last"])))
        high = int(math.floor(float(j["btc_usd"]["high"])))
        low = int(math.floor(float(j["btc_usd"]["low"])))
    except subprocess.CalledProcessError as e:
        cmdoutput = "{\"error\":  }"
    return (last,high,low)

while True:
    createimage()
    time.sleep(3600)
