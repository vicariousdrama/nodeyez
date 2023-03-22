#! /usr/bin/env python3
from PIL import Image, ImageDraw

sourceFile="../images/nodeyez-catseyes.png"
outputFile="../imageoutput/logo.png"
stretchEdge=True

def createimage(width=480, height=320):

    sourceImage=Image.open(sourceFile)
    sourceWidth=int(sourceImage.getbbox()[2])
    sourceHeight=int(sourceImage.getbbox()[3])
    sourceRatio=float(sourceWidth)/float(sourceHeight)

    imageRatio=float(width)/float(height)

    if sourceRatio > imageRatio:
        print("need to extend top and bottom")
        newSourceHeight=int(sourceWidth/imageRatio)
        print(f"original width x height is {sourceWidth} x {sourceHeight}.  New ratio height {newSourceHeight}")
        offset = int((newSourceHeight-sourceHeight)/2)
        imTaller = Image.new(mode="RGB", size=(sourceWidth, newSourceHeight))
        imTaller.paste(sourceImage, (0, offset))
        if stretchEdge:
            imLine = sourceImage.crop((0,0,sourceWidth,1))
            for y in range(offset):
                imTaller.paste(imLine, (0, y))
            imLine = sourceImage.crop((0,sourceHeight-1,sourceWidth,sourceHeight))
            for y in range(offset):
                imTaller.paste(imLine, (0, y+offset+sourceHeight))
        im = imTaller.resize(size=(width,height))

    if imageRatio > sourceRatio:
        print("need to extend sides")
        newSourceWidth=int(sourceHeight * imageRatio)
        print(f"original width x height is {sourceWidth} x {sourceHeight}.  New ratio width {newSourceWidth}")
        offset = int((newSourceWidth-sourceWidth)/2)
        imWider = Image.new(mode="RGB", size=(newSourceWidth, sourceHeight))
        imWider.paste(sourceImage, (offset, 0))
        if stretchEdge:
            imLine = sourceImage.crop((0,0,1,sourceHeight))
            for x in range(offset):
                imWider.paste(imLine, (x, 0))
            imLine = sourceImage.crop((sourceWidth-1,0,sourceWidth,sourceHeight))
            for x in range(offset):
                imWider.paste(imLine, (x+offset+sourceWidth, 0))
        im = imWider.resize(size=(width,height))

    if imageRatio == sourceRatio:
        print("same ratio")
        im = sourceImage.resize(size=(width,height))


    im.save(outputFile)


createimage()
