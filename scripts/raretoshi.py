#! /usr/bin/env python3
from PIL import Image, ImageDraw, ImageColor
from os.path import exists
import json
import os
import qrcode
import random
import subprocess
import sys
import time
import vicarioustext

def getConnectTimeouts():
    global downloadConnectTimeout
    global downloadMaxTimeout
    return " --connect-timeout " + str(downloadConnectTimeout) + " --max-time " + str(downloadMaxTimeout) + " "

def getRaretoshiUserinfo():
    global userInfo
    global userInfoLast
    userFilename = raretoshiUser + ".json"
    localFilename = raretoshiDataDirectory + userFilename
    tempFilename = localFilename + ".tmp"
    refreshUser = False
    if not exists(localFilename):
        refreshUser = True
    if userInfoInterval + userInfoLast < int(time.time()):
        refreshUser = True
    if refreshUser:
        print(f"Calling raretoshi website for user data")
        userInfoLast = int(time.time())
        url = "https://raretoshi.com/" + userFilename
        cmd = "curl -s -o " + tempFilename + getConnectTimeouts() + url
        try:
            cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
            with open(tempFilename) as f:
                userInfo = json.load(f)
            if exists(localFilename):
                os.remove(localFilename)
            os.rename(tempFilename, localFilename)
        except subprocess.CalledProcessError as e:
            print(f"Error downloading and loading file {tempFilename}. Error is {e}")
            if exists(localFilename):
                print("Attempting to reload from cached result {localFilename}")
                try:
                    with open(localFilename) as f:
                        userInfo = json.load(f)
                except:
                    print("Error raised reading {localFilename} as json")
    else:
        print(f"Using cached data from {userInfoLast}")
    return userInfo

def pickRaretoshiUser(raretoshiInfo):
    global randomUserLast
    global raretoshiUser
    if randomUserInterval + randomUserLast < int(time.time()):
        # pick new user
        randomUserLast=int(time.time())
        userlist=[]
        # look at holdings and favorites
        if "subject" in raretoshiInfo:
            if "holdings" in raretoshiInfo["subject"]:
                for holding in raretoshiInfo["subject"]["holdings"]:
                    owner = holding["owner"]["username"]
                    if not owner in userlist:
                        userlist.append(owner)
                    artist = holding["artist"]["username"]
                    if not artist in userlist:
                        userlist.append(artist)
            if "favorites" in raretoshiInfo["subject"]:
                for favorite in raretoshiInfo["subject"]["favorites"]:
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
        raretoshiUser = userlist[userindex]


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
    cmd = "curl -s -o " + saveto + getConnectTimeouts() + url
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
        print(f"IPFS Downloaded to {saveto}")
    except subprocess.CalledProcessError as e:
        print(f"error {e}")
        # If we were originally hitting IPFS, we can try fallback to raretoshi
        if url.startswith("https://ipfs.io/"):
            url = url.replace("https://ipfs.io/", "https://raretoshi.com/api/")
            print(f"Retrying with {url}")
            cmd = "curl -s -o " + saveto + getConnectTimeouts() + url
            try:
                cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
                print(f"IPFS Downloaded to {saveto}")
            except:
                print(f"error {e}")

