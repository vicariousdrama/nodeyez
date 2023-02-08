# import packages
from os.path import exists
from urllib3.exceptions import InsecureRequestWarning
import binascii
import json
import math
import re
import requests
import subprocess
import vicariousnetwork

useMockData=False

# ------ Bitcoin Core Related ------------------------------------------------------

def countblockopreturns(blocknum):
    cmd = "bitcoin-cli getblock `bitcoin-cli getblockhash " + str(blocknum) + "` 2|grep asm|grep OP_RETURN|wc -l"
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
        return int(cmdoutput)
    except subprocess.CalledProcessError as e:
        print(e)
        return 0

def countblockordinals(blocknum):
    cmd = "bitcoin-cli getblock `bitcoin-cli getblockhash " + str(blocknum) + "` 2|grep hex|grep 0063036f72640101|wc -l"
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
        return int(cmdoutput)
    except subprocess.CalledProcessError as e:
        print(e)
        return 0

def getblock(blocknum, verbosity=1):
    if useMockData:
        if exists("../mock-data/getblock.json"):
            with open("../mock-data/getblock.json") as f:
                return json.load(f)
    cmd = "bitcoin-cli getblock `bitcoin-cli getblockhash " + str(blocknum) + "` " + str(verbosity)
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
        j = json.loads(cmdoutput)
        return j
    except subprocess.CalledProcessError as e:
        print(e)
        fakejson = "{\"confirmations\": 1, \"time\": 0}"
        return json.loads(fakejson)

def getblockhash(blocknumber=1):
    if useMockData:
        if exists("../mock-data/getblockhash.json"):
            with open("../mock-data/getblockhash.json") as f:
                return f.readline()
    cmd = "bitcoin-cli getblockhash " + str(blocknumber)
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
        return cmdoutput
    except subprocess.CalledProcessError as e:
        print(e)
        return "0000000000000000000000000000000000000000000000000000000000000000"

def getblockopreturns(blocknum):
    if useMockData:
        return ["This is an example OP_RETURN", "Another OP_RETURN found in the block", "Only utf-8 or ascii decodable OP_RETURNs are rendered","Support for\nmulti-line OP_RETURN values\nexists as well","Some spammy OP_RETURN values are excluded","There must be at least one space","Lengthy OP_RETURN values without new lines may end up running off the side of the image","It depends on the fontsize set, which is based on number of OP_RETURN\nentries in the block","NODEYEZ","Nodeyez - Display panels to get the most from your node","NODEYEZ","NODEYEZ"]

    opreturns = []
    if countblockopreturns(blocknum) == 0:
        return opreturns
    b = getblock(blocknum, 2)
    if "tx" in b:
        txidx = 0
        for tx in b["tx"]:
            txidx += 1
            voutidx = 0
            if "vout" in tx:
                for vout in tx["vout"]:
                    voutidx += 1
                    if "scriptPubKey" in vout:
                        scriptPubKey = vout["scriptPubKey"]
                        if "asm" in scriptPubKey:
                            asm = scriptPubKey["asm"]
                            if "OP_RETURN" in asm:
                                ophex = asm.replace("OP_RETURN ", "")
                                # require even number of characters
                                if len(ophex) % 2 == 1:
                                    continue
                                # require more than one word
#                                if "20" not in ophex:
#                                    continue
                                #encodinglist = ["utf-8","gb18030","euc-kr","cp1253","utf-32","utf-16","euc-kr","cp1253","cp1252","iso8859-16","ascii","latin-1","iso8859-1"]
                                encodinglist = ["utf-8","ascii"]
                                hasError = True
                                try:
                                    opbytes = bytes.fromhex(ophex)
                                except Exception as e:
                                    print(f"error handling ophex '{ophex}'")
                                    print(f"error is {e}")
                                for encoding in encodinglist:
                                    if hasError == False:
                                        break
                                    try:
                                        optext = opbytes.decode(encoding)
#                                        print(f"successfully converted with encoding {encoding}: {optext}")
                                        hasError = False
                                        opreturns.append(optext)
                                    except Exception as e:
