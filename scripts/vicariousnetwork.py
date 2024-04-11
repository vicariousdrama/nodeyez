# import packages
from PIL import Image, ImageColor
from datetime import datetime
from os.path import exists
from requests.auth import HTTPBasicAuth
from urllib3.exceptions import InsecureRequestWarning
from wand.api import library
import glob
import io
import json
import math
import os
import requests
import time
import wand.color
import wand.image
from pathlib import Path


def gettimeouts():
    return (10,20)

def gettorproxies():
    # with tor service installed, default port is 9050
    # to find the port to use, can run the following
    #     cat /etc/tor/torrc | grep SOCKSPort | grep -v "#" | awk '{print $2}'
    return {'http': 'socks5h://127.0.0.1:9050','https': 'socks5h://127.0.0.1:9050'}

# do a GET call on specified url, save response body contents as file, return 0 if success, 1 if error
def getandsavefile(useTor=True, url="https://nodeyez.com/images/logo.png", savetofile="../data/logo.png", headers={}):
    if not exists(savetofile.rpartition("/")[0]):
        os.makedirs(savetofile.rpartition("/")[0])
    try:
        proxies = gettorproxies() if useTor else {}
        timeout = gettimeouts()
        requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
        with requests.get(url,headers=headers,timeout=timeout,proxies=proxies,verify=False,stream=True) as response:
            response.raise_for_status()
            with open(savetofile, 'wb') as filetowriteto:
                for chunk in response.iter_content(chunk_size=8192):
                    filetowriteto.write(chunk)
        #print(f"file saved to {savetofile}\n")
        return 0
    except Exception as e:
        print(f"error saving file {savetofile} from url {url}\n{e}")
        return 1

# do a GET call on the specified url, and return the response body
def getpage(useTor=True, url=None, defaultResponse="{}", headers={}):
    cmdoutput = ""
    try:
        proxies = gettorproxies() if useTor else {}
        timeout = gettimeouts()
        requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
        cmdoutput = requests.get(url,timeout=timeout,proxies=proxies,headers=headers,verify=False).text
    except Exception as e:
        print(f"error calling geturl: {e}")
        print(f"using default response {defaultResponse}")
        cmdoutput = defaultResponse
    return cmdoutput

# do a GET call on the specified url, and with response body, load and return as json
def geturl(useTor=True, url=None, defaultResponse="{}", headers={}):
    cmdoutput = ""
    try:
        proxies = gettorproxies() if useTor else {}
        timeout = gettimeouts()
        requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
        cmdoutput = requests.get(url,timeout=timeout,proxies=proxies,headers=headers,verify=False).text
    except Exception as e:
        print(f"error calling geturl: {e}")
        print(f"using default response {defaultResponse}")
        cmdoutput = defaultResponse
    try:
        j = json.loads(cmdoutput)
    except Exception as e:
        print(f"error loading response as json: {e}")
        print(f"using default response {defaultResponse}")
        j = json.loads(defaultResponse)
    return j

# do a GET call on the specified url, and with response body, load into pillow image
def getimagefromurl(useTor=True, url=None, headers={}):
    if url.startswith("file://"):
        return getimagefromfile(filepath=url)
    img = Image.new(mode="RGB", size=(1,1), color=ImageColor.getrgb("#7f007f")) # default response is a 1x1 purple
    try:
        proxies = gettorproxies() if useTor else {}
        timeout = gettimeouts()
        requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
        with requests.get(url,headers=headers,timeout=timeout,proxies=proxies,verify=False,stream=True) as response:
            response.raise_for_status()
            ct = response.headers['content-type']
            if ct in ['image/png','image/bmp','image/gif','image/jpeg']:
                img = Image.open(response.raw)
            if ct in ['image/svg','image/svg+xml']:
                response.raw.decode_content=True
                svgfile=response.raw
                with wand.image.Image() as image:
                    with wand.color.Color('transparent') as background_color:
                        library.MagickSetBackgroundColor(image.wand, background_color.resource)
                    image.read(blob=svgfile.read(),format="svg")
                    img = Image.open(io.BytesIO(image.make_blob("png32")))
    except Exception as e:
        print(f"error retrieving image from url {url}\n")
        print(f"{e}")
    return img

