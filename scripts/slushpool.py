#! /usr/bin/python3
from datetime import datetime
from PIL import Image, ImageDraw, ImageColor
import json
import math
import subprocess
import time
import vicarioustext

configFile = "/home/bitcoin/nodeyez/config/slushpool.json"
outputFile = "/home/bitcoin/images/slushpool.png"
authtoken = "--put-your-auth-token-in-nodeyez/config/slushpool.json--"
useTor=False
price_url = "https://bisq.markets/bisq/api/markets/ticker"
price_per_kwh = .12
kw_per_hour_used = 1.100
price_last=1
price_high=1
price_low=1
price_countdown_height = 10800	# controls how often (in seconds), the market price is checked.  10800 is once every 3 hours
price_countdown = 0
sleepInterval = 600                               # controls how often this display panel is updated. 600 is once every 10 minutes
breakevendaily = 9999999                          # will get calculated below
sats_per_btc = 100000000
colorHeader=ImageColor.getrgb("#ffffff")          # The header text color. Need to pass to also specify bolding
colorMiningReward=ImageColor.getrgb("#6b50ff")    # Slushpool mining rewards color
colorBOSReward=ImageColor.getrgb("#fb82a8")       # Slushpool BOS rewards color
colorReferralReward=ImageColor.getrgb("#00bac5")  # Slushpool referral rewards color
colorGraphLineLight=ImageColor.getrgb("#a0a0a0")  # Chart border left and bottom
colorGraphLineDark=ImageColor.getrgb("#606060")   # Chart border top and right
colorMALine=ImageColor.getrgb("#d69f06")          # The moving average line
colorDataValue=ImageColor.getrgb("#4040ff")       # Color for hashrate, yesterday and today's earnings
colorBreakEvenMiss=ImageColor.getrgb("#ff0000")   # The break even color when the average is at or above the value
colorBreakEvenGood=ImageColor.getrgb("#00ff00")   # Break even color when average is below the value (cheaper to buy than mine)

def getaccountprofile():
    cmd = "curl --silent -H \"SlushPool-Auth-Token: " + authtoken + "\" https://slushpool.com/accounts/profile/json/btc/"
    if useTor:
        cmd = "torify " + cmd
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
        j = json.loads(cmdoutput)
    except subprocess.CalledProcessError as e:
        cmdoutput = ""
    if len(cmdoutput) == 0:
        cmdoutput = "{\"btc\":{\"confirmed_reward\": null, \"unconfirmed_reward\": \"0.00000000\", \"estimated_reward\": \"0.00000000\", \"hash_rate_unit\": \"Gh/s\", \"hash_rate_5m\": 0.0000}}"
        j = json.loads(cmdoutput)
    return j

def getaccountrewards():
    time.sleep(6)
    cmd = "curl --silent -H \"SlushPool-Auth-Token: " + authtoken + "\" https://slushpool.com/accounts/rewards/json/btc/"
    if useTor:
        cmd = "torify " + cmd
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
        j = json.loads(cmdoutput)
    except subprocess.CalledProcessError as e:
        cmdoutput = ""
    if len(cmdoutput) == 0:
        cmdoutput = "{\"btc\":{\"daily_rewards\":[]}}"
        j = json.loads(cmdoutput)
    return j

def getpoolstats():
    time.sleep(6)
    cmd = "curl --silent -H \"SlushPool-Auth-Token: " + authtoken + "\" https://slushpool.com/stats/json/btc/"
    if useTor:
        cmd = "torify " + cmd
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
        j = json.loads(cmdoutput)
    except subprocess.CalledProcessError as e:
        cmdoutput = ""
    if len(cmdoutput) == 0:
        cmdoutput = "{\"btc\":{\"blocks\":{\"0\":{\"date_found\":0,\"mining_duration\":0,\"total_shares\":0,\"state\":\"confirmed\",\"confirmations_left\":0,\"value\": \"0.00000000\",\"user_reward\": \"0.00000000\",\"pool_scoring_hash_rate\": 0.000000}}}}"
        j = json.loads(cmdoutput)
    return j

def getpriceinfo():
    cmd = "curl --silent " + price_url
    if useTor:
        cmd = "torify " + cmd
    global price_last
    global price_high
    global price_low
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
        if len(cmdoutput) > 0:
            j = json.loads(cmdoutput)
            price_last = int(math.floor(float(j["btc_usd"]["last"])))
            price_high = int(math.floor(float(j["btc_usd"]["high"])))
            price_low = int(math.floor(float(j["btc_usd"]["low"])))
    except subprocess.CalledProcessError as e:
        cmdoutput = "{\"error\": \"dont care\" }"
    return (price_last,price_high,price_low)

def getaccounthashrate(accountprofile):
    hashrate = accountprofile["btc"]["hash_rate_5m"]
    hashdesc = accountprofile["btc"]["hash_rate_unit"]
    while (hashrate > 1000.0) and (hashdesc != "Ph/s"):
        hashrate = hashrate/1000.0
        if hashdesc == "Ph/s":
            hashdesc = "Eh/s"
        if hashdesc == "Th/s":
            hashdesc = "Ph/s"
        if hashdesc == "Gh/s":
            hashdesc = "Th/s"
        if hashdesc == "Mh/s":
            hashdesc = "Gh/s"
    hashfmt = str(format(hashrate, ".2f")) + " " + hashdesc
    return hashfmt

