#! /usr/bin/env python3
from datetime import datetime
from luxor import API
from os.path import exists
import json
import os
import subprocess
import sys
import time
import vicariousnetwork

def getdatefile():
    return datetime.utcnow().strftime("%Y-%m-%d-%H") + ".json"

def isFirstOfTheMonth():
    return (int(datetime.utcnow().strftime("%e")) == 1)

def getAndSaveFile(url, savetofile, headers={}):
    vicariousnetwork.getandsavefile(True, url, savetofile, headers)

def makeDirIfNotExists(path):
    if not exists(path):
        print(f"Creating folder {path}")
        os.makedirs(path)

# --------------------------------------------------------------------------------------------------------------------
# getAndSaveBisqInfo
#
# Retrieves the current bisq market data and saves to the data directory for historical tracking
# Some relevant fields are within a currency pair: last, high, low.  The buy and sell reflect offer spreads
#   btc_usd <last, high, low, volume_left, volume_right, buy, sell>
#   bsq_btc <last, high, low, volume_left, volume_right, buy, sell>
# --------------------------------------------------------------------------------------------------------------------
def getAndSaveBisqInfo():
    if not enableBisq:
        print("WARNING: Call to getAndSaveBisqInfo made but enableBisq is False")
        return
    datefile = getdatefile()
    print(f"Retrieving and saving Bisq Market Price info to {datefile}")
    with open(configFileBisq) as f:
        config = json.load(f)
    filename = bisqDataDirectory + datefile
    getAndSaveFile(config["priceurl"], filename)

def getAndSaveCollectAPIInfo():
    if not enableCollectAPI:
        print("WARNING: Call to getAndSaveCollectAPIInfo made but enableCollectAPI is False")
        return
    datefile = getdatefile()
    with open(configFileCollectAPI) as f:
        config = json.load(f)
    if "dailyretrieve" in config:
        for dailyretrieve in config["dailyretrieve"]:
            url = dailyretrieve["url"]
            subfolder = dailyretrieve["saveToSubfolder"]
            targetfolder = collectAPIDataDirectory + subfolder + "/"
            makeDirIfNotExists(targetfolder)
            filename = targetfolder + datefile
            print(f"Retrieving and saving Collect API info for {url} to {datefile}")
            if not os.path.exists(filename):
                headers = {}
                if "headers" in dailyretrieve:
                    headers = dailyretrieve["headers"]
                getAndSaveFile(url, filename, headers)
                time.sleep(5)
            else:
                print(f"Skipping download of {filename} as it already exists")

# --------------------------------------------------------------------------------------------------------------------
# getAndSaveCompassMiningHardwareInfo
#
# Provides details about the hardware for sale available from compass mining as a snapshot.
# Some relevant fields are
#   payload.hardwareIsFeatured       array of new asics to be hosted at facilities new contract
#   payload.hardwareGrouped          array of reseller asics to stay in facilities new contract
#   payload.hardwareAtHome           array of new asics available to ship to home
#
# Within the hardwareGrouped, structure of an item has these fields
#   manufacturer, baseModelName, name, hashrate, description, algorithm, imageURL, images [ url, order], minCost,
#   maxCost, isPSP, power, compass_finance, pricePerHashrate, pricePerHashrateForSorting, 
#   minOnlineDateFormattedSeconds, maxOnlineDateFormattedSeconds, hashrateSorting
# Within the hardwareAtHome, structure of an item has these fields
#   manuracturer, batch, baseModelName, id, name, shipping_date, costPrice, prift, type, condition, available_stock,
#   deposit_months, images [order, url], hostingFacility, salePrice, weight_lbs, location, shipping_min_order,
#   photoURL, is_bundle, hashrate, cost, power, algorithm, power_watts, online_date, description, is_reseller,
#   max_items_per_user, monthly_bundle_price, pricePerHashrate, pricePerHashrateForSorting, hashrateSorting
# --------------------------------------------------------------------------------------------------------------------
def getAndSaveCompassMiningHardwareInfo():
    if not enableCompassHardware:
        print("WARNING: Call to getAndSaveCompassMiningHardwareInfo made but enableCompassHardware is False")
        return
    datefile = getdatefile()
    print(f"Retrieving and saving Compass Mining Hardware info to {datefile}")
    with open(configFileCompassHardware) as f:
        config = json.load(f)
    filename = compassHardwareDataDirectory + datefile
    getAndSaveFile(config["hardwareurl"], filename)

