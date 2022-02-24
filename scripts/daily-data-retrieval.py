#! /usr/bin/env python3
from datetime import datetime
from os.path import exists
import json
import os
import subprocess
import sys
import time
from luxor import API

def getdatefile():
    return datetime.utcnow().strftime("%Y-%m-%d-%H") + ".json"

def isFirstOfTheMonth():
    return (int(datetime.utcnow().strftime("%e")) == 1)

def getAndSaveFile(url, savetofile):
    cmd = "curl -s -o " + savetofile + " " + url
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
        print(f"file saved to {savetofile}\n")
    except subprocess.CalledProcessError as e:
        print(f"error saving file {savetofile} from url {url}\n")
        print(e)

# --------------------------------------------------------------------------------------------------------------------
# getAndSaveBisqInfo
#
# Retrieves the current bisq market data and saves to the data directory for historical tracking
# Some relevant fields are within a currency pair: last, high, low.  The buy and sell reflect offer spreads
#   btc_usd <last, high, low, volume_left, volume_right, buy, sell>
#   bsq_btc <last, high, low, volume_left, volume_right, buy, sell>
# --------------------------------------------------------------------------------------------------------------------
def getAndSaveBisqInfo():
    datefile = getdatefile()
    print(f"Retrieving and saving Bisq Mark Price info to {datefile}")
    with open(configFileBisq) as f:
        config = json.load(f)
    filename = dataDirectory + "bisq/" + datefile
    getAndSaveFile(config["priceurl"], filename)

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
    datefile = getdatefile()
    print(f"Retrieving and saving Compass Mining Hardware info to {datefile}")
    with open(configFileCompassHardware) as f:
        config = json.load(f)
    filename = dataDirectory + "compassmininghardware/" + datefile
    getAndSaveFile(config["hardwareurl"], filename)

# --------------------------------------------------------------------------------------------------------------------
# getAndSaveCompassMiningStatusInfo
#
# Provides details about the facility status at Compass Mining as a snapshot
#
# In addition, saving snapshots for details for individual facilities
# --------------------------------------------------------------------------------------------------------------------
def getAndSaveCompassMiningStatusInfo():
    datefile = getdatefile().replace(".json", ".html")
    print(f"Retrieving and saving Compass Mining Status info to {datefile}")
    with open(configFileCompassStatus) as f:
        config = json.load(f)
    filename = dataDirectory + "compassminingstatus/" + datefile
    baseurl = config["statusurl"]
    getAndSaveFile(baseurl, filename)
    if isFirstOfTheMonth():
        getAndSaveCompassFacilityStatus(baseurl, "canada/alberta", "3kdqgw2547nv", 1)
        getAndSaveCompassFacilityStatus(baseurl, "canada/manitoba1", "t9ck2m81j50d", 1)
        getAndSaveCompassFacilityStatus(baseurl, "canada/manitoba2", "3jz0mjsctwx8", 1)
        getAndSaveCompassFacilityStatus(baseurl, "canada/quebec", "n9yqj1td9v32", 1)
        getAndSaveCompassFacilityStatus(baseurl, "iceland/southern-peninsula", "0wtyz0xpgswf", 1)
        getAndSaveCompassFacilityStatus(baseurl, "kazakhstan/pavlodar-region", "k4kgphjfmg1q", 1)
        getAndSaveCompassFacilityStatus(baseurl, "russia/krasnoyarsk-krai", "9yg10xhkyzym", 1)
        getAndSaveCompassFacilityStatus(baseurl, "russia/irkutsk", "jsmkt30pdk16", 1)
        getAndSaveCompassFacilityStatus(baseurl, "usa/alabama", "44f9l6qw3723", 1)
        getAndSaveCompassFacilityStatus(baseurl, "usa/florida", "z056gck1hqh0", 1)
        getAndSaveCompassFacilityStatus(baseurl, "usa/florida2", "53db4g6rh5sc", 1)
        getAndSaveCompassFacilityStatus(baseurl, "usa/indiana", "dd5w0sjpymlt", 1)
        getAndSaveCompassFacilityStatus(baseurl, "usa/iowa", "nq11cxscsv6v", 1)
        getAndSaveCompassFacilityStatus(baseurl, "usa/kentucky1", "8zjbpfwpj6ph", 1)
        getAndSaveCompassFacilityStatus(baseurl, "usa/kentucky2", "dcg727xjytwy", 1)
        getAndSaveCompassFacilityStatus(baseurl, "usa/maine1", "0q8l9035qf85", 1)
        getAndSaveCompassFacilityStatus(baseurl, "usa/maine2", "pjmk518l4v5t", 1)
        getAndSaveCompassFacilityStatus(baseurl, "usa/nebraska", "mjlq41wzc465", 1)
        getAndSaveCompassFacilityStatus(baseurl, "usa/nevada", "5fjs6hpxdsv0", 1)
        getAndSaveCompassFacilityStatus(baseurl, "usa/new-mexico", "7gfpdjccgfzq", 1)
        getAndSaveCompassFacilityStatus(baseurl, "usa/north-carolina", "2vqp9540jn0t", 1)
        getAndSaveCompassFacilityStatus(baseurl, "usa/oklahoma1", "1l88pl4v2qtr", 1)
        getAndSaveCompassFacilityStatus(baseurl, "usa/oklahoma2", "ky917p6zlk1m", 1)
        getAndSaveCompassFacilityStatus(baseurl, "usa/pennsylvania", "11srlh63flpy", 1)
        getAndSaveCompassFacilityStatus(baseurl, "usa/washington", "6v408kf7qk7v", 1)