def createimage(width=480, height=320):
    # Setup alpha layer
    alpha_img = Image.new(mode="RGBA", size=(width, height), color=(255,255,255,0))
    draw = ImageDraw.Draw(alpha_img)
    print(f"Getting Raretoshi information for user {raretoshiUser}")
    raretoshiInfo = getRaretoshiUserinfo()
    holdingscount = len(raretoshiInfo["subject"]["holdings"])
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
        holding = raretoshiInfo["subject"]["holdings"][holdingindex]
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
        if stretchEdgeEnabled:
            # top side
            imLine = sourceImage.crop((0,0,sourceWidth,1))
            for y in range(offset-stretchEdgeSpacing):
                imTaller.paste(imLine, (0, y))
            # bottom side
            imLine = sourceImage.crop((0,sourceHeight-stretchEdgeSpacing,sourceWidth,sourceHeight))
            for y in range(offset-stretchEdgeSpacing):
                imTaller.paste(imLine, (0, y+offset+sourceHeight+stretchEdgeSpacing))
        print(f"Resizing to {width} x {height}")
        im = imTaller.resize(size=(width,height))
        imTaller.close()
    if imageRatio > sourceRatio:
        print("Need to extend sides")
        newSourceWidth=int(sourceHeight * imageRatio)
        print(f"Original width x height is {sourceWidth} x {sourceHeight}.  New ratio width {newSourceWidth}")
        offset = int((newSourceWidth-sourceWidth)/2)
        imWider = Image.new(mode="RGBA", size=(newSourceWidth, sourceHeight), color=colorBackground)
        imWider.paste(sourceImage, (offset, 0))
        if stretchEdgeEnabled:
            # left side
            imLine = sourceImage.crop((0,0,1,sourceHeight))
            for x in range(offset-stretchEdgeSpacing):
                imWider.paste(imLine, (x, 0))
            # right side
            imLine = sourceImage.crop((sourceWidth-1,0,sourceWidth,sourceHeight))
            for x in range(offset-stretchEdgeSpacing):
                imWider.paste(imLine, (x+offset+sourceWidth+stretchEdgeSpacing, 0))
        print(f"Resizing to {width} x {height}")
        im = imWider.resize(size=(width,height))
        imWider.close()
    if imageRatio == sourceRatio:
        print("Same ratio")
        im = sourceImage.resize(size=(width,height))
    sourceImage.close()
    # Labeling
    overlayTextBottomHeight=0
    if overlayTextEnabled:
        print("Writing overlay text")
        bgoffset=1
        overlayTextTopHeight=24
        titleWidth = width + 2
        titleFontSize=int(overlayTextTopHeight * 2/3)
        while (titleWidth > width) and titleFontSize > 6:
            titleWidth,titleHeight,titleFont=vicarioustext.gettextdimensions(draw, title, titleFontSize, True)
            if titleWidth > width:
                titleFontSize -= 1
        overlayTextTopHeight = int(titleFontSize * 1.5)
        draw.rectangle(xy=((0,0),(width,overlayTextTopHeight)),fill=overlayTextColorBG)
        if titleFontSize > 6:
            vicarioustext.drawcenteredtext(draw, title, titleFontSize, int(width/2), int(overlayTextTopHeight/2), overlayTextColorFG, True)
        else:
            vicarioustext.drawlefttext(draw, title, titleFontSize, 0, int(overlayTextTopHeight/2), overlayTextColorFG, True)
        overlayTextBottomHeight=28
        metaFontSize=12
        draw.rectangle(xy=((0,height-overlayTextBottomHeight),(width,height)),fill=overlayTextColorBG)
        vicarioustext.drawbottomlefttext(draw, "Artist:" + artist, metaFontSize, 0, height-12, overlayTextColorFG)
        editionText = "Edition:" + str(holding["edition"]) + "/" + str(holding["editions"])
        if holding["editions"] == 1:
            editionText = "Edition: One of a Kind"
        vicarioustext.drawbottomlefttext(draw, editionText, metaFontSize, 0, height, overlayTextColorFG)
        vicarioustext.drawbottomrighttext(draw, "Owner:" + owner, metaFontSize, width, height, overlayTextColorFG)
    # Show QR code?
    if qrCodeEnabled:
        print("Creating QR code")
        slug=holding["slug"]
        raretoshiurl="https://raretoshi.com/a/" + slug
        qr = qrcode.QRCode(box_size=qrCodeSize)
        qr.add_data(raretoshiurl)
        qr.make()
        img_qr = qr.make_image()
        # determine position for bottom left, but not over the artist info
        qrx = 0
        qry = height - img_qr.size[1]
        if overlayTextEnabled:
            qry = qry - overlayTextBottomHeight #bottom overlay
        qrpos = (qrx, qry)
        im.paste(img_qr, qrpos)
        img_qr.close()
    # Combine and save
    composite = Image.alpha_composite(im, alpha_img)
    print(f"Done. Saving image to {outputFile}")
    composite.save(outputFile)
    alpha_img.close()
    im.close()
    composite.close()
    # Set new raretoshiuser?
    if randomUserEnabled:
        pickRaretoshiUser(raretoshiInfo)

