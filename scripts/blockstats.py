#! /usr/bin/env python3
from PIL import Image, ImageDraw, ImageColor
from os.path import exists
import json
import math
import os
import sys
import time
import vicariousbitcoin
import vicarioustext
import vicariouswatermark

def getcolorstep(s, e, i, m):
    si = int(s,16)
    ei = int(e,16)
    di = ei - si
    ri = si + int(float(di)*float(i)/float(m))
    rh = "{:02x}".format(ri)
    return rh

def drawLabel(draw, s, fontsize, anchorposition, anchorx, anchory):
    sw,sh,f = vicarioustext.gettextdimensions(draw, s, fontsize, False)
    padding = 1
    border = 1
    nx = anchorx
    ny = anchory
    if anchorposition == "tl":
        # no change to nx, ny
        pass
    elif anchorposition == "tr":
        nx = anchorx - sw
        pass
    elif anchorposition == "t":
        nx = anchorx - (sw/2)
        pass
    elif anchorposition == "bl":
        ny = anchory - sh
        pass
    elif anchorposition == "br":
        nx = anchorx - sw
        ny = anchory - sh
        pass
    elif anchorposition == "b":
        nx = anchorx - (sw/2)
        ny = anchory - sh
        pass
    elif anchorposition == "l":
        ny = anchory - (sh/2)
        pass
    elif anchorposition == "r":
        nx = anchorx - sw
        ny = anchory - (sh/2)
        pass
    draw.rectangle(xy=[(nx-padding-border,ny-padding-border),(nx+sw+padding+border,ny+sh+padding+border)],fill=colorBackground,outline=colorShapeOutline,width=1)
    draw.text(xy=(nx,ny), text=s, font=f, fill=colorTextFG)

def getFieldMinMaxAvgValues(thelist, thefield):
    if len(thelist) == 0:
        return -1, -1, -1
    valuemin = 99999999
    valuemax = 0
    valueminx0 = 99999999
    valueminx1 = 99999999
    total = 0
    thefieldparts = thefield.split(".")
    for item in thelist:
        o = item
        bOK = True
        for thefieldpart in thefieldparts:
            if thefieldpart in o:
                o = o[thefieldpart]
            else:
                bOK = False
        v = 0 if not bOK else int(o)
        total += v
        valuemin = v if v < valuemin else valuemin
        valuemax = v if v > valuemax else valuemax
        valueminx0 = v if v < valueminx0 and v > 0 else valueminx0
        valueminx1 = v if v < valueminx1 and v > 1 else valueminx1
    valueavg = int(float(total) / float(len(thelist)))
    return valuemin, valuemax, valueavg, valueminx0, valueminx1

def drawBarChart(draw, left, top, width, height, thelist, fieldname, showlabels, chartlabel, grouping):
    low, high, avg, xo, x1 = getFieldMinMaxAvgValues(thelist, fieldname)
    lowx, highx = -1, -1
    lowy, highy = -1, -1
    # process each column from right to left
    l = len(thelist) - 1
    for i in range(l, 0, -1):
        item = thelist[i]
        # determine x coordinate for column
        px = float(i) / float(l)
        x = left + int(width * px)
        # get current value
        curval = int(item[fieldname])
        # determine y coordinate for column based on value
        py = float(curval) / float(high)
        y = top + int((1.0 - py) * height)
        y = top if y < top else y
        y = top + height - 1 if y > top + height - 1 else y
        if curval <= low:
            lowx = x
            lowy = y
        if curval >= high:
            highx = x
            highy = y
        # plot the value as a vertical bar
        draw.rectangle(xy=[(x,y),(x,top+height-1)],fill=colorGraphValue)
    # draw average line
    avgy = top + int(   (1.0-(float(avg) / float(high))) * height)
    draw.line(xy=[(left,avgy),(left+width-1,avgy)],fill=colorGraphAverage,width=2)
    # draw box
    draw.rectangle(xy=[(left,top),(left+width-1,top+height-1)],outline=colorGraphOutline,width=1)
    # draw labels
    if showlabels:
        if highx > 0 and highy > 0:
            highy = highy + 20 if highx - 100 < left else highy
            highpos = "tr" if highx + 150 > left + width else "tl"
            highx = highx + 3 if highpos == "tl" else highx - 3
            drawLabel(draw, "HIGH:" + str(high), 10, highpos, highx, highy+2)
        avgpos = "tl" if avgy + 20 < top+height-1 else "bl"
        avgx = left+2
        avgy = avgy - 2 if avgpos == "bl" else avgy + 2
        drawLabel(draw, "AVG:" + str(avg), 10, avgpos, avgx, avgy)
        if len(chartlabel) > 0:
            drawLabel(draw, chartlabel, 12, "tl", left+2, top+2)


