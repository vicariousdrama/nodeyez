# import packages
from os.path import exists
from urllib3.exceptions import InsecureRequestWarning
import json
import math
import os
import requests
import shutil
import subprocess
import sys
import time

def gettimeouts():
    return (5,20)

def gettorproxies():
    # with tor service installed, default port is 9050
    # to find the port to use, can run the following
    #     cat /etc/tor/torrc | grep SOCKSPort | grep -v "#" | awk '{print $2}'
    return {'http': 'socks5h://127.0.0.1:9050','https': 'socks5h://127.0.0.1:9050'}


# do a GET call on specified url, save response body contents as file, return 0 if success, 1 if error
def getandsavefile(useTor=True, url="https://raw.githubusercontent.com/vicariousdrama/nodeyez/main/images/logo.png", savetofile="/home/nodeyez/nodeyez/data/logo.png", headers={}):
    try:
        if useTor:
            proxies = gettorproxies()
        else:
            proxies = {}
        timeout = gettimeouts()
        requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
        with requests.get(url,headers=headers,timeout=timeout,proxies=proxies,verify=False,stream=True) as response:
            response.raise_for_status()
            with open(savetofile, 'wb') as filetowriteto:
                for chunk in response.iter_content(chunk_size=8192):
                    filetowriteto.write(chunk)
                #shutil.copyfileobj(response.raw, filetowriteto)
        print(f"file saved to {savetofile}\n")
        return 0
    except Exception as e:
        print(f"error saving file {savetofile} from url {url}\n")
        print(f"{e}")
        return 1

# do a GET call on the specified url, and with response body, load and return as json
def geturl(useTor=True, url=None, defaultResponse="{}", headers={}):
    cmdoutput = ""
    try:
        if useTor:
            proxies = gettorproxies()
        else:
            proxies = {}
        timeout = gettimeouts()
        requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
        cmdoutput = requests.get(url,timeout=timeout,proxies=proxies,headers=headers,verify=False).text
    except Exception as e:
        print(f"error calling geturl: {e}")
        print(f"using default")
        cmdoutput = defaultResponse
    #print(cmdoutput)
    try:
        j = json.loads(cmdoutput)
    except Exception as e:
        print(f"error loading response as json: {e}")
        print(f"using default")
        j = json.loads(defaultResponse)
    return j

def getblockclockapicall(url="http://21.21.21.21/api/show/text/NODEYEZ", blockclockPassword=""):
    if url == "http://21.21.21.21/api/show/text/NODEYEZ":
        print(f"ignoring command to display text to blockclock as url has not been set")
        return
    if len(blockclockPassword) > 0:
        auth = requests.HTTPDigestAuth("",blockclockPassword)
        cmdoutput = requests.get(url,auth=auth).text
    else:
        cmdoutput = requests.get(url).text
    #print(cmdoutput)
    return cmdoutput

def getcompassmininghardwareinfo(useTor=True, url="https://us-central1-hashr8-compass.cloudfunctions.net/app/hardware/group?isWeb=true&sortByCost=asc"):
    defaultResponse = '{"ok":true,"payload":{"hardwareGrouped":[]}}'
    return geturl(useTor, url, defaultResponse)

def getf2poolaccountinfo(useTor=True, account=""):
    defaultResponse = '{"hashrate":0,"hashrate_history":{},"value_last_date":0.00,"value_today":0.00,"value_last_day":0.00}'
    url = "https://api.f2pool.com/bitcoin/" + account
    return geturl(useTor, url, defaultResponse)

def getmempoolblocks(useTor=True, url="https://mempool.space/api/v1/fees/mempool-blocks"):
    defaultResponse = "[]"
    return geturl(useTor, url, defaultResponse)

def getmempoolrecommendedfees(useTor=True, url="https://mempool.space/api/v1/fees/recommended"):
    defaultResponse = '{"fastestFee":1,"halfHourFee":1,"hourFee":1,"minimumFee":1}'
    j = geturl(useTor, url, defaultResponse)
    return j["fastestFee"], j["halfHourFee"], j["hourFee"], j["minimumFee"]

def getmempoolhistograminfo(useTor=True, url="https://mempool.space/api/mempool"):
    defaultResponse = '{"count":0,"vsize":0,"total_fee":0,"fee_histogram":[]}'
    return geturl(useTor, url, defaultResponse)

def getpriceinfo(useTor=True, url="https://bisq.markets/bisq/api/markets/ticker", price_last=-1, price_high=-1, price_low=-1):
    defaultResponse = '{"error": "dont care"}'
    j = geturl(useTor, url, defaultResponse)
    if "error" not in j:
        price_last = int(math.floor(float(j["btc_usd"]["last"])))
        price_high = int(math.floor(float(j["btc_usd"]["high"])))
        price_low = int(math.floor(float(j["btc_usd"]["low"])))
    return (price_last,price_high,price_low)

