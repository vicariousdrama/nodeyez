#! /usr/bin/python3
from datetime import datetime
from PIL import Image, ImageFilter, ImageDraw, ImageFont, ImageColor
import json
import locale
import math
import subprocess
import time
import sys

outputFile="/home/bitcoin/images/arthash.png"
color000000=ImageColor.getrgb("#000000")
colorFFFFFF=ImageColor.getrgb("#ffffff")
fontDeja12=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",12)
fontDeja24=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",24)

def getdateandtime():
    now = datetime.utcnow()
    return now.strftime("%Y-%m-%d %H:%M:%S")
def getfont(size):
    if size == 12:
        return fontDeja12
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

def createimage(width=480, height=320, blocknumber=1):
    blockhash = getblockhash(blocknumber)
    outputFileBlock = outputFile.replace(".png","-" + str(blocknumber) + ".png")
    padtop=40
    # our art canvas and offsets
    artheight=200
    artwidth=200
    arttop=(height/2)-(artheight/2)
    artleft=(width/2)-(artwidth/2)
    lwidth=2
    outlinecolor=colorFFFFFF
    # basic pythagoras theorem math
    triclen=artwidth/4  # hypotenuese
    triblen=artwidth/8  # base
    trialen=int(math.sqrt((triclen*triclen)-(triblen*triblen))) # height
    im = Image.new(mode="RGB", size=(width, height))
    draw = ImageDraw.Draw(im)
    # iterate over last 24 bytes of the blockhash
    for i in range(24):
        s = ((8+i)*2)
        e = s+2
        c = blockhash[s:e]
        if i%3 == 0:
            r = c
        if i%3 == 1:
            g = c
        if i%3 == 2:
            b = c
        j = i
        y = 0
        if j > 11:
           j = j - 12
           y = triclen*2
        if j == 0:
            draw.polygon(((artleft+triblen,y+arttop+triclen-trialen),(artleft,y+arttop+triclen),(artleft+triclen,y+arttop+triclen)),fill=ImageColor.getrgb("#" + c + "0000"),outline=outlinecolor)
        if j == 1:
            draw.polygon(((artleft+triblen,y+arttop+triclen-trialen),(artleft+triclen,y+arttop+triclen),(artleft+triblen+triclen,y+arttop+triclen-trialen)),fill=ImageColor.getrgb("#00" + c + "00"),outline=outlinecolor)
        if j == 2:
            draw.polygon(((artleft+triclen,y+arttop+triclen),(artleft+triblen+triclen,y+arttop+triclen-trialen),(artleft+(triclen*2),y+arttop+triclen)),fill=ImageColor.getrgb("#0000" + c),outline=outlinecolor)
#            draw.chord(((artleft+triclen-trialen,y+arttop+triclen-trialen),(artleft+triclen+trialen,y+arttop+triclen+trialen)),start=180,end=360,fill=ImageColor.getrgb("#"+r+g+b),width=2)
            draw.chord(((artleft+triblen,y+arttop+triblen),(artleft+triclen+triblen,y+arttop+triclen+triblen)),start=180,end=360,fill=ImageColor.getrgb("#"+r+g+b),width=2)
        if j == 3:
            draw.polygon(((artleft+(triclen*2)+triblen,y+arttop+triclen-trialen),(artleft+(triclen*2),y+arttop+triclen),(artleft+(triclen*3),y+arttop+triclen)),fill=ImageColor.getrgb("#" + c + "0000"),outline=outlinecolor)
        if j == 4:
            draw.polygon(((artleft+(triclen*2)+triblen,y+arttop+triclen-trialen),(artleft+(triclen*3),y+arttop+triclen),(artleft+(triclen*3)+triblen,y+arttop+triclen-trialen)),fill=ImageColor.getrgb("#00" + c + "00"),outline=outlinecolor)
        if j == 5:
            draw.polygon(((artleft+(triclen*3)+triblen,y+arttop+triclen-trialen),(artleft+(triclen*3),y+arttop+triclen),(artleft+(triclen*4),y+arttop+triclen)),fill=ImageColor.getrgb("#0000" + c),outline=outlinecolor)
            draw.chord(((artleft+triblen+(triclen*2),y+arttop+triblen),(artleft+triclen+triblen+(triclen*2),y+arttop+triclen+triblen)),start=180,end=360,fill=ImageColor.getrgb("#"+r+g+b),width=2)
        if j == 6:
            draw.polygon(((artleft,y+arttop+triclen),(artleft+triclen,y+arttop+triclen),(artleft+triblen,y+arttop+triclen+trialen)),fill=ImageColor.getrgb("#" + c + "0000"),outline=outlinecolor)
        if j == 7:
            draw.polygon(((artleft+triclen,y+arttop+triclen),(artleft+triblen,y+arttop+triclen+trialen),(artleft+triclen+triblen,y+arttop+triclen+trialen)),fill=ImageColor.getrgb("#00" + c + "00"),outline=outlinecolor)
        if j == 8:
            draw.polygon(((artleft+triclen,y+arttop+triclen),(artleft+triclen+triblen,y+arttop+triclen+trialen),(artleft+(triclen*2),y+arttop+triclen)),fill=ImageColor.getrgb("#0000" + c),outline=outlinecolor)
            draw.chord(((artleft+triblen,y+arttop+triblen),(artleft+triclen+triblen,y+arttop+triclen+triblen)),start=0,end=180,fill=ImageColor.getrgb("#"+r+g+b),width=2)
        if j == 9:
            draw.polygon(((artleft+(triclen*2),y+arttop+triclen),(artleft+(triclen*2)+triblen,y+arttop+triclen+trialen),(artleft+(triclen*3),y+arttop+triclen)),fill=ImageColor.getrgb("#" + c + "0000"),outline=outlinecolor)
        if j == 10:
            draw.polygon(((artleft+(triclen*3),y+arttop+triclen),(artleft+(triclen*2)+triblen,y+arttop+triclen+trialen),(artleft+(triclen*3)+triblen,y+arttop+triclen+trialen)),fill=ImageColor.getrgb("#00" + c + "00"),outline=outlinecolor)
        if j == 11:
            draw.polygon(((artleft+(triclen*3),y+arttop+triclen),(artleft+(triclen*3)+triblen,y+arttop+triclen+trialen),(artleft+(triclen*4),y+arttop+triclen)),fill=ImageColor.getrgb("#0000" + c),outline=outlinecolor)
            draw.chord(((artleft+triblen+(triclen*2),y+arttop+triblen),(artleft+triclen+triblen+(triclen*2),y+arttop+triclen+triblen)),start=0,end=180,fill=ImageColor.getrgb("#"+r+g+b),width=2)
    drawcenteredtext(draw, "Blockhash Art For Block " + str(blocknumber), 24, int(width/2), int(padtop/2))
    drawbottomrighttext(draw, "as of " + getdateandtime(), 12, width, height)
    im.save(outputFileBlock)

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

def getblockhash(blocknumber=1):
    cmd = "bitcoin-cli getblockhash " + str(blocknumber)
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
        return cmdoutput
    except subprocess.CalledProcessError as e:
        print(e)
        return "0000000000000000000000000000000000000000000000000000000000000000"

if len(sys.argv) > 0:
    createimage(480, 320, int(sys.argv[1]))
else:
    while True:
        blocknumber = getcurrentblock()
        createimage(480, 320, blocknumber)
        time.sleep(300)