def drawStackedPercentageBarChart(draw, left, top, width, height, thelist, fieldnames, showlabels, chartlabel, fieldlabels, grouping):
    # check inputs
    if len(fieldnames) > 8:
        drawLabel(draw, "TOO MANY FIELDNAMES DEFINED", 12, "tl", left, top)
        return
    if len(fieldnames) == 0:
        drawLabel(draw, "NO FIELDS PROVIDED FOR RENDERING", 12, "tl", left, top)
        return
    field0 = fieldnames[0]
    totalprovided = len(field0) > 0
    # determine chart range (if first field name isn't empty, it represents the total range)
    chartlow, charthigh = 99999999, -1
    if totalprovided:
        chartlow, charthigh, _, _, _ = getFieldMinMaxAvgValues(thelist, field0)
    else:
        for fieldname in fieldnames:
            if len(fieldname) == 0:
                continue
            low, high, _, _, _ = getFieldMinMaxAvgValues(thelist, fieldname)
            chartlow = low if low < chartlow else chartlow
            charthigh = high if high > charthigh else charthigh
    # process each column from right to left
    l = len(thelist)
    barwidthF = (float(grouping)/float(l))*float(width)
    print(f"barwidth: {barwidthF}")
    groupNum = 0
    for i in range(l-1, 0, (-1 * grouping)):
        x2 = left + width - int(barwidthF * groupNum)
        groupNum += 1
        x1 = left + width - int(barwidthF * groupNum)
        y2 = top + height - 1
        # get total for this time point
        timetotal = 0
        for g in range(grouping):
            item = thelist[i-g]
            if not totalprovided:
                # when first field is empty, we sum up from remaining fields
                for fieldname in fieldnames:
                    if len(fieldname) == 0:
                        continue
                    fieldvalue = int(item[fieldname])
                    timetotal = timetotal + fieldvalue
            else:
                # when first field is given, we use that to denote total being compared against
                timetotal = timetotal + int(item[field0])
        # then process each field
        fieldnum = 0
        for fieldname in fieldnames:
            fieldnum += 1 # for legend and coloring
            # skip field if empty
            if len(fieldname) == 0:
                continue
            # skip field if on total
            if totalprovided and fieldname == field0:
                continue
            # total for the grouping
            grouptotal = 0
            for g in range(grouping):
                item = thelist[i-g]
                itemvalue = int(item[fieldname])
                grouptotal = grouptotal + itemvalue
            # with grouptotal for this field, determine height and coordinates for the bar
            valuepct = float(grouptotal) / float(timetotal)
            valueheight = int(float(height) * valuepct)
            y1 = y2 - valueheight
            y1 = top if y1 < top or (fieldnum == len(fieldnames) and not totalprovided) else y1
            # draw the bar
            draw.rectangle(xy=[(x1,y1),(x2,y2)],fill=colorBands[fieldnum],width=1)
            # draw value
            if showlabels:
                pcttext = str(int(valuepct * 100.0)) + "%"
                vicarioustext.drawtoplefttext(draw, pcttext, 9, x1+1, y1+1, colorBackground)
            # assign new bottom
            y2 = y1
    # draw box
    draw.rectangle(xy=[(left,top),(left+width-1,top+height-1)],outline=colorGraphOutline,width=1)
    # draw labels
    if showlabels:
        if len(chartlabel) > 0:
            drawLabel(draw, chartlabel, 12, "tl", left+2, top+2)
        fieldnum = 0
        legendx = left+10
        legendy = top+height-10
        legendsize = 10
        for fieldname in fieldnames:
            fieldnum += 1
            if len(fieldname) == 0:
                continue
            if totalprovided and fieldname == field0:
                continue
            legendlabel = fieldname if fieldlabels[fieldnum-1] == "" else fieldlabels[fieldnum-1]
            if len(legendlabel) > 0:
                legendlabel = "    " + legendlabel
                sw,sh,f = vicarioustext.gettextdimensions(draw, legendlabel, legendsize, False)
                drawLabel(draw, legendlabel, legendsize, "bl", legendx, legendy)
                draw.rectangle(xy=[(legendx,legendy-legendsize),(legendx+legendsize,legendy)],fill=colorBands[fieldnum],outline=colorGraphOutline,width=1)
                legendx += sw + 10


