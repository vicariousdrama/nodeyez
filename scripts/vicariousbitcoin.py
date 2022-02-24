# import packages
import json
import math
import subprocess

# ------ Bitcoin Core Related ------------------------------------------------------

def getblock(blocknum):
    cmd = "bitcoin-cli getblock `bitcoin-cli getblockhash " + str(blocknum) + "`"
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
        j = json.loads(cmdoutput)
        return j
    except subprocess.CalledProcessError() as e:
        print(e)
        fakejson = "{\"confirmations\": 1, \"time\": " + str(getcurrenttimeinseconds) + "\"}"
        return json.loads(fakejson)

def getblockhash(blocknumber=1):
    cmd = "bitcoin-cli getblockhash " + str(blocknumber)
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
        return cmdoutput
    except subprocess.CalledProcessError as e:
        print(e)
        return "0000000000000000000000000000000000000000000000000000000000000000"

def getcurrentblock():
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
    return int(epochnum * 2016) + 1



# ------ Lightning LND Related ------------------------------------------------------

pubkey_alias = {'pubkey':'alias'}

def getdefaultaliasfrompubkey(pubkey):
    return pubkey[0:10]

def getnodealias(nodeinfo):
    return nodeinfo["node"]["alias"]

def getnodealiasfrompubkey(pubkey):
    alias = getdefaultaliasfrompubkey(pubkey)
    if pubkey in pubkey_alias.keys():
        alias = pubkey_alias[pubkey]
        if len(alias) < 1:
            alias = getdefaultaliasfrompubkey(pubkey)
    else:
        nodeinfo = getnodeinfo(pubkey)
        alias = getnodealias(nodeinfo)
        pubkey_alias[pubkey] = alias
    return alias

def getnodechannels():
    cmd = "lncli listchannels 2>&1"
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
    except subprocess.CalledProcessError as e:
        cmdoutput = '{\"channels\": []}'
    j = json.loads(cmdoutput)
    return j

def getnodeinfo(pubkey):
    cmd = "lncli getnodeinfo --pub_key " + pubkey + " --include_channels 2>&1"
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
    except subprocess.CalledProcessError as e:
        cmdoutput = "{\"node\":{\"alias\":\"" + pubkey + "\",\"pub_key\":\"" + pubkey + "\",\"addresses\":[{\"network\":\"tcp\",\"addr\":\"0.0.0.0:65535\"}]}}"
    j = json.loads(cmdoutput)
    return j





