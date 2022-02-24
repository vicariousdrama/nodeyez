# import packages
from datetime import datetime
from PIL import ImageColor, ImageFont
import time

colorFFFFFF=ImageColor.getrgb("#ffffff")

def getdateandtime():
    now = datetime.utcnow()
    return now.strftime("%Y-%m-%d %H:%M:%S")

def getfont(size, isbold=False):
    if isbold:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",size)
    else:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",size)

def gettextdimensions(draw, s, fontsize, isbold=False):
    thefont = getfont(fontsize, isbold)
    sw,sh = draw.textsize(s, thefont)
    return sw,sh,thefont

def drawcenteredtext(draw, s, fontsize, x, y, textcolor=colorFFFFFF, isbold=False):
    sw,sh,thefont = gettextdimensions(draw, s, fontsize, isbold)
    ox,oy = thefont.getoffset(s)
    sw += ox
    sh += oy
    draw.text(xy=(x-(sw/2),y-(sh/2)), text=s, font=thefont, fill=textcolor)

def drawbottomlefttext(draw, s, fontsize, x, y, textcolor=colorFFFFFF, isbold=False):
    sw,sh,thefont = gettextdimensions(draw, s, fontsize, isbold)
    ox,oy = thefont.getoffset(s)
    sw += ox
    sh += oy
    draw.text(xy=(x,y-sh), text=s, font=thefont, fill=textcolor)

def drawbottomrighttext(draw, s, fontsize, x, y, textcolor=colorFFFFFF, isbold=False):
    sw,sh,thefont = gettextdimensions(draw, s, fontsize, isbold)
    ox,oy = thefont.getoffset(s)
    sw += ox
    sh += oy
    draw.text(xy=(x-sw,y-sh), text=s, font=thefont, fill=colorFFFFFF)

def drawtoplefttext(draw, s, fontsize, x, y, textcolor=colorFFFFFF, isbold=False):
    sw,sh,thefont = gettextdimensions(draw, s, fontsize, isbold)
    ox,oy = thefont.getoffset(s)
    sw += ox
    sh += oy
    draw.text(xy=(x,y), text=s, font=thefont, fill=textcolor)

def drawtoprighttext(draw, s, fontsize, x, y, textcolor=colorFFFFFF, isbold=False):
    sw,sh,thefont = gettextdimensions(draw, s, fontsize, isbold)
    ox,oy = thefont.getoffset(s)
    sw += ox
    sh += oy
    draw.text(xy=(x-sw,y), text=s, font=thefont, fill=textcolor)

def drawrighttext(draw, s, fontsize, x, y, textcolor=colorFFFFFF, isbold=False):
    sw,sh,thefont = gettextdimensions(draw, s, fontsize, isbold)
    ox,oy = thefont.getoffset(s)
    sw += ox
    sh += oy
    draw.text(xy=(x-sw,y-(sh/2)), text=s, font=thefont, fill=textcolor)

def drawlefttext(draw, s, fontsize, x, y, textcolor=colorFFFFFF, isbold=False):
    sw,sh,thefont = gettextdimensions(draw, s, fontsize, isbold)
    ox,oy = thefont.getoffset(s)
    sw += ox
    sh += oy
    draw.text(xy=(x,y-(sh/2)), text=s, font=thefont, fill=textcolor)
