#! /usr/bin/env python3
from datetime import datetime
from PIL import Image, ImageFilter, ImageDraw, ImageFont, ImageColor
from os.path import exists
import glob
import json
import math
import os
import redis
import subprocess
import sys
import time
import vicariousbitcoin
import vicariousnetwork
import vicarioustext

def getlndhubusers():
    return r.keys("user_*")

def getlndhubuser(k):
    return r.get(k)

def getlndhubispaids():
    return r.keys("ispaid_*")

def islndhubpaymentforuser(s, u):
    return r.get("payment_hash_" + s).decode("utf-8") == u

def getlndhubpaymentamount(k):
    return r.get(k)

def getlndhubusertx(k):
    min = 0
    max = 10000
    return r.lrange("txs_for_" + k, min, max)

def getuseralias(k):
    l = k
    if exists(configFile):
        if l in config:
            a = config[l]
            if enableLogDetails:
                print(f"configured alias: {a}")
            return a
    m = l[0:8] + ".." + l[40:48]
    if enableLogDetails:
        print(f"calculated alias: {m}")
        print("---")
        print(f"There was no configured alias found for '{l}'")
        print("You may configure an alias for this account by adding the following field to the")
        print(f"config file: {configFile}")
        print()
        print(f"\"{l}\": \"your alias, e.g. Vic\"")
        print("---")
    return m

def getusermetadata(u):
    return r.get("metadata_for_" + u)

