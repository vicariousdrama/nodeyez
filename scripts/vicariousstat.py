# import packages
import psutil
import subprocess

# gets hottest temperature (cpu) in degrees C, * 1000
def getcputemp():
    cmd = "grep . /sys/class/hwmon/*/* /sys/class/thermal/*/* 2>/dev/null | grep \"temp\" | grep \"input\" | awk '{split($0,a,\":\"); print a[2]}' | sort -r | head -n 1"
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8").strip()
        return (float(cmdoutput)/1000.0)
    except subprocess.CalledProcessError as e:
        print(e)
        return 0

def getcputempwarnlevel():
    h = 60 # based on raspberry pi, which doesnt report high or critical
    s = psutil.sensors_temperatures()
    for k in s.keys():
        v = s[k][0]
        if v.high is not None:
            if v.high > h: h = v.high
    return h

def getcputempdangerlevel():
    h = 75 # based on raspberry pi, which doesnt report high or critical
    s = psutil.sensors_temperatures()
    for k in s.keys():
        v = s[k][0]
        if v.critical is not None:
            if v.critical > h: h = v.critical
    return h

# gets available memory, in MB
def getmemoryavailable():
    cmd = "free --mebi | grep Mem | awk '{ print $7 }'"
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8").strip()
        return int(cmdoutput)
    except subprocess.CalledProcessError as e:
        print(e)
        return 0

def getmemoryinfo(memtype="Mem"):
    cmd = f"free --mebi | grep {memtype}"
    info = {"label":memtype,"total":0,"used":0,"percentused":100}
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8").strip()
        parts = cmdoutput.split()
        info["label"] = memtype
        info["total"] = parts[1]
        info["used"] = parts[2]
        info["percentused"] = int((float(info["used"])/float(info["total"]))*100)
    except subprocess.CalledProcessError as e:
        print(e)
    return info

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
def getdrivefreespace(path="/$"):
    cmd = "printf \"%s\" \"$(df -h|grep '" + path + "'|sed -n 1p|awk '{print $4}')\" 2>/dev/null"
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8").strip()
        return cmdoutput
    except subprocess.CalledProcessError as e:
        print(e)
        return "?"

# get drive free percent
def getdrivefreepercent(path="/$"):
    #cmd = "printf \"%.0f\" \"$(df | grep '" + path + "'|sed -n 1p|awk '{print $4/$2*100 }')\" 2>/dev/null"
    cmd = "printf \"%.0f\" \"$(df | grep '" + path + "'|sed -n 1p|awk '{print $4/($3+$4)*100 }')\" 2>/dev/null"
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8").strip()
        return cmdoutput
    except subprocess.CalledProcessError as e:
        print(e)
        return "?"

# get drive2 path
def getdrive2path():
    cmd = "df -t ext4 | grep / | awk '{print $6}' | grep -v /boot | sort | wc -l"
    try:
        cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8").strip()
        if len(cmdoutput) > 0:
            drivecount = int(cmdoutput)
            if drivecount > 1:
                cmd = "df -t ext4 | grep / | awk '{print $6}' | grep -v /boot | sort | sed -n 2p"
                drive2path = subprocess.check_output(cmd, shell=True).decode("utf-8").strip()
                return drive2path
    except subprocess.CalledProcessError as e:
        print(e)
        return "?"
    return None

# get drive1 info
def getdrive1info():
    drive1path = "/"
    drivefreespace = getdrivefreespace()
    drivefreepercent = getdrivefreepercent()
    return drive1path, drivefreespace, drivefreepercent

# get drive2 info
def getdrive2info():
    drive2path = getdrive2path()
    if drive2path is None or drive2path == "?":
        return "None", 0, 0
    else:
        drivefreespace = getdrivefreespace(drive2path)
        drivefreepercent = getdrivefreepercent(drive2path)
        return drive2path, drivefreespace, drivefreepercent
