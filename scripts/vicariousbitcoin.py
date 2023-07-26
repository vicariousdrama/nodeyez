# import packages
from os.path import exists
from urllib3.exceptions import InsecureRequestWarning
import json
import random
import re
import requests
import subprocess
import time
import vicariousnetwork

def loadJSONData(dataFile=None, default={}):
    if dataFile is None:
        return default
    j = None
    if exists(dataFile):
        with open(dataFile) as f:
            j = json.load(f)
    if j is None:
        j = default
    return j

def binaryExists(binName):
    cmd = f"which {binName} | wc -l"
    cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
    return int(cmdoutput) > 0

# ------ Bitcoin Core Related ------------------------------------------------------

# config opts
bitcoinMode="MOCK"  # available modes are MOCK, CLI, and REST
                    # to force a mode, assign it below
# support for profile options in config, generally only need default
# additional profiles can be configured for development testing
bitcoinCLIOptions=loadJSONData("../config/bitcoin-cli.json")
if "activeProfile" in bitcoinCLIOptions and "profiles" in bitcoinCLIOptions:
    if bitcoinCLIOptions["activeProfile"] in bitcoinCLIOptions["profiles"]:
        bitcoinCLIOptions = bitcoinCLIOptions["profiles"][bitcoinCLIOptions["activeProfile"]]
        bitcoinMode="CLI"
bitcoinRESTOptions=loadJSONData("../config/bitcoin-rest.json")
if "activeProfile" in bitcoinRESTOptions and "profiles" in bitcoinRESTOptions:
    bitcoinRESTProfileName = bitcoinRESTOptions["activeProfile"]
    for bitcoinRESTProfile in bitcoinRESTOptions["profiles"]:
        if "name" in bitcoinRESTProfile and bitcoinRESTProfile["name"] == bitcoinRESTProfileName:
            bitcoinRESTOptions = bitcoinRESTProfile
            bitcoinMode="REST"
            break
# if you want to force mode for bitcoin, set it here
#bitcoinMode="CLI"

# Pruned Block Height for tracking lowest block we can return data for
prunedBlockHeight = None
prunedBlockDiff = None
prunedMode = True

# ------

def isBitcoinAvailable():
    return binaryExists("bitcoin-cli")

def isBitcoinRESTOK():
    if type(bitcoinRESTOptions) is dict and "name" in bitcoinRESTOptions: return True
    if type(bitcoinRESTOptions) is list and len(bitcoinRESTOptions) > 0: return True
    return False

def countblockopreturns(blocknum):
    j = getblock(blocknum, 2)
    if j is None:
        return 0
    if "tx" not in j:
        return 0
    c = 0
    for tx in j["tx"]:
        if "vout" not in tx:
            continue
        for vout in tx["vout"]:
            if "scriptPubKey" not in vout:
                continue
            scriptPubKey = vout["scriptPubKey"]
            if "asm" in scriptPubKey:
                asm = scriptPubKey["asm"]
                if "OP_RETURN" in asm:
                    c = c + 1
    return c

def countblockordinals(blocknum):
    j = getblock(blocknum, 2)
    if j is None:
        return 0
    thepattern = re.compile("(.*)0063036f72640101(.*)68$")
    if "tx" not in j:
        return 0
    c = 0
    for tx in j["tx"]:
        if "vin" not in tx:
            continue
        for vin in tx["vin"]:
            if "txinwitness" not in vin:
                continue
            for txinwitness in vin["txinwitness"]:
                regexmatch = re.match(thepattern, txinwitness)
                if regexmatch is not None:
                    c = c + 1
    return c

