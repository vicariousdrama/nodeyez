#! /usr/bin/python3
from PIL import Image, ImageDraw, ImageColor
import math
import sys
import time
import vicariousbitcoin
import vicarioustext

outputFile="/home/bitcoin/images/arthash.png"
colorFFFFFF=ImageColor.getrgb("#ffffff")

def createimage(blocknumber=1, width=480, height=320):
    blockhash = vicariousbitcoin.getblockhash(blocknumber)
    if len(sys.argv) > 1:
        outputFileBlock = outputFile.replace(".png","-" + str(blocknumber) + ".png")
    else:
        outputFileBlock = outputFile
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
    vicarioustext.drawcenteredtext(draw, "Blockhash Art For Block " + str(blocknumber), 24, int(width/2), int(padtop/2), colorFFFFFF, True)
    vicarioustext.drawbottomrighttext(draw, "as of " + vicarioustext.getdateandtime(), 12, width, height)
    im.save(outputFileBlock)

if len(sys.argv) > 1:
    createimage(int(sys.argv[1]), 480, 320)
else:
    while True:
        blocknumber = vicariousbitcoin.getcurrentblock()
        createimage(blocknumber, 480, 320)
        time.sleep(300)