def getimagefromfile(filepath=None):
    img = Image.new(mode="RGB", size=(1,1), color=ImageColor.getrgb("#7f007f"))
    try:
        if filepath.startswith("file://"):
            filepath = filepath[7:]
            ext = filepath.rpartition('.')[2]
            if ext not in ['png','bmp','gif','jpg','webp','tiff','svg']:
                raise "Unsupported extension in getimagefromfile"
            if ext in ['png','bmp','gif','jpg','webp','tiff']:
                img = Image.open(filepath)
            if ext in ['svg']:
                with open(filepath,'rb') as file:
                    with wand.image.Image() as image:
                        with wand.color.Color('transparent') as background_color:
                            library.MagickSetBackgroundColor(image.wand, background_color.resource)
                        image.read(blob=file.read(),format="svg")
                        img = Image.open(io.BytesIO(image.make_blob("png32")))
    except Exception as e:
        print(f"error retrieving image from file {filepath}\n")
        print(f"{e}")
    return img

def getblockclockapicall(url="http://21.21.21.21/api/show/text/NODEYEZ", blockclockPassword=""):
    if url == "http://21.21.21.21/api/show/text/NODEYEZ":
        print(f"ignoring command to display text to blockclock as url has not been set")
        return
    if len(blockclockPassword) > 0:
        auth = requests.HTTPDigestAuth("",blockclockPassword)
        cmdoutput = requests.get(url,auth=auth).text
    else:
        cmdoutput = requests.get(url).text
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
    defaultResponse = '{"fastestFee":-1,"halfHourFee":-1,"hourFee":-1,"minimumFee":-1}'
    j = geturl(useTor, url, defaultResponse)
    return j["fastestFee"], j["halfHourFee"], j["hourFee"], j["minimumFee"]

def getmempoolhistograminfo(useTor=True, url="https://mempool.space/api/mempool"):
    defaultResponse = '{"count":-1,"vsize":0,"total_fee":0,"fee_histogram":[]}'
    return geturl(useTor, url, defaultResponse)

def getnewestfile(fileDirectory):
    files = glob.glob(fileDirectory)
    newestfile = ""
    if len(files) > 0:
        newestfile = max(files, key=os.path.getctime)
    return newestfile

def checkifstale(filePath=None, fileAge=86400):
    if filePath is None: return False
    if len(filePath) <= 0: return False
    mtime = int(os.path.getmtime(filePath))
    currenttime = int(time.time())
    diff = currenttime - mtime
    if diff > fileAge: return False
    return True

def getfromurlifstale(useTor=True, url="https://example.com/", basePath="../data/example", fileAge=86400):
    year = datetime.utcnow().strftime("%Y")
    month = datetime.utcnow().strftime("%m")
    path = f"{basePath}/{year}/{month}/"
    if not os.path.exists(path): os.makedirs(path)
    newestfile = getnewestfile(path + "*.json")
    fileOK = checkifstale(filePath=newestfile, fileAge=fileAge)
    if not fileOK:
        fn = datetime.utcnow().strftime("%Y-%m-%d-%H") + ".json"
        savetofile = f"{path}{fn}"
        getandsavefile(useTor, url, savetofile)
        newestfile = getnewestfile(path + "*.json")
    return newestfile

def posttourlifstale(useTor=True, url="https://example.com", data=None, defaultResponse="{}", headers={}, username=None, password=None, basePath="../data/example", fileAge=86400):
    year = datetime.utcnow().strftime("%Y")
    month = datetime.utcnow().strftime("%m")
    path = f"{basePath}/{year}/{month}/"
    if not os.path.exists(path): os.makedirs(path)
    newestfile = getnewestfile(path + "*.json")
    fileOK = checkifstale(filePath=newestfile, fileAge=fileAge)
    if not fileOK:
        fn = datetime.utcnow().strftime("%Y-%m-%d-%H") + ".json"
        savetofile = f"{path}{fn}"
        try:
            j = posturl(useTor=useTor, url=url, data=data, defaultResponse=defaultResponse, headers=headers, username=username, password=password)
            if j != {}:
                with open(savetofile, "w") as f:
                    json.dump(j, f)
        except Exception as e:
            # warn
            print("error in posttourlifstale")
            print(f"{e}")
        newestfile = getnewestfile(path + "*.json")
    return newestfile

def getgeysertags(useTor=False):
    geyserUrl = "https://api.geyser.fund/graphql"
    graphqlHeaders = {"content-type": "application/json"}
    graphqlQuery = '{"operationName":"TagsGet","query":"query TagsGet {tagsGet {label id count} }"}'
    defaultResponse = "{}"
    basePath="../data/geyserfund/taglist"
    fileAge=86400
    errresponse={}
    j = errresponse
    try:
        newestfile = posttourlifstale(useTor=useTor, url=geyserUrl, data=graphqlQuery, defaultResponse=defaultResponse, headers=graphqlHeaders, username=None, password=None, basePath=basePath, fileAge=fileAge)
        if len(newestfile) > 0:
            with open(newestfile) as f:
                j = json.load(f)
        while "data" in j: j = j["data"]
        while "tagsGet" in j: j = j["tagsGet"]
    except:
        j = errresponse
    return j