#                                        print(f"error converting hex to text with encoding {encoding} for tx[{txidx}].vout[{voutidx}]: {e}")
                                        pass
#                                if hasError:
#                                    opreturns.append(ophex)


    return opreturns

def getblockordinals(blocknum, blockIndexesToSkip=[]):
    ordinals = []
    if countblockordinals(blocknum) == 0:
        return ordinals
    b = getblock(blocknum, 2)
    thepattern = re.compile("(.*)0063036f72640101(.*)68$")
    if "tx" in b:
        txidx = 0
        for tx in b["tx"]:
            txidx += 1
            if txidx in blockIndexesToSkip:
                continue
            txid = tx["txid"]
            txsize = tx["size"]
            vinidx = 0
            if "vin" in tx:
                for vin in tx["vin"]:
                    vinidx += 1
                    if "txinwitness" in vin:
                        for txinwitness in vin["txinwitness"]:
                            match = re.match(thepattern, txinwitness)
                            if match is not None:
                                # This is an ordinal inscription.
                                # Get parent info
                                parenttxid = ""
                                parentsize = 0
                                if "txid" in vin:
                                    parenttxid = vin["txid"]
                                    parentsize = gettransaction(parenttxid)["size"]
                                #print(f"found ordinal in tx idx:{txidx} of block {blocknum}")
                                g2 = match.group(2)
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
                                ordinal = {"block":blocknum,"txid":txid,"txsize":txsize,"txidx":txidx,"contenttype":contenttype,"size":totaldatalen,"parenttxid":parenttxid,"parentsize":parentsize,"data":rawbytes}
                                ordinals.append(ordinal)
    return ordinals

def getcurrentblock():
    if useMockData:
        return 726462
    cmd = "bitcoin-cli getblockchaininfo"
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
        j = json.loads(cmdoutput)
        blockcurrent = int(j["blocks"])
        return blockcurrent
    except subprocess.CalledProcessError as e:
        print(e)
        return 1

def getepochnum(blocknum):
    return int(math.floor(blocknum / 2016))

def getfirstblockforepoch(blocknum):
    epochnum = getepochnum(blocknum)
    return min(blocknum, (int(epochnum * 2016) + 1))

def getmempool():
    cmd = "bitcoin-cli getrawmempool"
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
        j = json.loads(cmdoutput)
        return j
    except subprocess.CalledProcessError as e:
        print(e)
        fakejson = "[]"
        return json.loads(fakejson)

def gettransaction(txid, blockhash=""):
    cmd = "bitcoin-cli getrawtransaction " + txid + " true 2>&1"
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
        j = json.loads(cmdoutput)
        return j
    except subprocess.CalledProcessError as e:
        print(e)
        fakejson = '{"txid":"' + txid + '","hash":"?","size":0,"weight":0,"version":1,"vsize":0,"locktime":0,"vin":[],"vout":[]}'
        return json.loads(fakejson)




# ------ Lightning LND Related ------------------------------------------------------

pubkey_alias = {'pubkey':'alias'}

def attemptconnect(nodeinfo):
    nodestatus = 0
    pubkey = nodeinfo["node"]["pub_key"]
    addr = getnodeaddress(nodeinfo)
    if addr == "0.0.0.0:65535":
        return 0
    cmd = "lncli" + getlndglobaloptions() + " connect " + pubkey + "@" + addr + " --timeout 5s 2>&1"
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
        if "error" in cmdoutput:
            nodestatus = 0
        else:
            cmd = "lncli" + getlndglobaloptions() + " disconnect " + pubkey + " 2>&1"
            try:
                cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
                if "error" in cmdoutput:
                    nodestatus = 0
                else:
                    nodestatus = 1
            except subprocess.CalledProcessError as e2:
                print(f"error calling disconnect in attempconnect: {e}")
                nodestatus = 0
    except subprocess.CalledProcessError as e:
        print(f"error in attemptconnect: {e}")
        nodestatus = 0
    return nodestatus

