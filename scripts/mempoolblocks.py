#! /usr/bin/python3
from datetime import datetime
from PIL import Image, ImageDraw, ImageColor
from os.path import exists
import json
import locale
import math
import subprocess
import sys
import time
import vicarioustext

def convert_size(size_bytes):
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])

def drawmempoolblock(draw,x,y,w,h,blockinfo,mpb):
    blocksize=blockinfo["blockSize"]
    blockvsize=blockinfo["blockVSize"]
    transactions=blockinfo["nTx"]
    feeranges=list(blockinfo["feeRange"])
    feelow=feeranges[0]
    feehigh=feeranges[len(feeranges)-1]
    feemedian=blockinfo["medianFee"]
    feelowint = int(math.floor(float(feelow)))
    feehighint = int(math.floor(float(feehigh)))
    feemedianint = int(math.floor(float(feemedian)))
    depth=int(math.floor(w*.14))
    pad=2
    colorBlockText = colorTextFG
    colorBlockFace = colorBlock0
    colorBlockFace = colorBlock1 if feelowint > satLevel1 else colorBlockFace
    colorBlockFace = colorBlock2 if feelowint > satLevel2 else colorBlockFace
    colorBlockFace = colorBlock3 if feelowint > satLevel3 else colorBlockFace
    colorBlockFace = colorBlock4 if feelowint > satLevel4 else colorBlockFace
    colorBlockFace = colorBlock5 if feelowint > satLevel5 else colorBlockFace
    draw.polygon(xy=((x+pad,y+pad),(x+pad,y+h-pad-depth),(x+pad+depth,y+h-pad),(x+pad+depth,y+pad+depth)),outline=colorBlockEdgeOutline,fill=colorBlockSide)
    draw.polygon(xy=((x+pad,y+pad),(x+pad+depth,y+pad+depth),(x+w-pad,y+pad+depth),(x+w-pad-depth,y+pad)),outline=colorBlockEdgeOutline,fill=colorBlockTop)
    draw.polygon(xy=((x+pad+depth,y+pad+depth),(x+w-pad,y+pad+depth),(x+w-pad,y+h-pad),(x+pad+depth,y+h-pad)),outline=colorBlockEdgeOutline,fill=colorBlockFace)
    centerx=x+depth+(int(math.floor((w-depth)/2)))
    # Text labels
    if blocksToRender == 3:
        descriptor="~" + str(feemedianint) + " sat/vB"
        vicarioustext.drawcenteredtext(draw, descriptor, 14, centerx, y+pad+(depth*2),colorBlockText)
        descriptor=str(feelowint) + " - " + str(feehighint) + " sat/vB"
        vicarioustext.drawcenteredtext(draw, descriptor, 14, centerx, y+pad+(depth*3),colorBlockText)
        descriptor=convert_size(int(blocksize))
        vicarioustext.drawcenteredtext(draw, descriptor, 18, centerx, y+pad+(depth*4),colorBlockText)
        locale.setlocale(locale.LC_ALL, '')
        descriptor='{:n}'.format(int(transactions)) + " transactions"
        vicarioustext.drawcenteredtext(draw, descriptor, 14, centerx, y+pad+(depth*5),colorBlockText)
        descriptor="In ~" + str((mpb+1)*10) + " minutes"
        vicarioustext.drawcenteredtext(draw, descriptor, 14, centerx, y+pad+(depth*6),colorBlockText)
    if blocksToRender == 4:
        descriptor="~" + str(feemedianint) + " sat/vB"
        vicarioustext.drawcenteredtext(draw, descriptor, 12, centerx, y+pad+(depth*2),colorBlockText)
        descriptor="(" + str(feelowint) + " - " + str(feehighint) + ")"
        vicarioustext.drawcenteredtext(draw, descriptor, 12, centerx, y+pad+(depth*3),colorBlockText)
        descriptor=convert_size(int(blocksize))
        vicarioustext.drawcenteredtext(draw, descriptor, 14, centerx, y+pad+(depth*4),colorBlockText)
        locale.setlocale(locale.LC_ALL, '')
        descriptor='{:n}'.format(int(transactions)) + " tx"
        vicarioustext.drawcenteredtext(draw, descriptor, 12, centerx, y+pad+(depth*5),colorBlockText)
        descriptor="In ~" + str((mpb+1)*10) + " minutes"
        vicarioustext.drawcenteredtext(draw, descriptor, 12, centerx, y+pad+(depth*6),colorBlockText)
    if blocksToRender == 5:
        descriptor="~" + str(feemedianint) + " sat/vB"
        vicarioustext.drawcenteredtext(draw, descriptor, 10, centerx, y+pad+(depth*2),colorBlockText)
        descriptor="(" + str(feelowint) + " - " + str(feehighint) + ")"
        vicarioustext.drawcenteredtext(draw, descriptor, 10, centerx, y+pad+(depth*3.3),colorBlockText)
        locale.setlocale(locale.LC_ALL, '')
        descriptor='{:n}'.format(int(transactions)) + " tx"
        vicarioustext.drawcenteredtext(draw, descriptor, 12, centerx, y+pad+(depth*4.6),colorBlockText)
        descriptor="~" + str((mpb+1)*10) + " minutes"
        vicarioustext.drawcenteredtext(draw, descriptor, 10, centerx, y+pad+(depth*6),colorBlockText)
    if blocksToRender == 6:
        descriptor="~" + str(feemedianint) + " sat/vB"
        vicarioustext.drawcenteredtext(draw, descriptor, 9, centerx, y+pad+(depth*2),colorBlockText)
        descriptor="(" + str(feelowint) + " - " + str(feehighint) + ")"
        vicarioustext.drawcenteredtext(draw, descriptor, 9, centerx, y+pad+(depth*4),colorBlockText)
        locale.setlocale(locale.LC_ALL, '')
        descriptor="~" + str((mpb+1)*10) + " mins"
        vicarioustext.drawcenteredtext(draw, descriptor, 9, centerx, y+pad+(depth*6),colorBlockText)

