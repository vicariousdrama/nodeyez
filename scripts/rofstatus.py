#! /usr/bin/python3
from datetime import datetime
from PIL import Image, ImageFilter, ImageDraw, ImageFont, ImageColor
from os.path import exists
import json
import math
import subprocess
import sys
import time
import vicariousbitcoin
import vicarioustext

def xy4nodeindex(index, total, center, radius):
    degrees=360/total
    degreeso=-90+(degrees/2)
    angle=index*degrees-degreeso
    x = center[0] + radius * math.cos(angle * math.pi / 180)
    y = center[1] + radius * math.sin(angle * math.pi / 180)
    return (x,y)

def createimage(nodesonline, nodeschannel, nodesinfos, nodes, width=480, height=320):
    padding=height/10
    nodesize=(padding*1.4)/1
    cx = height/2
    cy = height/2
    thickness=10
    radius=(height - (padding*2))/2
    nodecount=len(nodes)
    degrees=360/nodecount
    degreeso=-90+(degrees/2)
    im = Image.new(mode="RGB", size=(width, height))
    draw = ImageDraw.Draw(im)
    # for non-existant channels between nodes
    breaksize=20
    breakcolor=coloroffline
    # draw the main ring
    draw.ellipse(xy=(padding, padding, height-padding, height-padding), outline=colorcircle, width=thickness)
    # draw the crosscutting from channels
    nodenumber = -1
    for nodestatus in nodesonline:
        nodenumber = nodenumber+1
        # find center of node circle
        xy=xy4nodeindex(nodenumber+1, nodecount, (cx,cy),radius)
        x=xy[0]
        y=xy[1]
        # iterate all channels of this node, look for cross cutting channels
        if "channels" in nodesinfos[nodenumber]:
            for channel in nodesinfos[nodenumber]["channels"]:
                pub1 = channel["node1_pub"]
                pub2 = channel["node2_pub"]
                for nidx in range(nodecount):
                    if nidx != nodenumber:
                        pubthis = nodes[nodenumber]["pubkey"]
                        pubthat = nodes[nidx]["pubkey"]
                        if (pub1 == pubthis and pub2 == pubthat) or (pub2 == pubthis and pub1 == pubthat):
                            thatxy=xy4nodeindex(nidx+1,nodecount,(cx,cy),radius)
                            thatx=thatxy[0]
                            thaty=thatxy[1]
                            draw.line(xy=(x,y,thatx,thaty),fill=coloronline,width=int(thickness/2))
    nodenumber = -1
    # Circles for the nodes
    for nodestatus in nodesonline:
        nodenumber = nodenumber+1
        # find center of node circle
        xy=xy4nodeindex(nodenumber+1, nodecount, (cx,cy),radius)
        x=xy[0]
        y=xy[1]
        # online/offline status check for color
        nodecolor=coloroffline
        nodecolortext=colorofflinetext
        if nodestatus == 1:
            nodecolor=coloronline
            nodecolortext=coloronlinetext
        # channel with next node?
        if nodeschannel[nodenumber] == 0:
            bxy=xy4nodeindex(((nodenumber*2)+1), nodecount*2, (cx,cy), radius)
            bx=xy[0]
            by=xy[1]
#            vicarioustext.drawcenteredtext(draw,btt,24,bx,by,breakcolor)
        # sidebar text
        operator = str(nodenumber) + ". " + nodes[nodenumber]["operator"]
        vicarioustext.drawtoplefttext(draw, operator, 16, height, int(nodenumber*(height/nodecount)), nodecolor)
        # node circle and text label
        draw.ellipse(xy=(x-(nodesize/2), y-(nodesize/2), x+(nodesize/2), y+(nodesize/2)), fill=nodecolor, outline=colorcircle, width=1)
        if nodestatus == 0:
            draw.ellipse(xy=(x-((nodesize/2)+3), y-((nodesize/2)+3), x+((nodesize/2)+3), y+((nodesize/2)+3)), fill=None, outline=nodecolor, width=1)
            draw.ellipse(xy=(x-((nodesize/2)+6), y-((nodesize/2)+6), x+((nodesize/2)+6), y+((nodesize/2)+6)), fill=None, outline=nodecolor, width=1)
        vicarioustext.drawcenteredtext(draw, str(nodenumber), 24, x, y, nodecolortext)
    # Ring name
    vicarioustext.drawcenteredtext(draw, ringname, 24, cx+1, cy+1, colortextshadow)
    vicarioustext.drawcenteredtext(draw, ringname, 24, cx-1, cy-1, colortext)
    # Date and Time
    vicarioustext.drawbottomrighttext(draw, "as of " + vicarioustext.getdateandtime(), 12, width, height)
    # Save to file
    im.save(outputFile)

def getnodeinfo(pubkey):
    cmd = "lncli getnodeinfo --pub_key " + pubkey + " --include_channels 2>&1"
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
    except subprocess.CalledProcessError as e:
        cmdoutput = "{\"node\":{\"alias\":\"" + pubkey + "\",\"pub_key\":\"" + pubkey + "\",\"addresses\":[{\"network\":\"tcp\",\"addr\":\"0.0.0.0:65535\"}]}}"
    j = json.loads(cmdoutput)
    return j