def attemptconnectrest(nodeinfo, node):
    if not nodeconfigvalid(node):
        return attemptconnect(nodeinfo)
    nodestatus = 0
    pubkey = nodeinfo["node"]["pub_key"]
    addr = getnodeaddressrest(nodeinfo, node)
    if addr == "0.0.0.0:65535":
        return nodestatus # 0
    errorResponse = '{"error":"failed command"}'
    connectData = '{"addr":"' + pubkey + '@' + addr + '","timeout":"5"}'
    connectResponse = noderestcommandpost(node, "/v1/peers", connectData, errorResponse)
    if "error" not in connectResponse:
        disconnectResponse = noderestcommanddelete(node, "/v1/peers/" + pubkey, errorResponse)
        if "error" not in disconnectResponse:
            nodestatus = 1
    return nodestatus

def getdefaultaliasfrompubkey(pubkey):
    return pubkey[0:10] + "..."

def getfwdinghistory():
    if useMockData:
        if exists("../mock-data/getfwdinghistory.json"):
            with open("../mock-data/getfwdinghistory.json") as f:
                return json.load(f)
    cmd = "lncli" + getlndglobaloptions() + " fwdinghistory --start_time -5y --max_events 50000 2>&1"
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
    except subprocess.CalledProcessError as e:
        print(f"error in getfwdinghistory: {e}")
        cmdoutput = '{\"forwarding_events\": []}'
    j = json.loads(cmdoutput)
    return j

def getfwdinghistoryrest(node):
    if useMockData or not nodeconfigvalid(node):
        return getfwdinghistory()
    postData = '{"start_time":0,"num_max_events":50000}'
    defaultResponse = '{"forwarding_events":[]}'
    return noderestcommandpost(node, "/v1/switch", postData, defaultResponse)

def getlndglobaloptions():
    return " --macaroonpath=${HOME}/.lnd/nodeyez.macaroon"

def getnodeaddress(nodeinfo):
    bestresult = ""
    for addr in nodeinfo["node"]["addresses"]:
        nodehostandport = addr["addr"]
        if bestresult == "":
            bestresult = nodehostandport
        elif "onion" in nodehostandport:
            if "onion" not in bestresult:
                bestresult = nodehostandport
            elif len(nodehostandport) > 56:
                bestresult = nodehostandport
    return bestresult

def getnodealias(nodeinfo):
    if "alias" in nodeinfo:
        return nodeinfo["alias"]
    if "node" in nodeinfo:
        return getnodealias(nodeinfo["node"])
    return "UNKNOWN ALIAS"

def getnodealiasandstatus(pubkey, nextnodepubkey):
    nodeinfo = getnodeinfo(pubkey)
    nodealias = getnodealias(nodeinfo)
    nodeonline = 0
    if isnodeconnected(pubkey):
        nodeonline = 1
    else:
        nodeonline = attemptconnect(nodeinfo)
    # look if there is a channel
    haschannel = 0
    if "channels" in nodeinfo:
        for channel in nodeinfo["channels"]:
            node1_pub = channel["node1_pub"]
            node2_pub = channel["node2_pub"]
            if pubkey == node1_pub and nextnodepubkey == node2_pub:
                haschannel = 1
                break
            if pubkey == node2_pub and nextnodepubkey == node1_pub:
                haschannel = 1
                break
    return (nodealias, nodeonline, haschannel, nodeinfo)

def getnodealiasandstatusrest(pubkey, nextnodepubkey, node):
    if not nodeconfigvalid(node):
        return getnodealiasandstatus(pubkey, nextnodepubkey)
    nodeinfo = getnodeinforest(pubkey, node)
    nodealias = getnodealias(nodeinfo)
    nodeonline = 0
    if isnodeconnectedrest(pubkey, node):
        nodeonline = 1
    else:
        nodeonline = attemptconnectrest(nodeinfo, node)
    # look if there is a channel
    haschannel = 0
    if "channels" in nodeinfo:
        for channel in nodeinfo["channels"]:
            node1_pub = channel["node1_pub"]
            node2_pub = channel["node2_pub"]
            if pubkey == node1_pub and nextnodepubkey == node2_pub:
                haschannel = 1
                break
            if pubkey == node2_pub and nextnodepubkey == node1_pub:
                haschannel = 1
                break
    return (nodealias, nodeonline, haschannel, nodeinfo)

