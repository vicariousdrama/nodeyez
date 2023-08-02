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

def getmaxfontsize(draw, s, maxwidth=480, maxheight=320, isbold=False, maxfontsize=128, minfontsize=8):
    sw = maxwidth
    sh = maxheight
    fontsize = maxfontsize + 1
    while (sw >= maxwidth or sh >= maxheight) and fontsize >= minfontsize:
        fontsize = fontsize - 1
        sw,sh,thefont = gettextdimensions(draw, s, fontsize, isbold)
    return fontsize,sw,sh

def getmaxtextforwidth(draw, words, width, fontsize, isbold=False):
    wlen = len(words)
    if wlen == 0:
        return "", []
    for x in range(wlen, 1, -1):
        s = " ".join(words[0:x])
        sw,sh,f = gettextdimensions(draw, s, fontsize, isbold)
        if sw <= width:
            return s, words[x:]
    return " ".join(words[0:1]), []

def gettextdimensions(draw, s, fontsize, isbold=False):
    thefont = getfont(fontsize, isbold)
    # Deprecated, removed in Pillow 10.0.0
    #sw,sh = draw.textsize(s, thefont)
    # New in 8.0.0, required in Pillow 10.0.0
    left, top, right, bottom = thefont.getbbox(text=s)
    return right, bottom, thefont

def gettextoffset(thefont,s):
    # Deprecated, removed in Pillow 10.0.0
    #ox,oy = thefont.getoffset(s)
    # New in 8.0.0, required in Pillow 10.0.0
    left,top,_,_ = thefont.getbbox(text=s)
    return left, top

def drawcenteredtext(draw, s, fontsize, x, y, textcolor=colorFFFFFF, isbold=False):
    sw,sh,thefont = gettextdimensions(draw, s, fontsize, isbold)
    ox,oy = gettextoffset(thefont,s)
    sw += ox
    sh += oy
    draw.text(xy=(x-(sw/2),y-(sh/2)), text=s, font=thefont, fill=textcolor)

def drawbottomlefttext(draw, s, fontsize, x, y, textcolor=colorFFFFFF, isbold=False):
    sw,sh,thefont = gettextdimensions(draw, s, fontsize, isbold)
    ox,oy = gettextoffset(thefont,s)
    sw += ox
    sh += oy
    draw.text(xy=(x,y-sh), text=s, font=thefont, fill=textcolor)

def drawbottomrighttext(draw, s, fontsize, x, y, textcolor=colorFFFFFF, isbold=False):
    sw,sh,thefont = gettextdimensions(draw, s, fontsize, isbold)
    ox,oy = gettextoffset(thefont,s)
    sw += ox
    sh += oy
    draw.text(xy=(x-sw,y-sh), text=s, font=thefont, fill=textcolor)

def drawLabel(draw, s="", fontsize=12, anchorposition="tl", anchorx=0, anchory=0, backgroundColor="#000000", textColor="#ffffff", borderColor="#888888"):
    sw,sh,f = gettextdimensions(draw, s, fontsize, False)
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
    elif anchorposition == "c":
        nx = anchorx - (sw/2)
        ny = anchory - (sh/2)
    draw.rectangle(xy=[(nx-padding-border,ny-padding-border),(nx+sw+padding+border,ny+sh+padding+border)],fill=ImageColor.getrgb(backgroundColor),outline=ImageColor.getrgb(borderColor),width=1)
    draw.text(xy=(nx,ny), text=s, font=f, fill=ImageColor.getrgb(textColor))

def drawtoplefttext(draw, s, fontsize, x, y, textcolor=colorFFFFFF, isbold=False):
    sw,sh,thefont = gettextdimensions(draw, s, fontsize, isbold)
    ox,oy = gettextoffset(thefont,s)
    sw += ox
    sh += oy
    draw.text(xy=(x,y), text=s, font=thefont, fill=textcolor)

def drawtoprighttext(draw, s, fontsize, x, y, textcolor=colorFFFFFF, isbold=False):
    sw,sh,thefont = gettextdimensions(draw, s, fontsize, isbold)
    ox,oy = gettextoffset(thefont,s)
    sw += ox
    sh += oy
    draw.text(xy=(x-sw,y), text=s, font=thefont, fill=textcolor)

def drawrighttext(draw, s, fontsize, x, y, textcolor=colorFFFFFF, isbold=False):
    sw,sh,thefont = gettextdimensions(draw, s, fontsize, isbold)
    ox,oy = gettextoffset(thefont,s)
    sw += ox
    sh += oy
    draw.text(xy=(x-sw,y-(sh/2)), text=s, font=thefont, fill=textcolor)

def drawlefttext(draw, s, fontsize, x, y, textcolor=colorFFFFFF, isbold=False):
    sw,sh,thefont = gettextdimensions(draw, s, fontsize, isbold)
    ox,oy = gettextoffset(thefont,s)
    sw += ox
    sh += oy
    draw.text(xy=(x,y-(sh/2)), text=s, font=thefont, fill=textcolor)
