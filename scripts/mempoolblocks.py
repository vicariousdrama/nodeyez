#! /usr/bin/env python3
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
import vicariousnetwork
import vicariouswatermark

def convert_size(size_bytes):
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])

def getColorsForBlock(satFee):
    satFee = float(satFee)
    b = "#404040"
    t = "#ffffff"
    for x in blockSatLevels:
        satMin = float(0.0)
        satMax = float(0.0)
        if "satMin" in x:
            satMin = float(x["satMin"])
        if "satMax" in x:
            satMax = float(x["satMax"])
        if satMin <= float(satFee):
            if satMax >= float(satFee):
                if "colorBlock" in x:
                    b = x["colorBlock"]
                if "colorText" in x:
                    t = x["colorText"]
    return ImageColor.getrgb(b), ImageColor.getrgb(t)

def getColorForHistogram(satFee):
    f = "#404040"
    for x in histogramSatLevels:
        if "satMin" in x and float(x["satMin"]) <= float(satFee):
            if "satMax" in x and float(x["satMax"]) >= float(satFee):
                if "colorFill" in x:
                    f = x["colorFill"]
    return ImageColor.getrgb(f)

def drawmempoolblock(draw,x,y,w,h,blockinfo,mpb,mpblen,btr):
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
    # side
    draw.polygon(xy=((x+pad,y+pad),(x+pad,y+h-pad-depth),(x+pad+depth,y+h-pad),(x+pad+depth,y+pad+depth)),outline=colorBlockEdgeOutline,fill=colorBlockSide)
    # top
    draw.polygon(xy=((x+pad,y+pad),(x+pad+depth,y+pad+depth),(x+w-pad,y+pad+depth),(x+w-pad-depth,y+pad)),outline=colorBlockEdgeOutline,fill=colorBlockTop)
    # face
    draw.polygon(xy=((x+pad+depth,y+pad+depth),(x+w-pad,y+pad+depth),(x+w-pad,y+h-pad),(x+pad+depth,y+h-pad)),outline=colorBlockEdgeOutline,fill=colorBlockFace)
    # fill
    colorBlockFaceMedian, colorBlockText = getColorsForBlock(feemedian)
    fillxstart=(x+w-pad)-int(float((x+w-pad)-(x+pad+depth))*float(float(blockvsize)/float(1000000))) # default (righttoleft)
    fillxend=(x+w-pad)
    if renderStyle == "lefttoright":
        fillxstart=x+pad+depth
        fillxend=x+pad+depth+int(float((x+w-pad)-(x+pad+depth))*float(float(blockvsize)/float(1000000)))
    draw.polygon(xy=((fillxstart,y+pad+depth),(fillxend,y+pad+depth),(fillxend,y+h-pad),(fillxstart,y+h-pad)),outline=colorBlockEdgeOutline,fill=colorBlockFaceMedian)
    centerx=x+depth+(int(math.floor((w-depth)/2)))
    # Text labels
    if btr <= 3:
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
    if btr == 4:
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
    if btr == 5:
        descriptor="~" + str(feemedianint) + " sat/vB"
        vicarioustext.drawcenteredtext(draw, descriptor, 10, centerx, y+pad+(depth*2),colorBlockText)
        descriptor="(" + str(feelowint) + " - " + str(feehighint) + ")"
        vicarioustext.drawcenteredtext(draw, descriptor, 10, centerx, y+pad+(depth*3.3),colorBlockText)
        locale.setlocale(locale.LC_ALL, '')
        descriptor='{:n}'.format(int(transactions)) + " tx"
        vicarioustext.drawcenteredtext(draw, descriptor, 12, centerx, y+pad+(depth*4.6),colorBlockText)
        descriptor="~" + str((mpb+1)*10) + " minutes"
        vicarioustext.drawcenteredtext(draw, descriptor, 10, centerx, y+pad+(depth*6),colorBlockText)
    if btr == 6:
        descriptor="~" + str(feemedianint) + " sat/vB"
        vicarioustext.drawcenteredtext(draw, descriptor, 9, centerx, y+pad+(depth*2),colorBlockText)
        descriptor="(" + str(feelowint) + " - " + str(feehighint) + ")"
        vicarioustext.drawcenteredtext(draw, descriptor, 9, centerx, y+pad+(depth*4),colorBlockText)
        locale.setlocale(locale.LC_ALL, '')
        descriptor="~" + str((mpb+1)*10) + " mins"
        vicarioustext.drawcenteredtext(draw, descriptor, 9, centerx, y+pad+(depth*6),colorBlockText)

