#! /usr/bin/env python3
from PIL import Image, ImageDraw, ImageColor
from os.path import exists
import json
import os
import random
import subprocess
import sys
import time
import vicarioustext

def getRaretoshiUserinfo():
    global userinfo
    global userinfoLast
    userfilename = raretoshiuser + ".json"
    localfilename = raretoshiDataDirectory + userfilename
    tempfilename = localfilename + ".tmp"
    refreshUser = False
    if not exists(localfilename):
        refreshUser = True
    if userinfoInterval + userinfoLast < int(time.time()):
        refreshUser = True
    if refreshUser:
        print(f"Calling raretoshi website for user data")
        userinfoLast = int(time.time())
        url = "https://raretoshi.com/" + userfilename
        cmd = "curl -s -o " + tempfilename + " --max-time 5 " + url
        try:
            cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
            with open(tempfilename) as f:
                userinfo = json.load(f)
            if exists(localfilename):
                os.remove(localfilename)
            os.rename(tempfilename, localfilename)
        except subprocess.CalledProcessError as e:
            print(f"Error downloading and loading file {tempfilename}. Error is {e}")
            if exists(localfilename):
                print("Attempting to reload from cached result {localfilename}")
                try:
                    with open(localfilename) as f:
                        userinfo = json.load(f)
                except:
                    print("Error raised reading {localfilename} as json")
    else:
        print(f"Using cached data from {userinfoLast}")
    return userinfo

def pickRaretoshiUser(raretoshiinfo):
#    global userinfoLast
    global randomuserLast
    global raretoshiuser
    if randomuserInterval + randomuserLast < int(time.time()):
        # pick new user
 #       userinfoLast=0
        randomuserLast=int(time.time())
        userlist=[]
        # look at holdings and favorites
        if "subject" in raretoshiinfo:
            if "holdings" in raretoshiinfo["subject"]:
                for holding in raretoshiinfo["subject"]["holdings"]:
                    owner = holding["owner"]["username"]
                    if not owner in userlist:
                        userlist.append(owner)
                    artist = holding["artist"]["username"]
                    if not artist in userlist:
                        userlist.append(artist)
            if "favorites" in raretoshiinfo["subject"]:
                for favorite in raretoshiinfo["subject"]["favorites"]:
                    if "artwork" in favorite:
                        owner = favorite["artwork"]["owner"]["username"]
                        if not owner in userlist:
                            userlist.append(owner)
                        artist = favorite["artwork"]["artist"]["username"]
                        if not artist in userlist:
                            userlist.append(artist)
        # pick random index
        usercount = len(userlist)
        userindex = int(random.random() * usercount)
        raretoshiuser = userlist[userindex]


def getIPFSLocalFilename(ipfshash):
    return ipfsDataDirectory + ipfshash

def downloadIPFSfile(ipfshash):
    downloadFromRaretoshi = False
    if ipfshash.endswith(".png") or ipfshash.endswith(".jpeg"):
        # seems that avatar_url for artist and owner may not be in ipfs.io.
        # these urls also contain the file extension, which needs to be removed
        downloadFromRaretoshi = True
        ipfshash = ipfshash.replace(".png", "")
        ipfshash = ipfshash.replace(".jpeg", "")
    saveto = getIPFSLocalFilename(ipfshash)
    if exists(saveto):
        print(f"Skipping IPFS download. File already exists at {saveto}")
        return
    if downloadFromRaretoshi:
        url = "https://raretoshi.com/api/ipfs/" + ipfshash
    else:
        url = "https://ipfs.io/ipfs/" + ipfshash
    print(f"Downloading from {url}")
    cmd = "curl -s -o " + saveto + " --max-time 5 " + url
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
        print(f"IPFS Downloaded to {saveto}")
    except subprocess.CalledProcessError as e:
        print(f"error {e}")
        # If we were originally hitting IPFS, we can try fallback to raretoshi
        if url.startswith("https://ipfs.io/"):
            url = url.replace("https://ipfs.io/", "https://raretoshi.com/api/")
            print(f"Retrying with {url}")
            cmd = "curl -s -o " + saveto + " --max-time 5 " + url
            try:
                cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
                print(f"IPFS Downloaded to {saveto}")
            except:
                print(f"error {e}")