def createimage(width=480, height=320):
    mempoolblocks = getmempoolblocks()
    feefastest, feehalfhour, feehour, feeminimum = getrecommendedfees()
    bw = width/blocksToRender
    padtop=40
    im = Image.new(mode="RGB", size=(width, height))
    draw = ImageDraw.Draw(im)
    mpblist=list(mempoolblocks)
    mpblen=len(mpblist)
    for mpb in range(mpblen):
        if mpb > (blocksToRender -1):
            break
        drawmempoolblock(draw,(width-((mpb+1)*bw)),padtop,bw,bw,mpblist[mpb],mpb)
    vicarioustext.drawcenteredtext(draw, "Mempool Block Fee Estimates", 24, int(width/2), int(padtop/2), colorTextFG, True)
    vicarioustext.drawcenteredtext(draw, "Next: " + str(feefastest), 20, int(width/8*1), height-padtop, colorTextFG)
    vicarioustext.drawcenteredtext(draw, "30 Min: " + str(feehalfhour), 20, int(width/8*3), height-padtop, colorTextFG)
    vicarioustext.drawcenteredtext(draw, "1 Hr: " + str(feehour), 20, int(width/8*5), height-padtop, colorTextFG)
    vicarioustext.drawcenteredtext(draw, "Minimum: " + str(feeminimum), 20, int(width/8*7), height-padtop, colorTextFG)
    vicarioustext.drawbottomrighttext(draw, "as of " + vicarioustext.getdateandtime(), 12, width, height, colorTextFG)
    im.save(outputFile)

def getmempoolblocks():
    cmd = "curl --silent " + urlmempool
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
        j = json.loads(cmdoutput)
        return j
    except subprocess.CalledProcessError as e:
        cmdoutput = "[]"
        j = json.loads(cmdoutput)
        return j

def getrecommendedfees():
    cmd = "curl --silent " + urlfeerecs
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
        j = json.loads(cmdoutput)
        return j["fastestFee"], j["halfHourFee"], j["hourFee"], j["minimumFee"]
    except subprocess.CalledProcessError as e:
        return 1, 1, 1, 1


