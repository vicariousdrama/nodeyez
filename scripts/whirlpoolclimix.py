#! /usr/bin/env python3
from datetime import datetime, timedelta
from os.path import exists
from PIL import Image, ImageDraw, ImageColor
import json
import math
import os
import stat
import subprocess
import sys
import time
import vicarioustext
import vicariousnetwork


def gethumantime(timeinms, partcount=1):
    d = timedelta(milliseconds=timeinms)
    seconds = int(d.total_seconds() // 1)
    o = ""
    if partcount > 0 and (seconds // 86400) > 0:
        days = seconds // 86400
        o = o + ", " if len(o) > 0 else o
        o = o + str(days) + " day"
        o = o + "s" if days > 1 else ""
        partcount = partcount - 1
        seconds -= (days * 86400)
    if partcount > 0 and (seconds // 3600) > 0:
        hours = seconds // 3600
        o = o + ", " if len(o) > 0 else o
        o = o + str(hours) + " hour"
        o = o + "s" if hours > 1 else ""
        partcount = partcount - 1
        seconds -= (hours * 3600)
    if partcount > 0 and (seconds // 60) > 0:
        minutes = seconds // 60
        o = o + ", " if len(o) > 0 else o
        o = o + str(minutes) + " minute"
        o = o + "s" if minutes > 1 else ""
        partcount = partcount - 1
    if partcount > 0 and seconds > 0:
        o = o + ", " if len(o) > 0 else o
        o = o + str(seconds) + " second"
        o = o + "s" if seconds > 1 else ""
        partcount = partcount - 1
    if o == "":
        o = "now"
    else:
        o += " ago"
    return o

def btctosats(s):
    return str(int(float(s.replace("btc","")) * 100000000)) + " sats"

def getunicodebool(b):
    if b:
        return u"✓"
    else:
        return u"✗"

def stepstatus(s):
    if s == "CONNECTING":
        return "connecting..."
    if s == "CONNECTED":
        return "connected"
    if s == "REGISTERED_INPUT":
        return "input registered"
    if s == "CONFIRMING_INPUT":
        return "waiting for mix"
    if s == "CONFIRMED_INPUT":
        return "joined a mix!"
    if s == "REGISTERING_OUTPUT":
        return "registering output"
    if s == "REGISTERED_OUTPUT":
        return "output registered"
    if s == "SIGNING":
        return "signing tx"
    if s == "SIGNED":
        return "tx signed"
    if s == "REVEALED_OUTPUT":
        return "round aborted"
    if s == "SUCCESS":
        return "mix success!"
    if s == "FAIL":
        return "mix failed"
    return s

def isWhirlpoolCoordinator():
    if "udkmfc5j6zvv3ysavbrwzhwji4hpyfe3apqa6yst7c7l32mygf65g4ad.onion" in whirlpoolurl:
        return True
    if "pool.whirl.mx" in whirlpoolurl:
        return True
    return False

def drawfieldvalue(draw, label, value, left, top, right, bottom):
    centerh = left + ((right-left)//2)
    centerv = top + ((bottom-top)//2)
    colorValue = colorDataValue
    fontSize = 14
    fontBold = False
    if value == getunicodebool(True):
        colorValue = colorDataOn
        fontSize = 32
        fontBold = True
    if value == getunicodebool(False):
        colorValue = colorDataOff
        fontSize = 32
        fontBold = True
    vicarioustext.drawcenteredtext(draw, label, 16, centerh, centerv - 10, colorDataLabel, True)
    vicarioustext.drawcenteredtext(draw, value, fontSize, centerh, centerv + 10, colorValue, fontBold)

def createimage(width=480, height=320):
    headerheight = 30
    footerheight = 15
    qw = width//4
    qh = (height-(headerheight+footerheight))//5
    qt = headerheight
    clistatus = vicariousnetwork.getwhirlpoolcliconfig(useTor, whirlpoolurl, apiKey)
    mixstatus = vicariousnetwork.getwhirlpoolmix(useTor, whirlpoolurl, apiKey)
    im = Image.new(mode="RGB", size=(width, height), color=colorBackground)
    draw = ImageDraw.Draw(im)
    # Header
    vicarioustext.drawcenteredtext(draw, "Whirlpool CLI + MIX", 24, int(width/2), int(headerheight/2), colorHeader, True)
    # Basic meta data
    rv = 2 # render variant
    #print(clistatus)
    #print("---")
    #print(mixstatus)
    #print("---")
    errormsg = ""
    if "cliStatus" in clistatus:
        s_status = clistatus["cliStatus"]
        if s_status == "ERROR":
            errormsg += "\nError accessing CLI\nIs Whirlpool running?"
    s_network = clistatus["network"]
    b_tor = clistatus["tor"]
    b_dojo = clistatus["dojo"]
    b_loggedin = clistatus["loggedIn"]
    s_version = clistatus["version"]
    b_started = False
    i_mixing = 0
    i_queued = 0
    if "started" in mixstatus:
       b_started = mixstatus["started"]
    if "nbMixing" in mixstatus:
       i_mixing = mixstatus["nbMixing"]
    if "nbQueued" in mixstatus:
       i_queued = mixstatus["nbQueued"]
    if "message" in mixstatus:
        print("---")
        print(mixstatus["message"])
        if "No wallet opened" in mixstatus["message"]:
            errormsg += "\n" + mixstatus["message"]
    if "error" in mixstatus:
        if mixstatus["error"] != None:
            errormsg += "\n" + mixstatus["error"]
    errormsg = errormsg.replace(".",".\n")

    if rv == 1: # original
        drawfieldvalue(draw, "Network",   s_network,                  qw*0, qt+(qh*0), qw*1, qt+(qh*1))
        drawfieldvalue(draw, "Tor",       getunicodebool(b_tor),      qw*1, qt+(qh*0), qw*2, qt+(qh*1))
        drawfieldvalue(draw, "Dojo",      getunicodebool(b_dojo),     qw*2, qt+(qh*0), qw*3, qt+(qh*1))
        drawfieldvalue(draw, "Logged In", getunicodebool(b_loggedin), qw*3, qt+(qh*0), qw*4, qt+(qh*1))
        drawfieldvalue(draw, "Version",   s_version,                  qw*0, qt+(qh*1), qw*1, qt+(qh*2))
        drawfieldvalue(draw, "Started",   getunicodebool(b_started),  qw*1, qt+(qh*1), qw*2, qt+(qh*2))
        drawfieldvalue(draw, "Mixing",    str(i_mixing),              qw*2, qt+(qh*1), qw*3, qt+(qh*2))
        drawfieldvalue(draw, "Queued",    str(i_queued),              qw*3, qt+(qh*1), qw*4, qt+(qh*2))
    if rv == 2: # mod with all booleans on top progressing left to right
        drawfieldvalue(draw, "Tor",       getunicodebool(b_tor),      qw*0, qt+(qh*0), qw*1, qt+(qh*1))
        drawfieldvalue(draw, "Dojo",      getunicodebool(b_dojo),     qw*1, qt+(qh*0), qw*2, qt+(qh*1))
        drawfieldvalue(draw, "Logged In", getunicodebool(b_loggedin), qw*2, qt+(qh*0), qw*3, qt+(qh*1))
        drawfieldvalue(draw, "Started",   getunicodebool(b_started),  qw*3, qt+(qh*0), qw*4, qt+(qh*1))
        drawfieldvalue(draw, "Network",   s_network,                  qw*0, qt+(qh*1), qw*1, qt+(qh*2))
        drawfieldvalue(draw, "Version",   s_version,                  qw*1, qt+(qh*1), qw*2, qt+(qh*2))
        drawfieldvalue(draw, "Mixing",    str(i_mixing),              qw*2, qt+(qh*1), qw*3, qt+(qh*2))
        drawfieldvalue(draw, "Queued",    str(i_queued),              qw*3, qt+(qh*1), qw*4, qt+(qh*2))
    # Error Message
    vicarioustext.drawtoplefttext(draw, errormsg, 20, 5, int(height/2), colorDataOff, True)
    # Pools mixing
    tc = 0
    tw = width//3
    if "threads" in mixstatus:
        threadheads = ["Pool", "Mix Step", "Last Activity"]
        for t in mixstatus["threads"]:
            if tc > 0:
                threadheads = ["","",""]
            yt = qt+int(qh*(2.5 + float(tc) * 0.3)) - 16
            yb = qt+int(qh*(3.0 + float(tc) * 0.3)) - 16
            drawfieldvalue(draw, threadheads[0], btctosats(t["poolId"]),                 tw*0, yt, tw*1, yb)
            drawfieldvalue(draw, threadheads[1], stepstatus(t["mixStep"]),               tw*1, yt, tw*2, yb)
            drawfieldvalue(draw, threadheads[2], gethumantime(t["lastActivityElapsed"]), tw*2, yt, tw*3, yb)
            tc = tc + 1
    # Date and Time
    vicarioustext.drawbottomrighttext(draw, "as of " + vicarioustext.getdateandtime(), 12, width, height, colorTextFG)
    # Attribution
    attributionLine = "Data from Whirlpool Client"
    vicarioustext.drawbottomlefttext(draw, attributionLine, 16, 0, height, colorDataLabel)
    # Save to file
    im.save(outputFile)
    im.close()


if __name__ == '__main__':
    # Defaults
    configFile = "../config/whirlpoolclimix.json"
    outputFile = "../imageoutput/whirlpoolclimix.png"
    logoSamouraiFile = "../images/samourai.png"
    dataDirectory = "../data/"
    useTor=False
    whirlpoolurl="https://127.0.0.1:8899"             # Your local whirlpool cli instance
    apiKey=""
    width=480
    height=320
    sleepInterval = 300                               # controls how often this display panel is updated. 300 is once every five minutes
    colorHeader=ImageColor.getrgb("#ffffff")          # The header text color. Need to pass to also specify bolding
    colorDataLabel=ImageColor.getrgb("#aa2222")       # Color for each field label
    colorDataValue=ImageColor.getrgb("#bbbbbb")       # Color for each field value
    colorDataOn=ImageColor.getrgb("#40ff40")          # Color for on/true checkmark
    colorDataOff=ImageColor.getrgb("#ff4040")         # Color for off/false checkmark
    colorTextFG=ImageColor.getrgb("#ffffff")          # General text color other than header and data values
    colorBackground=ImageColor.getrgb("#000000")      # Background color
    # Overide defaults
    if exists(configFile):
        with open(configFile) as f:
            config = json.load(f)
        if "whirlpool" in config:
            config = config["whirlpool"]
        if "outputFile" in config:
            outputFile = config["outputFile"]
        if "useTor" in config:
            useTor = config["useTor"]
        if "whirlpoolurl" in config:
            whirlpoolurl = config["whirlpoolurl"]
        if isWhirlpoolCoordinator():
            print(f"You must specify the url to your local whirlpool instance as whirlpoolurl in {configFile}")
            exit(1)
        if "apiKey" in config:
            apiKey = config["apiKey"]
        else:
            print(f"You must configure an apiKey in {configFile}")
            exit(1)
        if "width" in config:
            width = int(config["width"])
        if "height" in config:
            height = int(config["height"])
        if "sleepInterval" in config:
            sleepInterval = int(config["sleepInterval"])
            sleepInterval = 300 if sleepInterval < 30 else sleepInterval # local, but minimum 30 seconds for sanity
        if "colorHeader" in config:
            colorHeader = ImageColor.getrgb(config["colorHeader"])
        if "colorDataLabel" in config:
            colorDataLabel = ImageColor.getrgb(config["colorDataLabel"])
        if "colorDataValue" in config:
            colorDataValue = ImageColor.getrgb(config["colorDataValue"])
        if "colorDataOn" in config:
            colorDataOn = ImageColor.getrgb(config["colorDataOn"])
        if "colorDataOff" in config:
            colorDataOff = ImageColor.getrgb(config["colorDataOff"])
        if "colorTextFG" in config:
            colorTextFG = ImageColor.getrgb(config["colorTextFG"])
        if "colorBackground" in config:
            colorBackground = ImageColor.getrgb(config["colorBackground"])
    # Data directories
    if not os.path.exists(dataDirectory):
        os.makedirs(dataDirectory)
    whirlDirectory = dataDirectory + "whirlpool/"
    if not os.path.exists(whirlDirectory):
        os.makedirs(whirlDirectory)
    # Check for single run
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h','--help']:
            print(f"Creates a summary image of Whirlpool Mix Status.")
            print(f"Usage:")
            print(f"1) Call without arguments to run continuously using the configuration or defaults")
            print(f"2) Pass with an argument other than -h or --help to run once and exit.")
            print(f"You must specify a custom configuration file at {configFile}")
            exit(0)
        else:
            print(f"Running once and exiting")
    # Loop
    while True:
        print("Creating image")
        createimage(width,height)
        print("Image created")
        if len(sys.argv) > 1:
            exit(0)
        print(f"sleeping for {sleepInterval} seconds")
        time.sleep(sleepInterval)