def createimage(width=480, height=320):
    # Setup alpha layer
    alpha_img = Image.new(mode="RGBA", size=(width, height), color=(255,255,255,0))
    draw = ImageDraw.Draw(alpha_img)
    print(f"Getting Raretoshi information for user {raretoshiuser}")
    raretoshiinfo = getRaretoshiUserinfo()
    holdingscount = len(raretoshiinfo["subject"]["holdings"])
    # quick bail if no holdings
    if holdingscount == 0:
        print("User has no holdings on raretoshi")
        return
    # pick a random one
    allowedfiletypes = ['image/png','image/jpeg']
    filetype = ""
    holdingchecks = 0
    while (filetype not in allowedfiletypes) and (holdingchecks < holdingscount):
        holdingchecks += 1
        holdingindex = int(random.random() * holdingscount)
        if len(sys.argv) > 2:
            holdingindex = int(sys.argv[2])
        holding = raretoshiinfo["subject"]["holdings"][holdingindex]
        filetype = holding["filetype"]
        if filetype not in allowedfiletypes:
            print(f"Holding {holdingindex} is {filetype} which is unsupported.")
            print(f"Picking another at random. Check count {holdingchecks}.")
    if holdingchecks > holdingscount:
        print(f"User has no holdings on raretoshi that match allowed types {allowedfiletypes}")
        return
    title = holding["title"]
    ipfshash = holding["filename"]
    print(f"Picked holding {holdingindex} titled {title} with ipfshash {ipfshash} ")
    downloadIPFSfile(ipfshash)
    artist = holding["artist"]["username"]
    downloadIPFSfile(holding["artist"]["avatar_url"])
    owner = holding["owner"]["username"]
    downloadIPFSfile(holding["owner"]["avatar_url"])
    sourceFile = getIPFSLocalFilename(ipfshash)
    if not exists(sourceFile):
        print(f"The file was not found at {sourceFile}")
        print(f"There may be a problem with the IPFS servers")
        slug = holding["slug"]
        print(f"This is for https://raretoshi.com/a/{slug}")
        return
    sourceImage=Image.open(sourceFile).convert("RGBA")
    sourceWidth=int(sourceImage.getbbox()[2])
    sourceHeight=int(sourceImage.getbbox()[3])
    sourceRatio=float(sourceWidth)/float(sourceHeight)
    imageRatio=float(width)/float(height)
    if sourceRatio > imageRatio:
        print("Need to extend top and bottom")
        newSourceHeight=int(sourceWidth/imageRatio)
        print(f"Original width x height is {sourceWidth} x {sourceHeight}.  New ratio height {newSourceHeight}")
        offset = int((newSourceHeight-sourceHeight)/2)
        imTaller = Image.new(mode="RGBA", size=(sourceWidth, newSourceHeight), color=colorBackground)
        imTaller.paste(sourceImage, (0, offset))
        if stretchEdge:
            # top side
            imLine = sourceImage.crop((0,0,sourceWidth,1))
            for y in range(offset-stretchSpacing):
                imTaller.paste(imLine, (0, y))
            # bottom side
            imLine = sourceImage.crop((0,sourceHeight-stretchSpacing,sourceWidth,sourceHeight))
            for y in range(offset-stretchSpacing):
                imTaller.paste(imLine, (0, y+offset+sourceHeight+stretchSpacing))
        print(f"Resizing to {width} x {height}")
        im = imTaller.resize(size=(width,height))
    if imageRatio > sourceRatio:
        print("Need to extend sides")
        newSourceWidth=int(sourceHeight * imageRatio)
        print(f"Original width x height is {sourceWidth} x {sourceHeight}.  New ratio width {newSourceWidth}")
        offset = int((newSourceWidth-sourceWidth)/2)
        imWider = Image.new(mode="RGBA", size=(newSourceWidth, sourceHeight), color=colorBackground)
        imWider.paste(sourceImage, (offset, 0))
        if stretchEdge:
            # left side
            imLine = sourceImage.crop((0,0,1,sourceHeight))
            for x in range(offset-stretchSpacing):
                imWider.paste(imLine, (x, 0))
            # right side
            imLine = sourceImage.crop((sourceWidth-1,0,sourceWidth,sourceHeight))
            for x in range(offset-stretchSpacing):
                imWider.paste(imLine, (x+offset+sourceWidth+stretchSpacing, 0))
        print(f"Resizing to {width} x {height}")
        im = imWider.resize(size=(width,height))

    if imageRatio == sourceRatio:
        print("Same ratio")
        im = sourceImage.resize(size=(width,height))
    # Labeling
    if overlayText:
        print("Writing overlay text")
        bgoffset=1
        draw.rectangle(xy=((0,0),(width,24)),fill=colorTextBG)
        titlewidth = width + 2
        titlefontsize=16
        while (titlewidth > width) and titlefontsize > 6:
            titlewidth,titleheight,titlefont=vicarioustext.gettextdimensions(draw, title, titlefontsize, True)
            if titlewidth > width:
                titlefontsize -= 1
        if titlefontsize > 6:
            vicarioustext.drawcenteredtext(draw, title, titlefontsize, int(width/2), 12, colorTextFG, True)
        else:
            vicarioustext.drawlefttext(draw, title, titlefontsize, 0, 12, colorTextFG, True)
        draw.rectangle(xy=((0,height-28),(width,height)),fill=colorTextBG)
        vicarioustext.drawbottomlefttext(draw, "Artist:" + artist, 12, 0, height-12, colorTextFG)
        vicarioustext.drawbottomlefttext(draw, "Edition:" + str(holding["edition"]) + "/" + str(holding["editions"]), 12, 0, height, colorTextFG)
        vicarioustext.drawbottomrighttext(draw, "Owner:" + owner, 12, width, height, colorTextFG)
    # Combine and save
    composite = Image.alpha_composite(im, alpha_img)
    print(f"Done. Saving image to {outputFile}")
    composite.save(outputFile)
    # Set new raretoshiuser?
    if randomuser:
        pickRaretoshiUser(raretoshiinfo)