def getblock(blocknum, verbosity=1):
    fakeresult = {"confirmations": 1, "time": 0}
    j = fakeresult
    if bitcoinMode == "MOCK":
        if verbosity == 0: # hex encoded data
            j = loadJSONData("../mock-data/getblock-verbose0.json", fakeresult)
        elif verbosity == 2: # json with only tx id
            j = loadJSONData("../mock-data/getblock-verbose2.json", fakeresult)
        elif verbosity == 3: # json with transaction data and prevout for inputs
            j = loadJSONData("../mock-data/getblock-verbose3.json", fakeresult)
        else: # json with transaction data (verbosity=1 and all others), the default
            j = loadJSONData("../mock-data/getblock.json", fakeresult)
        if j is not None and "result" in j:
            j = j["result"]
    blockhash = getblockhash(blocknum)
    if bitcoinMode == "CLI" and isBitcoinAvailable():
        if prunedBlockHeight is None:
            setPrunedBlockHeight()
        if prunedBlockHeight > blocknum:
            print(f"Call to getblock for blocknum {blocknum} below pruned height {prunedBlockHeight}")
        else:
            cmd = f"bitcoin-cli {bitcoinCLIOptions} getblock {blockhash} {verbosity}"
            try:
                cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
                j = json.loads(cmdoutput)
            except subprocess.CalledProcessError as e:
                print(e)
                j = fakeresult
    if bitcoinMode == "REST" and isBitcoinRESTOK():
        blockhash = getblockhash(blocknum)
        data = f'{{"jsonrpc": "1.0", "id": "nodeyez", "method": "getblock", "params": ["{blockhash}", {verbosity}]}}'
        headers = {"content-type":"text/plain;"}
        url, rpcuser, rpcpassword, useTor = pickBitcoinRESTSettingsFromPool()
        j = vicariousnetwork.posturl(useTor=useTor, url=url, data=data, defaultResponse="{}", headers=headers, username=rpcuser, password=rpcpassword)
        if j is not None and "result" in j:
            j = j["result"]
        if j is None:
            j = fakeresult
        elif len(j.keys()) == 0:
            j = fakeresult
    if j is None: 
        j = fakeresult
    return j

def getblockchaininfo():
    fakeresult = {"chain":"main","blocks":785671,"headers":785671,"bestblockhash":"000000000000000000044b9ca9835afb2925cb5b681d060ccf0cdb4fbafd68d1","difficulty":47887764338536.25,"time":1681659952,"mediantime":1681658374,"verificationprogress":0.9999960223040104,"initialblockdownload":False,"chainwork":"000000000000000000000000000000000000000045c08760c1aff423a74e7fe0","size_on_disk":537705569832,"pruned":False,"warnings":""}
    j = None
    if bitcoinMode == "MOCK":
        j = loadJSONData("../mock-data/getblockchaininfo.json", fakeresult)
        if j is not None and "result" in j:
            j = j["result"]
    if bitcoinMode == "CLI" and isBitcoinAvailable():
        cmd = f"bitcoin-cli {bitcoinCLIOptions} getblockchaininfo"
        try:
            cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
            j = json.loads(cmdoutput)
        except subprocess.CalledProcessError as e:
            print(e)
            j = fakeresult
    if bitcoinMode == "REST" and isBitcoinRESTOK():
        data = '{"jsonrpc": "1.0", "id": "nodeyez", "method": "getblockchaininfo", "params": []}'
        headers = {"content-type":"text/plain;"}
        url, rpcuser, rpcpassword, useTor = pickBitcoinRESTSettingsFromPool()
        j = vicariousnetwork.posturl(useTor=useTor, url=url, data=data, defaultResponse="{}", headers=headers, username=rpcuser, password=rpcpassword)
        if j is not None and "result" in j:
            j = j["result"]
    if j is None: 
        j = fakeresult
    return j

def getblockhash(blocknum=1):
    fakeresult = "0000000000000000000000000000000000000000000000000000000000000000"
    j = fakeresult
    if bitcoinMode == "MOCK":
        j = loadJSONData("../mock-data/getblockhash.json", fakeresult)
        if j is not None and "result" in j:
            j = j["result"]
    if bitcoinMode == "CLI" and isBitcoinAvailable():
        if prunedBlockHeight is None:
            setPrunedBlockHeight()
        if prunedBlockHeight > blocknum:
            print(f"Call to getblockhash for blocknum {blocknum} below pruned height {prunedBlockHeight}")
        else:
            cmd = f"bitcoin-cli {bitcoinCLIOptions} getblockhash {blocknum}"
            try:
                cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
                j = cmdoutput
            except subprocess.CalledProcessError as e:
                print(e)
                j = fakeresult
    if bitcoinMode == "REST" and isBitcoinRESTOK():
        data = f'{{"jsonrpc": "1.0", "id": "nodeyez", "method": "getblockhash", "params": [{blocknum}]}}'
        headers = {"content-type":"text/plain;"}
        url, rpcuser, rpcpassword, useTor = pickBitcoinRESTSettingsFromPool()
        j = vicariousnetwork.posturl(useTor=useTor, url=url, data=data, defaultResponse="{}", headers=headers, username=rpcuser, password=rpcpassword)
        if j is not None and "result" in j:
            j = j["result"]
    if j is None: 
        j = fakeresult
    return j.strip()