def getraretoshiuserinfo1(useTor=True, raretoshiDataDirectory="/home/nodeyez/nodeyez/data/raretoshi/", raretoshiUser="rapidstart", userInfo=None, userInfoLast=0, userInfoInterval=3600):
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
    url = "https://raretoshi.com/" + userFilename
    headers = {}
    rc = getandsavefile(useTor, url, tempFilename, headers)
    if rc == 0:
        userInfoLast = int(time.time())
        with open(tempFilename) as f:
            userInfo = json.load(f)
        if exists(localFilename):
            os.remove(localFilename)
        os.rename(tempFilename, localFilename)
    if rc == 1:
        print(f"Error downloading and loading file {tempFilename}.")
        if exists(localFilename):
            print("Attempting to reload from cached result {localFilename}")
            try:
                with open(localFilename) as f:
                    userInfo = json.load(f)
            except:
                print("Error raised reading {localFilename} as json")
    return userInfo, userInfoLast

def getraretoshiuserinfo2(useTor=True, raretoshiDataDirectory="/home/nodeyez/nodeyez/data/raretoshi/", raretoshiUser="rapidstart", userInfo=None, userInfoLast=0, userInfoInterval=3600):
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
    url = "https://raretoshi.com/" + raretoshiUser
    print(f"Retrieving user properties from {url}")
    try:
        if useTor:
            proxies = gettorproxies()
        else:
            proxies = {}
        timeout = gettimeouts()
        requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
        cmdoutput = requests.get(url,timeout=timeout,proxies=proxies,verify=False).text
        # look for props
        scriptprops = '<script type="application/json" sveltekit:data-type="props">'
        scriptpropsidx = cmdoutput.find(scriptprops)
        if scriptpropsidx != -1:
            props = cmdoutput[len(scriptprops) + scriptpropsidx:]
            scriptpropsend = '</script>'
            scriptpropsendidx = props.find(scriptpropsend)
            if scriptpropsendidx != -1:
                props = props[:scriptpropsendidx]
                #print(props)
                # write to the tempFilename
                with open(tempFilename, 'w') as f:
                    f.write(props)
                userInfoLast = int(time.time())
                # load it back as json
                with open(tempFilename) as f:
                    userInfo = json.load(f)
                if exists(localFilename):
                    os.remove(localFilename)
                os.rename(tempFilename, localFilename)
                return userInfo, userInfoLast
            else:
                print("could not find scriptpropsend")
        else:
            print("could not find scriptprops")
    except Exception as e:
        print("could not get user")
        print(f"{e}")
    print("falling back to getraretoshiuserinfo1 logic")
    return getraretoshiuserinfo1(useTor, raretoshiDataDirectory, raretoshiUser, userInfo, userInfoLast, userInfoInterval)

def getraretoshiuserinfo(useTor=True, raretoshiDataDirectory="/home/nodeyez/nodeyez/data/raretoshi/", raretoshiUser="rapidstart", userInfo=None, userInfoLast=0, userInfoInterval=3600):
    return getraretoshiuserinfo2(useTor, raretoshiDataDirectory, raretoshiUser, userInfo, userInfoLast, userInfoInterval)

def getslushpoolheaders(authtoken):
    headers = {"SlushPool-Auth-Token": authtoken}
    return headers

def getslushpoolaccountprofile(useTor=True, authtoken="invalid"):
    url = "https://slushpool.com/accounts/profile/json/btc/"
    headers = getslushpoolheaders(authtoken)
    defaultResponse = '{"btc":{"confirmed_reward":null,"unconfirmed_reward":"0.00000000","estimated_reward":"0.00000000","hash_rate_unit":"Gh/s","hash_rate_5m": 0.0000}}'
    return geturl(useTor, url, defaultResponse, headers)

def getslushpoolaccountrewards(useTor=True, authtoken="invalid"):
    url = "https://slushpool.com/accounts/rewards/json/btc/"
    headers = getslushpoolheaders(authtoken)
    defaultResponse = '{"btc":{"daily_rewards":[]}}'
    return geturl(useTor, url, defaultResponse, headers)

def getslushpoolstats(useTor=True, authtoken="invalid"):
    url = "https://slushpool.com/stats/json/btc/"
    headers = getslushpoolheaders(authtoken)
    defaultResponse = '{"btc":{"blocks":{"0":{"date_found":0,"mining_duration":0,"total_shares":0,"state":"confirmed","confirmations_left":0,"value": "0.00000000","user_reward": "0.00000000","pool_scoring_hash_rate": 0.000000}}}}'
    return geturl(useTor, url, defaultResponse, headers)

