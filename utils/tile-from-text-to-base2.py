#! /usr/bin/env python3
from datetime import datetime
from PIL import Image, ImageFilter, ImageDraw, ImageFont, ImageColor
import json
import locale
import math
import numpy
import random
import subprocess
import time
import sys

# Configuration =================================================================================
outputFile="../imageoutput/tile-from-text-to-base2.png"
# 1 - Number of Tiles Wide
tilesWide = 1
# 2 - Width of Tile in Pixels
tileSize = 32
# 3 - On Color in Hex
colorOn=ImageColor.getrgb("#277dd8")
# 4 - Off Color in Hex
colorOff=ImageColor.getrgb("#1f75d8")
colorOff2=ImageColor.getrgb("#176dd8")
colorOff3=ImageColor.getrgb("#0f65d8")
colorOff4=ImageColor.getrgb("#075dd8")
colorOff5=ImageColor.getrgb("#0055d8")

# 5 - Text
text="""Bitcoin: A Peer-to-Peer Electronic Cash System

Satoshi Nakamoto
satoshin@gmx.com
www.bitcoin.org

Abstract. A purely peer-to-peer version of electronic cash would allow online
payments to be sent directly from one party to another without going through a
financial institution. Digital signatures provide part of the solution, but the main
benefits are lost if a trusted third party is still required to prevent double-spending.
We propose a solution to the double-spending problem using a peer-to-peer network.
The network timestamps transactions by hashing them into an ongoing chain of
hash-based proof-of-work, forming a record that cannot be changed without redoing
the proof-of-work. The longest chain not only serves as proof of the sequence of
events witnessed, but proof that it came from the largest pool of CPU power. As
long as a majority of CPU power is controlled by nodes that are not cooperating to
attack the network, they'll generate the longest chain and outpace attackers. The
network itself requires minimal structure. Messages are broadcast on a best effort
basis, and nodes can leave and rejoin the network at will, accepting the longest
proof-of-work chain as proof of what happened while they were gone.
"""

def writebyte(draw,width,x,y,bs):
    while(len(bs)):
        bc = bs[0]
        if bc == "0":
            draw.point(xy=[x,y],fill=colorOff)
            if (x*y) % 3 == 1:
                draw.point(xy=[x,y],fill=colorOff2)
            if (x*y) % 5 >= 3:
                draw.point(xy=[x,y],fill=colorOff3)
            if (x*y) % 7 >= 5:
                draw.point(xy=[x,y],fill=colorOff4)
            if (x*y) % 11 >= 7:
                draw.point(xy=[x,y],fill=colorOff5)
        else:
            draw.point(xy=[x,y],fill=colorOn)
        bs = bs[1:len(bs)]
        x += 1
        if x == width:
            x = 0
            y += 1
    return x, y

def createimage():
    global outputFile
    global tilesWide
    global tileSize
    global colorOn
    global colorOff
    global text
    bitsPerByte    = 7
    characterCount = len(text)
    pixelLength    = characterCount * bitsPerByte
    width          = tilesWide * tileSize
    height         = int(pixelLength / width)
    if (pixelLength % width > 0):
        height += 1
    if (height % tileSize > 0):
        height += (tileSize - (height % tileSize))
    im             = Image.new(mode="RGB", size=(width, height))
    draw           = ImageDraw.Draw(im)
    x              = 0
    y              = 0
    while(len(text)):
        currentCharacter = text[0]
        n = ord(currentCharacter)
        bs = "00000000" + bin(n)[2:]
        bs = bs[len(bs) - bitsPerByte:]
        x,y = writebyte(draw,width,x,y,bs)
        text = text[1:len(text)]
    if x <= width or y <= height:
        # end of text marker
        bs = "00000000" + bin(3)[2:]
        bs = bs[len(bs) - bitsPerByte:]
        x,y = writebyte(draw,width,x,y,bs)
        # random ascii flood
        while x + (x*y) < width * height:
            n = int(random.random() * (126-32)) + 32
            bs = "00000000" + bin(n)[2:]
            bs = bs[len(bs) - bitsPerByte:]
            x,y = writebyte(draw,width,x,y,bs)
    im.save(outputFile)

createimage()