def getnodealiasfrompubkey(pubkey):
    return getnodealiasfrompubkeyrest(pubkey, {})

def getnodealiasfrompubkeyrest(pubkey, node):
    alias = getdefaultaliasfrompubkey(pubkey)
    if pubkey in pubkey_alias.keys():
        alias = pubkey_alias[pubkey]
        if len(alias) < 1:
            alias = getdefaultaliasfrompubkey(pubkey)
    else:
        if nodeconfigvalid(node):
            nodeinfo = getnodeinforest(pubkey, node)
        else:
            nodeinfo = getnodeinfo(pubkey)
        alias = getnodealias(nodeinfo)
        pubkey_alias[pubkey] = alias
    return alias

def getnodechannels():
    if useMockData:
        if exists("../mock-data/getnodechannels.json"):
            with open("../mock-data/getnodechannels.json") as f:
                r = json.load(f)
                return r
    cmd = "lncli" + getlndglobaloptions() + " listchannels 2>&1"
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
    except subprocess.CalledProcessError as e:
        print(f"error in getnodechannels: {e}")
        cmdoutput = '{"channels": []}'
    j = json.loads(cmdoutput)
    return j

def getnodechannelsrest(node):
    if useMockData or not nodeconfigvalid(node):
        return getnodechannels()
    defaultResponse = '{"channels":[]}'
    return noderestcommandget(node, "/v1/channels", defaultResponse)

def getnodeinfo(pubkey):
    if useMockData:
        if exists("../mock-data/getnodeinfo.json"):
            with open("../mock-data/getnodeinfo.json") as f:
                r = json.load(f)
                r["node"]["alias"] = mockaliasforpubkey(pubkey)
                return r
    cmd = "lncli" + getlndglobaloptions() + " getnodeinfo --pub_key " + pubkey + " --include_channels 2>&1"
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
    except subprocess.CalledProcessError as e:
        print(f"error in getnodeinfo: {e}")
        cmdoutput = '{"node":{"alias":"' + pubkey + '","pub_key":"' + pubkey + '","last_update":0,"addresses":[{"network":"tcp","addr":"0.0.0.0:65535"}]}}'
    j = json.loads(cmdoutput)
    return j

def getnodeinforest(pubkey, node):
    if not nodeconfigvalid(node):
        return getnodeinfo(pubkey)
    defaultResponse = '{"node":{"alias":"' + pubkey + '","pub_key":"' + pubkey + '","last_update":0,"addresses":[{"network":"tcp","addr":"0.0.0.0:65535"}]}}'
    return noderestcommandget(node, "/v1/graph/node/" + pubkey + "?include_channels=true", defaultResponse)

def getnodepayments():
    if useMockData:
        if exists("../mock-data/getnodepayments.json"):
            with open("../mock-data/getnodepayments.json") as f:
                return json.load(f)
    cmd = "lncli" + getlndglobaloptions() + " listpayments 2>&1"
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
    except subprocess.CalledProcessError as e:
        print(f"error in getnodepayments: {e}")
        cmdoutput = '{"payments": []}'
    j = json.loads(cmdoutput)
    return j

def getnodepaymentsrest(node):
    if useMockData or not nodeconfigvalid(node):
        return getnodepayments()
    defaultResponse = '{"payments":[]}'
    return noderestcommandget(node, "/v1/payments", defaultResponse)

def getnodepeers():
    cmd = "lncli" + getlndglobaloptions() + " listpeers 2>&1"
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
        return cmdoutput
    except subprocess.CalledProcessError as e:
        print(f"error in getnodepeers: {e}")
        return '{"peers": []}'

def getnodepeersrest(node):
    if not nodeconfigvalid(node):
        return getnodepeers()
    defaultResponse = '{"peers":[]}'
    return noderestcommandget(node, "/v1/peers", defaultResponse)

def isnodeconnected(pubkey):
    nodepeers = getnodepeers()
    j = json.loads(nodepeers)
    for peer in j["peers"]:
        if pubkey == peer["pub_key"]:
            return True
    return False

