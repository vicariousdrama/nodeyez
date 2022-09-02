# import packages
from os.path import exists
import json
import math
import os
import subprocess
import time

def getandsavefile(useTor=True, url="https://raw.githubusercontent.com/vicariousdrama/nodeyez/main/images/logo.png", savetofile="/home/nodeyez/nodeyez/data/logo.png", extra=""):
    cmd = "curl --silent " + getconnecttimeouts() + extra + " --output " + savetofile + " " + url
    if useTor:
        cmd = "torify " + cmd
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
        print(f"file saved to {savetofile}\n")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"error saving file {savetofile} from url {url}\n")
        print(e)
        return 1

def getblockclockapicall(url="http://21.21.21.21/api/show/text/NODEYEZ", blockclockPassword=""):
    extra = ""
    if len(blockclockPassword) > 0:
        extra = " --digest -u :" + blockclockPassword + " "
    cmd = "curl --silent " + extra + " \"" + url + "\""
    try:
        if url == "http://21.21.21.21/api/show/text/NODEYEZ":
            print(f"ignoring command to display text to blockclock as url has not been set")
        else:
            cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
            print(cmdoutput)
    except subprocess.CalledProcessError as e:
        print(f"error {e}")

def getcompassmininghardwareinfo(useTor=True, hardwareurl="https://us-central1-hashr8-compass.cloudfunctions.net/app/hardware/group?isWeb=true&sortByCost=asc"):
    cmd = "curl --silent " + getconnecttimeouts() + hardwareurl
    if useTor:
        cmd = "torify " + cmd
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
    except subprocess.CalledProcessError as e:
        print(f"Error retrieving compass mining hardware data from {hardwareurl}")
        print(f"{e}")
        cmdoutput = '{"ok":true,"payload":{"hardwareGrouped":[]}}'
    j = json.loads(cmdoutput)
    return j

def getconnecttimeouts():
    return " --connect-timeout 5 --max-time 20 "

def getf2poolaccountinfo(useTor=True, account=""):
    emptyresult = '{"hashrate":0,"hashrate_history":{},"value_last_date":0.00,"value_today":0.00,"value_last_day":0.00}'
    url = "https://api.f2pool.com/bitcoin/" + account
    cmd = "curl --silent " + getconnecttimeouts() + url
    if useTor:
        cmd = "torify " + cmd
    cmdoutput = ""
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
    except subprocess.CalledProcessError as e:
        cmdoutput = emptyresult
    if len(cmdoutput) == 0:
        cmdoutput = emptyresult
    j = json.loads(cmdoutput)
    return j

def getmempoolblocks(useTor=True, url="https://mempool.space/api/v1/fees/mempool-blocks"):
    cmd = "curl --silent " + getconnecttimeouts() + url
    if useTor:
        cmd = "torify " + cmd
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
        j = json.loads(cmdoutput)
        return j
    except subprocess.CalledProcessError as e:
        cmdoutput = "[]"
        j = json.loads(cmdoutput)
        return j

def getmempoolrecommendedfees(useTor=True, url="https://mempool.space/api/v1/fees/recommended"):
    cmd = "curl --silent " + getconnecttimeouts() + url
    if useTor:
        cmd = "torify " + cmd
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
        j = json.loads(cmdoutput)
        return j["fastestFee"], j["halfHourFee"], j["hourFee"], j["minimumFee"]
    except subprocess.CalledProcessError as e:
        return 1, 1, 1, 1

def getmempoolhistograminfo(useTor=True, url="https://mempool.space/api/mempool"):
    cmd = "curl --silent " + getconnecttimeouts() + url
    if useTor:
        cmd = "torify " + cmd
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
        j = json.loads(cmdoutput)
        return j
    except subprocess.CalledProcessError as e:
        cmdoutput = '{"count":0,"vsize":0,"total_fee":0,"fee_histogram":[]}'
        j = json.loads(cmdoutput)
        return j

def getpriceinfo(useTor=True, priceUrl="https://bisq.markets/bisq/api/markets/ticker", price_last=-1, price_high=-1, price_low=-1):
    cmd = "curl --silent " + getconnecttimeouts() + priceUrl
    if useTor:
        cmd = "torify " + cmd
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