def loadblockstatshistory():
    global blockstatshistory
    blockstatshistory = []
    fn = dataDirectory + "blockstatshistory.json"
    # for loading specific ranges, primarily for testing
    if len(sys.argv) > 1:
        fn = fn.replace(".json","-" + sys.argv[1] + ".json")
    if os.path.exists(fn):
        with open(fn, "r") as f:
            blockstatshistory = json.load(f)

def saveblockstatshistory():
    global blockstatshistory
    fn = dataDirectory + "blockstatshistory.json"
    # for saving specific ranges, primarily for testing
    if len(sys.argv) > 1:
        fn = fn.replace(".json","-" + sys.argv[1] + ".json")
    with open(fn, "w") as f:
        json.dump(blockstatshistory, f)

def updateBlockStatsHistory(blocknumber, itemsneeded):
    global blockstatshistory
    startblock = blocknumber - (itemsneeded-1)
    # load if empty
    if len(blockstatshistory) == 0:
        loadblockstatshistory()
    # if we have some data
    if len(blockstatshistory) > 0:
        # get highest block so far
        blockheight = blockstatshistory[-1]["height"]
        # adjust startblock
        if blockheight > startblock:
            startblock = blockheight + 1
    # fetch to tip as needed
    if startblock < blocknumber:
        print(f"Fetching blockstats history from {startblock} to {blocknumber}")
        for i in range(startblock, blocknumber+1):
            # eye candy to logs as this can take time
            if i % 50 == 0:
                print(f"- up to block {i} for {startblock} to {blocknumber} range")
                saveblockstatshistory()
            blockstats = vicariousbitcoin.getblockstats(i)
            #blockstats["extra"] = vicariousbitcoin.getblockscriptpubkeytypes(i)
            blockstatshistory.append(blockstats)
        print(f"- done fetching. up to {blocknumber}")
    # check if need at beginning
    if len(blockstatshistory) < itemsneeded:
        startblock = blocknumber - itemsneeded
        endblock = blockstatshistory[0]["height"]
        print(f"Fetching blockstats history from {startblock} to {endblock}")
        for i in range(endblock, startblock-1, -1):
            # eye candy logs
            if i % 50 == 0:
                print(f"- down to block {i} for {startblock} to {endblock} range")
                saveblockstatshistory()
            blockstats = vicariousbitcoin.getblockstats(i)
            #blockstats["extra"] = vicariousbitcoin.getblockscriptpubkeytypes(i)
            blockstatshistory.insert(0, blockstats)
    # remove early entries no longer needed
    itemstoremove = len(blockstatshistory) - itemsneeded
    if itemstoremove > 0:
        blockstatshistory = blockstatshistory[itemstoremove:]
    # save current state
    saveblockstatshistory()