def drawhistogrambar(draw,bw,curhistvsize,curhistsatfee,histx1,histx2,histy1,histy2,padtop):
    histpixelwidth = int(float(bw) * (float(curhistvsize)/float(1000000)))
    histcolor = getColorForHistogram(curhistsatfee)
    histx1 = histx2 - histpixelwidth # default (righttoleft)
    if renderStyle == "lefttoright":
        histx1 = histx2 + histpixelwidth
    draw.polygon(xy=((histx1,histy1),(histx2,histy1),(histx2,histy2),(histx1,histy2)),outline=colorBlockEdgeOutline, fill=histcolor)

    histtext = str(int(curhistsatfee)) + " sat/vB"
    histtextw, histtexth, histtextfont = vicarioustext.gettextdimensions(draw, histtext, 10, False)
    alignCenter = False
    alignRight = True
    texty = histy1 + int(padtop/2)
    if histtextw < (histpixelwidth-4):
        if alignCenter:
            textx = histx1 + int(histpixelwidth/2) # default (righttoleft)
            if renderStyle == "lefttoright":
                textx = histx2 + int(histpixelwidth/2)
            vicarioustext.drawcenteredtext(draw, histtext, 10, textx, texty)
        if alignRight:
            textx = histx1 + histpixelwidth-2 # default (righttoleft)
            if renderStyle == "lefttoright":
                textx = histx2 + histtextw + 2
                #textx = histx1 - 2
            vicarioustext.drawrighttext(draw, histtext, 10, textx, texty)
    else:
        histtext = str(int(curhistsatfee))
        histtextw, histtexth, histtextfont = vicarioustext.gettextdimensions(draw, histtext, 10, False)
        if histtextw < (histpixelwidth-4):
            if alignCenter:
                textx = histx1 + int(histpixelwidth/2) # default (righttoleft)
                if renderStyle == "lefttoright":
                    textx = histx2 + int(histpixelwidth/2)
                vicarioustext.drawcenteredtext(draw, histtext, 10, textx, texty)
            if alignRight:
                textx = histx1 + histpixelwidth - 2 # default (righttoleft)
                if renderStyle == "lefttoright":
                    textx = histx1 - 2
                vicarioustext.drawrighttext(draw, histtext, 10, textx, texty)
    return histx1