def getnodealias(nodeinfo):
    return nodeinfo["node"]["alias"]

def getnodeaddress(nodeinfo):
    bestresult = ""
    for addr in nodeinfo["node"]["addresses"]:
        nodehostandport = addr["addr"]
        if bestresult == "":
            bestresult = nodehostandport
        elif "onion" in nodehostandport:
            if "onion" not in bestresult:
                bestresult = nodehostandport
            elif len(nodehostandport) > 56:
                bestresult = nodehostandport
    return bestresult

def getnodepeers():
    cmd = "lncli listpeers 2>&1"
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
        return cmdoutput
    except subprocess.CalledProcessError as e:
        return '{\"peers\": []}'

def isnodeconnected(pubkey):
    nodepeers = getnodepeers()
    j = json.loads(nodepeers)
    for peer in j["peers"]:
        if pubkey == peer["pub_key"]:
            return True
    return False

def attemptconnect(nodeinfo):
    nodestatus = 0
    pubkey = nodeinfo["node"]["pub_key"]
    addr = getnodeaddress(nodeinfo)
    if addr == "0.0.0.0:65535":
        return 0
    cmd = "lncli connect " + pubkey + "@" + addr + " --timeout 5s 2>&1"
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
        if "error" in cmdoutput:
            nodestatus = 0
        else:
            cmd = "lncli disconnect " + pubkey + " 2>&1"
            try:
                cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
                if "error" in cmdoutput:
                    nodestatus = 0
                else:
                    nodestatus = 1
            except subprocess.CalledProcessError as e2:
                nodestatus = 0
    except subprocess.CalledProcessError as e:
        nodestatus = 0
    return nodestatus

def getnodealiasandstatus(pubkey, nextnodepubkey):
    nodeinfo = getnodeinfo(pubkey)
    nodealias = getnodealias(nodeinfo)
    nodeonline = 0
    if isnodeconnected(pubkey):
        nodeonline = 1
    else:
        nodeonline = attemptconnect(nodeinfo)
    # look if there is a channel
    haschannel = 0
    if "channels" in nodeinfo:
        for channel in nodeinfo["channels"]:
            node1_pub = channel["node1_pub"]
            node2_pub = channel["node2_pub"]
            if pubkey == node1_pub and nextnodepubkey == node2_pub:
                haschannel = 1
                break
            if pubkey == node2_pub and nextnodepubkey == node1_pub:
                haschannel = 1
                break
    return (nodealias, nodeonline, haschannel, nodeinfo)

def checknodestatus(nodes):
    nodealiases=[]
    nodeonline=[]
    nodechannel=[]
    nodeinfos=[]
    nlen = len(nodes)
    for n in range(nlen):
        l=list(nodes)
        node=l[n]
        nextnodeidx=n+1
        if nextnodeidx >= nlen:
            nextnodeidx=0
        nextnode=l[nextnodeidx]
        nodepubkey = node["pubkey"]
        nodeoperator = node["operator"]
        nextnodepubkey = nextnode["pubkey"]
        nodeas = getnodealiasandstatus(nodepubkey, nextnodepubkey)
        nodealiases.append(nodeas[0])
        nodeonline.append(nodeas[1])
        nodechannel.append(nodeas[2])
        nodeinfos.append(nodeas[3])
    createimage(nodeonline, nodechannel, nodeinfos, nodes)

def getcolorconfig(config, colorid):
    colors = config["imagesettings"]["colors"]
    return ImageColor.getrgb(colors[colorid])

def setfontandcolor(config):
    global colorcircle, coloroffline, coloronline, colorofflinetext, coloronlinetext, colortext, colortextshadow
    # color config
    colorcircle = getcolorconfig(config, "circle")
    coloroffline = getcolorconfig(config, "offline")
    coloronline = getcolorconfig(config, "online")
    colorofflinetext = getcolorconfig(config, "offlinetext")
    coloronlinetext = getcolorconfig(config, "onlinetext")
    colortext = getcolorconfig(config, "text")
    colortextshadow = getcolorconfig(config, "textshadow")


if __name__ == '__main__':
    # Defaults
    configFile="/home/bitcoin/nodeyez/config/rofstatus.json"
    # Require configuration
    if not exists(configFile):
        print(f"You need to make a config file at {configFile}")
        exit(1)
    # Load configuration (there is no defaults, everything is in the config)
    with open(configFile) as f:
        config = json.load(f)
    # Loop
    while True:
        # iterate the rings
        for ring in config["rings"]:
            outputFile = ring["imagefilename"]
            ringname = ring["name"]
            print(f"Creating ring of fire image for ring {ringname} at {outputFile}")
            if "imagesettings" in ring:
                setfontandcolor(ring)
            else:
                setfontandcolor(config)
            checknodestatus(ring["nodes"])
        time.sleep(int(config["sleepInterval"]))