def createimage_statsblock(blocknumber=1, width=480, height=320):
    padtop=40
    shadowdepth=4
    artheight=256
    artwidth=256
    arttop=(height/2)-(artheight/2)
    artleft=(width/2)-(artwidth/2)
    lwidth=2
    outlinecolor=colorShapeOutline
    startbyte = 8
    colorchanges = 8
    gradientwidth = int(artwidth / colorchanges)

    blockstats = blockstatshistory[-1]
    if len(sys.argv) > 1:
        outputFileName = outputFile.replace(".png","-" + str(blocknumber) + ".png")
    else:
        outputFileName = outputFile
    print(f"Generating image for Stat Block at {outputFileName}")
    im = Image.new(mode="RGBA", size=(width, height), color=colorBackground)
    draw = ImageDraw.Draw(im)
    i = -1
    blockhash = blockstats["blockhash"]
    # determine first start color parts
    cstart = ((startbyte+(i*3))*2) # 3 is color band (r,g,b), 2 is for hex representation of a byte
    rstart = blockhash[cstart:cstart+2]
    gstart = blockhash[cstart+2:cstart+2+2]
    bstart = blockhash[cstart+4:cstart+4+2]
    # 8 gradients
    for i in range(colorchanges):
        # determine ending color parts
        rend = blockhash[cstart+6:cstart+6+2]
        gend = blockhash[cstart+8:cstart+8+2]
        bend = blockhash[cstart+10:cstart+10+2]
        # gradient fill
        startx = artleft + (i * gradientwidth)
        endx = startx + gradientwidth
        for j in range(gradientwidth):
            # calculate gradient stepping per pixel of width
            r = getcolorstep(rstart, rend, j, gradientwidth)
            g = getcolorstep(gstart, gend, j, gradientwidth)
            b = getcolorstep(bstart, bend, j, gradientwidth)
            # build the color
            hc = "#" + r + g + b
            pointcolor=ImageColor.getrgb(hc)
            # determine where to draw and plot it
            x = startx + j
            y = arttop