def getgeyserprojects(useTor=False, tagId=1, pagination=None):
    pageSize = 20
    paginationCursorInfo = ""
    if pagination is not None:
        # want to produce to look like      "cursor":{"id":476},
        paginationCursorInfo = '"cursor":{"id":' + f"{pagination}" + '},'
    geyserUrl = "https://api.geyser.fund/graphql"
    graphqlHeaders = {"content-type": "application/json"}
    graphqlQuery = '{"operationName":"ProjectsForLandingPage","variables":{"input":{"pagination":{' + paginationCursorInfo + '"take":' + f"{pageSize}" + '},"where":{"tagIds":[' + f"{tagId}" + ']},"orderBy":{"field":"balance", "direction":"desc"}}},"query":"fragment ProjectForLandingPage on Project {id name image tags {label} status thumbnailImage shortDescription title} query ProjectsForLandingPage($input: ProjectsGetQueryInput) {projectsGet(input: $input) {projects {...ProjectForLandingPage}}}"}'
    defaultResponse = "{}"
    basePath=f"../data/geyserfund/tagid-{tagId}"
    fileAge=86400
    errresponse={}
    j = errresponse
    try:
        newestfile = posttourlifstale(useTor=useTor, url=geyserUrl, data=graphqlQuery, defaultResponse=defaultResponse, headers=graphqlHeaders, username=None, password=None, basePath=basePath, fileAge=fileAge)
        if len(newestfile) > 0:
            with open(newestfile) as f:
                j = json.load(f)
        readjust = True
        while readjust:
            readjust = False
            while "data" in j: j = j["data"]; readjust = True
            while "projectsGet" in j: j = j["projectsGet"]; readjust = True
            while "projects" in j: j = j["projects"]; readjust = True                
        # subsequent requests to get more
        if len(j) == pageSize:
            k = j[pageSize-1]
            if "id" in k:
                nextPagination = k["id"]
                os.remove(newestfile)
                l = getgeyserprojects(useTor=useTor, tagId=tagId, pagination=nextPagination)
                j.extend(l)
                with open(newestfile, "w") as f:
                    json.dump(j, f)
    except:
        j = errresponse
    return j

def getnostrstats(useTor=True, url="https://stats.nostr.band/stats_api?method=stats&options="):
    errresponse = {"relays":-1,"pubkeys":-1,"users":-1,"trusted_users":-1,
                   "events":-1,"posts":-1,"zaps":-1,"zap_amount":-1,
                   "daily":None,"daily_totals":None,"relay_stats":None}
    j = errresponse
    try:
        newestfile = getfromurlifstale(useTor, url, "../data/nostrbandstats", 86400)
        if len(newestfile) > 0:
            # 2024-04 NostrBand may have errors in their JSON output. We need to read the file and massage it
            with open(newestfile, 'r') as file:
                s = " ".join(line for line in file)
                s = s.replace("-nan", "0")
                s = s.replace("nan", "0")
                j = json.loads(s)

            # Original way
            #with open(newestfile) as f:
            #    j = json.load(f)
    except Exception as e:
        print(e)
        j = errresponse
    return j

def getpriceinfo(useTor=True, url="https://bisq.markets/bisq/api/markets/ticker", price_last=-1, price_high=-1, price_low=-1, fiatUnit="USD"):
    newestfile = getfromurlifstale(useTor, url, "../data/bisq", 3600)
    if len(newestfile) > 0:
        with open(newestfile) as f:
            j = json.load(f)
        if "error" not in j:
            keyname = f"btc_{fiatUnit}".lower()
            if keyname not in j:
                print(f"Price service does not have BTC to {fiatUnit} currency pair. Using btc_usd")
                keyname = "btc_usd"
            price_last = int(math.floor(float(j[keyname]["last"])))
            price_high = int(math.floor(float(j[keyname]["high"])))
            price_low = int(math.floor(float(j[keyname]["low"])))
    return (price_last,price_high,price_low,keyname)

def getraretoshiuserinfoFallback(useTor=True, raretoshiDataDirectory="../data/raretoshi/", raretoshiUser="rapidstart", userInfo=None, userInfoLast=0, userInfoInterval=3600):
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

