# import packages
from datetime import datetime
from PIL import ImageColor, ImageFont
import math
import time
import vicarioustext

def drawBarChart(draw, left=0, top=0, width=480, height=320, thelist=[], fieldname=None, 
                 showlabels=False, chartlabel="", grouping=1, valueColor="#ff8888",
                 averageColor="#8888ff", borderColor="#888888"
                  ):
    low, high, avg, xo, x1 = getFieldMinMaxAvgValues(thelist, fieldname)
    lowx, highx = -1, -1
    lowy, highy = -1, -1
    # process each column from right to left
    l = len(thelist) - 1
    xwidth = width // l
    xhalfwidth = (xwidth // 2) - 1
    if xhalfwidth < 0: xhalfwidth = 0
    for i in range(l, 0, -1):
        item = thelist[i]
        # determine x coordinate for column
        px = float(i) / float(l)
        x = left + int(width * px) - xhalfwidth
        # get current value
        if type(item) is dict and fieldname is not None:
            curval = int(item[fieldname])
        else:
            curval = int(item)
        # determine y coordinate for column based on value
        py = 1.0 if high <= 0 else float(curval) / float(high)
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
        draw.rectangle(xy=[(x-xhalfwidth,y),(x+xhalfwidth,top+height-1)],fill=ImageColor.getrgb(valueColor))
    # draw average line
    avgy = top if high == 0 else top + int(   (1.0-(float(avg) / float(high))) * height)
    draw.line(xy=[(left,avgy),(left+width-1,avgy)],fill=ImageColor.getrgb(averageColor),width=2)
    # draw box
    draw.rectangle(xy=[(left,top),(left+width-1,top+height-1)],outline=ImageColor.getrgb(borderColor),width=1)
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

def drawDotChart(draw, left=0, top=0, width=480, height=320, list=[], fieldName=None,
                 valueColor="#2f3fc5", valueRadius=3,
                 movingAverageDuration=10, movingAverageColor="#40ff40", movingAverageWidth=3,
                 lowValueColor="#ffaa00", lowValueThreshold=-1
                ):
    low, high, avg, _, _ = getFieldMinMaxAvgValues(list, fieldName)
    ma = []
    if fieldName is not None: fieldParts = fieldName.split(".")
    index = 0
    listLength = len(list)
    for item in list:
        index += 1
        o = item
        bOK = True
        if type(o) is dict or fieldName is not None:
            for fieldPart in fieldParts:
                if type(o) is dict and fieldPart in o:
                    o = o[fieldPart]
                else:
                    bOK = False
        v = 0 if not bOK else int(o)
        # assign color
        dotColor = valueColor
        if v < lowValueThreshold: dotColor = lowValueColor
        # plot the dot
        px = left + ((width * index) // listLength)
        pp = .5
        if high - low > 0: pp = float(v - low)/float(high - low)
        py = top + ((1.0 - pp) * height)
        px1 = px-1
        px2 = px+1
        py1 = py-1
        py2 = py+1
        if px1 < left: px1 = left
        if px2 > left+width: px2 = left + width
        if py1 < top: py1 = top
        if py2 > top + height: py2 = top + height
        draw.ellipse(xy=[(px1,py1),(px2,py2)],fill=ImageColor.getrgb(dotColor),outline=ImageColor.getrgb(dotColor),width=valueRadius)
        # process moving average
        if movingAverageDuration > 0:
            ma = ma[-1 * movingAverageDuration:]
            maold = v if len(ma) == 0 else sum(ma) / len(ma)
            ma.append(v)
            ma = ma[-1 * movingAverageDuration:]
            manew = v if len(ma) == 0 else sum(ma) / len(ma)
            if index > 1:
                pp = .5
                if high - low > 0: pp = float(maold - low)/float(high - low)
                maoldy = top + ((1.0 - pp) * height)
                pp = .5
                if high - low > 0: pp = float(manew - low)/float(high - low)
                manewy = top + ((1.0 - pp) * height)
                if manewy < top + movingAverageWidth: manewy = top + movingAverageWidth
                if manewy > top + height - movingAverageWidth: manewy = top + height - movingAverageWidth
                draw.line(xy=[(maoldx,maoldy),(px,manewy)],fill=ImageColor.getrgb(movingAverageColor),width=movingAverageWidth)
            maoldx = px

    return low, high, avg
    

def drawStackedPercentageBarChart(draw, left=0, top=0, width=480, height=320, 
                                  thelist=[], fieldnames=[], showlabels=False, chartlabel="", 
                                  fieldlabels=[], grouping=1, backgroundColor="#000000", 
                                  dataColors=["#ffff00", "#0000ff", "#00ff00", "#808000", 
                                              "#ff0000", "#00ffff", "#800000", "#808080", 
                                              "#008000", "#800080", "#ff00ff", "#008080"], 
                                  borderColor="#888888"):
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
    chartlow, charthigh = None, 0
    if totalprovided:
        chartlow, charthigh, _, _, _ = getFieldMinMaxAvgValues(thelist, field0)
    else:
        for fieldname in fieldnames:
            if len(fieldname) == 0:
                continue
            low, high, _, _, _ = getFieldMinMaxAvgValues(thelist, fieldname)
            chartlow = low if chartlow is None or low < chartlow else chartlow
            charthigh = high if high > charthigh else charthigh
    # process each column from right to left
    fieldtotals = {}
    l = len(thelist)
    barwidthF = (float(grouping)/float(l))*float(width)
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
                    fieldvalue, fieldvalueok = getNestedField(item, fieldname)
                    if fieldvalueok:
                        timetotal = timetotal + int(fieldvalue)
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
                itemvalue, itemvalueok = getNestedField(item, fieldname)
                if itemvalueok:
                    grouptotal = grouptotal + int(itemvalue)
            # with grouptotal for this field, determine height and coordinates for the bar
            if grouptotal > 0 and timetotal > 0:
                fieldtotals[fieldname] = grouptotal if fieldname not in fieldtotals else fieldtotals[fieldname] + grouptotal
                valuepct = float(grouptotal) / float(timetotal)
                valueheight = int(float(height) * valuepct)
                y1 = y2 - valueheight
                y1 = top if y1 < top or (fieldnum == len(fieldnames) and not totalprovided) else y1
                # draw the bar
                draw.rectangle(xy=[(x1,y1),(x2,y2)],fill=dataColors[fieldnum],width=1)
                # draw value
                if showlabels:
                    pcttext = str(int(valuepct * 100.0)) + "%"
                    vicarioustext.drawtoplefttext(draw, pcttext, 9, x1+1, y1+1, ImageColor.getrgb(backgroundColor))
                # assign new bottom
                y2 = y1
    # draw box
    draw.rectangle(xy=[(left,top),(left+width-1,top+height-1)],outline=ImageColor.getrgb(borderColor),width=1)
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
            if len(legendlabel) > 0 and fieldname in fieldtotals and fieldtotals[fieldname] > 0:
                legendlabel = "    " + legendlabel
                sw,sh,f = vicarioustext.gettextdimensions(draw, legendlabel, legendsize, False)
                drawLabel(draw, legendlabel, legendsize, "bl", legendx, legendy)
                draw.rectangle(xy=[(legendx,legendy-legendsize),(legendx+legendsize,legendy)],fill=dataColors[fieldnum],outline=ImageColor.getrgb(borderColor),width=1)
                legendx += sw + 10


def drawLabel(draw, s="", fontsize=12, anchorposition="tl", anchorx=0, anchory=0, backgroundColor="#000000", textColor="#ffffff", borderColor="#888888"):
    sw,sh,f = vicarioustext.gettextdimensions(draw, s, fontsize, False)
    padding = 1
    border = 1
    nx = anchorx
    ny = anchory
    if anchorposition == "tl":
        pass
    elif anchorposition == "tr":
        nx = anchorx - sw
    elif anchorposition == "t":
        nx = anchorx - (sw//2)
    elif anchorposition == "bl":
        ny = anchory - sh
    elif anchorposition == "br":
        nx = anchorx - sw
        ny = anchory - sh
    elif anchorposition == "b":
        nx = anchorx - (sw//2)
        ny = anchory - sh
    elif anchorposition == "l":
        ny = anchory - (sh//2)
    elif anchorposition == "r":
        nx = anchorx - sw
        ny = anchory - (sh//2)
    draw.rectangle(xy=[(nx-padding-border,ny-padding-border),(nx+sw+padding+border,ny+sh+padding+border)],fill=ImageColor.getrgb(backgroundColor),outline=ImageColor.getrgb(borderColor),width=1)
    draw.text(xy=(nx,ny), text=s, font=f, fill=ImageColor.getrgb(textColor))

def getNestedField(thedict, thefield):
    fieldDelimiter = "."
    if thefield.find(fieldDelimiter) > -1:
        thefieldparts = thefield.split(fieldDelimiter)
        nextpart = thefieldparts[0]
        remainder = fieldDelimiter.join(thefieldparts[1:])
        if nextpart in thedict:
            return getNestedField(thedict[nextpart], remainder)
    if thefield in thedict:
        return thedict[thefield], True
    else:
        return None, False

def getFieldMinMaxAvgValues(thelist, thefield=None):
    if len(thelist) == 0:
        return -1, -1, -1, -1, -1
    valuemin = None
    valuemax = 0
    valueminx0 = None
    valueminx1 = None
    total = 0
    if thefield is not None:
        thefieldparts = thefield.split(".")
    for item in thelist:
        o = item
        bOK = True
        if type(o) is dict or thefield is not None:
            for thefieldpart in thefieldparts:
                if type(o) is dict and thefieldpart in o:
                    o = o[thefieldpart]
                else:
                    bOK = False
        v = 0 if not bOK else int(o)
        total += v
        valuemin = v if valuemin is None or v < valuemin else valuemin
        valuemax = v if v > valuemax else valuemax
        valueminx0 = v if valueminx0 is None or v < valueminx0 and v > 0 else valueminx0
        valueminx1 = v if valueminx1 is None or v < valueminx1 and v > 1 else valueminx1
    valueavg = int(float(total) / float(len(thelist)))
    return valuemin, valuemax, valueavg, valueminx0, valueminx1