def createimage(width=480, height=320):
    padtop=40
    im = Image.new(mode="RGBA", size=(width, height), color=colorBackground)
    draw = ImageDraw.Draw(im)
    # header
    vicarioustext.drawcenteredtext(draw, "Mempool Fees", 24, int(width/2), int(padtop/2), colorTextFG, True)
    # blocks
    mempoolblocks = vicariousnetwork.getmempoolblocks(useTor, urlmempool)
    global oldmempoolblocks
    if mempoolblocks == []:  # default response if error fetching
        mempoolblocks = oldmempoolblocks # assign previous (which initializes as empty array as well)
    if mempoolblocks != oldmempoolblocks: # if its different
        oldmempoolblocks = mempoolblocks # update the previous, which presumably is good data.
    mpblist=list(mempoolblocks)
    mpblen=len(mpblist)
    btr=blocksToRender
    btr=mpblen if btr > mpblen else btr
    btr=3 if btr < 3 else btr
    bw=width/btr
    for mpb in range(mpblen):
        if mpb > (btr -1):
            break
        blockx = int(width-((mpb+1)*bw)) # default (righttoleft)
        if renderStyle == "lefttoright":
            blockx = int(mpb*bw)
        drawmempoolblock(draw,blockx,padtop,bw,bw,mpblist[mpb],mpb,mpblen,btr)
    # calculate approx total number of potential blocks and txs
    totalvsize = 0
    totaltx = 0
    for mpb in range(mpblen):
        totalvsize = totalvsize + mpblist[mpb]["blockVSize"]
        totaltx = totaltx + mpblist[mpb]["nTx"]
    totalblocks = math.ceil(totalvsize / 1000000)
    totaltime = str(int(totalblocks / 6)) + " hours" if totalblocks > 12 else str(int(totalblocks * 10)) + " minutes"
    memsummary = str(totaltx) + " tx with vsize " + convert_size(totalvsize) + ", ~ " + str(totalblocks) + " blocks, ~ " + totaltime
    vicarioustext.drawcenteredtext(draw, memsummary, 12, int(width/2), padtop+bw+int(padtop/4), colorTextFG, False)
    # histogram info
    histogramdata = vicariousnetwork.getmempoolhistograminfo(useTor, urlfeehistogram)
    histy1=padtop+bw+int(padtop/2)
    histy2=histy1+padtop
    histx1=0 # default (righttoleft)
    histx2=width # default (righttoleft)
    if renderStyle == "lefttoright":
        histx1=width
        histx2=0
    histlist=list(histogramdata["fee_histogram"])
    histlen=len(histlist)
    curhistsatfee = 0 # to consolidate like fees
    curhistvsize = 0
    for histidx in range(histlen):
        histrender = False
        histsatfee = int(histlist[histidx][0])
        histvsize = int(histlist[histidx][1])
        if histidx == 0:
            curhistsatfee = histsatfee
            curhistvsize = histvsize
            if histlen == 1:
                histrender = True
            else:
                if int(histlist[histidx+1][0]) != histsatfee:
                    histrender = True
        else:
            if histsatfee == curhistsatfee:
                curhistvsize += histvsize
            else:
                histrender = True
        if histrender:
            histx1 = drawhistogrambar(draw,bw,curhistvsize,curhistsatfee,histx1,histx2,histy1,histy2,padtop)
            histx2 = histx1
            curhistsatfee = histsatfee
            curhistvsize = histvsize
            if renderStyle == "righttoleft" and histx2 <= 0:
                break
            if renderStyle == "lefttoright" and histx2 >= width:
                break
    histx1 = drawhistogrambar(draw,bw,curhistvsize,curhistsatfee,histx1,histx2,histy1,histy2,padtop)
    # fee recommendations
    feefastest, feehalfhour, feehour, feeminimum = vicariousnetwork.getmempoolrecommendedfees(useTor, urlfeerecs)
    if renderStyle == "righttoleft":
        vicarioustext.drawlefttext(draw, "Minimum: " + str(feeminimum), 18, 0, height-padtop, colorTextFG)
        vicarioustext.drawcenteredtext(draw, "1 Hour: " + str(feehour), 16, int(width/8*3), height-padtop, colorTextFG)
        vicarioustext.drawcenteredtext(draw, "30 Minutes: " + str(feehalfhour), 16, int(width/8*5), height-padtop, colorTextFG)
        vicarioustext.drawrighttext(draw, "Next: " + str(feefastest), 18, width, height-padtop, colorTextFG)
    if renderStyle == "lefttoright":
        vicarioustext.drawlefttext(draw, "Next: " + str(feefastest), 18, 0, height-padtop, colorTextFG)
        vicarioustext.drawcenteredtext(draw, "30 Minutes: " + str(feehalfhour), 16, int(width/8*3), height-padtop, colorTextFG)
        vicarioustext.drawcenteredtext(draw, "1 Hour: " + str(feehour), 16, int(width/8*5), height-padtop, colorTextFG)
        vicarioustext.drawrighttext(draw, "Minimum: " + str(feeminimum), 18, width, height-padtop, colorTextFG)
    # footer
    vicarioustext.drawbottomrighttext(draw, "as of " + vicarioustext.getdateandtime(), 12, width, height, colorTextFG)
    # attribution
    if isMempoolSpace():
        vicarioustext.drawbottomlefttext(draw, "Data from mempool.space", 14, 0, height, colorMempool)
    else:
        vicarioustext.drawbottomlefttext(draw, "Data from sovereign node", 14, 0, height, colorMempool)
    # Watermark
    vicariouswatermark.do(im,width=100,box=(int(width/2)-50,height-28))
    print(f"saving image to {outputFile}")
    im.save(outputFile)
    im.close()

def isMempoolSpace():
    if "mempoolhqx4isw62xs7abwphsq7ldayuidyx2v2oethdhhj6mlo2r6ad.onion" in urlmempool:
        return True
    if "mempool.space" in urlmempool:
        return True
    return False