def getraretoshiuserinfoNew(useTor=True, raretoshiDataDirectory="../data/raretoshi/", raretoshiUser="rapidstart", userInfo=None, userInfoLast=0, userInfoInterval=3600):
    userFilename = raretoshiUser + ".json"
    localFilename = raretoshiDataDirectory + userFilename
    tempFilename = localFilename + ".tmp"
    refreshUser = False
    if not exists(localFilename):
        refreshUser = True
    if userInfoInterval + userInfoLast < int(time.time()):
        refreshUser = True
    if refreshUser == False:
        #print(f"Using cached data from {userInfoLast}")
        return userInfo, userInfoLast
    # Do the work to get new user data
    url = "https://raretoshi.com/" + raretoshiUser
    #print(f"Retrieving user properties from {url}")
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
    print("falling back to getraretoshiuserinfoFallback logic")
    return getraretoshiuserinfoFallback(useTor, raretoshiDataDirectory, raretoshiUser, userInfo, userInfoLast, userInfoInterval)

def getraretoshiuserinfo(useTor=True, raretoshiDataDirectory="../data/raretoshi/", raretoshiUser="rapidstart", userInfo=None, userInfoLast=0, userInfoInterval=3600):
    return getraretoshiuserinfoNew(useTor, raretoshiDataDirectory, raretoshiUser, userInfo, userInfoLast, userInfoInterval)

def getbraiinspoolheaders(authtoken):
    headers = {"SlushPool-Auth-Token": authtoken}
    return headers

def getbraiinspoolaccountprofile(useTor=True, authtoken="invalid"):
    url = "https://pool.braiins.com/accounts/profile/json/btc/"
    headers = getbraiinspoolheaders(authtoken)
    defaultResponse = '{"btc":{"confirmed_reward":null,"unconfirmed_reward":"0.00000000","estimated_reward":"0.00000000","hash_rate_unit":"Gh/s","hash_rate_5m": 0.0000}}'
    return geturl(useTor, url, defaultResponse, headers)

def getbraiinspoolaccountrewards(useTor=True, authtoken="invalid"):
    url = "https://pool.braiins.com/accounts/rewards/json/btc/"
    headers = getbraiinspoolheaders(authtoken)
    defaultResponse = '{"btc":{"daily_rewards":[]}}'
    return geturl(useTor, url, defaultResponse, headers)

def getbraiinspoolstats(useTor=True, authtoken="invalid"):
    url = "https://pool.braiins.com/stats/json/btc/"
    headers = getbraiinspoolheaders(authtoken)
    defaultResponse = '{"btc":{"blocks":{"0":{"date_found":0,"mining_duration":0,"total_shares":0,"state":"confirmed","confirmations_left":0,"value": "0.00000000","user_reward": "0.00000000","pool_scoring_hash_rate": 0.000000}}}}'
    return geturl(useTor, url, defaultResponse, headers)

def getwhirlpoolheaders(apiKey=""):
    headers = {}
    if len(apiKey) > 0 and apiKey != "NOT_SET": headers["apiKey"] = apiKey
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
    path = "/rest/mix"
    whirlpoolurl = url + path
    headers = getwhirlpoolheaders(apiKey)
    defaultResponse = '''{
          "started": false,
          "nbMixing": 0,
          "nbQueued": 0,
          "error": "Unable to get info about mix",
          "message": "Unable to get info about mix"
        }'''
    return geturl(useTor, whirlpoolurl, defaultResponse, headers)

def getwhirlpoolcliconfig(useTor=True, url=None, apiKey=""):
    path = "/rest/cli"
    whirlpoolurl = url + path
    headers = getwhirlpoolheaders(apiKey)
    defaultResponse = '''{
         "cliStatus":"ERROR", "cliMessage": null, "loggedIn": false, "torProgress": 0, "network": "unknown",
         "serverUrl": "unknown.onion", "serverName": "Unknown",
         "dojoUrl": "ERROR", "tor": false, "dojo": false, "version": "unknown"
        }'''
    return geturl(useTor, whirlpoolurl, defaultResponse, headers)

# do a POST call on the specified url, with the specified data.
# with response body, load and return as json
def posturl(useTor=True, url=None, data=None, defaultResponse="{}", headers={}, username=None, password=None):
    cmdoutput = ""
    try:
        proxies = gettorproxies() if useTor else {}
        timeout = gettimeouts()
        auth = None
        if username is not None and password is not None:
            auth = HTTPBasicAuth(username, password)
        requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
        cmdoutput = requests.post(url=url, data=data, headers=headers, auth=auth, timeout=timeout, proxies=proxies, verify=False).text
    except Exception as e:
        print(f"error calling posturl: {e}")
        print(f"using default response {defaultResponse}")
        cmdoutput = defaultResponse
    try:
        j = json.loads(cmdoutput)
    except Exception as e:
        print(f"error loading response as json: {e}")
        print(f"using default response {defaultResponse}")
        j = json.loads(defaultResponse)
    return j