# --------------------------------------------------------------------------------------------------------------------
# getAndSaveCompassMiningStatusInfo
#
# Provides details about the facility status at Compass Mining as a snapshot
#
# In addition, saving snapshots for details for individual facilities
# --------------------------------------------------------------------------------------------------------------------
def getAndSaveCompassMiningStatusInfo():
    if not enableCompassStatus:
        print("WARNING: Call to getAndSaveCompassMiningStatusInfo made but enableCompassStatus is False")
        return
    datefile = getdatefile().replace(".json", ".html")
    print(f"Retrieving and saving Compass Mining Status info to {datefile}")
    with open(configFileCompassStatus) as f:
        config = json.load(f)
    filename = compassStatusDataDirectory + datefile
    baseurl = config["statusurl"]
    getAndSaveFile(baseurl, filename)
    if isFirstOfTheMonth():
#        getAndSaveCompassFacilityStatus(baseurl, "canada/alberta", "3kdqgw2547nv", 1)
        getAndSaveCompassFacilityStatus(baseurl, "canada/british-columbia", "5zbr66zwp1ch", 1)
        getAndSaveCompassFacilityStatus(baseurl, "canada/manitoba1", "t9ck2m81j50d", 1)
        getAndSaveCompassFacilityStatus(baseurl, "canada/manitoba2", "3jz0mjsctwx8", 1)
#        getAndSaveCompassFacilityStatus(baseurl, "canada/manitoba3", "rdv8ddlbyhyb", 1)
        getAndSaveCompassFacilityStatus(baseurl, "canada/manitoba4", "y266jn235v5k", 1)
        getAndSaveCompassFacilityStatus(baseurl, "canada/manitoba5", "9hcxtxzr6m3p", 1)
        getAndSaveCompassFacilityStatus(baseurl, "canada/manitoba6", "n89q0k5qwf85", 1)
        getAndSaveCompassFacilityStatus(baseurl, "canada/manitoba7", "zdj1pbf1p8dg", 1)
        getAndSaveCompassFacilityStatus(baseurl, "canada/newfoundland1", "0p5x9pj0xg1z", 1) # new august 2022
        getAndSaveCompassFacilityStatus(baseurl, "canada/newfoundland2", "mj5mff51w9dy", 1) # new august 2022
        getAndSaveCompassFacilityStatus(baseurl, "canada/ontario", "1zjg8wgylr7x", 1) # 54x
#        getAndSaveCompassFacilityStatus(baseurl, "canada/quebec", "n9yqj1td9v32", 1)
        getAndSaveCompassFacilityStatus(baseurl, "iceland/southern-peninsula", "0wtyz0xpgswf", 1)
#        getAndSaveCompassFacilityStatus(baseurl, "kazakhstan/pavlodar-region", "k4kgphjfmg1q", 1)
#        getAndSaveCompassFacilityStatus(baseurl, "russia/krasnoyarsk-krai", "9yg10xhkyzym", 1)
#        getAndSaveCompassFacilityStatus(baseurl, "russia/irkutsk", "jsmkt30pdk16", 1)
#        getAndSaveCompassFacilityStatus(baseurl, "usa/alabama", "44f9l6qw3723", 1)
        getAndSaveCompassFacilityStatus(baseurl, "usa/florida", "z056gck1hqh0", 1)
