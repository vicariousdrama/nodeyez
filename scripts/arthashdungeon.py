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
maze=[]

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

def dfsmazegen(x, y, d):
    global maze
    mynode = maze[x][y]
    if not maze[x][y]['visited']:
        maze[x][y]['visited'] = True
        maze[x][y][d + 'o'] = True  # open where we came from
        maze[x][y][d + 'a'] = False # no longer available
        availabledirections = []
        if maze[x][y]['na']:
            if y > 0:
                availabledirections.append('na')
            else:
                maze[x][y]['na'] = False
        if maze[x][y]['ea']:
            if x < len(maze) - 1:
                availabledirections.append('ea')
            else:
                maze[x][y]['ea'] = False
        if maze[x][y]['wa']:
            if x > 0:
                availabledirections.append('wa')
            else:
                maze[x][y]['wa'] = False
        if maze[x][y]['sa']:
            if y < len(maze[x]) - 1:
                availabledirections.append('sa')
            else:
                maze[x][y]['sa'] = False
        while len(availabledirections):
            chosenslot = int(random.random() * len(availabledirections))
            chosendirection = availabledirections[chosenslot]
            del availabledirections[chosenslot]
            if chosendirection == 'na':
                maze[x][y]['na'] = False
                if not maze[x][y-1]['visited']:
                    maze[x][y]['no'] = True
                    dfsmazegen(x,y-1,'s')
            if chosendirection == 'ea':
                maze[x][y]['ea'] = False
                if not maze[x+1][y]['visited']:
                    maze[x][y]['eo'] = True
                    dfsmazegen(x+1,y,'w')
            if chosendirection == 'wa':
                maze[x][y]['wa'] = False
                if not maze[x-1][y]['visited']:
                    maze[x][y]['wo'] = True
                    dfsmazegen(x-1,y,'e')
            if chosendirection == 'sa':
                maze[x][y]['sa'] = False
                if not maze[x][y+1]['visited']:
                    maze[x][y]['so'] = True
                    dfsmazegen(x,y+1,'n')
        maze[x][y] = mynode