def getblockopreturns(blocknum):
    opreturns = []
    encodinglist = ["utf-8","ascii"]
    j = getblock(blocknum, 2)
    if "tx" not in j:
        return opreturns
    txidx = 0
    for tx in j["tx"]:
        txidx += 1
        voutidx = 0
        if "vout" not in tx:
            continue
        for vout in tx["vout"]:
            voutidx += 1
            if "scriptPubKey" not in vout:
                continue
            scriptPubKey = vout["scriptPubKey"]
            if "asm" not in scriptPubKey:
                continue
            asm = scriptPubKey["asm"]
            if "OP_RETURN" not in asm:
                continue
            ophex = asm.replace("OP_RETURN ", "")
            if len(ophex) % 2 == 1:  # hex is 2 char per byte
                continue
            try:
                opbytes = bytes.fromhex(ophex)
            except Exception as e:
                print(f"error handling ophex '{ophex}'")
                print(f"error is {e}")
            hasError = True
            for encoding in encodinglist:
                if hasError == False:
                    break
                try:
                    optext = opbytes.decode(encoding)
                    hasError = False
                    opreturns.append(optext)
                except Exception as e:
                    #print(f"error converting hex to text with encoding {encoding} for tx[{txidx}].vout[{voutidx}]: {e}")
                    pass
    return opreturns

def getblockordinals(blocknum, blockIndexesToSkip=[]):
    print(f"Call to vicariousbitcoin.getblockordinals instead of vicariousbitcoin.getblockinscriptions")
    return getblockordinals(blocknum, blockIndexesToSkip)

def getblockinscriptions(blocknum, blockIndexesToSkip=[]):
    inscriptions = []
    j = getblock(blocknum, 2)
    thepattern = re.compile("(.*)0063036f72640101(.*)68$")
    if "tx" not in j:
        return inscriptions
    txidx = 0
    for tx in j["tx"]:
        txidx += 1
        if txidx in blockIndexesToSkip:
            continue
        txid = tx["txid"]
        txsize = tx["size"]
        vinidx = 0
        if "vin" not in tx:
            continue
        for vin in tx["vin"]:
            vinidx += 1
            if "txinwitness" not in vin:
                continue
            for txinwitness in vin["txinwitness"]:
                regexmatch = re.match(thepattern, txinwitness)
                if regexmatch is not None:
                    # This is an ordinal inscription.
                    # Get parent info
                    parenttxid = ""
                    parentsize = 0
                    if "txid" in vin:
                        parenttxid = vin["txid"]
                        parentsize = gettransaction(parenttxid)["size"]
                    #print(f"found inscription in tx idx:{txidx} of block {blocknum}")
                    g2 = regexmatch.group(2)
                    pos = 0
                    contenttypelength = int.from_bytes(bytes.fromhex(g2[pos:pos+2]),"little")
                    pos += 2
                    contenttype = bytes.fromhex(g2[pos:pos+(contenttypelength*2)]).decode()
                    pos += (contenttypelength*2)
                    opcode = g2[pos:pos+2]
                    pos += 2
                    if opcode != '00':
                        print(f"warning. expected 0x00 divider between content type and data, but got 0x{opcode}")
                    #print(f"- content type: {contenttype}")
                    datalengthtype = g2[pos:pos+2]
                    pos +=2
                    datalen = 0
                    totaldatalen = 0
                    rawbytes = bytearray()
                    while datalengthtype in ['4c','4d','4e']:
                        #print(f"- hex code for data length: {datalengthtype}")
                        # size was reporting 2050, which is 802 in hex. flip the endian, 208 = 520, the max bytes that can be pushed
                        if datalengthtype == "4c":
                            # next 1 byte for size
                            datalen = int.from_bytes(bytes.fromhex(g2[pos:pos+2]),"little")
                            pos += 2
                        if datalengthtype == "4d":
                            # next 2 bytes for size
                            datalen = int.from_bytes(bytes.fromhex(g2[pos:pos+4]),"little")
                            pos += 4
                        if datalengthtype == "43":
                            # next 4 bytes for size
                            datalen = int.from_bytes(bytes.fromhex(g2[pos:pos+8]),"little")
                            pos += 8
                        totaldatalen += datalen
                        morebytes = bytes.fromhex(g2[pos:pos+(datalen*2)])
                        rawbytes.extend(morebytes)
                        pos += (datalen*2)
                        # see if more op codes to continue data
                        datalengthtype = g2[pos:pos+2]
                        pos += 2
                    # Check for extra bytes trailing into end. For now, we'll append these to existing, but this may be incorrect
                    remaininghex = g2[pos:]
                    remaininghexlength = len(remaininghex)
                    #print(f"pos: {pos}, totaldatalen: {totaldatalen}, remaining: {remaininghex}, remaininghexlength: {remaininghexlength}")
                    if remaininghexlength > 0:
                        morebytes = bytes.fromhex(g2[pos:])
                        rawbytes.extend(morebytes)
                        totaldatalen += (remaininghexlength/2)
                    #print(f"- total data length: {totaldatalen}")
                    # append an object
                    inscription = {"block":blocknum,"txid":txid,"txsize":txsize,"txidx":txidx,"contenttype":contenttype,"size":totaldatalen,"parenttxid":parenttxid,"parentsize":parentsize,"data":rawbytes}
                    inscriptions.append(inscription)
    return inscriptions

