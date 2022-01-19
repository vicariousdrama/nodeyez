#! /usr/bin/python3
from datetime import datetime
from PIL import Image, ImageFilter, ImageDraw, ImageFont, ImageColor
import json
import locale
import math
import numpy
import random
import subprocess
import time
import sys

# This tileset is a subset of the ProjectUltimno_full.png from Dungeon Crawl Stone Soup
# The images are available at https://opengameart.org/content/dungeon-crawl-32x32-tiles-supplemental
# To find out more about Dungeon Crawl Stone Soup and how to play go to https://crawl.develz.org/wordpress/
tilesetFile="/home/bitcoin/nodeyez/images/arthash-dungeon-tiles.png"
outputFile="/home/bitcoin/images/arthashdungeon.png"
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

def createimage(blocknumber=1, width=480, height=320):
    blockhash = getblockhash(blocknumber)
    outputFileBlock = outputFile.replace(".png","-" + str(blocknumber) + ".png")
    padtop=32
    im = Image.new(mode="RGB", size=(width, height))
    draw = ImageDraw.Draw(im)
    drawcenteredtext(draw, "Blockhash Dungeon For Level " + str(blocknumber), 24, int(width/2), int(padtop/2))
    tileset  = Image.open(tilesetFile)
    iconsize =32
    thingmap = []
    # draw the dungeon (playing field of base tile and alt tile, walls)
    theme    = (int(blockhash[62:64],16) & int("11111000",2)) >> 3
    basetile = int(blockhash[62:64],16) & int("00000111",2)
    walltile = (int(blockhash[60:62],16) & int("10000000",2)) >> 7
    alttile  = (int(blockhash[60:62],16) & int("01110000",2)) >> 4
    altseed  = int(blockhash[60:62],16) & int("00001111",2)
    themex = 0
    if theme%2 == 1:
        themex = iconsize * 8
    themey = int(theme / 2) * iconsize
    if basetile == 6:
        basetile = 0
    if basetile == 7:
        basetile = 5
    if alttile == 6:
        alttile = 0
    if alttile == 7:
        alttile = 5
    basetiley = themey
    basetilex = themex + (basetile * iconsize)
    basetileimage = tileset.crop((basetilex, basetiley, basetilex + iconsize, basetiley + iconsize))
    walltilex = themex + ((6 + walltile) * iconsize)
    walltileimage = tileset.crop((walltilex, basetiley, walltilex + iconsize, basetiley + iconsize))
    alttilex = themex + (alttile * iconsize)
    alttileimage = tileset.crop((alttilex, basetiley, alttilex + iconsize, basetiley + iconsize))
    #random.seed(altseed)
    for fieldcolumn in range(15):
        thingmap.append([])
        for fieldrow in range(7):
            thingmap[fieldcolumn].append(0)
            im.paste(basetileimage, ((fieldcolumn * iconsize), ((fieldrow+2) * iconsize)))
            if (random.random() * 10) > 7:
                im.paste(alttileimage, ((fieldcolumn * iconsize), ((fieldrow+2) * iconsize)))
        im.paste(walltileimage, ((fieldcolumn * iconsize), (1 * iconsize)))
        im.paste(walltileimage, ((fieldcolumn * iconsize), (9 * iconsize)))
    # now draw some characters
    for charnum in range(8):
        charrow = (int(blockhash[58 - (charnum * 2):58 - (charnum * 2) + 2],16) & int("11110000",2)) >> 4
        charcol = (int(blockhash[58 - (charnum * 2):58 - (charnum * 2) + 2],16) & int("00001111",2))
        charx   = (int(blockhash[58 - (charnum * 2) - 1:58 - (charnum * 2) - 1 + 2],16) & int("11110000",2)) >> 4
        chary   = (int(blockhash[58 - (charnum * 2) - 1:58 - (charnum * 2) - 1 + 2],16) & int("00001110",2)) >> 1
        if charx > 0:
            if chary > 0:
                if thingmap[charx-1][chary-1] == 0:
                    charimage = tileset.crop((charcol * iconsize, (charrow + 16) * iconsize, (charcol+1) * iconsize, (charrow + 16 + 1) * iconsize))
                    im.paste(charimage, ( (charx - 1) * iconsize, (chary - 1 + 2) * iconsize), charimage)
                    thingmap[charx-1][chary-1] = 1
    # now draw some items
    for itemnum in range(4):
        itemrow = (int(blockhash[42 - (itemnum * 2):42 - (itemnum * 2) + 2],16) & int("11110000",2)) >> 4
        itemcol = (int(blockhash[42 - (itemnum * 2):42 - (itemnum * 2) + 2],16) & int("00001111",2))
        itemx   = (int(blockhash[42 - (itemnum * 2) - 1:42 - (itemnum * 2) - 1 + 2],16) & int("11110000",2)) >> 4
        itemy   = (int(blockhash[42 - (itemnum * 2) - 1:42 - (itemnum * 2) - 1 + 2],16) & int("00001110",2)) >> 1
        if itemx > 0:
            if itemy > 0:
                if thingmap[itemx-1][itemy-1] == 0:
                    itemimage = tileset.crop((itemcol * iconsize, (itemrow + 32) * iconsize, (itemcol+1) * iconsize, (itemrow + 32 + 1) * iconsize))
                    im.paste(itemimage, ( (itemx - 1) * iconsize, (itemy - 1 + 2) * iconsize), itemimage)
                    thingmap[itemx-1][itemy-1] = 1
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
        return "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"

if len(sys.argv) > 0:
    createimage(int(sys.argv[1]))
else:
    while True:
        blocknumber = getcurrentblock()
        createimage(blocknumber)
        time.sleep(300)