#        getAndSaveCompassFacilityStatus(baseurl, "usa/florida2", "53db4g6rh5sc", 1)
        getAndSaveCompassFacilityStatus(baseurl, "usa/georgia", "2zhw91nntctn", 1)
        getAndSaveCompassFacilityStatus(baseurl, "usa/georgia2", "m6tgmv50632p", 1) # 49x closing september 2022. moving to Texas 1
        getAndSaveCompassFacilityStatus(baseurl, "usa/indiana", "dd5w0sjpymlt", 1)
        getAndSaveCompassFacilityStatus(baseurl, "usa/iowa", "nq11cxscsv6v", 1)
        getAndSaveCompassFacilityStatus(baseurl, "usa/kentucky1", "8zjbpfwpj6ph", 1)
#        getAndSaveCompassFacilityStatus(baseurl, "usa/kentucky2", "dcg727xjytwy", 1)
#        getAndSaveCompassFacilityStatus(baseurl, "usa/maine1", "0q8l9035qf85", 1)
#        getAndSaveCompassFacilityStatus(baseurl, "usa/maine2", "pjmk518l4v5t", 1)
        getAndSaveCompassFacilityStatus(baseurl, "usa/minnesota", "hy8mm5gxdtqm", 1)
        getAndSaveCompassFacilityStatus(baseurl, "usa/missouri", "rp79n8732323", 1)
        getAndSaveCompassFacilityStatus(baseurl, "usa/nebraska", "mjlq41wzc465", 1)
        getAndSaveCompassFacilityStatus(baseurl, "usa/nevada", "5fjs6hpxdsv0", 1)
        getAndSaveCompassFacilityStatus(baseurl, "usa/new-mexico", "7gfpdjccgfzq", 1)
        getAndSaveCompassFacilityStatus(baseurl, "usa/north-carolina", "2vqp9540jn0t", 1)
        getAndSaveCompassFacilityStatus(baseurl, "usa/oklahoma1", "1l88pl4v2qtr", 1)
#        getAndSaveCompassFacilityStatus(baseurl, "usa/oklahoma2", "ky917p6zlk1m", 1)
        getAndSaveCompassFacilityStatus(baseurl, "usa/oklahoma3", "1hczfjx1kvhb", 1)
#        getAndSaveCompassFacilityStatus(baseurl, "usa/pennsylvania", "11srlh63flpy", 1)
        getAndSaveCompassFacilityStatus(baseurl, "usa/south-carolina", "14kjx3pjvvbl", 1)
        getAndSaveCompassFacilityStatus(baseurl, "usa/texas", "hqy3cy37xcsp", 1)
        getAndSaveCompassFacilityStatus(baseurl, "usa/texas2", "fzy7c2q8z6m8", 1) # 56x
        getAndSaveCompassFacilityStatus(baseurl, "usa/washington", "6v408kf7qk7v", 1)

# --------------------------------------------------------------------------------------------------------------------
# getAndSaveCompassFacilityStatus
#
# Helper method to build directories as needed and download multiple pages of reported status for a facility over time
# --------------------------------------------------------------------------------------------------------------------
def getAndSaveCompassFacilityStatus(baseurl, facilityname, facilityid, pages):
    if not enableCompassStatus:
        print("WARNING: Call to getAndSaveCompassFacilityStatus made but enableCompassStatus is False")
        return
    folder = compassStatusDataDirectory + facilityname + "-" + facilityid + "/"
    makeDirIfNotExists(folder)
    for page in range(pages):
        strpage = str(int(page+1))
        filename = folder + "page" + strpage + ".html"
        fileurl = baseurl + "uptime/" + facilityid + "?page=" + strpage
        getAndSaveFile(fileurl, filename)
        time.sleep(10) # wait between queries