def getblockstats(blocknum):
    fakeresult = {"avgfee":4815,"avgfeerate":8,"avgtxsize":1246,"blockhash":"000000000000000000044b9ca9835afb2925cb5b681d060ccf0cdb4fbafd68d1","feerate_percentiles":[1,1,1,9,24],"height":785671,"ins":6259,"maxfee":160000,"maxfeerate":224,"maxtxsize":243764,"medianfee":2973,"mediantime":1681658374,"mediantxsize":246,"minfee":120,"minfeerate":1,"mintxsize":150,"outs":4191,"subsidy":625000000,"swtotal_size":1886545,"swtotal_weight":3261196,"swtxs":1457,"time":1681659952,"total_out":447889278607,"total_size":2069233,"total_weight":3991948,"totalfee":7994356,"txs":1661,"utxo_increase":-2068,"utxo_size_inc":-149003}
    j = None
    if bitcoinMode == "MOCK":
        j = loadJSONData("../mock-data/getblockstats.json", fakeresult)
        if j is not None and "result" in j:
            j = j["result"]
    if bitcoinMode == "CLI" and isBitcoinAvailable():
        if prunedBlockHeight is None:
            setPrunedBlockHeight()
        if prunedBlockHeight > blocknum:
            print(f"Call to getblock for blocknum {blocknum} below pruned height {prunedBlockHeight}")
        else:
            cmd = f"bitcoin-cli {bitcoinCLIOptions} getblockstats {blocknum}"
            try:
                cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
                j = json.loads(cmdoutput)
            except subprocess.CalledProcessError as e:
                print(e)
                j = fakeresult
    if bitcoinMode == "REST" and isBitcoinRESTOK():
        data = f'{{"jsonrpc": "1.0", "id": "nodeyez", "method": "getblockstats", "params": [{blocknum}]}}'
        headers = {"content-type":"text/plain;"}
        url, rpcuser, rpcpassword, useTor = pickBitcoinRESTSettingsFromPool()
        j = vicariousnetwork.posturl(useTor=useTor, url=url, data=data, defaultResponse="{}", headers=headers, username=rpcuser, password=rpcpassword)
        if j is not None and "result" in j:
            j = j["result"]
    if j is None: 
        j = fakeresult
    return j

