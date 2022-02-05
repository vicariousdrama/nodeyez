#! /usr/bin/python3
from datetime import datetime
import json
import subprocess
import time
from luxor import API

dataDirectory="/home/bitcoin/nodeyez/data/"

configFileF2Pool="/home/bitcoin/nodeyez/config/f2pool.json"
configFileLuxor="/home/bitcoin/nodeyez/config/luxor.json"

sleepInterval=82800 #  82800 = every 23 hours, 86400 is a full day.  We use the lower value to ensure no missing data, despite the overlap

def getdatefile():
    return datetime.utcnow().strftime("%Y-%m-%d") + ".json"

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
        filename = dataDirectory + "luxor/" + datetime.utcnow().strftime("%Y-%m-%d") + ".json"
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

while True:
    getAndSaveF2PoolAccountInfo()
    getAndSaveLuxorHashrateInfo()
    time.sleep(sleepInterval)