def gethighestreward(accountrewards):
    highestreward = 0.00
    days = 0
    for reward in accountrewards["btc"]["daily_rewards"]:
        days = days + 1
        currenttotal = float(reward["total_reward"])
        if currenttotal > highestreward:
            highestreward = currenttotal
    return highestreward

def getlowestreward(accountrewards):
    lowestreward = 0.00
    days = 0
    for reward in accountrewards["btc"]["daily_rewards"]:
        days = days + 1
        currenttotal = float(reward["total_reward"])
        if days == 1:
            lowestreward = currenttotal
        else:
            if currenttotal < lowestreward:
                lowestreward = currenttotal
    return lowestreward

def createimage(accountrewards, accountprofile, poolstats, price_last, width=480, height=320):
    headerheight = 30
    footerheight = 15
    hashheight = (height - headerheight - footerheight) * .4
    rewardheight = (height - headerheight - footerheight) * .5
    im = Image.new(mode="RGB", size=(width, height))
    draw = ImageDraw.Draw(im)
    # Header
    vicarioustext.drawcenteredtext(draw, "SlushPool Mining Summary", 24, int(width/2), int(headerheight/2), colorHeader, True)
    # Hashrate
    hashrate = getaccounthashrate(accountprofile)
    vicarioustext.drawcenteredtext(draw, "Hashrate", 16, (width/4*1), (headerheight + (hashheight/2) - 24))
    vicarioustext.drawcenteredtext(draw, hashrate, 24, (width/4*1), (headerheight + (hashheight/2)), colorDataValue)
    # Yesterday and Today value
    earningspad = 24
    value_last_day = "0 sats"
    value_today = "0 sats"
    if len(accountrewards["btc"]["daily_rewards"]) > 0:
        since_date = accountrewards["btc"]["daily_rewards"][0]["date"]
        sattally = 0
        for key in poolstats["btc"]["blocks"]:
            block = poolstats["btc"]["blocks"][key]
            if block["date_found"] > since_date:
                if block["user_reward"] is not None:
                    sattally = sattally + int(float(block["user_reward"]) * sats_per_btc)
            else:
                break
        sattally2 = sattally
        since_date = since_date + 86400
        sattally = 0
        for key in poolstats["btc"]["blocks"]:
            block = poolstats["btc"]["blocks"][key]
            if block["date_found"] > since_date:
                if block["user_reward"] is not None:
                    sattally = sattally + int(float(block["user_reward"]) * sats_per_btc)
            else:
                break
        value_last_day = str(sattally2 - sattally) + " sats"
        value_today = str(sattally) + " sats"
    vicarioustext.drawcenteredtext(draw, "Earnings Yesterday", 16, (width/4*3), (headerheight + (hashheight/2) - 22 - earningspad))
    vicarioustext.drawcenteredtext(draw, value_last_day, 24, (width/4*3), (headerheight + (hashheight/2) - earningspad), colorDataValue)
    vicarioustext.drawcenteredtext(draw, "Earnings Today", 16, (width/4*3), (headerheight + (hashheight/2) - 22 + earningspad))
    vicarioustext.drawcenteredtext(draw, value_today, 24, (width/4*3), (headerheight + (hashheight/2) + earningspad), colorDataValue)
    # 30 Days Rewards
    highestreward = gethighestreward(accountrewards)
    lowestreward = getlowestreward(accountrewards)
    labelwidth = math.floor(width / 5)
    graphedge = 3
    charttop = headerheight + hashheight + 32
    chartleft = labelwidth + graphedge
    chartright = width - graphedge
    chartbottom = height - footerheight - graphedge
    # - chart border
    draw.line(xy=[chartleft, charttop, chartleft, chartbottom],fill=colorGraphLineLight,width=1)
    draw.line(xy=[chartleft, chartbottom, chartright, chartbottom],fill=colorGraphLineLight,width=1)
    draw.line(xy=[chartleft, charttop, chartright, charttop],fill=colorGraphLineDark,width=1)
    draw.line(xy=[chartright, charttop, chartright, chartbottom],fill=colorGraphLineDark,width=1)
    # - dashed line background
    chart25 = int(math.floor(charttop + ((chartbottom - charttop)/4*1)))
    chart50 = int(math.floor(charttop + ((chartbottom - charttop)/4*2)))
    chart75 = int(math.floor(charttop + ((chartbottom - charttop)/4*3)))
    for i in range(chartleft, chartright, 10):
        draw.line(xy=[i,chart25,i+1,chart25],fill=colorGraphLineDark,width=1)
        draw.line(xy=[i,chart50,i+1,chart50],fill=colorGraphLineDark,width=1)
        draw.line(xy=[i,chart75,i+1,chart75],fill=colorGraphLineDark,width=1)
    # - left labels
    reward25 = int(math.floor((lowestreward + ((highestreward - lowestreward)/4*3)) * sats_per_btc))
    reward50 = int(math.floor((lowestreward + ((highestreward - lowestreward)/4*2)) * sats_per_btc))
    reward75 = int(math.floor((lowestreward + ((highestreward - lowestreward)/4*1)) * sats_per_btc))
    vicarioustext.drawrighttext(draw, str(reward25) + " sats", 12, labelwidth, chart25)
    vicarioustext.drawrighttext(draw, str(reward50) + " sats", 12, labelwidth, chart50)
    vicarioustext.drawrighttext(draw, str(reward75) + " sats", 12, labelwidth, chart75)
    # - 30 days of bars
    totaldays = 31
    days = 0
    daystoskip = 1
    daywidth = int(math.floor((chartright - chartleft) / totaldays))
    barwidth = daywidth - 2
    overalltotal = 0
    masize = 14 # days of simple moving average.
    maoldx = -1
    maoldy = -1
    for reward in accountrewards["btc"]["daily_rewards"]:
        days = days + 1
        # skip the first day entry, something not right, and it doesnt show on slushpool.com
        if days < (daystoskip + 1):
           continue
        if days > totaldays + 1:
           break
        currenttotal = 0
        if reward["total_reward"] is not None:
            currenttotal = float(reward["total_reward"])
        overalltotal = overalltotal + currenttotal
        dayx = chartright - ((days - daystoskip) * daywidth)
        barpct = 0
        if highestreward > lowestreward:
            barpct = (currenttotal-lowestreward)/(highestreward-lowestreward)
        bartop = chartbottom - int(math.floor((chartbottom-charttop)*barpct))
        draw.rectangle(xy=[dayx,bartop,dayx+barwidth,chartbottom-1],fill=colorMiningReward)
        if reward["bos_plus_reward"] is not None:
            bosreward = float(reward["bos_plus_reward"])
            bospct = bosreward/(highestreward-lowestreward)
            bosbottom = bartop + int(math.floor((chartbottom-charttop)*bospct))
            if bosbottom > chartbottom:
                bosbottom = chartbottom
            draw.rectangle(xy=[dayx,bartop,dayx+barwidth,bosbottom],fill=colorBOSReward)
        # referral_bonus, referral_reward also available, but i dont know what they would look like yet
        # moving average line
        max = dayx + int(barwidth/2)
        matotal = 0
        for maidx in range(masize):
            marewardidx = days + maidx
            if len(accountrewards["btc"]["daily_rewards"]) > marewardidx:
                mareward = accountrewards["btc"]["daily_rewards"][marewardidx]
                marewardtotal = float(mareward["total_reward"])
                matotal = matotal + marewardtotal
        maavg = (matotal / masize)
        mapct = 0
        if highestreward > lowestreward:
            mapct = (maavg-lowestreward)/(highestreward-lowestreward)
        may = chartbottom - int(math.floor((chartbottom-charttop)*mapct))
        if maoldx != -1:
            draw.line(xy=[(max,may),(maoldx,maoldy)],fill=colorMALine,width=2)
        maoldx = max
        maoldy = may
    overalltotal = overalltotal * sats_per_btc
    # Chart header
    if days > 0:
        dailyavg = (overalltotal / days)
        # Warn if missing breakeven. 
        breakevendaily = int((sats_per_btc / price_last) * (kw_per_hour_used * 24 * price_per_kwh))
        breakevencolor = colorBreakEvenGood
        if dailyavg < breakevendaily:
            breakevencolor = colorBreakEvenMiss
            vicarioustext.drawtoplefttext(draw, "Warning: Mining at a loss", 16, 0, (headerheight + hashheight + 16), breakevencolor)
        vicarioustext.drawtoplefttext(draw, "Last 30 days " + str(int(overalltotal)) + " sats", 16, 0, (headerheight + hashheight))
        vicarioustext.drawtoprighttext(draw, "Daily avg " + str(int(dailyavg)) + " sats", 16, width, (headerheight + hashheight))
        vicarioustext.drawtoprighttext(draw, "Break even " + str(int(breakevendaily)) + " sats", 16, width, (headerheight + hashheight + 16), breakevencolor)
    else:
        vicarioustext.drawcenteredtext(draw, "Rewards will be graphed below once earnings are recorded"  , 16, int(width/2), (headerheight + hashheight))

    # Date and Time
    vicarioustext.drawbottomrighttext(draw, "as of " + vicarioustext.getdateandtime(), 12, width, height)
    # Save to file
    im.save(outputFile)

while True:
    with open(configFile) as f:
        config = json.load(f)
    authtoken = config["authtoken"]
    accountprofile = getaccountprofile()
    accountrewards = getaccountrewards()
    poolstats = getpoolstats()
    if price_countdown <= 0:
        price_last, price_high, price_low = getpriceinfo()
        price_countdown = price_countdown_height
    else:
        price_countdown = price_countdown - sleep_time
    createimage(accountrewards,accountprofile,poolstats,price_last)
    time.sleep(sleepInterval)