def getblockscriptpubkeytypes(blocknum):
    t0 = time.time()
    j = getblock(blocknum, 3)
    t1 = time.time()
    t = {"multisig":0,
         "nonstandard":0,
         "nulldata":0,
         "pubkey":0,
         "pubkeyhash":0,
         "scripthash":0,
         "witness_v0_scripthash":0,
         "witness_v0_keyhash":0,
         "witness_v1_taproot":0,
         "witness_unknown":0
        }
    r = {"vin": dict(t), "vout": dict(t)}
    if "tx" not in j:
        return r
    for tx in j["tx"]:
        if "vin" in tx:
            for vin in tx["vin"]:
                if "prevout" not in vin:
                    continue
                intype = vin["prevout"]["scriptPubKey"]["type"]
                if intype not in r["vin"]:
                    r["vin"][intype] = 1
                else:
                    r["vin"][intype] = r["vin"][intype] + 1
        if "vout" in tx:
            for vout in tx["vout"]:
                if "scriptPubKey" not in vout:
                    continue
                outtype = vout["scriptPubKey"]["type"]
                if outtype not in r["vout"]:
                    r["vout"][outtype] = 1
                else:
                    r["vout"][outtype] = r["vout"][outtype] + 1
    t2 = time.time()
    # t0 = start   t1-t0 is total network transfer time   t2-t1 is local logic time
    #print(f"blocknum: {blocknum}, t0: {t0}, t1-t0: {t1-t0}, t2-t1: {t2-t1}")
    return r

def getcurrentblock():
    j = getblockchaininfo()
    if "blocks" in j:
        return int(j["blocks"])
    else:
        return 1

def getepochnum(blocknum):
    return blocknum // 2016

def getfirstblockforepoch(blocknum):
    epochnum = getepochnum(blocknum)
    return min(blocknum, (int(epochnum * 2016) + 1))

def gethalvingnum(blocknum):
    return blocknum // 210000

def getfirstblockforhalving(blocknum):
    halvingnum = gethalvingnum(blocknum)
    return min(blocknum, (int(halvingnum * 210000) + 1))

def gethashratestring(hashrate=0, hashdesc="h/s"):
    units=["h/s","Kh/s","Mh/s","Gh/s","Th/s","Ph/s","Eh/s","Zh/s"]
    while (hashrate > 1000.0) and (hashdesc != units[-2]):
        hashrate = hashrate/1000.0
        hashdesc = units[units.index(hashdesc) + 1]
    hashfmt = f"{hashrate:.2f} {hashdesc}"
    return hashfmt

def getmempool():
    fakeresult = []
    j = None
    if bitcoinMode == "MOCK":
        j = loadJSONData("../mock-data/getrawmempool.json", fakeresult)
        if j is not None and "result" in j:
            j = j["result"]
    if bitcoinMode == "CLI" and isBitcoinAvailable():
        cmd = "bitcoin-cli " + bitcoinCLIOptions + " getrawmempool"
        try:
            cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
            j = json.loads(cmdoutput)
        except subprocess.CalledProcessError as e:
            print(e)
            j = fakeresult
    if bitcoinMode == "REST" and isBitcoinRESTOK():
        data = f'{{"jsonrpc": "1.0", "id": "nodeyez", "method": "getrawmempool", "params": []}}'
        headers = {"content-type":"text/plain;"}
        url, rpcuser, rpcpassword, useTor = pickBitcoinRESTSettingsFromPool()
        j = vicariousnetwork.posturl(useTor=useTor, url=url, data=data, defaultResponse="[]", headers=headers, username=rpcuser, password=rpcpassword)
        if j is not None and "result" in j:
            j = j["result"]
    if j is None: 
        j = fakeresult
    return j

def gettransaction(txid, blockhash=""):
    # getrawtransaction     txid    true(verbose)   blockhash
    # getmempoolentry       txid
    fakeresult ={"txid":"' + txid + '","hash":"?","size":0,"weight":0,"version":1,"vsize":0,"locktime":0,"vin":[],"vout":[]}
    j = None
    if bitcoinMode == "MOCK":
        j = loadJSONData("../mock-data/getrawtransaction.json", fakeresult)
        if j is not None and "result" in j:
            j = j["result"]
    if bitcoinMode == "CLI" and isBitcoinAvailable():
        cmd = f"bitcoin-cli {bitcoinCLIOptions} getrawtransaction {txid} true {blockhash} 2>&1"
        try:
            cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
            j = json.loads(cmdoutput)
            return j
        except subprocess.CalledProcessError as e:
            print(e)    
            j = fakeresult
    if bitcoinMode == "REST" and isBitcoinRESTOK():
        if len(blockhash) > 0:
            data = f'{{"jsonrpc": "1.0", "id": "nodeyez", "method": "getrawtransaction", "params": ["{txid}", true, "{blockhash}"]}}'
        else:
            data = f'{{"jsonrpc": "1.0", "id": "nodeyez", "method": "getrawtransaction", "params": ["{txid}", true]}}'
        headers = {"content-type":"text/plain;"}
        url, rpcuser, rpcpassword, useTor = pickBitcoinRESTSettingsFromPool()
        j = vicariousnetwork.posturl(useTor=useTor, url=url, data=data, defaultResponse="[]", headers=headers, username=rpcuser, password=rpcpassword)
        if j is not None and "result" in j:
            j = j["result"]
    if j is None: 
        j = fakeresult
    return j