# --------------------------------------------------------------------------------------------------------------------
# getAndSaveF2PoolAccountInfo
#
# Provides details about the hashrate of account, but only for a 24 hour period.
# Payout history goes back quite a ways and should be consistent, adding new records each day there was activity
# Some relevant fields are
#   hashrate_history.<fieldname>				<fieldname> date time in 10 minute increments
#   payout_history[][<date value>, <description>, <amount>]	<date value> ISO8601 timestamp in day increment
#								<description> `txid moved to user_payout`
#								<value> is a float amount, may have e notation
#   payout_history_fee[][<date value>,<description>,<amount>]	same as above, just the fees for the pool
#   user_payout[][<date value>, <txid>, <amount>, <address>]	<date value> ISO8601 timestamp of payout time
#								<txid> bitcoin transaction id of the payout
#								<amount> amount of bitcoin sent
#								<address> bitcoin address sent to
# --------------------------------------------------------------------------------------------------------------------
def getAndSaveF2PoolAccountInfo():
    if not enableF2Pool:
        print("WARNING: Call to getAndSaveF2PoolAccountInfo made but enableF2Pool is False")
        return
    datefile = getdatefile()
    print(f"Retrieving and saving F2Pool info to {datefile}")
    with open(configFileF2Pool) as f:
        config = json.load(f)
    filename = f2PoolDataDirectory + datefile
    fileurl = "https://api.f2pool.com/bitcoin/" + config["account"]
    getAndSaveFile(fileurl, filename)

# --------------------------------------------------------------------------------------------------------------------
# getAndSaveLuxorHashrateInfo
#
# Retrieves information from Luxor Mining for an account via graphql
# Full API documentation at https://docs.luxor.tech/docs/
# Using Python library from https://github.com/LuxorLabs/graphql-python-client
# --------------------------------------------------------------------------------------------------------------------
def getAndSaveLuxorHashrateInfo():
    if not enableLuxor:
        print("WARNING: Call to getAndSaveLuxorHashrateInfo made but enableLuxor is False")
        return
    datefile = getdatefile()
    print(f"Retrieving and saving Luxor Hashrate info to {datefile}")
    try:
        with open(configFileLuxor) as f:
            config = json.load(f)
        filename = luxorDataDirectory + datefile
        apikey = config["apikey"]
        username = config["username"]
        LUXORAPI = API(host = 'https://api.beta.luxor.tech/graphql', method='POST', org='luxor', key=apikey)
        resp = LUXORAPI.get_hashrate_score_history(username,'BTC',100)
        with open(filename, 'a', encoding="utf-8") as outfile:
            json.dump(resp, outfile)
        print("ok.\n")
    except Error as e:
        print("error\n")
        print(e)

# --------------------------------------------------------------------------------------------------------------------
# getAndSaveSlushpoolInfo
#
# Retrieves information from Slushpool for an account via REST
# API documentation at https://help.slushpool.com/en/support/solutions/articles/77000433512-api-configuration-guide
# --------------------------------------------------------------------------------------------------------------------
def getAndSaveSlushpoolInfo():
    if not enableSlushpool:
        print("WARNING: Call to getAndSaveSlushpoolInfo made but enableSlushpool is False")
        return
    with open(configFileSlushpool) as f:
        config = json.load(f)
    headers = {"Slushpool-Auth-Token": config["authtoken"]}
    getAndSaveSlushpoolFile("pool stats", "poolstats/", "https://slushpool.com/stats/json/btc", headers)
    getAndSaveSlushpoolFile("user performance", "userprofile/", "https://slushpool.com/accounts/profile/json/btc", headers)
    getAndSaveSlushpoolFile("90 day daily rewards", "dailyreward/", "https://slushpool.com/accounts/reward/json/btc", headers)
    getAndSaveSlushpoolFile("worker performance", "workers/", "https://slushpool.com/accounts/workers/json/btc", headers)

# --------------------------------------------------------------------------------------------------------------------
# getAndSaveSlushpoolFile
#
# Helper method to build directories as needed, log what being done, and download respective file
# --------------------------------------------------------------------------------------------------------------------
def getAndSaveSlushpoolFile(comment, subdirectory, fileurl, headers):
    datefile = getdatefile()
    folder=slushpoolDataDirectory + subdirectory
    makeDirIfNotExists(folder)
    filename=folder + datefile
    print(f"Retrieving and saving Slushpool {comment} to {filename}")
    time.sleep(6)  # slushpool throttles/blocks if more than 1 per 5 seconds
    getAndSaveFile(fileurl, filename, headers)