#            draw.point(xy=[(x,y)],fill=pointcolor)
            draw.polygon(xy=[(x,y),(x,y+artheight-1)],fill=pointcolor)
        # update for next round
        cstart = ((startbyte+(i*3))*2)
        rstart = blockhash[cstart:cstart+2]
        gstart = blockhash[cstart+2:cstart+2+2]
        bstart = blockhash[cstart+4:cstart+4+2]
    # Outline the artwork
    draw.rectangle(xy=[(artleft-1,arttop-1),(artleft+artwidth,arttop+artheight)],outline=colorShapeOutline,width=1)
    # Shadow it (right+bottom)
    draw.polygon(xy=[(artleft+artwidth+1,arttop+shadowdepth),
                     (artleft+artwidth+shadowdepth,arttop+shadowdepth),
                     (artleft+artwidth+shadowdepth,arttop+artheight+shadowdepth),
                     (artleft+shadowdepth,arttop+artheight+shadowdepth),
                     (artleft+shadowdepth,arttop+artheight+1),
                     (artleft+artwidth+1,arttop+artheight+1)],
                 fill=colorShapeShadow)
    # Labels
    drawLabel(draw, blockstats["blockhash"], 10, "t", (width/2), 75)
    # IOD
    drawLabel(draw, "INPUTS          ", 12, "tl", (width/2)-100, 95)
    drawLabel(draw, str(blockstats["ins"]), 12, "tr", (width/2)-5, 95)
    drawLabel(draw, "OUTPUTS         ", 12, "tl", (width/2)-100, 111)
    drawLabel(draw, str(blockstats["outs"]), 12, "tr", (width/2)-5, 111)
    drawLabel(draw, "DELTA           ", 12, "tl", (width/2)-100, 127)
    drawLabel(draw, str(blockstats["utxo_increase"]), 12, "tr", (width/2)-5, 127)
    # TX
    drawLabel(draw, "TXS             ", 12, "tl", (width/2)+5, 95)
    drawLabel(draw, str(blockstats["txs"]), 12, "tr", (width/2)+100, 95)
    drawLabel(draw, "SEGWIT          ", 12, "tl", (width/2)+5, 111)
    drawLabel(draw, str(blockstats["swtxs"]), 12, "tr", (width/2)+100, 111)
    drawLabel(draw, str(int(float(blockstats["swtxs"])*100/float(blockstats["txs"])))+"%", 12, "tr", (width/2)+100, 127)
    # BLK SIZE, WEIGHT, UTXO SIZE
    drawLabel(draw, "BLK SIZE                                ", 12, "tl", (width/2)-100, 147)
    drawLabel(draw, str(blockstats["total_size"]), 12, "tr", (width/2)+100, 147)
    drawLabel(draw, "BLK WEIGHT                           ", 12, "tl", (width/2)-100, 163)
    drawLabel(draw, str(blockstats["total_weight"]), 12, "tr", (width/2)+100, 163)
    drawLabel(draw, "UTXO SIZE DELTA                   ", 12, "tl", (width/2)-100, 179)
    drawLabel(draw, str(blockstats["utxo_size_inc"]), 12, "tr", (width/2)+100, 179)
    # MIN / AVG / MAX FEE RATES
    drawLabel(draw, "FEERATES         ", 12, "tl", (width/2)-100, 199)
    drawLabel(draw, "MIN                ", 12, "tl", (width/2)-100, 215)
    drawLabel(draw, str(blockstats["minfeerate"]), 12, "tr", (width/2)-5, 215)
    drawLabel(draw, "AVG                ", 12, "tl", (width/2)-100, 231)
    drawLabel(draw, str(blockstats["avgfeerate"]), 12, "tr", (width/2)-5, 231)
    drawLabel(draw, "MAX                ", 12, "tl", (width/2)-100, 247)
    drawLabel(draw, str(blockstats["maxfeerate"]), 12, "tr", (width/2)-5, 247)
    drawLabel(draw, "FEES                 ", 12, "tl", (width/2)+5, 199)
    drawLabel(draw, "MIN            ", 12, "tl", (width/2)+5, 215)
    drawLabel(draw, str(blockstats["minfee"]), 12, "tr", (width/2)+100, 215)
    drawLabel(draw, "AVG            ", 12, "tl", (width/2)+5, 231)
    drawLabel(draw, str(blockstats["avgfee"]), 12, "tr", (width/2)+100, 231)
    drawLabel(draw, "MAX            ", 12, "tl", (width/2)+5, 247)
    drawLabel(draw, str(blockstats["maxfee"]), 12, "tr", (width/2)+100, 247)
    vicarioustext.drawcenteredtext(draw, "Stats For Block " + str(blocknumber), 20, int(width/2), int(padtop/2), colorTextFG, True)
    vicarioustext.drawbottomrighttext(draw, "as of " + vicarioustext.getdateandtime(), 12, width, height, colorTextFG)
    vicariouswatermark.do(im,width=140,box=(0,height-16))
    im.save(outputFileName)
    im.close()