def pickBitcoinRESTSettingsFromPool():
    o = bitcoinRESTOptions
    if type(o) is list:
        l = len(o)
        i = int(random.random() * l)
        o = o[i]
    address = o["address"] if "address" in o else ""
    port = o["port"] if "port" in o else ""
    rpcuser = o["rpcuser"] if "rpcuser" in o else ""
    rpcpassword = o["rpcpassword"] if "rpcpassword" in o else ""
    useTor = o["useTor"] if "useTor" in o else True
    protocol = o["protocol"] if "protocol" in o else "http"
    rpcurl = f"{protocol}://{address}:{port}/"
    return rpcurl, rpcuser, rpcpassword, useTor

def setPrunedBlockHeight():
    global prunedBlockHeight
    global prunedBlockDiff
    global prunedMode
    j = getblockchaininfo()
    prunedBlockHeight = 0
    prunedMode = False
    if "pruned" in j: prunedMode = j["pruned"]
    if "pruneheight" in j: prunedBlockHeight = int(j["pruneheight"])
    prunedBlockDiff = int(j["blocks"]) - prunedBlockHeight


# ------ Lightning LND Related ------------------------------------------------------

# config opts
lndMode="MOCK"  # available modes are MOCK, CLI, and REST
                # to force a mode, assign it below
# support for profile options in config, generally only need default
# additional profiles can be configured for development testing
lndCLIOptions=loadJSONData("../config/lnd-cli.json")
if "activeProfile" in lndCLIOptions and "profiles" in lndCLIOptions:
    if lndCLIOptions["activeProfile"] in lndCLIOptions["profiles"]:
        lndCLIOptions = lndCLIOptions["profiles"][lndCLIOptions["activeProfile"]]
        lndMacaroonOpts = "--macaroonpath=${HOME}/.lnd/nodeyez.macaroon" if "macaroonOpt" not in lndCLIOptions else lndCLIOptions["macaroonOpt"]
        lndTimeoutOpts = "--timeout 5s" if "timeoutOpt" not in lndCLIOptions else lndCLIOptions["timeoutOpt"]
        lndMode="CLI"
lndRESTOptions=loadJSONData("../config/lnd-rest.json")
if "activeProfile" in lndRESTOptions and "profiles" in lndRESTOptions:
    lndRESTProfileName = lndRESTOptions["activeProfile"]
    for lndRESTProfile in lndRESTOptions["profiles"]:
        if "name" in lndRESTProfile and lndRESTProfile["name"] == lndRESTProfileName:
            lndRESTOptions = lndRESTProfile
            lndMode="REST"
            break

# if you want to force mode for lnd, set it here
#lndMode="MOCK"

# ------

lndPubKeyAliases = {'pubkey':'alias'}

def lndCreateMockAliasForPubkey(pubkey):
    mfn = "../mock-data/bip39words.txt"
    if exists(mfn):
        wordnum = int(pubkey[0:8], base=16) % 2048
        with open(mfn) as f:
            for i, line in enumerate(f):
                if i == wordnum:
                    return line.replace("\n","") + "-" + str(i)
    return "mockup node"

def lndDoNodeRestCommand(node=None, method="GET", suffix="/", defaultResponse="{}", postData="{}"):
    if node is None or not lndIsNodeConfigValid(node):
        print(f"rest command for node could not be processed. node value is not valid: {node}")
        print(f"using default response {defaultResponse}")
        return json.loads(defaultResponse)
    url, headers, timeout, proxies = lndGetNodeRestVars(node, suffix)    
    cmdoutput = ""
    try:
        requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
        if method == "GET":
            cmdoutput = requests.get(url,headers=headers,timeout=timeout,proxies=proxies,verify=False).text
        elif method == "DELETE":
            cmdoutput = requests.delete(url,headers=headers,timeout=timeout,proxies=proxies,verify=False).text
        elif method == "POST":
            cmdoutput = requests.post(url,data=postData,headers=headers,timeout=timeout,proxies=proxies,verify=False).text
    except Exception as e:
        print(f"error calling lndNodeRest({method}) for suffix: {suffix}. {e}")
        print(f"using default response {defaultResponse}")
        cmdoutput = defaultResponse
    try:
        j = json.loads(cmdoutput)
    except Exception as e:
        print(f"error loading response from lndNodeRest({method}) as json: {e}")
        print(f"using default response {defaultResponse}")
        j = json.loads(defaultResponse)
    return j

