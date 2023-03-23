# import packages
from os.path import exists
import binascii
import json
import math
import requests
import subprocess
import vicariousnetwork

# gets hottest temperature (cpu) in degrees C, * 1000
def getcputemp():
    cmd = "grep . /sys/class/hwmon/*/* /sys/class/thermal/*/* 2>/dev/null | grep \"temp\" | grep \"input\" | awk '{split($0,a,\":\"); print a[2]}' | sort -r | head -n 1"
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8").strip()
        return int(cmdoutput)
    except subprocess.CalledProcessError as e:
        print(e)
        return 0

# gets avialable memory, in MB
def getmemoryavailable():
    cmd = "free --mebi | grep Mem | awk '{ print $7 }'"
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8").strip()
        return int(cmdoutput)
    except subprocess.CalledProcessError as e:
        print(e)
        return 0

# gets network transmitted
def getnetworktx():
    cmd = "ip -j -s link show | jq '.[] | [(select(.ifname!=\"lo\") | .stats64.tx.bytes)//0] | add' | awk -v OFMT='%.0f' '{sum+=$0} END{print sum}' | numfmt --to=iec | head -n 1"
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8").strip()
        return cmdoutput
    except subprocess.CalledProcessError as e:
        print(e)
        return "?"

# gets network received
def getnetworkrx():
    cmd = "ip -j -s link show | jq '.[] | [(select(.ifname!=\"lo\") | .stats64.rx.bytes)//0] | add' | awk -v OFMT='%.0f' '{sum+=$0} END{print sum}' | numfmt --to=iec | head -n 1"
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8").strip()
        return cmdoutput
    except subprocess.CalledProcessError as e:
        print(e)
        return "?"

# gets uptime (days)
def getuptime():
    cmd = "w|head -1|sed -E 's/.*up (.*),.*user.*/\\1/'|sed -E 's/([0-9]* days).*/\\1/'"
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8").strip()
        return cmdoutput
    except subprocess.CalledProcessError as e:
        print(e)
        return "?"

# gets load (1, 5, 15 minute periods)
def getload():
    cmd = "w|head -1|sed -E 's/.*load average: (.*)/\\1/'"
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8").strip()
        v = cmdoutput.split(",")
        return float(v[0]),float(v[1]),float(v[2])
    except subprocess.CalledProcessError as e:
        print(e)
        return (0.00, 0.00, 0.00)

def getcpucount():
    cmd = "cat /proc/cpuinfo | grep processor | wc -l"
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8").strip()
        return int(cmdoutput)
    except subprocess.CalledProcessError as e:
        print(e)
        return 1

# get drive free
def getdrivefree(path="/$"):
    cmd = "printf \"%s\" \"$(df -h|grep '" + path + "'|awk '{print $4}')\" 2>/dev/null"
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8").strip()
        return cmdoutput
    except subprocess.CalledProcessError as e:
        print(e)
        return "?"

# get drive free percent
def getdriveratio(path="/$"):
    cmd = "printf \"%.0f\" \"$(df | grep '" + path + "'|awk '{print $4/$2*100 }')\" 2>/dev/null"
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8").strip()
        return cmdoutput
    except subprocess.CalledProcessError as e:
        print(e)
        return "?"

# get drive2 path
def getdrive2path():
    cmd = "lsblk --output MOUNTPOINT | grep / | grep -v /boot | grep -v /snap | sort | wc -l"
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8").strip()
        if len(cmdoutput) > 0:
            drivecount = int(cmdoutput)
            if drivecount > 1:
                cmd = "lsblk --output MOUNTPOINT | grep / | grep -v /boot | grep -v /snap | sort | sed -n 2p"
                drive2path = subprocess.check_output(cmd, shell=True).decode("utf-8").strip()
                return drive2path
    except subprocess.CalledProcessError as e:
        print(e)
        return "?"
    return None

# get drive1 info
def getdrive1info():
    drive1path = "/"
    drivefree = getdrivefree()
    driveratio = getdriveratio()
    return drive1path, drivefree, driveratio

# get drive2 info
def getdrive2info():
    drive2path = getdrive2path()
    if drive2path is None or drive2path == "?":
        return "None", 0, 0
    else:
        drivefree = getdrivefree(drive2path)
        driveratio = getdriveratio(drive2path)
        return drive2path, drivefree, driveratio
