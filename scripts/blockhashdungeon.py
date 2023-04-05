#! /usr/bin/env python3
from datetime import datetime
from os.path import exists
from PIL import Image, ImageDraw, ImageColor
import json
import locale
import math
import numpy
import random
import subprocess
import time
import sys
import vicariousbitcoin
import vicarioustext
import vicariouswatermark

def dfsmazegen(x, y, d, t):
    global maze
    mynode = maze[x][y]
    if not maze[x][y]['visited']:
        maze[x][y]['visited'] = True
        r = t + (int(random.random() * 3) - 1)
        if r < 0:
            r = 0
        if r > 6:
            r = 6
        maze[x][y]['t'] = r
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
                    dfsmazegen(x,y-1,'s',r)
            if chosendirection == 'ea':
                maze[x][y]['ea'] = False
                if not maze[x+1][y]['visited']:
                    maze[x][y]['eo'] = True
                    dfsmazegen(x+1,y,'w',r)
            if chosendirection == 'wa':
                maze[x][y]['wa'] = False
                if not maze[x-1][y]['visited']:
                    maze[x][y]['wo'] = True
                    dfsmazegen(x-1,y,'e',r)
            if chosendirection == 'sa':
                maze[x][y]['sa'] = False
                if not maze[x][y+1]['visited']:
                    maze[x][y]['so'] = True
                    dfsmazegen(x,y+1,'n',r)
        maze[x][y] = mynode