def lndGetNodeAddressFromNodeInfo(nodeinfo):
    if "node" in nodeinfo:
        return lndGetNodeAddressFromNodeInfo(nodeinfo["node"])
    best = ""
    if "addresses" not in nodeinfo:
        return best
    for addr in nodeinfo["addresses"]:
        nodehostandport = addr["addr"]
        best = nodehostandport if len(best) == 0 else best
        best = nodehostandport if "onion" in nodehostandport else best  # favor onion
        best = nodehostandport if "onion" in nodehostandport and len(nodehostandport) > 56 else best
    return best

def lndGetNodeAliasFromNodeInfo(nodeinfo):
    if "alias" in nodeinfo:
        return nodeinfo["alias"]
    if "node" in nodeinfo:
        return lndGetNodeAliasFromNodeInfo(nodeinfo["node"])
    return ""

def lndGetNodeAliasFromPubkey(pubkey, node=None):
    if pubkey not in lndPubKeyAliases:
        if lndMode == "MOCK":
            lndPubKeyAliases[pubkey] = lndCreateMockAliasForPubkey(pubkey)
        else:
            lndPubKeyAliases[pubkey] = lndGetNodeAliasFromNodeInfo(lndGetNodeInfo(pubkey,node))
    return lndPubKeyAliases[pubkey]

def lndGetNodeChannels(node=None):
    fakeresult = '{"channels":[]}'
    j = None
    if lndMode == "MOCK":
        j = loadJSONData("../mock-data/getnodechannels.json")
        if j is not None and "result" in j: j = j["result"]
    if lndMode == "CLI":    
        if lndIsAvailable():
            cmd = f"lncli {lndMacaroonOpts} listchannels {lndTimeoutOpts} 2>&1"
            try:
                cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
            except subprocess.CalledProcessError as e:
                print(f"error in lndGetNodeChannels: {e}")
                cmdoutput = fakeresult
            j = json.loads(cmdoutput)
    if lndMode == "REST":
        suffix = f"/v1/channels"
        defaultResponse = fakeresult
        j = lndDoNodeRestCommand(node, "GET", suffix, defaultResponse)
    if j is None:
        j = json.loads(fakeresult)
    return j

def lndGetNodeForwardingHistory(startTime:str="-5y", maxEvents:int=50000, node=None):
    fakeresult = '{"forwarding_events":[]}'
    j = None
    if lndMode == "MOCK":
        j = loadJSONData("../mock-data/getfwdinghistory.json")
        if j is not None and "result" in j: j = j["result"]
    if lndMode == "CLI":
        if lndIsAvailable():
            cmd = f"lncli {lndMacaroonOpts} fwdinghistory --start_time {startTime} --max_events {maxEvents} {lndTimeoutOpts} 2>&1"
            try:
                cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
            except subprocess.CalledProcessError as e:
                print(f"error in lndGetForwardingHistory: {e}")
                cmdoutput = fakeresult
            j = json.loads(cmdoutput)
    if lndMode == "REST":
        suffix = "/v1/switch"
        defaultResponse = fakeresult
        postData = '{"start_time":0,"num_max_events":50000}'       
        j = lndDoNodeRestCommand(node, "POST", suffix, defaultResponse, postData)
    if j is None:
        j = json.loads(fakeresult)
    return j