def createimage_feerates(blocknumber=1, width=480, height=320):
    padtop=40
    padbottom=20
    chartpad=10
    h3 = int((height-padtop-padbottom)/3)
    blockheight_low = blockstatshistory[0]["height"]
    outputFileName = outputFile.replace(".png", "-feerates.png")
    if len(sys.argv) > 1:
        outputFileName = outputFileName.replace(".png","-" + str(blocknumber) + ".png")
    print(f"Generating image for Fee Rates at {outputFileName}")
    im = Image.new(mode="RGBA", size=(width,height), color=colorBackground)
    draw = ImageDraw.Draw(im)
    draw = ImageDraw.Draw(im)
    drawBarChart(draw, 0, padtop + (h3*0), width, h3-chartpad, blockstatshistory, "maxfeerate", True, "Maximum Fee Rate", 144)
    drawBarChart(draw, 0, padtop + (h3*1), width, h3-chartpad, blockstatshistory, "avgfeerate", True, "Average Fee Rate", 144)
    drawBarChart(draw, 0, padtop + (h3*2), width, h3-chartpad, blockstatshistory, "minfeerate", True, "Minimum Fee Rate", 144)
    vicarioustext.drawcenteredtext(draw, "Fee Rates from " + str(blockheight_low) + " to " + str(blocknumber), 20, int(width/2), int(padtop/2), colorTextFG, True)
    vicarioustext.drawbottomrighttext(draw, "as of " + vicarioustext.getdateandtime(), 12, width, height, colorTextFG)
    vicariouswatermark.do(im,width=140,box=(0,height-16))
    im.save(outputFileName)
    im.close()

def createimage_segwitprevalence(blocknumber=1, width=480, height=320):
    padtop=40
    padbottom=20
    blockheight_low = blockstatshistory[0]["height"]
    outputFileName = outputFile.replace(".png", "-segwit.png")
    if len(sys.argv) > 1:
        outputFileName = outputFileName.replace(".png","-" + str(blocknumber) + ".png")
    print(f"Generating image for Segwit Prevalence at {outputFileName}")
    im = Image.new(mode="RGBA", size=(width,height), color=colorBackground)
    draw = ImageDraw.Draw(im)
    drawStackedPercentageBarChart(draw, 0, padtop, width, height-padtop-padbottom, blockstatshistory, ("txs","swtxs"), True, "24 Block (~6 hour) Intervals", ("NON-SEGWIT TRANSACTIONS","SEGWIT TRANSACTIONS"), 24)
    vicarioustext.drawcenteredtext(draw, "Segwit Prevalence from " + str(blockheight_low) + " to " + str(blocknumber), 20, int(width/2), int(padtop/2), colorTextFG, True)
    vicarioustext.drawbottomrighttext(draw, "as of " + vicarioustext.getdateandtime(), 12, width, height, colorTextFG)
    vicariouswatermark.do(im,width=140,box=(0,height-16))
    im.save(outputFileName)
    im.close()

def createimage_test(blocknumber=1, width=480, height=320):
    padtop=40
    padbottom=20
    blockheight_low = blockstatshistory[0]["height"]
    outputFileName = outputFile.replace(".png", "-test.png")
    if len(sys.argv) > 1:
        outputFileName = outputFileName.replace(".png","-" + str(blocknumber) + ".png")
    print(f"Test image at {outputFileName}")
    im = Image.new(mode="RGBA", size=(width,height), color=colorBackground)
    draw = ImageDraw.Draw(im)
    drawStackedPercentageBarChart(draw, 0, padtop, width, height-padtop-padbottom, blockstatshistory, ("", "txs","swtxs","maxfeerate","medianfee"), True, "Testing 24 blocks = 4 hour groupings", ("","ALL TXS","SEGWIT","MAX FEE RATE","MEDIAN FEE"), 24)
    vicarioustext.drawcenteredtext(draw, "Test from " + str(blockheight_low) + " to " + str(blocknumber), 20, int(width/2), int(padtop/2), colorTextFG, True)
    vicarioustext.drawbottomrighttext(draw, "as of " + vicarioustext.getdateandtime(), 12, width, height, colorTextFG)
    vicariouswatermark.do(im,width=140,box=(0,height-16))
    im.save(outputFileName)
    im.close()