if __name__ == '__main__':
    # Defaults
    configFile="../config/mempoolblocks.json"
    outputFile="../imageoutput/mempoolblocks.png"
    urlmempool="https://mempool.space/api/v1/fees/mempool-blocks"
    urlfeerecs="https://mempool.space/api/v1/fees/recommended"
    urlfeehistogram="https://mempool.space/api/mempool"
    useTor=True
    colorBackground=ImageColor.getrgb("#000000")
    colorBlockEdgeOutline=ImageColor.getrgb("#202020")
    colorBlockSide=ImageColor.getrgb("#404040")
    colorBlockTop=ImageColor.getrgb("#505050")
    colorBlockFace=ImageColor.getrgb("#606060")
    colorTextFG=ImageColor.getrgb("#ffffff")
    colorMempool=ImageColor.getrgb("#4cbae6") # "#699fed"
    blockSatLevels = [
        {"satMin": 0.0, "satMax": 10.0, "colorBlock": "#40c040", "colorText": "#ffffff"},
        {"satMin": 10.0, "satMax": 30.0, "colorBlock": "#9ea90b", "colorText": "#ffffff"},
        {"satMin": 30.0, "satMax": 60.0, "colorBlock": "#d1ac08", "colorText": "#ffffff"},
        {"satMin": 60.0, "satMax": 100.0, "colorBlock": "#f4511e", "colorText": "#ffffff"},
        {"satMin": 100.0, "satMax": 150.0, "colorBlock": "#b71c1c", "colorText": "#ffffff"},
        {"satMin": 150.0, "satMax": 9999.0, "colorBlock": "#4a148c", "colorText": "#ffffff"}
    ]
    histogramSatLevels = [
        {"satMin": 0.0, "satMax": 2.0, "colorFill": "#d81b60"},
        {"satMin": 2.0, "satMax": 3.0, "colorFill": "#8e24aa"},
        {"satMin": 3.0, "satMax": 4.0, "colorFill": "#5e35b1"},
        {"satMin": 4.0, "satMax": 5.0, "colorFill": "#3949ab"},
        {"satMin": 5.0, "satMax": 6.0, "colorFill": "#1e88e5"},
        {"satMin": 6.0, "satMax": 8.0, "colorFill": "#039be5"},
        {"satMin": 8.0, "satMax": 10.0, "colorFill": "#00acc1"},
        {"satMin": 10.0, "satMax": 12.0, "colorFill": "#00897b"},
        {"satMin": 12.0, "satMax": 15.0, "colorFill": "#43a047"},
        {"satMin": 15.0, "satMax": 20.0, "colorFill": "#7cb342"},
        {"satMin": 20.0, "satMax": 30.0, "colorFill": "#c0ca33"},
        {"satMin": 30.0, "satMax": 40.0, "colorFill": "#fdd835"},
        {"satMin": 40.0, "satMax": 50.0, "colorFill": "#ffb300"},
        {"satMin": 50.0, "satMax": 60.0, "colorFill": "#fb8c00"},
        {"satMin": 60.0, "satMax": 70.0, "colorFill": "#f4511e"},
        {"satMin": 70.0, "satMax": 80.0, "colorFill": "#6d4c41"},
        {"satMin": 80.0, "satMax": 90.0, "colorFill": "#757575"},
        {"satMin": 90.0, "satMax": 100.0, "colorFill": "#546e7a"},
        {"satMin": 100.0, "satMax": 125.0, "colorFill": "#b71c1c"},
        {"satMin": 125.0, "satMax": 150.0, "colorFill": "#880e4f"},
        {"satMin": 150.0, "satMax": 9999.0, "colorFill": "#4a148c"}
    ]
    blocksToRender=3
    width=480
    height=320
    renderStyle="righttoleft"
    sleepInterval=300
    # Override config
    if exists(configFile):
        with open(configFile) as f:
            config = json.load(f)
        if "mempoolblocks" in config:
            config = config["mempoolblocks"]
        if "outputFile" in config:
            outputFile = config["outputFile"]
        if "urlmempool" in config:
            urlmempool = config["urlmempool"]
        if "urlfeerecs" in config:
            urlfeerecs = config["urlfeerecs"]
        if "urlfeehistogram" in config:
            urlfeehistogram = config["urlfeehistogram"]
        if "useTor" in config:
            useTor = config["useTor"]
        if "width" in config:
            width = int(config["width"])
        if "height" in config:
            height = int(config["height"])
        if "renderStyle" in config:
            renderStyle = config["renderStyle"]
        if "sleepInterval" in config:
            sleepInterval = int(config["sleepInterval"])
            sleepInterval = 300 if (sleepInterval < 300 and "mempool.space" in urlmempool) else sleepInterval # 5 minutes minimum when accessing others
        if "blocksToRender" in config:
            blocksToRender = int(config["blocksToRender"])
            blocksToRender = 6 if blocksToRender > 6 else blocksToRender
            blocksToRender = 3 if blocksToRender < 3 else blocksToRender
        if "colorBlockEdgeOutline" in config:
            colorBlockEdgeOutline = ImageColor.getrgb(config["colorBlockEdgeOutline"])
        if "colorBlockSide" in config:
            colorBlockSide = ImageColor.getrgb(config["colorBlockSide"])
        if "colorBlockTop" in config:
            colorBlockTop = ImageColor.getrgb(config["colorBlockTop"])
        if "colorBlockFace" in config:
            colorBlockFace = ImageColor.getrgb(config["colorBlockFace"])
        if "colorTextFG" in config:
            colorTextFG = ImageColor.getrgb(config["colorTextFG"])
        if "blockSatLevels" in config:
            blockSatLevels = config["blockSatLevels"]
        if "histogramSatLevels" in config:
            histogramSatLevels = config["histogramSatLevels"]
    oldmempoolblocks = []
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
            createimage(width, height)
        exit(0)

    # Loop
    while True:
        createimage(width, height)
        print(f"sleeping for {sleepInterval} seconds")
        time.sleep(sleepInterval)