def isnodeconnectedrest(pubkey, node):
    if not nodeconfigvalid(node):
        return isnodeconnected(pubkey)
    nodepeers = getnodepeersrest(node)
    if "peers" in nodepeers:
        for peer in j["peers"]:
            if pubkey == peer["pub_key"]:
                return True
    return False

def mockaliasforpubkey(pubkey):
    alias = "mockup node"
    mfn = "../mock-data/bip39words.txt"
    if exists(mfn):
        with open(mfn) as f:
            wordnum = int(pubkey[0:4], base=16)
            wordnum %= 2048
            for i, line in enumerate(f):
                if i == wordnum:
                    alias = line.replace("\n","") + "-" + str(i)
                    break
        pass
    return alias

def nodeconfigvalid(node):
    if "address" not in node:
        return False
    if "macaroon" not in node:
        return False
    if "port" not in node:
        return False
    return True

def noderestcommandget(node, suffix, defaultResponse="{}"):
    cmdoutput = ""
    try:
        nodeaddress = node["address"]
        nodeport = node["port"]
        nodemacaroon = node["macaroon"]
        useTor = False
        if "useTor" in node:
            useTor = node["useTor"]
        url = "https://" + nodeaddress + ":" + nodeport + suffix
        headers = {"Grpc-Metadata-macaroon": nodemacaroon}
        if useTor:
            proxies = vicariousnetwork.gettorproxies()
        else:
            proxies = {}
        timeout = vicariousnetwork.gettimeouts()
        requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
        cmdoutput = requests.get(url,headers=headers,timeout=timeout,proxies=proxies,verify=False).text
        #print(f"{suffix} response \n\n{cmdoutput}")
    except Exception as e:
        print(f"error calling noderestcommandget for {suffix}: {e}")
        print(f"using default")
        cmdoutput = defaultResponse
    try:
        j = json.loads(cmdoutput)
    except Exception as e:
        print(f"error loading response as json: {e}")
        print(f"using default")
        j = json.loads(defaultResponse)
    return j

def noderestcommanddelete(node, suffix, defaultResponse="{}"):
    cmdoutput = ""
    try:
        nodeaddress = node["address"]
        nodeport = node["port"]
        nodemacaroon = node["macaroon"]
        useTor = False
        if "useTor" in node:
            useTor = node["useTor"]
        url = "https://" + nodeaddress + ":" + nodeport + suffix
        headers = {"Grpc-Metadata-macaroon": nodemacaroon}
        if useTor:
            proxies = vicariousnetwork.gettorproxies()
        else:
            proxies = {}
        timeout = vicariousnetwork.gettimeouts()
        requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
        cmdoutput = requests.delete(url,headers=headers,timeout=timeout,proxies=proxies,verify=False).text
    except Exception as e:
        print(f"error calling noderestcommanddelete for {suffix}: {e}")
        print(f"using default")
        cmdoutput = defaultResponse
    try:
        j = json.loads(cmdoutput)
    except Exception as e:
        print(f"error loading response as json: {e}")
        print(f"using default")
        j = json.loads(defaultResponse)
    return j

def noderestcommandpost(node, suffix, postData="{}", defaultResponse="{}"):
    cmdoutput = ""
    try:
        nodeaddress = node["address"]
        nodeport = node["port"]
        nodemacaroon = node["macaroon"]
        useTor = False
        if "useTor" in node:
            useTor = node["useTor"]
        url = "https://" + nodeaddress + ":" + nodeport + suffix
        headers = {"Grpc-Metadata-macaroon": nodemacaroon}
        if useTor:
            proxies = vicariousnetwork.gettorproxies()
        else:
            proxies = {}
        timeout = vicariousnetwork.gettimeouts()
        requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
        cmdoutput = requests.post(url,data=postData,headers=headers,timeout=timeout,proxies=proxies,verify=False).text
        #print(f"{suffix} response \n\n{cmdoutput}")
    except Exception as e:
        print(f"error calling noderestcommandpost for {suffix}: {e}")
        print(f"using default")
        cmdoutput = defaultResponse
    try:
        j = json.loads(cmdoutput)
    except Exception as e:
        print(f"error loading response as json: {e}")
        print(f"using default")
        j = json.loads(defaultResponse)
    return j
