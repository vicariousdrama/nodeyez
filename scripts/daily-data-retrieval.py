#! /usr/bin/python3
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
    cmd = "curl -s -o " + filename + " https://api.f2pool.com/bitcoin/" + config["account"]
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
        print("ok.\n")
    except subprocess.CalledProcessError as e:
        cmdoutput = "{\"hashrate\":0,\"hashrate_history\":{},\"value_last_day\":0.00,\"value_today\":0.00}"
        print("error\n")
        print(e)

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
    cmd = "curl -s -o " + filename + " " + config["hardwareurl"]
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
        print("ok.\n")
    except subprocess.CalledProcessError as e:
        print("error\n")
        print(e)


if __name__ == '__main__':
    # Defaults
    configFileF2Pool="/home/bitcoin/nodeyez/config/f2pool.json"
    configFileLuxor="/home/bitcoin/nodeyez/config/luxor.json"
    configFileCompassHardware="/home/bitcoin/nodeyez/config/compassmininghardware.json"
    dataDirectory="/home/bitcoin/nodeyez/data/"
    sleepInterval=82800 #  82800 = every 23 hours, 86400 is a full day.  We use the lower value to ensure no missing data, despite the overlap
    # Check for config
    if not exists(configFileF2Pool):
        print(f"You must have a F2Pool configuration file defined at {configFileF2Pool}")
        exit(1)
    if not exists(configFileLuxor):
        print(f"You must have a Luxor configuration file defined at {configFileLuxor}")
        exit(1)
    if not exists(configFileCompassHardware):
        print(f"You must have a Compass Mining Hardware configuration file defined at {configFileCompassHardware}")
        exit(1)
    # Data directories
    if not exists(dataDirectory):
        os.makedirs(dataDirectory)
    f2PoolDataDirectory = dataDirectory + "f2pool/"
    if not exists(f2PoolDataDirectory):
        os.makedirs(f2PoolDataDirectory)
    luxorDataDirectory = dataDirectory + "luxor/"
    if not exists(luxorDataDirectory):
        os.makedirs(luxorDataDirectory)
    compassHardwareDataDirectory = dataDirectory + "compassmininghardware/"
    if not exists(compassHardwareDataDirectory):
        os.makedirs(compassHardwareDataDirectory)
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
            if apistub == 'f2pool':
                getAndSaveF2PoolAccountInfo()
            elif apistub == 'luxor':
                getAndSaveLuxorHashrateInfo()
            elif apistub == 'compassmininghardware':
                getAndSaveCompassMiningHardwareInfo()
            else:
                print("Value not recognized. Call the program with --help for more guidance")
                exit(1)
        exit(0)
    # Loop
    while True:
        getAndSaveF2PoolAccountInfo()
        getAndSaveLuxorHashrateInfo()
        getAndSaveCompassMiningHardwareInfo()
        time.sleep(sleepInterval)
