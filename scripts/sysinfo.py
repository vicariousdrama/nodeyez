from datetime import datetime
from PIL import Image, ImageFilter, ImageDraw, ImageFont, ImageColor
import json
import math
import subprocess
import time

color000000=ImageColor.getrgb("#000000")
color8080FF=ImageColor.getrgb("#8080ff")
colorC0C0C0=ImageColor.getrgb("#c0c0c0")
colorC0C0FF=ImageColor.getrgb("#c0c0ff")
#colorC0FFC0=ImageColor.getrgb("#c0ffc0")
colorC0FFC0=ImageColor.getrgb("#40ff40")
colorFF0000=ImageColor.getrgb("#ff0000")
colorFFFF00=ImageColor.getrgb("#ffff00")
colorFFFFFF=ImageColor.getrgb("#ffffff")
fontDeja12=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",12)
fontDeja16=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",16)
fontDeja18=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",18)
fontDeja20=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",20)
fontDeja24=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",24)
fontDeja48=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",48)
fontDeja64=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",64)
outputFile="/home/admin/images/sysinfo.png"

def drawicon(draw,icon,x,y,w,h,v=None):
    if icon == "thermometer":
        tw=w/3
        draw.ellipse(xy=(x,y+((h-y)/4*3),tw,h),fill=colorC0C0C0,outline=None,width=1)
        draw.ellipse(xy=(x+((tw-x)/4*1),y,x+((tw-x)/4*3),y+((h-y)/4*1)),fill=colorC0C0C0,outline=None,width=1)
        draw.rectangle(xy=(x+((tw-x)/4*1),y+((h-y)/8*1),x+((tw-x)/4*3),y+((h-y)/8*7)),fill=colorC0C0C0,outline=None,width=1)
        draw.ellipse(xy=(x+2,y+2+((h-y)/4*3),tw-2,h-2),fill=color000000,outline=None,width=1)
        draw.ellipse(xy=(x+2+((tw-x)/4*1),y+2,x-2+((tw-x)/4*3),y-2+((h-y)/4*1)),fill=color000000,outline=None,width=1)
        draw.rectangle(xy=(x+2+((tw-x)/4*1),y+2+((h-y)/8*1),x-2+((tw-x)/4*3),y-2+((h-y)/8*7)),fill=color000000,outline=None,width=1)
        barcolor=colorC0FFC0
        barpos=3
        if int(v) > 55:
            barcolor=colorFFFF00
            barpos=2
        if int(v) > 65:
            barcolor=colorFF0000
            barpos=1
        draw.ellipse(xy=(x+4,y+4+(h/4*3),tw-4,h-4),fill=barcolor,outline=None,width=1)
        draw.rectangle(xy=(x+4+((tw-x)/4*1),y+4+(h/8*barpos),x-4+((tw-x)/4*3),y-4+(h/8*7)),fill=barcolor,outline=None,width=1)
        for j in range(8):
            draw.rectangle(xy=(x+6+((tw-x)/4*3),y+(h/4)+((h/2/8)*j),x+26+((tw-x)/4*3),y+(h/4)+((h/2/8)*j)),fill=colorC0C0C0,outline=colorC0C0C0,width=3)
        tt = v + "°"
        ttw,tth = draw.textsize(tt, fontDeja48)
        ox,oy = fontDeja48.getoffset(tt)
        ttw += ox
        tth += oy
        draw.text((x+w-ttw,y+(h/2)),tt,font=fontDeja48,fill=colorFFFFFF,stroke_width=1)
        tt = "Temp"
        ttw,tth = draw.textsize(tt, fontDeja24)
        ox,oy = fontDeja24.getoffset(tt)
        ttw += ox
        tth += oy
        draw.text(xy=(x+(w/2)-(ttw/2),y+((h/8)*1)-(tth/2)),text=tt,font=fontDeja24,fill=colorFFFFFF,stroke_width=1)
    if icon == "piestorage":
        if list(v.split())[5] == "error":
            drawicon(draw,"pieerror",x,y,w,h)
            return
        pct = int(list(v.split())[4].replace("%",""))
        gbf = list(v.split())[3]
        pad = 30
        ox = 3
        oy = 3
        if pct == 50:
            ox = 0
        if pct > 50:
            ox = ox * -1
        sa = 0
        ea = sa + math.floor(pct*3.6)
        slicecolor = colorC0FFC0
        textcolor = color000000
        if pct > 80:
            slicecolor = colorFFFF00
            textcolor = color000000
        if pct > 90:
            slicecolor = colorFF0000
            textcolor = colorFFFFFF
        draw.pieslice(xy=(x+pad+ox,y+pad+oy,x+w+ox-pad,y+h+oy-pad),start=sa,end=ea,fill=slicecolor,outline=colorC0C0C0,width=2)
        tt = "used"
        ttw,tth = draw.textsize(tt, fontDeja16)
        ox,oy = fontDeja16.getoffset(tt)
        ttw += ox
        tth += oy
        draw.text(xy=(x+(w/2),y+(h/2)+(tth/2)),text=tt,font=fontDeja16,fill=textcolor)
        ox = ox * -1
        oy = oy * -1
        sa = ea
        ea = 360
        textcolor = colorFFFFFF
        draw.pieslice(xy=(x+pad+ox,y+pad+oy,x+w+ox-pad,y+h+oy-pad),start=sa,end=ea,fill=color000000,outline=colorC0C0C0,width=2)
        tt = "free"
        ttw,tth = draw.textsize(tt, fontDeja16)
        ox,oy = fontDeja16.getoffset(tt)
        ttw += ox
        tth += oy
        draw.text(xy=(x+(w/2),y+(h/2)-(tth/2)+oy-pad),text=tt,font=fontDeja16,fill=textcolor)
        tt = gbf + " free"
        ttw,tth = draw.textsize(tt, fontDeja20)
        ox,oy = fontDeja20.getoffset(tt)
        ttw += ox
        tth += oy
        draw.text(xy=(x+(w/2)-(ttw/2),y+h-(tth/2)-10),text=tt,font=fontDeja20,fill=colorFFFFFF)
    if icon == "sdcard":
        drawicon(draw,"piestorage",x,y,w,h,v)
        tt = "/dev/root"
        ttw,tth = draw.textsize(tt, fontDeja24)
        ox,oy = fontDeja24.getoffset(tt)
        ttw += ox
        tth += oy
        draw.text(xy=(x+((w/2)-(ttw/2))+1,y+(tth/2)+1-10),text=tt,font=fontDeja24,fill=color000000,stroke_width=3)
        draw.text(xy=(x+((w/2)-(ttw/2)),y+(tth/2)-10),text=tt,font=fontDeja24,fill=colorFFFFFF,stroke_width=1)
    if icon == "hdd":
        drawicon(draw,"piestorage",x,y,w,h,v)
        tt = "/dev/sda1"
        ttw,tth = draw.textsize(tt, fontDeja24)
        ox,oy = fontDeja24.getoffset(tt)
        ttw += ox
        tth += oy
        draw.text(xy=(x+((w/2)-(ttw/2))+1,y+(tth/2)+1-10),text=tt,font=fontDeja24,fill=color000000,stroke_width=3)
        draw.text(xy=(x+((w/2)-(ttw/2)),y+(tth/2)-10),text=tt,font=fontDeja24,fill=colorFFFFFF,stroke_width=1)
    if icon == "cpuload":
        tt = "CPU Load"
        ttw,tth = draw.textsize(tt, fontDeja24)
        ox,oy = fontDeja24.getoffset(tt)
        ttw += ox
        tth += oy
        draw.text(xy=(x+(w/2)-(ttw/2),y+((h/8)*1)-(tth/2)),text=tt,font=fontDeja24,fill=colorFFFFFF,stroke_width=1)
        tt = "1 min"
        ttw,tth = draw.textsize(tt, fontDeja16)
        ox,oy = fontDeja16.getoffset(tt)
        ttw += ox
        tth += oy
        draw.text(xy=(x,y+((h/8)*3)-(tth/2)),text=tt,font=fontDeja16,fill=colorFFFFFF)
        tt = "5 min"
        ttw,tth = draw.textsize(tt, fontDeja16)
        ox,oy = fontDeja16.getoffset(tt)
        ttw += ox
        tth += oy
        draw.text(xy=(x,y+((h/8)*5)-(tth/2)),text=tt,font=fontDeja16,fill=colorFFFFFF)
        tt = "15 min"
        ttw,tth = draw.textsize(tt, fontDeja16)
        ox,oy = fontDeja16.getoffset(tt)
        ttw += ox
        tth += oy
        draw.text(xy=(x,y+((h/8)*7)-(tth/2)),text=tt,font=fontDeja16,fill=colorFFFFFF)
        for j in range(3):
            draw.rounded_rectangle(xy=(x+ttw+3,y+((h/8)*((j*2)+2))+3,x+w,y+((h/8)*((j*2)+4))-3),radius=4,outline=colorC0C0C0,width=2)
            ld = list(v.split())[j]
            ldw = int(((x+w)-(x+ttw+3)) * (float(ld)/float(getprocessorcount())))
            barcolor=colorC0FFC0
            if float(ld) > .50:
                barcolor=colorFFFF00
            if float(ld) > .75:
                barcolor=colorFF0000
            draw.rounded_rectangle(xy=(x+ttw+3+1,y+((h/8)*((j*2)+2))+4,x+ttw+3+1+ldw,y+((h/8)*((j*2)+4))-3-1),radius=4,fill=barcolor,width=1)
    if icon == "memory":
        l = list(v.split())[0]
        p = list(v.split())[1]
        pad = 20
        draw.arc(xy=(x+pad,y+(pad*2),x+w-pad,y+h),start=120,end=420,fill=colorC0C0C0,width=20)
        draw.arc(xy=(x+pad+2,y+(pad*2)+2,x+w-pad-2,y+h-2),start=120+1,end=420-1,fill=color000000,width=16)
        arccolor=colorC0FFC0
        if int(p) == 0:
            p = "1"
        if int(p) > 75:
            arccolor=colorFFFF00
        if int(p) > 90:
            arccolor=colorFF0000
        ea=120+int((420-120)*(float(p)/100))
        draw.arc(xy=(x+pad+2,y+(pad*2)+2,x+w-pad-2,y+h-2),start=120,end=ea,fill=arccolor,width=16)
        tt = l
        ttw,tth = draw.textsize(tt, fontDeja24)
        ox,oy = fontDeja24.getoffset(tt)
        ttw += ox
        tth += oy
        draw.text(xy=(x+(w/2)-(ttw/2),y+((h/8)*1)-(tth/2)),text=tt,font=fontDeja24,fill=colorFFFFFF,stroke_width=1)
        tt = p + "%"
        ttw,tth = draw.textsize(tt, fontDeja20)
        ox,oy = fontDeja20.getoffset(tt)
        ttw += ox
        tth += oy
        draw.text(xy=(x+(w/2)-(ttw/2)+1,y+((h/8)*5)-(tth/2)+1),text=tt,font=fontDeja20,fill=color000000)
        draw.text(xy=(x+(w/2)-(ttw/2),y+((h/8)*5)-(tth/2)),text=tt,font=fontDeja20,fill=colorFFFFFF)
    if icon == "datetime":
        dt = "as of " + getdateandtime()
        dtw,dth = draw.textsize(dt, fontDeja12)
        ox,oy = fontDeja12.getoffset(dt)
        dtw += ox
        dth += oy
        draw.text((w-dtw,h-dth), dt, font=fontDeja12, fill=colorFFFFFF)