def lndGetNodeInfo(pubkey, node=None):
    fakeresult = f'{{"node":{{"alias":"{pubkey}","pub_key":"{pubkey}","last_update":0,"addresses":[{{"network":"tcp","addr":"0.0.0.0:65535"}}]}}}}'
    j = None
    if lndMode == "MOCK":
        j = loadJSONData("../mock-data/getnodeinfo.json")
        if j is not None and "result" in j: j = j["result"]
        if "node" in j and "alias" in j["node"]:
            j["node"]["alias"] = lndCreateMockAliasForPubkey(pubkey)
    if lndMode == "CLI":
        if lndIsAvailable():
            cmd = f"lncli {lndMacaroonOpts} getnodeinfo --pub_key {pubkey} --include_channels {lndTimeoutOpts} 2>&1"
            try:
                cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
            except subprocess.CalledProcessError as e:
                print(f"error in lndGetNodeInfo: {e}")
                cmdoutput = fakeresult
            j = json.loads(cmdoutput)
    if lndMode == "REST":
        suffix = f"/v1/graph/node/{pubkey}?include_channels=true"
        defaultResponse = fakeresult
        j = lndDoNodeRestCommand(node, "GET", suffix, defaultResponse)
    if j is None:
        j = json.loads(fakeresult)
    return j

def lndGetNodeInvoices(node=None):
    fakeresult = '{"invoices": []}'
    j = None
    if lndMode == "MOCK":
        j = loadJSONData("../mock-data/getnodeinvoices.json")
        if j is not None and "result" in j: j = j["result"]
    if lndMode == "CLI":
        if lndIsAvailable():
            cmd = f"lncli {lndMacaroonOpts} listinvoices {lndTimeoutOpts} 2>&1"
            try:
                cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
            except subprocess.CalledProcessError as e:
                print(f"error in lndGetNodeInvoices: {e}")
                cmdoutput = fakeresult
            j = json.loads(cmdoutput)
    if lndMode == "REST":
        suffix = "/v1/invoices"
        defaultResponse = fakeresult
        j = lndDoNodeRestCommand(node, "GET", suffix, defaultResponse)
    if j is None:
        j = json.loads(fakeresult)
    return j

def lndGetNodePayments(node=None):
    fakeresult = '{"payments": []}'
    j = None
    if lndMode == "MOCK":
        j = loadJSONData("../mock-data/getnodepayments.json")
        if j is not None and "result" in j: j = j["result"]
    if lndMode == "CLI":
        if lndIsAvailable():
            cmd = f"lncli {lndMacaroonOpts} listpayments {lndTimeoutOpts} 2>&1"
            try:
                cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
            except subprocess.CalledProcessError as e:
                print(f"error in lndGetNodePayments: {e}")
                cmdoutput = fakeresult
            j = json.loads(cmdoutput)
    if lndMode == "REST":
        suffix = "/v1/payments"
        defaultResponse = fakeresult
        j = lndDoNodeRestCommand(node, "GET", suffix, defaultResponse)
    if j is None:
        j = json.loads(fakeresult)
    return j

def lndGetNodePeers(node=None):
    fakeresult = '{"peers":[]}'
    j = None
    if lndMode == "MOCK":
        pass
    if lndMode == "CLI":
        if lndIsAvailable():
            cmd = f"lncli {lndMacaroonOpts} listpeers {lndTimeoutOpts} 2>&1"
            try:
                cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
            except subprocess.CalledProcessError as e:
                print(f"error in lndGetNodePeers: {e}")
                cmdoutput = fakeresult
            j = json.loads(cmdoutput)
    if lndMode == "REST":
        suffix = "/v1/peers"
        defaultResponse = fakeresult
        j = lndDoNodeRestCommand(node, "GET", suffix, defaultResponse)
    if j is None:
        j = json.loads(fakeresult)
    return j

def lndGetNodeRestVars(node, suffix):
    nodeaddress = node["address"]
    nodeport = node["port"]
    nodemacaroon = node["macaroon"]
    useTor = False
    if "useTor" in node: useTor = node["useTor"]
    url = f"https://{nodeaddress}:{nodeport}{suffix}"
    headers = {"Grpc-Metadata-macaroon": nodemacaroon}
    timeout = vicariousnetwork.gettimeouts()
    proxies = {} if not useTor else vicariousnetwork.gettorproxies()
    return url, headers, timeout, proxies

def lndIsAvailable():
    return binaryExists("lncli")

def lndIsNodeConfigValid(node):
    if type(node) is not dict: return False
    return node.keys() & {'address','macaroon','port'}

def lndIsNodeConnectedToPubkey(pubkey, node=None):
    nodepeers = lndGetNodePeers(node)
    if "peers" not in nodepeers:
        return False
    for peer in nodepeers["peers"]:
        if "pub_key" not in peer:
            continue
        if pubkey == peer["pub_key"]:
            return True
    return False
