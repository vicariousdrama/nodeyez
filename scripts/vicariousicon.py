from PIL import Image, ImageDraw, ImageColor
import math
import vicariousstat
import vicarioustext

class VicariousIcons:

    def __init__(self, draw=None):
        self.draw = draw

        self.cpuOutlineColor = ImageColor.getrgb("#c0c0c0")
        self.cpuEmptyColor = ImageColor.getrgb("#000000")
        self.cpuGoodColor = ImageColor.getrgb("#40ff40")
        self.cpuWarnColor = ImageColor.getrgb("#ffff00")
        self.cpuDangerColor = ImageColor.getrgb("#ff0000")
        self.cpuLabelTextColor = ImageColor.getrgb("#ffffff")

        self.drivePieOutlineColor = ImageColor.getrgb("#c0c0c0")
        self.drivePieEmptyFillColor = ImageColor.getrgb("#000000")
        self.drivePieEmptyTextColor = ImageColor.getrgb("#ffffff")
        self.drivePieGoodFillColor = ImageColor.getrgb("#40ff40")
        self.drivePieGoodTextColor = ImageColor.getrgb("#000000")
        self.drivePieWarnFillColor = ImageColor.getrgb("#ffff00")
        self.drivePieWarnTextColor = ImageColor.getrgb("#000000")
        self.drivePieDangerFillColor = ImageColor.getrgb("#ff0000")
        self.drivePieDangerTextColor = ImageColor.getrgb("#ffffff")
        self.drivePieLabelTextColor = ImageColor.getrgb("#ffffff")

        self.memoryOutlineColor = ImageColor.getrgb("#c0c0c0")
        self.memoryEmptyColor = ImageColor.getrgb("#000000")
        self.memoryGoodColor = ImageColor.getrgb("#40ff40")
        self.memoryWarnColor = ImageColor.getrgb("#ffff00")
        self.memoryDangerColor = ImageColor.getrgb("#ff0000")
        self.memoryLabelTextColor = ImageColor.getrgb("#ffffff")

        self.thermometerUnfilledColor = ImageColor.getrgb("#000000")
        self.thermometerOutlineColor = ImageColor.getrgb("#c0c0c0")
        self.thermometerBarNormalColor = ImageColor.getrgb("#40ff40")
        self.thermometerBarWarnColor = ImageColor.getrgb("#ffff00")
        self.thermometerBarDangerColor = ImageColor.getrgb("#ff0000")
        self.thermometerLabelTextColor = ImageColor.getrgb("#ffffff")
        self.thermometerWarnLevel = 55
        self.thermometerDangerLevel = 65

    def drawCPULoad(self, x,y,w,h, load1min=100, load5min=100, load15min=100):
        vicarioustext.drawcenteredtext(self.draw, "CPU Load", int(w*.15), x+int(w/2), y+int(h*.08), self.cpuLabelTextColor, True)
        vicarioustext.drawlefttext(self.draw, "1 min", int(w*.1125), x+int(w*.0375), y+(int(h/8)*3), self.cpuLabelTextColor)
        vicarioustext.drawlefttext(self.draw, "5 min", int(w*.1125), x+int(w*.0375), y+(int(h/8)*5), self.cpuLabelTextColor)
        vicarioustext.drawlefttext(self.draw, "15 min", int(w*.1125), x+int(w*.0375), y+(int(h/8)*7), self.cpuLabelTextColor)
        ttw = int(w*.45)
        pcount = vicariousstat.getcpucount()
        loads = [load1min, load5min, load15min]
        for j in range(len(loads)):
            # fill portion
            ld = loads[j]
            ldp = float(ld) * float(100) / float(pcount)
            ldw = int(((x+w)-(x+ttw+3)) * (float(ld)/float(pcount)))
            if ldw < 1: ldw = 1
            barcolor=self.cpuGoodColor
            if float(ldp) > 50.0:
                barcolor=self.cpuWarnColor
            if float(ldp) > 75.0:
                barcolor=self.cpuDangerColor
            x1 = x+ttw+3+1
            y1 = y+((h/8)*((j*2)+2))+4
            x2 = x1+ldw
            y2 = y+((h/8)*((j*2)+4))-3-1
            x2 = x1 + 1 if x2 <= x1 else x2
            y2 = y1 + 1 if y2 <= y1 else y2
            if ldw >= 10: r = 4
            elif ldw >= 8: r = 3
            elif ldw >= 6: r = 2
            elif ldw >= 4: r = 1
            else: r = 0
            if r > 0:
                self.draw.rounded_rectangle(xy=(x1,y1,x2,y2),radius=r,fill=barcolor,width=1)
            else:
                self.draw.rectangle(xy=(x1,y1,x2,y2),fill=barcolor,width=1)
            # outline portion
            x1 = x+ttw+3
            y1 = y+((h/8)*((j*2)+2))+3
            x2 = x+w
            y2 = y+((h/8)*((j*2)+4))-3
            x2 = x1 + 1 if x2 <= x1 else x2
            y2 = y1 + 1 if y2 <= y1 else y2
            self.draw.rounded_rectangle(xy=(x1,y1,x2,y2),radius=4,outline=self.cpuOutlineColor,width=1)


    def drawDrive(self, x,y,w,h, drivePath="/",freeSpace="0G",availPercent=0.00,driveLabel="Drive Space"):
        if drivePath in ["error","None"]: return
        pct = float(str(availPercent).replace("%",""))
        usedpct = 100 - pct
        gbf = freeSpace
        pad = int(w * .1875)
        ox = 2
        oy = 2
        if int(usedpct) == 50: ox = 0
        if int(usedpct) > 50:  ox *= -1
        sa = 0
        ea = sa + math.floor(usedpct*3.6)
        slicecolor = self.drivePieGoodFillColor
        textcolor = self.drivePieGoodTextColor
        if int(usedpct) > 75:
            slicecolor = self.drivePieWarnFillColor
            textcolor = self.drivePieWarnTextColor
        if int(usedpct) > 90:
            slicecolor = self.drivePieDangerFillColor
            textcolor = self.drivePieDangerTextColor
        self.draw.pieslice(xy=(x+pad+ox,y+pad+oy,x+w+ox-pad,y+h+oy-pad),start=sa,end=ea,fill=slicecolor,outline=self.drivePieOutlineColor,width=1)
        vicarioustext.drawtoplefttext(self.draw, "used", int(w*.10), x+(w/2)+ox, y+int(h/2)+int(h*.05), textcolor)
        ox *= -1
        oy *= -1
        sa = ea
        ea = 360
        self.draw.pieslice(xy=(x+pad+ox,y+pad+oy,x+w+ox-pad,y+h+oy-pad),start=sa,end=ea,fill=self.drivePieEmptyFillColor,outline=self.drivePieOutlineColor,width=1)
        vicarioustext.drawbottomlefttext(self.draw, "free", int(w*.10), x+(w/2)+ox, y+(h/2)-int(h*.05), self.drivePieEmptyTextColor)
        vicarioustext.drawcenteredtext(self.draw, gbf + " free", int(w*.125), x+(w/2), y+h-int(h*.0625), self.drivePieLabelTextColor)
        vicarioustext.drawcenteredtext(self.draw, driveLabel, int(w*.15), x+int(w/2), y+int(h*.08), self.cpuLabelTextColor, True)


    def drawMemory(self, x,y,w,h, label="", percentageUsed=100):
        pad = int(w * .125)
        self.draw.arc(xy=(x+pad,y+(pad*2),x+w-pad,y+h),start=120,end=420,fill=self.memoryOutlineColor,width=int(w*.125))
        self.draw.arc(xy=(x+pad+2,y+(pad*2)+2,x+w-pad-2,y+h-2),start=120+1,end=420-1,fill=self.memoryEmptyColor,width=(int(w*.125)-3))
        arccolor=self.memoryGoodColor
        p = percentageUsed
        if int(p) == 0:
            p = "1"
        if int(p) > 75:
            arccolor=self.memoryWarnColor
        if int(p) > 90:
            arccolor=self.memoryDangerColor
        ea=120+int((420-120)*(float(p)/100))
        self.draw.arc(xy=(x+pad+2,y+(pad*2)+2,x+w-pad-2,y+h-2),start=120,end=ea,fill=arccolor,width=(int(w*.125)-3))
        vicarioustext.drawcenteredtext(self.draw, label, int(w*.15), x+(w/2), y+int(h*.125), self.memoryLabelTextColor, True)
        vicarioustext.drawcenteredtext(self.draw, f"{p}%", int(w*.125), x+(w/2), y+(h/2)+int(h*.125), self.memoryLabelTextColor)

    def drawThermometer(self,x,y,w,h,temperature=None):
        tw=w//3
        # outline
        self.draw.ellipse(xy=(x,y+((h)/4*3),x+tw,y+h),fill=self.thermometerOutlineColor,outline=None,width=1) # bottom bulb
        self.draw.ellipse(xy=(x+((tw)/4*1),y,x+((tw)/4*3),y+((h)/4*1)),fill=self.thermometerOutlineColor,outline=None,width=1)  # top
        self.draw.rectangle(xy=(x+((tw)/4*1),y+((h)/8*1),x+((tw)/4*3),y+((h)/8*7)),fill=self.thermometerOutlineColor,outline=None,width=1) # middle
        # empty it
        self.draw.ellipse(xy=(x+2,y+2+((h)/4*3),x+tw-2,y+h-2),fill=self.thermometerUnfilledColor,outline=None,width=1) # bottom bulb
        self.draw.ellipse(xy=(x+2+((tw)/4*1),y+2,x-2+((tw)/4*3),y-2+((h)/4*1)),fill=self.thermometerUnfilledColor,outline=None,width=1) # top
        self.draw.rectangle(xy=(x+2+((tw)/4*1),y+2+((h)/8*1),x-2+((tw)/4*3),y-2+((h)/8*7)),fill=self.thermometerUnfilledColor,outline=None,width=1) # middle
        # fill it
        barcolor=self.thermometerBarNormalColor
        barpos=3
        if temperature is not None:
            if int(temperature) > self.thermometerWarnLevel:
                barcolor=self.thermometerBarWarnColor
                barpos=2
            if int(temperature) > self.thermometerDangerLevel:
                barcolor=self.thermometerBarDangerColor
                barpos=1
        xo = math.ceil(w * .025) # 4
        yo = 2
        self.draw.ellipse(xy=(x+xo,y+yo+(h/4*3),x-xo+tw,y-yo+h),fill=barcolor,outline=None,width=1)
        x1 = int( x+((tw)/4*1)+xo )
        x2 = int( x+((tw)/4*3)-xo )
        self.draw.rectangle(xy=(x1,y+yo+(h/8*barpos),x2,y-yo+(h/8*7)),fill=barcolor,outline=None,width=1)
        # degree lines
        for j in range(8):
            self.draw.rectangle(xy=(x+6+((tw-x)/4*3),y+(h/4)+((h/2/8)*j),x+6+int(w*.125)+((tw-x)/4*3),y+(h/4)+((h/2/8)*j)),fill=self.thermometerOutlineColor,outline=self.thermometerOutlineColor,width=int(w*.02))
        vicarioustext.drawtoprighttext(self.draw, f"{temperature:.0f}°", int(w*.3), x+w, y+int(h/2), self.thermometerLabelTextColor, True)
        vicarioustext.drawcenteredtext(self.draw, "Temp", int(w*.15), x+int(w/2), y+int(h*.08), self.thermometerLabelTextColor, True)

    def setDangerFillColor(self, newColor):
        self.cpuDangerColor = newColor
        self.drivePieDangerFillColor = newColor
        self.memoryDangerColor = newColor
        self.thermometerBarDangerColor = newColor

    def setGoodFillColor(self, newColor):
        self.cpuGoodColor = newColor
        self.drivePieGoodFillColor = newColor
        self.memoryGoodColor = newColor
        self.thermometerBarNormalColor = newColor

    def setLabelTextColor(self, newColor):
        self.cpuLabelTextColor = newColor
        self.drivePieLabelTextColor = newColor
        self.memoryLabelTextColor = newColor
        self.thermometerLabelTextColor = newColor

    def setOutlineColor(self, newColor):
        self.cpuOutlineColor = newColor
        self.drivePieOutlineColor = newColor
        self.memoryOutlineColor = newColor
        self.thermometerOutlineColor = newColor

    def setWarnFillColor(self, newColor):
        self.cpuWarnColor = newColor
        self.drivePieWarnFillColor = newColor
        self.memoryWarnColor = newColor
        self.thermometerBarWarnColor = newColor
    