# --------------------------------------------------------------------------------------------------------------------
# getAndSaveCompassFacilityStatus
#
# Helper method to build directories as needed and download multiple pages of reported status for a facility over time
# --------------------------------------------------------------------------------------------------------------------
def getAndSaveCompassFacilityStatus(baseurl, facilityname, facilityid, pages):
    folder = dataDirectory + "compassminingstatus/" + facilityname + "-" + facilityid + "/"
    if not exists(folder):
        os.makedirs(folder)
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
    datefile = getdatefile()
    print(f"Retrieving and saving F2Pool info to {datefile}")
    with open(configFileF2Pool) as f:
        config = json.load(f)
    filename = dataDirectory + "f2pool/" + datefile
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
    datefile = getdatefile()
    print(f"Retrieving and saving Luxor Hashrate info to {datefile}")
    try:
        with open(configFileLuxor) as f:
            config = json.load(f)
        filename = dataDirectory + "luxor/" + datefile
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
# Main program entry point
# --------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Defaults
    configFileBisq="/home/bitcoin/nodeyez/config/satsperusd.json"
    configFileCompassHardware="/home/bitcoin/nodeyez/config/compassmininghardware.json"
    configFileCompassStatus="/home/bitcoin/nodeyez/config/compassminingstatus.json"
    configFileF2Pool="/home/bitcoin/nodeyez/config/f2pool.json"
    configFileLuxor="/home/bitcoin/nodeyez/config/luxor.json"
    dataDirectory="/home/bitcoin/nodeyez/data/"
    sleepInterval=300 # This is for the main loop controller
    # Time Intervals for remote data pulls
    sleepIntervalBisq=3600
    sleepIntervalCompassHardware=3600
    sleepIntervalCompassStatus=82800
    sleepIntervalF2Pool=82800
    sleepIntervalLuxor=82800
    lastTimeBisq=0
    lastTimeCompassHardware=0
    lastTimeCompassStatus=0
    lastTimeF2Pool=0
    lastTimeLuxor=0
    # Check that config exists
    if not exists(configFileBisq):
        print(f"You must have a Bisq or SatsPerUSD configuration file defined at {configFileBisq}")
        exit(1)
    if not exists(configFileCompassHardware):
        print(f"You must have a Compass Mining Hardware configuration file defined at {configFileCompassHardware}")
        exit(1)
    if not exists(configFileCompassStatus):
        print(f"You must have a Compass Mining Status configuration file defined at {configFileCompassStatus}")
        exit(1)
    if not exists(configFileF2Pool):
        print(f"You must have a F2Pool configuration file defined at {configFileF2Pool}")
        exit(1)
    if not exists(configFileLuxor):
        print(f"You must have a Luxor configuration file defined at {configFileLuxor}")
        exit(1)
    # Data directories
    if not exists(dataDirectory):
        os.makedirs(dataDirectory)
    bisqDataDirectory = dataDirectory + "bisq/"
    if not exists(bisqDataDirectory):
        os.makedirs(bisqDataDirectory)
    compassHardwareDataDirectory = dataDirectory + "compassmininghardware/"
    if not exists(compassHardwareDataDirectory):
        os.makedirs(compassHardwareDataDirectory)
    compassStatusDataDirectory = dataDirectory + "compassminingstatus/"
    if not exists(compassStatusDataDirectory):
        os.makedirs(compassStatusDataDirectory)
    f2PoolDataDirectory = dataDirectory + "f2pool/"
    if not exists(f2PoolDataDirectory):
        os.makedirs(f2PoolDataDirectory)
    luxorDataDirectory = dataDirectory + "luxor/"
    if not exists(luxorDataDirectory):
        os.makedirs(luxorDataDirectory)
    # Check for single run
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h','--help']:
            print(f"Retrieves API information and stores in the data directory for later user")
            print(f"Usage:")
            print(f"1) Call without arguments to run continuously using the configuration or defaults")
            print(f"2) Pass the desired API identifier to retrieve and exit")
            arg0 = sys.argv[0]
            print(f"   {arg0} f2pool")
            print(f"  or")
            print(f"   {arg0} luxor")
            print(f"You may specify a custom configuration file at {configFile}")
        else:
            apistub = sys.argv[1]
            if apistub == 'bisq':
                getAndSaveBisqInfo()
            elif apistub == 'compassmininghardware':
                getAndSaveCompassMiningHardwareInfo()
            elif apistub == 'compassminingstatus':
                getAndSaveCompassMiningStatusInfo()
            elif apistub == 'f2pool':
                getAndSaveF2PoolAccountInfo()
            elif apistub == 'luxor':
                getAndSaveLuxorHashrateInfo()
            else:
                print("Value not recognized. Call the program with --help for more guidance")
                exit(1)
        exit(0)
    # Loop
    while True:
        currentTime = int(time.time())
        if currentTime > lastTimeBisq + sleepIntervalBisq:
            getAndSaveBisqInfo()
            lastTimeBisq = currentTime if lastTimeBisq == 0 else lastTimeBisq + sleepIntervalBisq
        if currentTime > lastTimeCompassHardware + sleepIntervalCompassHardware:
            getAndSaveCompassMiningHardwareInfo()
            lastTimeCompassHardware = currentTime if lastTimeCompassHardware == 0 else lastTimeCompassHardware + sleepIntervalCompassHardware
        if currentTime > lastTimeCompassStatus + sleepIntervalCompassStatus:
            getAndSaveCompassMiningStatusInfo()
            lastTimeCompassStatus = currentTime if lastTimeCompassStatus == 0 else lastTimeCompassStatus + sleepIntervalCompassStatus
        if currentTime > lastTimeF2Pool + sleepIntervalF2Pool:
            getAndSaveF2PoolAccountInfo()
            lastTimeF2Pool = currentTime if lastTimeF2Pool == 0 else lastTimeF2Pool + sleepIntervalF2Pool
        if currentTime > lastTimeLuxor + sleepIntervalLuxor:
            getAndSaveLuxorHashrateInfo()
            lastTimeLuxor = currentTime if lastTimeLuxor == 0 else lastTimeLuxor + sleepIntervalLuxor
        time.sleep(sleepInterval)