def logStats():
    blockheight_low, blockheight_high, _, _, _ = getFieldMinMaxAvgValues(blockstatshistory, "height")
    feerates_min_low, feerates_min_high, feerates_min_avg, fr_min_x0, fr_min_x1 = getFieldMinMaxAvgValues(blockstatshistory, "minfeerate")
    feerates_avg_low, feerates_avg_high, feerates_avg_avg, fr_avg_x0, fr_avg_x1 = getFieldMinMaxAvgValues(blockstatshistory, "avgfeerate")
    feerates_max_low, feerates_max_high, feerates_max_avg, fr_max_x0, fr_max_x1 = getFieldMinMaxAvgValues(blockstatshistory, "maxfeerate")
    inputs_low, inputs_high, inputs_avg, inputs_x0, inputs_x1 = getFieldMinMaxAvgValues(blockstatshistory, "ins")
    outputs_low, outputs_high, outputs_avg, outputs_x0, outputs_x1 = getFieldMinMaxAvgValues(blockstatshistory, "outs")
    txs_low, txs_high, txs_avg, txs_x0, txs_x1 = getFieldMinMaxAvgValues(blockstatshistory, "txs")
    segwit_low, segwit_high, segwit_avg, segwit_x0, segwit_x1 = getFieldMinMaxAvgValues(blockstatshistory, "swtxs")
    print(f"  Stats for Blocks  {blockheight_low} - {blockheight_high}")
    print(f"------------------------------------------------------------------------------")
    print(f"  Average fee rate: {feerates_avg_low : >5}[{fr_avg_x0 : >5}] - {feerates_avg_high : 7}, avg: {feerates_avg_avg : 5}, x0: {fr_avg_x0 : 5}, x1: {fr_avg_x1 : 5}")
    print(f"  Minimum fee rate: {feerates_min_low : >5}[{fr_min_x0 : >5}] - {feerates_min_high : 7}, avg: {feerates_min_avg : 5}, x0: {fr_min_x0 : 5}, x1: {fr_min_x1 : 5}")
    print(f"  Maximum fee rate: {feerates_max_low : >5}[{fr_max_x0 : >5}] - {feerates_max_high : 7}, avg: {feerates_max_avg : 5}, x0: {fr_max_x0 : 5}, x1: {fr_max_x1 : 5}")
    print(f"            Inputs: {inputs_low : >5}[{inputs_x0 : >5}] - {inputs_high : >7}, avg: {inputs_avg : >5}, x0: {inputs_x0 : >5}, x1: {inputs_x1 : >5}")
    print(f"           Outputs: {outputs_low : >5}[{outputs_x0 : >5}] - {outputs_high : >7}, avg: {outputs_avg : >5}, x0: {outputs_x0 : >5}, x1: {outputs_x1 : >5}")
    print(f"       Tansactions: {txs_low : >5}[{txs_x1 : >5}] - {txs_high : >7}, avg: {txs_avg : >5}, x0: {txs_x0 : >5}, x1: {txs_x1 : >5}")
    print(f"Segwit Tansactions: {segwit_low : >5}[{segwit_x0 : >5}] - {segwit_high : >7}, avg: {segwit_avg : >5}, x0: {segwit_x0 : >5}, x1: {segwit_x1 : >5}")


def createimages(blocknumber=1, width=480, height=320):
    # update stats history as necessary
    updateBlockStatsHistory(blocknumber, width) # 1px = 1 block

    # calculate and report stats as output
    if logStatsForRanges:
        logStats()

    # Create images
    # - stats block
    if showStatsBlock:
        createimage_statsblock(blocknumber, width, height)
    # - fee rates
    if showFeeRates:
        createimage_feerates(blocknumber, width, height)
    # - segwit transactions
    if showSegwitPrevalence:
        createimage_segwitprevalence(blocknumber, width, height)
    # - test
    if showTest:
        createimage_test(blocknumber, width, height)