def createimage(blocknumber=1, width=480, height=320):
    blockhash = vicariousbitcoin.getblockhash(blocknumber)
    outputFileBlock = outputFile
    if len(sys.argv) > 1:
        outputFileBlock = outputFile.replace(".png","-" + str(blocknumber) + ".png")
    padtop=32
    im       = Image.new(mode="RGBA", size=(width, height), color=colorBackground)
    draw     = ImageDraw.Draw(im)
    iconsize = 32
    tileset  = Image.open(bitcoinTilesFile)
    tilesetx = int(tileset.getbbox()[2] / iconsize)
    tilesety = int(tileset.getbbox()[3] / iconsize)
    logoset  = Image.open(bitcoinLogosFile)
    logosetx = int(logoset.getbbox()[2] / iconsize)
    logosety = int(logoset.getbbox()[3] / iconsize)
    #print(f"tilesetx={tilesetx}, tilesety={tilesety}")
    #print(f"logosetx={logosetx}, logosety={logosety}")
    maxcol   = int(width/iconsize)
    maxrow   = int(height/iconsize)-1
    if maxcol%2 == 0:
        maxcol -= 1
    if maxrow%2 == 0:
        maxrow -= 1
    xoffset  = int((width - (maxcol*iconsize))/2)
    yoffset  = int((height - ((maxrow+1)*iconsize))/2)
    thingmap = []
    global maze
    maze=[]
    byteidx  = len(blockhash)
    # get theme (currently assumes 2 themes wide in the tileset)
    byteidx  -= 2
    theme    = int(blockhash[byteidx:byteidx+2],16) % (tilesetx * tilesety / 8)
    themex   = 0
    if theme%2 == 1:
        themex = iconsize * 8
    themey = int(theme / 2) * iconsize
    # get starting basetile (0 .. 5)
    byteidx  -= 2
    basetile = int(blockhash[byteidx:byteidx+2],16) % 6
    basetilex = themex + (basetile * iconsize)
    basetileimage = tileset.crop((basetilex, themey, basetilex + iconsize, themey + iconsize))
    # get wall tile (0 or 1)
    byteidx  -= 2
    walltile = int(blockhash[byteidx:byteidx+2],16) % 2
    walltilex = themex + ((6 + walltile) * iconsize)
    walltileimage = tileset.crop((walltilex, themey, walltilex + iconsize, themey + iconsize))
    # get randomization seed
    byteidx  -= 6
    altseed  = int(blockhash[byteidx:byteidx+6],16)
    random.seed(altseed) # 0-16777215
    # initialize the field and thingmap
    for fieldcolumn in range(maxcol):
        thingmap.append([])
        for fieldrow in range(maxrow):
            thingmap[fieldcolumn].append(0)
            im.paste(basetileimage, (xoffset+(fieldcolumn * iconsize), yoffset+((fieldrow+1) * iconsize)))
    bytenum = 0
    # generate maze
    if 1 == 1:
        # improve the randomization by resetting the seed with a larger number
        for mazecolumn in range(int(maxcol/2)):
            maze.append([])
            for mazerow in range(int(maxrow/2)):
                maze[mazecolumn].append({'visited':False,'no':False,'eo':False,'wo':False,'so':False,'na':True,'ea':True,'wa':True,'sa':True,'t':0})
        dfsmazegen(0, 0, 'w', basetile)
    # draw walls based on generated maze
    if 1 == 1:
        mazerows = int(maxrow/2)
        mazecolumns = int(maxcol/2)
        for mazerow in range(mazerows):
            fieldrow = (mazerow*2)+1
            for mazecolumn in range(mazecolumns):
                fieldcolumn = (mazecolumn*2)
                if 1 == 1: # changing basetileimage
                    basetile = maze[mazecolumn][mazerow]['t'] % 6
                    basetilex = themex + (basetile * iconsize)
                    basetileimage.close()
                    basetileimage = tileset.crop((basetilex, themey, basetilex + iconsize, themey + iconsize))
                    im.paste(basetileimage, (xoffset+((fieldcolumn+1)*iconsize), yoffset+((fieldrow+0)*iconsize)))
                    im.paste(basetileimage, (xoffset+((fieldcolumn+0)*iconsize), yoffset+((fieldrow+1)*iconsize)))
                    im.paste(basetileimage, (xoffset+((fieldcolumn+1)*iconsize), yoffset+((fieldrow+1)*iconsize)))
                im.paste(walltileimage, (xoffset+((fieldcolumn+0)*iconsize), yoffset+((fieldrow+0)*iconsize)))
                thingmap[fieldcolumn+0][fieldrow+0-1]=1
                if not maze[mazecolumn][mazerow]['no']:
                    im.paste(walltileimage, (xoffset+((fieldcolumn+1)*iconsize), yoffset+((fieldrow+0)*iconsize)))
                    thingmap[fieldcolumn+1][fieldrow+0-1]=1
                if not maze[mazecolumn][mazerow]['wo']:
                    im.paste(walltileimage, (xoffset+((fieldcolumn+0)*iconsize), yoffset+((fieldrow+1)*iconsize)))
                    thingmap[fieldcolumn+0][fieldrow+1-1]=1
                if mazecolumn == int(maxcol/2) - 1:
                    im.paste(walltileimage, (xoffset+((fieldcolumn+2)*iconsize), yoffset+((fieldrow+0)*iconsize)))
                    thingmap[fieldcolumn+2][fieldrow+0-1]=1
                    if mazerow < int(maxrow/2) - 1:
                        im.paste(walltileimage, (xoffset+((fieldcolumn+2)*iconsize), yoffset+((fieldrow+1)*iconsize)))
                        thingmap[fieldcolumn+2][fieldrow+1-1]=1
                    else:
                        im.paste(walltileimage, (xoffset+((fieldcolumn+2)*iconsize), yoffset+((fieldrow+2)*iconsize)))
                        thingmap[fieldcolumn+2][fieldrow+2-1]=1
                if mazerow == int(maxrow/2) -1:
                    im.paste(walltileimage, (xoffset+((fieldcolumn+0)*iconsize), yoffset+((fieldrow+2)*iconsize)))
                    thingmap[fieldcolumn+0][fieldrow+2-1]=1
                    im.paste(walltileimage, (xoffset+((fieldcolumn+1)*iconsize), yoffset+((fieldrow+2)*iconsize)))
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
    # draw some logos
    if 1 == 1:
        logostodraw = int(maxrow/2)
        logostotry = 100
        while logostodraw > 0 and logostotry > 0:
            logostotry -= 1
            byteidx = byteidx - 4 if byteidx - 4 >= 0 else len(blockhash) - (4 + int(random.random() * 7))
            fieldcol = int(blockhash[byteidx:byteidx+4],16) % maxcol
            byteidx = byteidx - 4 if byteidx - 4 >= 0 else len(blockhash) - (4 + int(random.random() * 11))
            fieldrow = int(blockhash[byteidx:byteidx+4],16) % maxrow
            if thingmap[fieldcol][fieldrow] == 0:
                byteidx = byteidx - 2 if byteidx - 2 >= 0 else len(blockhash) - (2 + int(random.random() * 3))
                tilex   = int(blockhash[byteidx:byteidx+2],16) % logosetx
                byteidx = byteidx - 2 if byteidx - 2 >= 0 else len(blockhash) - (2 + int(random.random() * 5))
                tiley   = int(blockhash[byteidx:byteidx+2],16) % logosety
                logoimage = logoset.crop((tilex*iconsize,tiley*iconsize,(tilex+1)*iconsize,(tiley+1)*iconsize))
                im.paste(logoimage, (xoffset+(fieldcol*iconsize),yoffset+((fieldrow+1)*iconsize)), logoimage)
                logoimage.close()
                thingmap[fieldcol][fieldrow] = 1
                logostodraw = logostodraw - 1
    # draw stairs
    # draw top bar
    #  - level
    #  - sats
    vicarioustext.drawlefttext(draw, "Blockhash Dungeon", 24, 0, int(padtop/2), colorTextFG, True)
    vicarioustext.drawrighttext(draw, "Level " + str(blocknumber), 24, width, int(padtop/2), colorTextFG, True)
    # Watermark
    vicariouswatermark.do(im,width=140,box=(int(width/2)-50,height-24))
    im.save(outputFileBlock)
    # cleanup resources
    logoset.close()
    tileset.close()
    basetileimage.close()
    walltileimage.close()
    im.close()