if __name__ == '__main__':
    # Defaults
    configFile="/home/bitcoin/nodeyez/config/mempoolblocks.json"
    outputFile="/home/bitcoin/images/mempoolblocks.png"
    urlmempool="https://mempool.space/api/v1/fees/mempool-blocks"
    urlfeerecs="https://mempool.space/api/v1/fees/recommended"
    colorBlockEdgeOutline=ImageColor.getrgb("#202020")
    colorBlockSide=ImageColor.getrgb("#404040")
    colorBlockTop=ImageColor.getrgb("#606060")
    colorTextFG=ImageColor.getrgb("#ffffff")
    colorBlock0=ImageColor.getrgb("#40C040")
    colorBlock1=ImageColor.getrgb("#c0ca33")
    colorBlock2=ImageColor.getrgb("#fdd835")
    colorBlock3=ImageColor.getrgb("#f4511e")
    colorBlock4=ImageColor.getrgb("#b71c1c")
    colorBlock5=ImageColor.getrgb("#4a148c")
    satLevel1=10
    satLevel2=30
    satLevel3=60
    satLevel4=100
    satLevel5=150
    blocksToRender=3
    sleepInterval=300
    # Override config
    if exists(configFile):
        with open(configFile) as f:
            config = json.load(f)
        if "outputFile" in config:
            outputFile = config["outputFile"]
        if "urlmempool" in config:
            urlmempool = config["urlmempool"]
        if "urlfeerecs" in config:
            urlfeerecs = config["urlfeerecs"]
        if "sleepInterval" in config:
            sleepInterval = int(config["sleepInterval"])
        if "blocksToRender" in config:
            blocksToRender = int(config["blocksToRender"])
        if "colorBlockEdgeOutline" in config:
            colorBlockEdgeOutline = ImageColor.getrgb(config["colorBlockEdgeOutline"])
        if "colorBlockSide" in config:
            colorBlockSide = ImageColor.getrgb(config["colorBlockSide"])
        if "colorBlockTop" in config:
            colorBlockTop = ImageColor.getrgb(config["colorBlockTop"])
        if "colortextFG" in config:
            colorTextFG = ImageColor.getrgb(config["colorTextFG"])
        if "colorBlock0" in config:
            colorBlock0 = ImageColor.getrgb(config["colorBlock0"])
        if "colorBlock1" in config:
            colorBlock1 = ImageColor.getrgb(config["colorBlock1"])
        if "colorBlock2" in config:
            colorBlock2 = ImageColor.getrgb(config["colorBlock2"])
        if "colorBlock3" in config:
            colorBlock3 = ImageColor.getrgb(config["colorBlock3"])
        if "colorBlock4" in config:
            colorBlock4 = ImageColor.getrgb(config["colorBlock4"])
        if "colorBlock5" in config:
            colorBlock6 = ImageColor.getrgb(config["colorBlock5"])
        if "satLevel1" in config:
            satLevel1 = int(config["satLevel1"])
        if "satLevel2" in config:
            satLevel2 = int(config["satLevel2"])
        if "satLevel3" in config:
            satLevel3 = int(config["satLevel3"])
        if "satLevel4" in config:
            satLevel4 = int(config["satLevel4"])
        if "satLevel5" in config:
            satLevel5 = int(config["satLevel5"])

    # Check for single run
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h','--help']:
            print(f"Prepares an image depicting the upcoming blocks and fees in the Mempool")
            print(f"Provides recommended fees for confirmation by block time")
            print(f"Usage:")
            print(f"1) Call without arguments to run continuously using the configuration or defaults")
            print(f"2) Pass an argument denoting the maximum number of blocks to render and exit")
            arg0 = sys.argv[0]
            print(f"   {arg0} 2")
            print(f"You may specify a custom configuration file at {configFile}")
        else:
            blocksToRender = int(sys.argv[1])
            createimage()
        exit(0)

    # Loop
    while True:
        createimage()
        time.sleep(sleepInterval)