if __name__ == '__main__':
    # Defaults
    configFile="/home/nodeyez/nodeyez/config/raretoshi.json"
    raretoshiUser="BTCTKVR"
    outputFile="/home/nodeyez/nodeyez/imageoutput/raretoshi.png"
    dataDirectory="/home/nodeyez/nodeyez/data/"
    downloadConnectTimeout=5
    downloadMaxTimeout=20
    overlayTextEnabled=True
    overlayTextColorBG=ImageColor.getrgb("#00000080")
    overlayTextColorFG=ImageColor.getrgb("#ffffff")
    colorBackground=ImageColor.getrgb("#000000")
    stretchEdgeEnabled=True
    stretchEdgeSpacing=30
    randomUserEnabled=True
    randomUserInterval=300
    width=480
    height=320
    sleepInterval=30
    qrCodeEnabled=True
    qrCodeSize=2
    userInfoInterval=3600
    # Inits
    userInfoLast=0
    userInfo=json.loads('{"subject":{"holdings":[]}}')
    randomUserLast=0
    # Override config
    if exists(configFile):
        with open(configFile) as f:
            config = json.load(f)
        if "raretoshi" in config:
            config = config["raretoshi"]
        if "raretoshiUser" in config:
            raretoshiUser = config["raretoshiUser"]
        if "outputFile" in config:
            outputFile = config["outputFile"]
        if "dataDirectory" in config:
            dataDirectory = config["dataDirectory"]
        if "downloadConnectTimeout" in config:
            downloadConnectTimeout = config["downloadConnectTimeout"]
        if "downloadMaxTimeout" in config:
            downloadMaxTimeout = config["downloadMaxTimeout"]
        if "overlayTextEnabled" in config:
            overlayTextEnabled = config["overlayTextEnabled"]
        if "overlayTextColorBG" in config:
            overlayTextColorBG = ImageColor.getrgb(config["overlayTextColorBG"])
        if "overlayTextColorFG" in config:
            overlayTextColorFG = ImageColor.getrgb(config["overlayTextColorFG"])
        if "colorBackground" in config:
            colorBackground = ImageColor.getrgb(config["colorBackground"])
        if "stretchEdgeEnabled" in config:
            stretchEdgeEnabled = config["stretchEdgeEnabled"]
        if "stretchEdgeSpacing" in config:
            stretchEdgeSpacing = int(config["stretchEdgeSpacing"])
        if "randomUserEnabled" in config:
            randomUserEnabled = config["randomUserEnabled"]
        if "randomUserInterval" in config:
            randomUserInterval = int(config["randomUserInterval"])
            randomUserInterval = 30 if randomUserInterval < 30 else randomUserInterval # minimum 30 seconds, remote access
        if "qrCodeEnabled" in config:
            qrCodeEnabled = config["qrCodeEnabled"]
        if "qrCodeSize" in config:
            qrCodeSize = config["qrCodeSize"]
        if "width" in config:
            width = int(config["width"])
        if "height" in config:
            height = int(config["height"])
        if "sleepInterval" in config:
            sleepInterval = int(config["sleepInterval"])
            sleepInterval = 30 if sleepInterval < 30 else sleepInterval # minimum 30 seconds, mostly local
        if "userInfoInterval" in config:
            userInfoInterval = int(config["userInfoInterval"])
            userInfoInterval = 300 if userInfoInterval < 300 else userInfoInterval # minimum 5 minutes, remote access
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
            raretoshiUser = sys.argv[1]
            createimage(width,height)
        exit(0)
    # Loop
    while True:
        createimage(width,height)
        print(f"Sleeping for {sleepInterval} seconds")
        time.sleep(sleepInterval)