def getwhirlpoolheaders(apiKey=""):
    headers = {}
    if len(apiKey) > 0:
        headers["apiKey"] = apiKey
    return headers

def getwhirlpoolliquidity(useTor=True, url="https://pool.whirl.mx:8080", apiKey=""):
    path="/rest/pools"
    whirlpoolurl = url + path
    headers = getwhirlpoolheaders(apiKey)
    defaultResponse = '''{
        "pools":[
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
    return geturl(useTor, whirlpoolurl, defaultResponse, headers)

def getwhirlpoolmix(useTor=True, url=None, apiKey=""):
    path = "/rest/mixX"
    whirlpoolurl = url + path
    headers = getwhirlpoolheaders(apiKey)
    defaultResponse = '''{
          "started": true,
          "nbMixing": 5,
          "nbQueued": 43,
          "threads": [
            {
              "hash": "deadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef",
              "index": 3,
              "value": 100000,
              "confirmations": 1234,
              "path": "M/0/615",
              "address": "bc1qzuyh3i8e284wqpbdnjtx0r74gepg64erwzwt72",
              "account": "POSTMIX",
              "status": "MIX_STARTED",
              "mixStep": "REGISTERED_INPUT",
              "mixableStatus": "MIXABLE",
              "progressPercent": 30,
              "poolId": "0.001btc",
              "mixsDone": 11,
              "message": null,
              "error": null,
              "lastActivityElapsed": 131823
            },
            {
              "hash": "deadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef",
              "index": 3,
              "value": 100000,
              "confirmations": 1234,
              "path": "M/0/615",
              "address": "bc1qzuyh3i8e284wqpbdnjtx0r74gepg64erwzwt72",
              "account": "POSTMIX",
              "status": "MIX_STARTED",
              "mixStep": "REVEALED_OUTPUT",
              "mixableStatus": "MIXABLE",
              "progressPercent": 30,
              "poolId": "0.0025btc",
              "mixsDone": 11,
              "message": null,
              "error": null,
              "lastActivityElapsed": 31823
            },
            {
              "hash": "deadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef",
              "index": 3,
              "value": 100000,
              "confirmations": 1234,
              "path": "M/0/615",
              "address": "bc1qzuyh3i8e284wqpbdnjtx0r74gepg64erwzwt72",
              "account": "POSTMIX",
              "status": "MIX_STARTED",
              "mixStep": "REGISTERED_OUTPUT",
              "mixableStatus": "MIXABLE",
              "progressPercent": 30,
              "poolId": "0.005btc",
              "mixsDone": 11,
              "message": null,
              "error": null,
              "lastActivityElapsed": 231823
            },
            {
              "hash": "deadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef",
              "index": 3,
              "value": 100000,
              "confirmations": 1234,
              "path": "M/0/615",
              "address": "bc1qzuyh3i8e284wqpbdnjtx0r74gepg64erwzwt72",
              "account": "POSTMIX",
              "status": "MIX_STARTED",
              "mixStep": "CONFIRMED_INPUT",
              "mixableStatus": "MIXABLE",
              "progressPercent": 30,
              "poolId": "0.01btc",
              "mixsDone": 11,
              "message": null,
              "error": null,
              "lastActivityElapsed": 631823
            },
            {
              "hash": "deadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef",
              "index": 3,
              "value": 100000,
              "confirmations": 1234,
              "path": "M/0/615",
              "address": "bc1qzuyh3i8e284wqpbdnjtx0r74gepg64erwzwt72",
              "account": "POSTMIX",
              "status": "MIX_STARTED",
              "mixStep": "CONFIRMING_INPUT",
              "mixableStatus": "MIXABLE",
              "progressPercent": 30,
              "poolId": "0.025btc",
              "mixsDone": 11,
              "message": null,
              "error": null,
              "lastActivityElapsed": 1131823
            }
          ]
        }'''
    return geturl(useTor, whirlpoolurl, defaultResponse, headers)

def getwhirlpoolcliconfig(useTor=True, url=None, apiKey=""):
    path = "/rest/cli"
    whirlpoolurl = url + path
    headers = getwhirlpoolheaders(apiKey)
    defaultResponse = '''{
         "cliStatus":"ERROR", "cliMessage": null, "loggedIn": false, "torProgress": 0, "network": "main", 
         "serverUrl": "http://udkmfc5j6zvv3ysavbrwzhwji4hpyfe3apqa6yst7c7l32mygf65g4ad.onion", "serverName": "MAINNET",
         "dojoUrl": "ERROR", "tor": false, "dojo": false, "version": "0.10.15"
        }'''
    return geturl(useTor, whirlpoolurl, defaultResponse, headers)