if __name__ == '__main__':
    # Defaults
    configFile="/home/bitcoin/nodeyez/config/raretoshi.json"
    raretoshiuser="BTCTKVR"
    outputFile="/home/bitcoin/images/raretoshi.png"
    dataDirectory="/home/bitcoin/nodeyez/data/"
    colorTextBG=ImageColor.getrgb("#00000080")
    colorTextFG=ImageColor.getrgb("#ffffff")
    colorBackground=ImageColor.getrgb("#000000")
    stretchEdge=True
    stretchSpacing=30
    overlayText=True
    randomuser=True
    sleepInterval=30
    userinfoInterval=3600
    randomuserInterval=300
    # Inits
    userinfoLast=0
    userinfo=json.loads('{"subject":{"holdings":[]}}')
    randomuserLast=0
    # Override config
    if exists(configFile):
        with open(configFile) as f:
            config = json.load(f)
        if "raretoshi" in config:
            config = config["raretoshi"]
        if "raretoshiuser" in config:
            raretoshiuser = config["raretoshiuser"]
        if "outputFile" in config:
            outputFile = config["outputFile"]
        if "dataDirectory" in config:
            dataDirectory = config["dataDirectory"]
        if "colorTextBG" in config:
            colorTextBG = ImageColor.getrgb(config["colorTextBG"])
        if "colorTextFG" in config:
            colorTextFG = ImageColor.getrgb(config["colorTextFG"])
        if "colorBackground" in config:
            colorBackground = ImageColor.getrgb(config["colorBackground"])
        if "stretchEdge" in config:
            stretchEdge = config["stretchEdge"]
        if "stretchSpacing" in config:
            stretchSpacing = int(config["stretchSpacing"])
        if "overlayText" in config:
            overlayText = config["overlayText"]
        if "randomuser" in config:
            randomuser = config["randomuser"]
        if "randomuserInterval" in config:
            randomuserInterval = int(config["randomuserInterval"])
            randomuserInterval = 30 if randomuserInterval < 30 else randomuserInterval # minimum 30 seconds, remote access
        if "sleepInterval" in config:
            sleepInterval = int(config["sleepInterval"])
            sleepInterval = 30 if sleepInterval < 30 else sleepInterval # minimum 30 seconds, mostly local
        if "userinfoInterval" in config:
            userinfoInterval = int(config["userinfoInterval"])
            userinfoInterval = 300 if userinfoInterval < 300 else userinfoInterval # minimum 5 minutes, remote access
    # Data directories
    if not os.path.exists(dataDirectory):
        os.makedirs(dataDirectory)
    ipfsDataDirectory = dataDirectory + "ipfs/"
    if not os.path.exists(ipfsDataDirectory):
        os.makedirs(ipfsDataDirectory)
    raretoshiDataDirectory = dataDirectory + "raretoshi/"
    if not os.path.exists(raretoshiDataDirectory):
        os.makedirs(raretoshiDataDirectory)
    # Check for single run
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h','--help']:
            print(f"Retrieves an image from raretoshi collection for a user, scales and annotates")
            print(f"Usage:")
            print(f"1) Call without arguments to run continuously using the configuration or defaults")
            print(f"2) Pass the desired raretoshi user (case sensitive) as an argument as follows")
            arg0 = sys.argv[0]
            print(f"   {arg0} BTCTKVR")
            print(f"3) Pass the desired raretoshi user and an index number")
            print(f"   {arg0} valeriyageorg 3")
            print(f"You may specify a custom configuration file at {configFile}")
        else:
            raretoshiuser = sys.argv[1]
            createimage()
        exit(0)
    # Loop
    while True:
        createimage()
        print(f"Sleeping for {sleepInterval} seconds")
        time.sleep(sleepInterval)
