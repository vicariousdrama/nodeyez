from PIL import Image, ImageColor
import numpy as np
import random
import vicariousnetwork

def adjustcolor(imInput, fromRGB, toRGB):
    im = imInput.convert('RGBA')
    data = np.array(im)
    red,green,blue,alpha = data.T
    colorset = (red==fromRGB[0]) & (green==fromRGB[1]) & (blue==fromRGB[2])
    data[...,:-1][colorset.T]=toRGB
    imOutput = Image.fromarray(data)
    return imOutput

def getrandomcolor():
    r=random.randint(48,255)
    g=random.randint(48,255)
    b=random.randint(48,255)
    return (r,g,b)

def adjustalpha(imInput, reducealpha):
    if reducealpha == 0:
        return imInput
    # todo: adjust alpha up or down
    im = imInput.convert('RGBA')
    data = np.array(im)
    data[:,:,3] -= abs(reducealpha) # 64 # alpha
    imOutput = Image.fromarray(data)
    return imOutput

def resizeToWidth(imInput, desiredWidth):
    w = imInput.width
    h = imInput.height
    if w == desiredWidth:
        return imInput
    else:
        r = desiredWidth / w
        nw = int(w * r)
        nh = int(h * r)
        imOutput = imInput.resize((nw,nh))
        return imOutput

svgfile = None
def getsvgfile():
    global svgfile
    if svgfile is None:
#        svgfile = vicariousnetwork.getimagefromurl(True,"https://raw.githubusercontent.com/vicariousdrama/nodeyez/main/images/nodeyez.svg")
        svgfile = vicariousnetwork.getimagefromurl(True,"file://../images/nodeyez.svg")
    return svgfile

def do(canvas, width=80, box=(0,0), reducealpha=0, recolor=True, recolortorandom=True, recolorfrom=(102,102,102), recolorto=(255,255,255)):
    wm = getsvgfile()
    if recolor == True:
        if recolortorandom == True:
            recolorto=getrandomcolor()
        wm = adjustcolor(wm, recolorfrom, recolorto)
    wm = adjustalpha(wm, reducealpha)
    wm = resizeToWidth(wm, width)
    wmlayer = Image.new(mode="RGBA", size=(canvas.width, canvas.height), color=(00,00,00,00))
    wmlayer.paste(wm, box)
    canvas.alpha_composite(wmlayer)