def createimage(blocknumber=1, width=480, height=320):
    blockhash = getblockhash(blocknumber)
    outputFileBlock = outputFile.replace(".png","-" + str(blocknumber) + ".png")
    padtop=32
    im       = Image.new(mode="RGB", size=(width, height))
    draw     = ImageDraw.Draw(im)
    tileset  = Image.open(tilesetFile)
    iconsize = 32
    maxcol   = 15
    maxrow   = 9
    thingmap = []
    global maze
    byteidx  = 64
    # draw the dungeon (playing field of base tile and alt tile, walls)
    byteidx  -= 2
    theme    = (int(blockhash[byteidx:byteidx+2],16) & int("11111000",2)) >> 3
    basetile = int(blockhash[byteidx:byteidx+2],16) & int("00000111",2)
    byteidx  -= 2
    walltile = (int(blockhash[byteidx:byteidx+2],16) & int("10000000",2)) >> 7
    alttile  = (int(blockhash[byteidx:byteidx+2],16) & int("01110000",2)) >> 4
    altseed  = int(blockhash[byteidx:byteidx+2],16) & int("00001111",2)
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
    basetilex = themex + (basetile * iconsize)
    basetileimage = tileset.crop((basetilex, themey, basetilex + iconsize, themey + iconsize))
    walltilex = themex + ((6 + walltile) * iconsize)
    walltileimage = tileset.crop((walltilex, themey, walltilex + iconsize, themey + iconsize))
    alttilex = themex + (alttile * iconsize)
    alttileimage = tileset.crop((alttilex, themey, alttilex + iconsize, themey + iconsize))
    random.seed(altseed) # 0-15 as the seed is very small
    for fieldcolumn in range(maxcol):
        thingmap.append([])
        for fieldrow in range(maxrow):
            thingmap[fieldcolumn].append(0)
            im.paste(basetileimage, ((fieldcolumn * iconsize), ((fieldrow+1) * iconsize)))
            if (random.random() * 10) > 6:
                im.paste(alttileimage, ((fieldcolumn * iconsize), ((fieldrow+1) * iconsize)))
    # draw walls based on bits in half a byte (we only use 1 hex char per byte here, ensuring gaps)
    bytenum = 0
    if 1 == 0:
        for fieldcolumn in range(maxcol):
            for fieldrow in range(maxrow):
                bitidx  = (fieldcolumn*maxrow)+fieldrow
                bytenum = int(bitidx/8)
                bytepos = int(byteidx - bytenum)
                byteval = blockhash[bytepos:bytepos+1]
                byteint = int(byteval,16)
                # randomly add more gaps
                # if (random.random() * 10) > 8:
                #    byteint = byteint << 1
                # always add more gaps
                byteint = byteint >> 1
                bytebit = int(bitidx%8)
                bytebitval = (byteint >> bytebit) & int("00000001")
                if bytebitval > 0:
                    thingmap[fieldcolumn][fieldrow] = 1
                    im.paste(walltileimage, ((fieldcolumn * iconsize), ((fieldrow+1) * iconsize)))
    # generate maze
    if 1 == 1:
        # improve the randomization by resetting the seed with a larger number
        byteidx  -= 4
        altseed  = int(blockhash[byteidx:byteidx+4],16) & int("1111111111111111",2)
        random.seed(altseed) # 0-65535
        for mazecolumn in range(int(maxcol/2)):
            maze.append([])
            for mazerow in range(int(maxrow/2)):
                maze[mazecolumn].append({'visited':False,'no':False,'eo':False,'wo':False,'so':False,'na':True,'ea':True,'wa':True,'sa':True})
        dfsmazegen(0, 0, 'w')
    # draw walls based on generated maze
    if 1 == 1:
        for mazerow in range(int(maxrow/2)):
            fieldrow = (mazerow*2)+1
            for mazecolumn in range(int(maxcol/2)):
                fieldcolumn = (mazecolumn*2)
                im.paste(walltileimage, (((fieldcolumn+0)*iconsize), ((fieldrow+0)*iconsize)))
                thingmap[fieldcolumn+0][fieldrow+0-1]=1
                if not maze[mazecolumn][mazerow]['no']:
                    im.paste(walltileimage, (((fieldcolumn+1)*iconsize), ((fieldrow+0)*iconsize)))
                    thingmap[fieldcolumn+1][fieldrow+0-1]=1
                if not maze[mazecolumn][mazerow]['wo']:
                    im.paste(walltileimage, (((fieldcolumn+0)*iconsize), ((fieldrow+1)*iconsize)))
                    thingmap[fieldcolumn+0][fieldrow+1-1]=1
                if mazecolumn == int(maxcol/2) - 1:
                    im.paste(walltileimage, (((fieldcolumn+2)*iconsize), ((fieldrow+0)*iconsize)))
                    thingmap[fieldcolumn+2][fieldrow+0-1]=1
                    if mazerow < int(maxrow/2) - 1:
                        im.paste(walltileimage, (((fieldcolumn+2)*iconsize), ((fieldrow+1)*iconsize)))
                        thingmap[fieldcolumn+2][fieldrow+1-1]=1
                    else:
                        im.paste(walltileimage, (((fieldcolumn+2)*iconsize), ((fieldrow+2)*iconsize)))
                        thingmap[fieldcolumn+2][fieldrow+2-1]=1
                if mazerow == int(maxrow/2) -1:
                    im.paste(walltileimage, (((fieldcolumn+0)*iconsize), ((fieldrow+2)*iconsize)))
                    thingmap[fieldcolumn+0][fieldrow+2-1]=1
                    im.paste(walltileimage, (((fieldcolumn+1)*iconsize), ((fieldrow+2)*iconsize)))
                    thingmap[fieldcolumn+1][fieldrow+2-1]=1
    # print it out (for debug purposes)
    if 1 == 0:
        for mazerow in range(int(maxrow/2)):
            pn = "█"
            pw = ""
            if mazerow > 0:
                pw = pw + "█"
            else:
                pw = pw + " "
            for mazecolumn in range(int(maxcol/2)):
                if maze[fieldcolumn][fieldrow]['no']:
                    pn = pn + "█ "
                else:
                    pn = pn + "██"
                if maze[fieldcolumn][fieldrow]['wo']:
                    pw = pw + "  "
                else:
                    pw = pw + "█ "
            pn = pn + "█"
            if mazerow < int(maxrow/2) - 1:
                pw = pw + "█"
            print(pn)
            print(pw)
            if mazerow == int(maxrow/2) - 1:
                pn = "█"
                for mazecolumn in range(int(maxcol/2)):
                    pn = pn + "██"
                pn = pn + "█"
                print(pn)


    byteidx -= bytenum
    # draw some characters
    tileyoffset = 16
    for charnum in range(4):
        byteidx -= 2
        fieldcol = ((int(blockhash[byteidx:byteidx+2],16) & int("11110000",2)) >> 4)%maxcol
        fieldrow = ((int(blockhash[byteidx:byteidx+2],16) & int("00001111",2)))%maxrow
        if thingmap[fieldcol][fieldrow] == 0:
            byteidx -= 2
            tilex   = (int(blockhash[byteidx:byteidx+2],16) & int("11110000",2)) >> 4
            tiley   = (int(blockhash[byteidx:byteidx+2],16) & int("00001111",2))
            tileimage = tileset.crop((tilex*iconsize,(tiley+tileyoffset)*iconsize,(tilex+1)*iconsize,(tiley+tileyoffset+1)*iconsize))
            im.paste(tileimage, (fieldcol*iconsize,(fieldrow+1)*iconsize), tileimage)
            thingmap[fieldcol][fieldrow] = 1
    # draw some items
    tileyoffset = 32
    for charnum in range(4):
        byteidx -= 2
        fieldcol = ((int(blockhash[byteidx:byteidx+2],16) & int("11110000",2)) >> 4)%maxcol
        fieldrow = ((int(blockhash[byteidx:byteidx+2],16) & int("00001111",2)))%maxrow
        if thingmap[fieldcol][fieldrow] == 0:
            byteidx -= 2
            tilex   = (int(blockhash[byteidx:byteidx+2],16) & int("11110000",2)) >> 4
            tiley   = (int(blockhash[byteidx:byteidx+2],16) & int("00001111",2))
            tileimage = tileset.crop((tilex*iconsize,(tiley+tileyoffset)*iconsize,(tilex+1)*iconsize,(tiley+tileyoffset+1)*iconsize))
            im.paste(tileimage, (fieldcol*iconsize,(fieldrow+1)*iconsize), tileimage)
            thingmap[fieldcol][fieldrow] = 1
    # draw stairs
    # draw top bar
    #  - level
    #  - sats
    drawcenteredtext(draw, "Blockhash Dungeon For Level " + str(blocknumber), 24, int(width/2), int(padtop/2))
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