if __name__ == '__main__':
    # Defaults
    configFile="../config/blockhashdungeon.json"
    bitcoinLogosFile="../images/blockhash-dungeon-bitcoin-logos.png"
    bitcoinTilesFile="../images/blockhash-dungeon-bitcoin-tiles.png"
    outputFile="../imageoutput/blockhashdungeon.png"
    colorTextFG=ImageColor.getrgb("#ffffff")
    colorBackground=ImageColor.getrgb("#000000")
    width=480
    height=320
    sleepInterval=300
    # Inits
    maze=[]
    # Override config
    if exists(configFile):
        with open(configFile) as f:
            config = json.load(f)
        if "blockhashdungeon" in config:
            config = config["blockhashdungeon"]
        if "bitcoinLogosFile" in config:
            bitcoinLogosFile = config["bitcoinLogosFile"]
        if "bitcoinTilesFile" in config:
            bitcoinTilesFile = config["bitcoinTilesFile"]
        if "outputFile" in config:
            outputFile = config["outputFile"]
        if "colorTextFG" in config:
            colorTextFG = ImageColor.getrgb(config["colorTextFG"])
        if "colorBackground" in config:
            colorBackground = ImageColor.getrgb(config["colorBackground"])
        if "width" in config:
            width = int(config["width"])
        if "height" in config:
            height = int(config["height"])
        if "sleepInterval" in config:
            sleepInterval = int(config["sleepInterval"])
            sleepInterval = 30 if sleepInterval < 30 else sleepInterval # minimum 30 seconds, local only
    # Check for single run
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h','--help']:
            print(f"Produces artwork deterministically based on Bitcoin Blockhash values")
            print(f"Usage:")
            print(f"1) Call without arguments to run continuously using the configuration or defaults")
            print(f"2) Pass the desired block number as an argument as follows")
            arg0 = sys.argv[0]
            print(f"   {arg0} 722231")
            print(f"3) Pass the desired block number, width and height as arguments")
            print(f"   {arg0} 722231 1920 1080")
            print(f"You may specify a custom configuration file at {configFile}")
            exit(0)
        blocknumber = int(sys.argv[1])
        if len(sys.argv) > 3:
            width = int(sys.argv[2])
            height = int(sys.argv[3])
        createimage(blocknumber,width,height)
        exit(0)
    # Loop
    while True:
        blocknumber = vicariousbitcoin.getcurrentblock()
        createimage(blocknumber,width,height)
        print(f"sleeping for {sleepInterval} seconds")
        time.sleep(sleepInterval)