# --------------------------------------------------------------------------------------------------------------------
# Main program entry point
# --------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Defaults
    enableBisq = True
    enableCollectAPI = True
    enableCompassHardware = False # API changed. Data no longer available
    enableCompassStatus = True
    enableF2Pool = True
    enableLuxor = True
    enableSlushpool = True
    dataDirectory="/home/nodeyez/nodeyez/data/"
    configFolder="/home/nodeyez/nodeyez/config/"
    configFileBisq=configFolder + "satsperusd.json"
    configFileCollectAPI=configFolder + "collectapi.json"
    configFileCompassHardware=configFolder + "compassmininghardware.json"
    configFileCompassStatus=configFolder + "compassminingstatus.json"
    configFileF2Pool=configFolder + "f2pool.json"
    configFileLuxor=configFolder + "luxor.json"
    configFileSlushpool=configFolder + "slushpool.json"
    sleepInterval=300 # This is for the main loop controller
    # Time Intervals for remote data pulls
    sleepIntervalBisq=3600
    sleepIntervalCollectAPI=86400
    sleepIntervalCompassHardware=3600
    sleepIntervalCompassStatus=82800
    sleepIntervalF2Pool=82800
    sleepIntervalLuxor=82800
    sleepIntervalSlushpool=82800
    lastTimeBisq=0
    lastTimeCollectAPI=0
    lastTimeCompassHardware=0
    lastTimeCompassStatus=0
    lastTimeF2Pool=0
    lastTimeLuxor=0
    lastSlushpool=0
    # Check that config exists
    if enableBisq and not exists(configFileBisq):
        enableBisq = False
        print(f"The Bisq Sats per USD configuration file was not defined at {configFileBisq}")
        print(f"Bisq data will not be downloaded")
    if enableCollectAPI and not exists(configFileCollectAPI):
        enableCollectAPI = False
        print(f"The Collect API configuration file was not defined at {configFileCollectAPI}")
        print(f"Collect API data will not be downloaded")
    if enableCompassHardware and not exists(configFileCompassHardware):
        enableCompassHardware = False
        print(f"The Compass Mining Hardware configuration file was not defined at {configFileCompassHardware}")
        print(f"Compass Mining Hardware data will not be downloaded")
    if enableCompassStatus and not exists(configFileCompassStatus):
        enableCompassStatus = False
        print(f"The Compass Mining Status configuration file was not defined at {configFileCompassStatus}")
        print(f"Compass Mining Status will not be downloaded")
    if enableF2Pool and not exists(configFileF2Pool):
        enableF2Pool = False
        print(f"The F2Pool configuration file was not defined at {configFileF2Pool}")
        print(f"F2Pool data will not be downloaded")
    if enableLuxor and not exists(configFileLuxor):
        enableLuxor = False
        print(f"The Luxor configuration file was not defined at {configFileLuxor}")
        print(f"Luxor data will not be downloaded")
    if enableSlushpool and not exists(configFileSlushpool):
        enableSlushpool = False
        print(f"The Slushpool configuration file was not defined at {configFileSlushpool}")
        print(f"Slushpool data will not be downloaded")
    # Data directories
    if not exists(dataDirectory):
        os.makedirs(dataDirectory)
    bisqDataDirectory = dataDirectory + "bisq/"
    if enableBisq:
        makeDirIfNotExists(bisqDataDirectory)
    collectAPIDataDirectory = dataDirectory + "collectapi/"
    if enableCollectAPI:
        makeDirIfNotExists(collectAPIDataDirectory)
    compassHardwareDataDirectory = dataDirectory + "compassmininghardware/"
    if enableCompassHardware:
        makeDirIfNotExists(compassHardwareDataDirectory)
    compassStatusDataDirectory = dataDirectory + "compassminingstatus/"
    if enableCompassStatus:
        makeDirIfNotExists(compassStatusDataDirectory)
    f2PoolDataDirectory = dataDirectory + "f2pool/"
    if enableF2Pool:
        makeDirIfNotExists(f2PoolDataDirectory)
    luxorDataDirectory = dataDirectory + "luxor/"
    if enableLuxor:
        makeDirIfNotExists(luxorDataDirectory)
    slushpoolDataDirectory = dataDirectory + "slushpool/"
    if enableSlushpool:
        makeDirIfNotExists(slushpoolDataDirectory)
    # Check for single run
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h','--help']:
            print(f"Retrieves API information and stores in the data directory for later user")
            print(f"Usage:")
            print(f"1) Call without arguments to run continuously using the configuration or defaults")
            print(f"2) Pass the desired API identifier to retrieve and exit")
            arg0 = sys.argv[0]
            print(f"   {arg0} bisq")
            print(f"   {arg0} collectapi")
            print(f"   {arg0} compassmininghardware")
            print(f"   {arg0} compsasminingstatus")
            print(f"   {arg0} f2pool")
            print(f"   {arg0} luxor")
            print(f"   {arg0} slushpool")
        else:
            apistub = sys.argv[1]
            if apistub == 'bisq':
                if enableBisq:
                    getAndSaveBisqInfo()
            elif apistub == 'collectapi':
                if enableCollectAPI:
                    getAndSaveCollectAPIInfo()
            elif apistub == 'compassmininghardware':
                if enableCompassHardware:
                    getAndSaveCompassMiningHardwareInfo()
            elif apistub == 'compassminingstatus':
                if enableCompassStatus:
                    getAndSaveCompassMiningStatusInfo()
            elif apistub == 'f2pool':
                if enableF2Pool:
                    getAndSaveF2PoolAccountInfo()
            elif apistub == 'luxor':
                if enableLuxor:
                    getAndSaveLuxorHashrateInfo()
            elif apistub == 'slushpool':
                if enableSlushpool:
                    getAndSaveSlushpoolInfo()
            else:
                print("Value not recognized. Call the program with --help for more guidance")
                exit(1)
        exit(0)
    # Loop
    while True:
        currentTime = int(time.time())
        if enableBisq and currentTime > lastTimeBisq + sleepIntervalBisq:
            getAndSaveBisqInfo()
            lastTimeBisq = currentTime if lastTimeBisq == 0 else lastTimeBisq + sleepIntervalBisq
        if enableCollectAPI and currentTime > lastTimeCollectAPI + sleepIntervalCollectAPI:
            getAndSaveCollectAPIInfo()
            lastTimeCollectAPI = currentTime if lastTimeCollectAPI == 0 else lastTimeCollectAPI + sleepIntervalCollectAPI
        if enableCompassHardware and currentTime > lastTimeCompassHardware + sleepIntervalCompassHardware:
            getAndSaveCompassMiningHardwareInfo()
            lastTimeCompassHardware = currentTime if lastTimeCompassHardware == 0 else lastTimeCompassHardware + sleepIntervalCompassHardware
        if enableCompassStatus and currentTime > lastTimeCompassStatus + sleepIntervalCompassStatus:
            getAndSaveCompassMiningStatusInfo()
            lastTimeCompassStatus = currentTime if lastTimeCompassStatus == 0 else lastTimeCompassStatus + sleepIntervalCompassStatus
        if enableF2Pool and currentTime > lastTimeF2Pool + sleepIntervalF2Pool:
            getAndSaveF2PoolAccountInfo()
            lastTimeF2Pool = currentTime if lastTimeF2Pool == 0 else lastTimeF2Pool + sleepIntervalF2Pool
        if enableLuxor and currentTime > lastTimeLuxor + sleepIntervalLuxor:
            getAndSaveLuxorHashrateInfo()
            lastTimeLuxor = currentTime if lastTimeLuxor == 0 else lastTimeLuxor + sleepIntervalLuxor
        if enableSlushpool and currentTime > lastTimeSlushpool + sleepIntervalSlushpool:
            getAndSaveSlushpoolInfo()
            lastTimeSlushpool = currentTime if lastTimeSlushpool == 0 else lastTimeSlushpool + sleepIntervalSlushpool
        time.sleep(sleepInterval)