def getraretoshiuserinfo(useTor=True, raretoshiDataDirectory="/home/nodeyez/nodeyez/data/raretoshi/", raretoshiUser="rapidstart", userInfo=None, userInfoLast=0, userInfoInterval=3600):
    userFilename = raretoshiUser + ".json"
    localFilename = raretoshiDataDirectory + userFilename
    tempFilename = localFilename + ".tmp"
    refreshUser = False
    if not exists(localFilename):
        refreshUser = True
    if userInfoInterval + userInfoLast < int(time.time()):
        refreshUser = True
    if refreshUser == False:
        print(f"Using cached data from {userInfoLast}")
        return userInfo, userInfoLast
    # Do the work to get new user data
    print(f"Calling raretoshi website for user data")
    userInfoLast = int(time.time())
    url = "https://raretoshi.com/" + userFilename
    cmd = "curl --silent --output " + tempFilename + getconnecttimeouts() + url
    if useTor:
        cmd = "torify " + cmd
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
    return userInfo, userInfoLast

def getslushpoolaccountprofile(useTor=True, authtoken="invalid"):
    cmd = "curl --silent " + getconnecttimeouts() + " -H \"SlushPool-Auth-Token: " + authtoken + "\" https://slushpool.com/accounts/profile/json/btc/"
    if useTor:
        cmd = "torify " + cmd
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
        j = json.loads(cmdoutput)
    except subprocess.CalledProcessError as e:
        cmdoutput = ""
    if len(cmdoutput) == 0:
        cmdoutput = '''
        {"btc":
          {"confirmed_reward": null,
           "unconfirmed_reward": "0.00000000",
           "estimated_reward": "0.00000000",
           "hash_rate_unit": "Gh/s",
           "hash_rate_5m": 0.0000
          }
        }'''
        j = json.loads(cmdoutput)
    return j

def getslushpoolaccountrewards(useTor=True, authtoken="invalid"):
    time.sleep(6)
    cmd = "curl --silent " + getconnecttimeouts() + " -H \"SlushPool-Auth-Token: " + authtoken + "\" https://slushpool.com/accounts/rewards/json/btc/"
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

def getslushpoolstats(useTor=True, authtoken="invalid"):
    time.sleep(6)
    cmd = "curl --silent " + getconnecttimeouts() + " -H \"SlushPool-Auth-Token: " + authtoken + "\" https://slushpool.com/stats/json/btc/"
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

def getwhirlpoolliquidity(useTor=True):
    url = "https://pool.whirl.mx:8080/rest/pools"
    cmd = "curl --silent " + getconnecttimeouts() + url
    if useTor:
        cmd = "torify " + cmd
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
    except subprocess.CalledProcessError as e:
        cmdoutput = ""
    if len(cmdoutput) == 0:
        cmdoutput = '''
        {"pools":[
         {"poolId":"0.01btc","denomination":1000000,"feeValue":50000,
          "mustMixBalanceMin":1000170,"mustMixBalanceCap":1009690,"mustMixBalanceMax":1019125,"minAnonymitySet":5,"minMustMix":2,
          "tx0MaxOutputs":70,"nbRegistered":-1,"mixAnonymitySet":5,"mixStatus":"CONFIRM_INPUT","elapsedTime":5297,"nbConfirmed":-1},
         {"poolId":"0.001btc","denomination":100000,"feeValue":5000,
          "mustMixBalanceMin":100170,"mustMixBalanceCap":109690,"mustMixBalanceMax":119125,"minAnonymitySet":5,"minMustMix":2,
          "tx0MaxOutputs":25,"nbRegistered":-1,"mixAnonymitySet":5,"mixStatus":"CONFIRM_INPUT","elapsedTime":2296,"nbConfirmed":-1},
         {"poolId":"0.05btc","denomination":5000000,"feeValue":175000,
          "mustMixBalanceMin":5000170,"mustMixBalanceCap":5009690,"mustMixBalanceMax":5019125,"minAnonymitySet":5,"minMustMix":2,
          "tx0MaxOutputs":70,"nbRegistered":-1,"mixAnonymitySet":5,"mixStatus":"CONFIRM_INPUT","elapsedTime":9298,"nbConfirmed":-1},
         {"poolId":"0.5btc","denomination":50000000,"feeValue":1750000,
          "mustMixBalanceMin":50000170,"mustMixBalanceCap":50009690,"mustMixBalanceMax":50019125,"minAnonymitySet":5,"minMustMix":2,
          "tx0MaxOutputs":70,"nbRegistered":-1,"mixAnonymitySet":5,"mixStatus":"CONFIRM_INPUT","elapsedTime":1299,"nbConfirmed":-1}
         ]}'''
    j = json.loads(cmdoutput)
    return j