if __name__ == '__main__':
    # Defaults
    configFile="/home/nodeyez/nodeyez/config/blockstats.json"
    outputFile="/home/nodeyez/nodeyez/imageoutput/blockstats.png"
    dataDirectory="/home/nodeyez/nodeyez/data/"
    width=480
    height=320
    sleepInterval=300
    colorTextFG=ImageColor.getrgb("#ffffff")
    colorBackground=ImageColor.getrgb("#000000")
    colorShapeOutline=ImageColor.getrgb("#888888")
    colorShapeShadow=ImageColor.getrgb("#88888888")
    colorGraphOutline=ImageColor.getrgb("#888888")
    colorGraphValue=ImageColor.getrgb("#FF8888")
    colorGraphAverage=ImageColor.getrgb("#8888FF")
    colorBands = [
        ImageColor.getrgb("#FFFF00"), # yellow
        ImageColor.getrgb("#0000FF"), # blue
        ImageColor.getrgb("#00FF00"), # lime
        ImageColor.getrgb("#808000"), # olive (dark yellow)
        ImageColor.getrgb("#FF0000"), # red
        ImageColor.getrgb("#00FFFF"), # aqua
        ImageColor.getrgb("#800000"), # dark red / maroon
        ImageColor.getrgb("#808080"), # gray
        ImageColor.getrgb("#008000"), # green
        ImageColor.getrgb("#800080"), # purple
        ImageColor.getrgb("#FF00FF"), # fuchsia (pink)
        ImageColor.getrgb("#008080"), # teal
    ]
    logStatsForRanges = True
    showStatsBlock = True
    showFeeRates = True
    showSegwitPrevalence = True
    showTest = False
    # Initializations
    blockstatshistory = []
    # Override config
    if exists(configFile):
        with open(configFile) as f:
            config = json.load(f)
        if "blockstats" in config:
            config = config["blockstats"]
        if "outputFile" in config:
            outputFile = config["outputFile"]
        if "dataDirectory" in config:
            dataDirectory = config["dataDirectory"]
        if "width" in config:
            width = int(config["width"])
        if "height" in config:
            height = int(config["height"])
        if "sleepInterval" in config:
            sleepInterval = int(config["sleepInterval"])
            sleepInterval = 30 if sleepInterval < 30 else sleepInterval # minimum 30 seconds, local only
        if "colorTextFG" in config:
            colorTextFG = ImageColor.getrgb(config["colorTextFG"])
        if "colorBackground" in config:
            colorBackground = ImageColor.getrgb(config["colorBackground"])
        if "colorShapeOutline" in config:
            colorShapeOutline = ImageColor.getrgb(config["colorShapeOutline"])
        if "colorShapeShadow" in config:
            colorShapeShadow = ImageColor.getrgb(config["colorShapeShadow"])
        if "colorGraphOutline" in config:
            colorGraphOutline = ImageColor.getrgb(config["colorGraphOutline"])
        if "colorGraphValue" in config:
            colorGraphValue = ImageColor.getrgb(config["colorGraphValue"])
        if "colorGraphAverage" in config:
            colorGraphAverage = ImageColor.getrgb(config["colorGraphAverage"])
        if "colorBands" in config:
            colorBands.clear()
            for colorValue in config["colorBands"]:
                colorBands.append(ImageCOlor.getrgb(colorValue))
        if "logStatsForRanges" in config:
            logStatsForRanges = config["logStatsForRanges"]
        if "showStatsBlock" in config:
            showStatsBlock = config["showStatsBlock"]
        if "showSegwitPrevalence" in config:
            showSegwitPrevalence = config["showSegwitPrevalence"]
    # Data directories
    if not os.path.exists(dataDirectory):
        os.makedirs(dataDirectory)
    # Check for single run
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h','--help']:
            print(f"Produces a stat block for a bitcoin block reporting on metrics including inputs, outputs, change to the utxo set, block size and weight, transaction count and portion that is segwit, as well as fee information")
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
        createimages(blocknumber, width, height)
        exit(0)
    # Loop
    while True:
        blocknumber = vicariousbitcoin.getcurrentblock()
        createimages(blocknumber, width, height)
        print(f"sleeping for {sleepInterval} seconds")
        time.sleep(sleepInterval)