def createimage(width=480, height=320):
    # Info from redis
    print("Retrieving user information from LND Hub data store")
    users = getlndhubusers()
    usercount = len(users)
    # If there are no users, dont even both creating the image
    if usercount == 0:
        print("There are no user accounts in LND Hub. Skipping")
        return
    else:
        print(f"Processing {usercount} users")
    allpaids = getlndhubispaids()
    useridx = 0
    headerheight = 30
    footerheight = 30
    im = Image.new(mode="RGB", size=(width, height), color=colorBackground)
    draw = ImageDraw.Draw(im)
    # Header
    vicarioustext.drawcenteredtext(draw, "LNDhub Account Balances", 24, int(width/2), int(headerheight/2), colorTextFG, True)
    # Sub headers
    subheaderheight = 20
    subxaccount = 3
    subxreceived = int(width * .6)
    subxspent = int(width * .8)
    subxbalance = int(width - 3)
    suby = headerheight + int(subheaderheight // 2)
    subfontsize = 16
    vicarioustext.drawlefttext(draw, "Account", subfontsize, subxaccount, suby)
    vicarioustext.drawrighttext(draw, "Received", subfontsize, subxreceived, suby)
    vicarioustext.drawrighttext(draw, "Spent", subfontsize, subxspent, suby)
    vicarioustext.drawrighttext(draw, "Balance", subfontsize, subxbalance, suby)
    draw.line(xy=[subxaccount,headerheight+subheaderheight,subxbalance,headerheight+subheaderheight],fill=colorLine,width=1)
    # Iterate over users
    for user in users:
        if enableLogDetails:
            print()
            usercred = user.decode("utf-8")
            print(f"credential user record key: {usercred}")
        uservalue = getlndhubuser(user).decode("utf-8") # this is the internal mapped user
        if enableLogDetails:
            print(f"maps to internal user account {uservalue}")
        useralias = getuseralias(uservalue)             # this is a configurable alias
        usermetadata = getusermetadata(uservalue)
        usercreated = "unknown"
        try:
            j = json.loads(usermetadata)
            usercreated = j["created_at"][0:10]
        except Exception as e:
            print(f"error loading user metadata as json: {e}")
        if enableLogDetails:
            print(f"  created on {usercreated}")
        # get funds received by user
        userreceived = 0
        userreceivedcount = 0
        for paid in allpaids:
            suffix = paid.decode("utf-8").replace("ispaid_","")
            if islndhubpaymentforuser(suffix, uservalue):
                userreceivedcount = userreceivedcount + 1
                receivedamount = int(getlndhubpaymentamount(paid))
                userreceived = userreceived + receivedamount
        if enableLogDetails:
            print(f"+ received ({userreceivedcount} transactions): {userreceived}")
        # get funds spent by user
        usertxs = getlndhubusertx(uservalue)
        userspent = 0
        userspentcount = 0
        userhubfees = 0
        for tx in usertxs:
            try:
                j = json.loads(tx)
                j = j["payment_route"]
                total_amt_msat = j["total_amt_msat"]
                total_fees = j["total_fees"]
                txsum = math.ceil(int(total_amt_msat) / 1000) + int(total_fees)
                userspent = userspent + txsum
                userspentcount = userspentcount + 1
                userhubfees = userhubfees + int(total_fees)
            except Exception as e:
                print(f"error loading as json: {e}")
        if enableLogDetails:
            print(f"- spent ({userspentcount} transactions): {userspent}")
        userbalance = userreceived - userspent
        if enableLogDetails:
            print(f"= current balance: {userbalance}")
        # create text in image
        userLineHeight = 30
        if enableUserDetails:
            userLineHeight = 60
        ypos = headerheight + subheaderheight + 8 + (userLineHeight * useridx)
        vicarioustext.drawlefttext(draw, useralias, 14, subxaccount, ypos)
        vicarioustext.drawrighttext(draw, str(userreceived), 14, subxreceived, ypos)
        vicarioustext.drawrighttext(draw, str(userspent), 14, subxspent, ypos)
        vicarioustext.drawrighttext(draw, str(userbalance), 14, subxbalance, ypos)
        if enableUserDetails:
            ypos += 16
            userdesc = "created: " + usercreated + ", hub fees paid: " + str(userhubfees)
            vicarioustext.drawlefttext(draw, userdesc, 14, subxaccount, ypos, colorTextDark)
            ypos += 16
            userdesc = "# funding tx: " + str(userreceivedcount) + ", # spend tx: " + str(userspentcount)
            vicarioustext.drawlefttext(draw, userdesc, 14, subxaccount, ypos, colorTextDark)
        useridx += 1
        # bail from writing more users to image if exceeds size
        # todo: consider pagination as done in other scripts
        if ypos > height - 100:
            break
    # Date and Time
    dt = "as of " + vicarioustext.getdateandtime()
    vicarioustext.drawbottomrighttext(draw, dt, 12, width, height, colorTextFG)
    # Attribution
    attributionLine = "Data from local LNDhub instance"
    vicarioustext.drawbottomlefttext(draw, attributionLine, 16, 0, height, colorAttribution)
    # Save to file
    if enableLogDetails:
        print()
    print("Saving image")
    im.save(outputFile)
    im.close()


if __name__ == '__main__':
    # Defaults
    configFile="../config/lndhub.json"
    outputFile = "../imageoutput/lndhub.png"
    width=480
    height=320
    sleepInterval=86400
    colorTextFG=ImageColor.getrgb("#ffffff")
    colorBackground=ImageColor.getrgb("#000000")
    colorLine=ImageColor.getrgb("#4040ff")
    colorTextDark=ImageColor.getrgb("#808080")
    colorAttribution=ImageColor.getrgb("#80cef2")
    redisServer = "localhost"
    redisPort = 6379
    redisDb = 0
    enableUserDetails = True
    enableLogDetails = True
    # Override config
    if exists(configFile):
        with open(configFile) as f:
            config = json.load(f)
        if "lndhub" in config:
            config = config["lndhub"]
        if "outputFile" in config:
            outputFile = config["outputFile"]
        if "width" in config:
            width = int(config["width"])
        if "height" in config:
            height = int(config["height"])
        if "sleepInterval" in config:
            sleepInterval = int(config["sleepInterval"])
            sleepInterval = 60 if sleepInterval < 60 else sleepInterval
        if "colorTextFG" in config:
            colorTextFG = ImageColor.getrgb(config["colorTextFG"])
        if "colorBackground" in config:
            colorBackground = ImageColor.getrgb(config["colorBackground"])
        if "colorLine" in config:
            colorLine = ImageColor.getrgb(config["colorLine"])
        if "colorTextDark" in config:
            colorTextDark = ImageColor.getrgb(config["colorTextDark"])
        if "redisServer" in config:
            redisServer = config["redisServer"]
        if "redisPort" in config:
            redisPort = config["redisPort"]
        if "redisDb" in config:
            redisDb = config["redisDb"]
        if "enableUserDetails" in config:
            enableUserDetails = config["enableUserDetails"]
        if "enableLogDetails" in config:
            enableLogDetails = config["enableLogDetails"]
    # Initialize redis
    r = redis.Redis(host=redisServer, port=redisPort, db=redisDb)
    # Check for single run
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h','--help']:
            print(f"Prepares images for LND Hub Account Balances")
            print(f"Usage:")
            print(f"1) Call without arguments to run continuously using the configuration or defaults")
            print(f"2) Passing any arguments other then -h or --help will run once and exit")
            print(f"You may specify a custom configuration file at {configFile}")
            exit(0)
    # Loop
    while True:
        createimage(width,height)
        # only run once if an argument was passed
        if len(sys.argv) > 1:
            break
        print(f"Sleeping for {sleepInterval} seconds")
        time.sleep(sleepInterval)