def getdateandtime():
    now = datetime.utcnow()
    return now.strftime("%Y-%m-%d %H:%M:%S")

def createimage(width=480, height=320):
    bw=width/3
    bh=height/2
    im = Image.new(mode="RGB", size=(width, height))
    draw = ImageDraw.Draw(im)
    drawicon(draw,"thermometer",5,5,bw-10,bh-10,v=str(gettemp()))
    drawicon(draw,"sdcard",5+bw,5,bw-10,bh-10,v=str(getdrivefree("/dev/root")))
    drawicon(draw,"hdd",5+bw+bw,5,bw-10,bh-10,v=str(getdrivefree("/dev/sda1")))
    drawicon(draw,"cpuload",5,bh+5,bw,bh-10,v=str(getloadavg()))
    drawicon(draw,"memory",5+bw,bh+5,bw,bh-10,v=str(getmemusage("Mem","RAM")))
    drawicon(draw,"memory",5+bw+bw,bh+5,bw,bh-10,v=str(getmemusage("Swap","Swap")))
    drawicon(draw,"datetime",0,0,width,height)
    im.save(outputFile)

def gettemp():
    cmd = "cat /sys/class/thermal/thermal_zone0/temp"
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
        temp = int(cmdoutput)
        return math.floor(temp/1000)
    except subprocess.CalledProcessError as e:
        return -1

def getdrivefree(path):
    cmd = "df -h | grep " + path
    try:
        return subprocess.check_output(cmd, shell=True).decode("utf-8")
    except subprocess.CalledProcessError as e:
        return path + " 0G 0G 0G 1% error"

def getloadavg():
    cmd = "cat /proc/loadavg"
    try:
        return subprocess.check_output(cmd, shell=True).decode("utf-8")
    except subprocess.CalledProcessError as e:
        return "1.00 1.00 1.00 9 99999"

def getprocessorcount():
    cmd = "cat /proc/cpuinfo | grep processor | wc -l"
    try:
        return int(subprocess.check_output(cmd, shell=True).decode("utf-8"))
    except subprocess.CalledProcessError as e:
        return 4

def getmemusage(memtype,label):
    cmd = "free --mebi | grep " + memtype
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
        t = list(cmdoutput.split())[1]
        u = list(cmdoutput.split())[2]
        v = int((float(u)/float(t))*100)
        return label + " " + str(v)
    except subprocess.CalledProcessError as e:
        return label + " ?"



while True:
    createimage()
    time.sleep(30)
