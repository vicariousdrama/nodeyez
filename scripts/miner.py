#! /usr/bin/env python3
from PIL import ImageColor
from os.path import exists
from vicariouspanel import NodeyezPanel
import json
import os
import subprocess
import sys
import time
import vicariousbitcoin
import vicariouschart
import vicarioustext

class MinerPanel(NodeyezPanel):

    def __init__(self):
        """Instantiates a new Miner panel"""

        # Define which additional attributes we have
        self.configAttributes = {
            # legacy key name mappings
            "colorBackground": "backgroundColor",
            "colorHashrateBox": "hashrateBoxColor",
            "colorHashrateMA": "hashrateMovingAverageColor",
            "colorHashratePlot": "hashrateValueColor",
            "colorHot": "warningTextColor",
            "colorTextFG": "textColor",
            "sleepInterval": "interval",
            # panel specific key names
            "hashrateBoxColor": "hashrateBoxColor",
            "hashrateLowValueColor": "hashrateLowValueColor",
            "hashrateLowValueTextColor": "hashrateLowValueTextColor",
            "hashrateMovingAverageColor": "hashrateMovingAverageColor",
            "hashrateValueColor": "hashrateValueColor",
            "miners": "miners",
            "saveInterval": "saveInterval",
            "warningStatusBackgroundColor": "warningStatusBackgroundColor",
            "warningStatusTextColor": "warningStatusTextcolor",
            "warningTextColor": "warningTextColor",
        }

        # Define our defaults (all panel specific key names should be listed)
        self._defaultattr("hashrateBoxColor", "#202020")
        self._defaultattr("hashrateLowValueColor", "#ffaa00")
        self._defaultattr("hashrateLowValueTextColor", "#202020")
        self._defaultattr("hashrateMovingAverageColor", "#40ff40")
        self._defaultattr("hashrateValueColor", "#2f3fc5")
        self._defaultattr("headerText", "Miner Status")
        self._defaultattr("interval", 60)
        self._defaultattr("miners", []) # wants keys: enabled, address, port, expectations
        self._defaultattr("saveInterval", 600)
        self._defaultattr("warningStatusBackgroundColor", "#ff0000")
        self._defaultattr("warningStatusTextColor", "#ffffff")
        self._defaultattr("warningTextColor", "#ff0000")

        # Initialize
        super().__init__(name="miner")
        self.saveLastTime = int(time.time())

    def _getMinerInfo(self, miner={}, command="summary"):
        minerAddress = miner["address"] if "address" in miner else "127.0.0.1"        
        minerPort = miner["port"] if "port" in miner else 4028
        cmd = "echo '{\"command\":\"" + command + "\"}'"
        cmd += f"|nc -w 5 {minerAddress} {minerPort} | jq ."
        cmdoutput = ""
        try:
            cmdoutput = subprocess.check_output(cmd, shell=True).decode("utf-8")
            if len(cmdoutput) > 0:
                return json.loads(cmdoutput)
        except subprocess.CalledProcessError as e:
            self.log(f"error in _getMinerInfo: {e}")
        cmdoutput = "{"
        commandParts = command.split("+")
        for commandPart in commandParts:
            if cmdoutput[-1:] == "]": cmdoutput += ", "
            cmdoutput += "\"" + commandPart + "\": []"
        cmdoutput += "}"
        return json.loads(cmdoutput)

    def _detectMinerType(self, info):
        minerType = "unknown"
        if info is None: return minerType
        if "summary" in info:
            for o in info["summary"]:
                if "SUMMARY" not in o: continue
                for i in o["SUMMARY"]:
                    if all(key in i for key in ["Chip Temp Max",
                        "Env Temp", "Fan Speed In", "Fan Speed Out",
                        "Power", "Power Limit", "Power Mode",
                        "Temperature" ]): minerType = "microbt"
        if "tunerstatus" in info:
            for o in info["tunerstatus"]:
                if "TUNERSTATUS" not in o: continue
                for i in o["TUNERSTATUS"]:
                    if all(key in i for key in ["PowerLimit",
                        "ApproximateChainPowerConsumption",
                        "ApproximateMinerPowerConsumption"]): minerType = "braiins"
        if "STATS" in info:
            for i in info["STATS"]:
                if "Type" in i: 
                    if i["Type"].find("Antminer S19") > -1: minerType = "antminer-s19"
        return minerType

    def fetchData(self):
        """Fetches all the data needed for this panel"""

        saveCounter = 0
        minerNumber = 0
        for miner in self.miners:
            minerNumber += 1
            if "enabled" not in miner: continue
            if not miner["enabled"]: continue
            if "type" in miner:
                if miner["type"] == "detect": del miner["type"]
            if "type" not in miner:
                minerSummary = self._getMinerInfo(miner, "summary")
                miner["type"] = self._detectMinerType(minerSummary)
                if miner["type"] == "unknown":
                    minerTunerStatus = self._getMinerInfo(miner, "tunerstatus")
                    miner["type"] = self._detectMinerType(minerTunerStatus)
                if miner["type"] == "unknown":
                    minerStats = self._getMinerInfo(miner, "stats")
                    miner["type"] = self._detectMinerType(minerStats)
                if miner["type"] == "unknown":
                    self.log(f"unable to detect miner type for configured miner number {minerNumber}. disabling")
                    miner["enabled"] = False
                    continue
            self._updateMinerData(minerNumber)
            # Periodically, we save the overall hashrate history for miners
            if (self.saveLastTime + self.saveInterval) < int(time.time()):
                self._saveMinerHashrateHistory(minerNumber)
                saveCounter += 1
        if saveCounter > 0:
            self.saveLastTime = int(time.time())
    
    # Normalizes to consistent format
    def _updateMinerDataFromAntminerS19(self, miner, minerData):
        # Power (not found yet)
        miner["data"]["Power"] = 3250       # may be 3250-3600 depending on model
        miner["data"]["PowerLimit"] = 3250  # can also be influenced by STATS[].frequency or .Mode
        # Boards & Temp
        if "STATS" in minerData:
            for i in minerData["STATS"]:
                if "miner_count" in i:
                    boards = i["miner_count"]
                    counter = 0
                    miner["data"]["Boards"].clear()
                    for boardNumber in range(boards):
                        counter += 1
                        id = counter
                        boardfield = f"temp{counter}"
                        chipfield = f"temp2_{counter}"
                        temp = 0 if boardfield not in i else i[boardfield]
                        chip = 0 if chipfield not in i else i[chipfield]
                        board = {"ID": f"Board {id}", "Temp": temp, "ChipTemp": chip}
                        miner["data"]["Boards"].append(board)
        # Fans
        if "STATS" in minerData:
            for i in minerData["STATS"]:
                if "fan_num" in i:
                    fans = i["fan_num"]
                    counter = 0
                    miner["data"]["Fans"].clear()
                    for fanNumber in range(fans):
                        counter += 1
                        id = counter
                        fanfield = f"fan{counter}"
                        rpm = 0 if fanfield not in i else i[fanfield]
                        if rpm == 0 and counter > 2: continue
                        fan = {"ID": f"Fan {id}", "RPM": rpm}
                        miner["data"]["Fans"].append(fan)
        # Hashrate
        miner["data"]["HashrateUnit"] = "Gh/s"
        hashrate = 0
        if "STATS" in minerData:
            for i in minerData["STATS"]:
                if "GHS 5s" in i: hashrate = i["GHS 5s"]
        miner["data"]["Hashrate"].append(hashrate)
        # Pools
        if "POOLS" in minerData:
            miner["data"]["Pools"].clear()
            for i in minerData["POOLS"]:
                url = "NOT_SET" if "URL" not in i else i["URL"]
                user = "NOT_SET" if "User" not in i else i["User"]
                status = "NOT_SET" if "Status" not in i else i["Status"]
                pool = {"URL": url, "User": user, "Status": status}
                miner["data"]["Pools"].append(pool)

    # Normalizes to consistent format
    def _updateMinerDataFromBraiins(self, miner, minerData):
        # Power
        if "tunerstatus" in minerData:
            for o in minerData["tunerstatus"]:
                if "TUNERSTATUS" not in o: continue
                for i in o["TUNERSTATUS"]:
                    if "PowerLimit" in i: miner["data"]["PowerLimit"] = i["PowerLimit"]
                    if "ApproximateMinerPowerConsumption" in i: miner["data"]["Power"] = i["ApproximateMinerPowerConsumption"]
        # Boards & Temp
        if "temps" in minerData:
            for o in minerData["temps"]:
                if "TEMPS" not in o: continue
                miner["data"]["Boards"].clear()
                counter = 0
                for i in o["TEMPS"]:
                    counter += 1
                    id = counter
                    temp = 0 if "Board" not in i else i["Board"]
                    chip = 0 if "Chip" not in i else i["Chip"]
                    board = {"ID": f"Board {id}", "Temp": temp, "ChipTemp": chip}
                    miner["data"]["Boards"].append(board)
        # Fans
        if "fans" in minerData:
            for o in minerData["fans"]:
                if "FANS" not in o: continue
                miner["data"]["Fans"].clear()
                counter = 0
                for i in o["FANS"]:
                    counter += 1
                    id = counter
                    rpm = 0 if "RPM" not in i else i["RPM"]
                    if rpm == 0 and counter > 2: continue
                    fan = {"ID": f"Fan {id}", "RPM": rpm}
                    miner["data"]["Fans"].append(fan)
        # Hashrate
        miner["data"]["HashrateUnit"] = "Mh/s"
        hashrate = 0
        if "summary" in minerData:
            for o in minerData["summary"]:
                if "SUMMARY" not in o: continue
                for i in o["SUMMARY"]:
                    if "MHS 1m" in i: hashrate = i["MHS 1m"]
        miner["data"]["Hashrate"].append(hashrate)
        # Pools
        if "pools" in minerData:
            for o in minerData["pools"]:
                if "POOLS" not in o: continue
                miner["data"]["Pools"].clear()
                for i in o["POOLS"]:
                    url = "NOT_SET" if "URL" not in i else i["URL"]
                    user = "NOT_SET" if "User" not in i else i["User"]
                    status = "NOT_SET" if "Status" not in i else i["Status"]
                    pool = {"URL": url, "User": user, "Status": status}
                    miner["data"]["Pools"].append(pool)
        # Others which were referenced in the past but not in this panel
        # Temperature
        #   "tempctrl"[]."TEMPCTRL"[]."Target"
        #   "tempctrl"[]."TEMPCTRL"[]."Hot"
        #   "tempctrl"[]."TEMPCTRL"[]."Dangerous"

    # Normalizes to consistent format
    def _updateMinerDataFromMicroBT(self, miner, minerData):
        # Power
        if "summary" in minerData:
            for o in minerData["summary"]:
                if "SUMMARY" not in o: continue
                for i in o["SUMMARY"]:
                    if "Power Limit" in i: miner["data"]["PowerLimit"] = i["Power Limit"]
                    if "Power" in i: miner["data"]["Power"] = i["Power"]
                    if "Power Mode" in i: miner["data"]["PowerMode"] = i["Power Mode"]
        # Boards & Temp
        if "devs" in minerData:
            for o in minerData["devs"]:
                if "DEVS" not in o: continue
                miner["data"]["Boards"].clear()
                counter = 0
                for i in o["DEVS"]:
                    counter += 1
                    id = counter if "ID" not in i else i["ID"]
                    temp = 0 if "Temperature" not in i else i["Temperature"]
                    chip = 0 if "Chip Temp Max" not in i else i["Chip Temp Max"]
                    board = {"ID": f"Board {id}", "Temp": temp, "ChipTemp": chip}
                    miner["data"]["Boards"].append(board)
        # Fans
        if "summary" in minerData:
            for o in minerData["summary"]:
                if "SUMMARY" not in o: continue
                miner["data"]["Fans"].clear()
                for i in o["SUMMARY"]:
                    if "Fan Speed In" in i: miner["data"]["Fans"].append({"ID": "Fan In", "RPM": i["Fan Speed In"]})
                    if "Fan Speed Out" in i: miner["data"]["Fans"].append({"ID": "Fan Out", "RPM": i["Fan Speed Out"]})
        # Hashrate
        miner["data"]["HashrateUnit"] = "Mh/s"
        hashrate = 0
        if "summary" in minerData:
            for o in minerData["summary"]:
                if "SUMMARY" not in o: continue
                for i in o["SUMMARY"]:
                    if "MHS 1m" in i: hashrate = i["MHS 1m"]
        miner["data"]["Hashrate"].append(hashrate)
        # Pools
        if "pools" in minerData:
            for o in minerData["pools"]:
                if "POOLS" not in o: continue
                miner["data"]["Pools"].clear()
                for i in o["POOLS"]:
                    url = "NOT_SET" if "URL" not in i else i["URL"]
                    user = "NOT_SET" if "User" not in i else i["User"]
                    status = "NOT_SET" if "Status" not in i else i["Status"]
                    pool = {"URL": url, "User": user, "Status": status}
                    miner["data"]["Pools"].append(pool)

    def _saveMinerHashrateHistory(self, minerNumber):
        if len(self.miners) < minerNumber: return
        fn = self._getMinerHashrateHistoryFilename(minerNumber)
        with open(fn, "w") as f:
            json.dump(self.miners[minerNumber-1]["data"]["Hashrate"],f)

    def _getMinerHashrateHistoryFilename(self, minerNumber):
        d = f"{self.dataDirectory}miner/"
        if not exists(d): os.makedirs(d)
        miner = self.miners[minerNumber - 1]
        suffix = miner["address"] if "address" in miner else f"miner{minerNumber}"
        return f"{d}hashrate-{suffix}.json"

    def _loadMinerHashrateHistory(self, minerNumber):
        emptyHashrate = [-1] * self.width
        if len(self.miners) < minerNumber: return emptyHashrate
        fn = self._getMinerHashrateHistoryFilename(minerNumber)
        if not exists(fn): return emptyHashrate
        mtime = int(os.path.getmtime(fn))
        currenttime = int(time.time())
        diff = currenttime - mtime
        emptyTicks = int(diff / self.interval)
        with open(fn) as f: minerHashrateHistory = json.load(f)
        if emptyTicks > 0: minerHashrateHistory.extend([-1] * emptyTicks)
        return minerHashrateHistory

    def _updateMinerData(self, minerNumber):
        if len(self.miners) < minerNumber: return
        miner = self.miners[minerNumber - 1]
        if "data" not in miner: 
            hashrateHistory = self._loadMinerHashrateHistory(minerNumber)
            miner["data"] = {
                "Power": 0,
                "PowerLimit": 0,
                "PowerMode": "Normal",
                "Boards": [{"ID": 0, "Temp": 0, "ChipTemp": 0}],
                "Fans": [{"ID": 0, "RPM": 0}],
                "Hashrate": hashrateHistory,
                "HashrateUnit": "Mh/s",
                "Pools": [{"URL": "NOT_SET", "User": "NOT_SET", "Status": "NOT_SET"}]
            }
        else:
            miner["data"]["Power"] = 0
            miner["data"]["PowerLimit"] = 0
            miner["data"]["PowerMode"] = "Normal"
            for board in miner["data"]["Boards"]:
                board["Temp"] = 0
                board["ChipTemp"] = 0
            for fan in miner["data"]["Fans"]:
                fan["RPM"] = 0
            for pool in miner["data"]["Pools"]:
                pool["URL"] = "NOT_SET"
                pool["User"] = "NOT_SET"
                pool["Status"] = "Offline"
        minerType = miner["type"]
        if minerType == "antminer-s19":
            # S19 only handles one command at a time, erroring on multiple, 
            # so we build up a composite from multiple calls
            minerStats = self._getMinerInfo(miner, "stats")
            minerPools = self._getMinerInfo(miner, "pools")
            minerData = {}
            if "STATS" in minerStats: minerData["STATS"] = minerStats["STATS"]
            if "POOLS" in minerPools: minerData["POOLS"] = minerPools["POOLS"]
            self._updateMinerDataFromAntminerS19(miner, minerData)
        elif minerType == "braiins":
            minerData = self._getMinerInfo(miner, "fans+pools+summary+tempctrl+temps+tunerstatus")
            self._updateMinerDataFromBraiins(miner, minerData)
        elif minerType ==  "microbt":
            minerData = self._getMinerInfo(miner, "devs+pools+summary")
            self._updateMinerDataFromMicroBT(miner, minerData)
        else:
            self.log(f"unable to update miner data for type {minerType}")

    def _isMinerPowerValid(self, miner, power):
        if "expectations" not in miner: return True
        if "Power" not in miner["expectations"]: return True
        if "Min" in miner["expectations"]["Power"]:
            minExpected = miner["expectations"]["Power"]["Min"]
            if power < minExpected: return False
        if "Max" in miner["expectations"]["Power"]:
            maxExpected = miner["expectations"]["Power"]["Max"]
            if power > maxExpected: return False
        return True

    def _renderPower(self, miner, left, top, width):
        groupFontSize = int(self.height * 16/320)
        subtextFontSize = int(self.height * 12/320)
        subtextPadding = int(self.height * 5/320)
        power = miner["data"]["Power"]
        powerColor = self.textColor
        if not self._isMinerPowerValid(miner, power):
            powerColor = self.warningTextColor
            if power > 0:
                self.Status.append(f"Power is out of expected range")
            else:
                self.Status.append(f"No valid data from miner. Is it online?")
            self.StatusType = "Warning"
        powerLimit = miner["data"]["PowerLimit"]
        power = f"{power}w" if power > 0 else "unknown"
        powerLimit = f"{powerLimit}w" if powerLimit > 0 else "unknown"
        if power > powerLimit: 
            powerColor = self.warningTextColor
            self.Status.append(f"Power exceeds the power limit")
            self.StatusType = "Warning"
        vicarioustext.drawtoplefttext(self.draw, "Power: ", groupFontSize, left, top, ImageColor.getrgb(self.textColor), True)
        vicarioustext.drawtoprighttext(self.draw, power, groupFontSize, left+width, top, ImageColor.getrgb(powerColor), True)
        vicarioustext.drawtoplefttext(self.draw, "Limit:", subtextFontSize, left+subtextPadding, top+groupFontSize + (subtextFontSize//2), ImageColor.getrgb(self.textColor))
        vicarioustext.drawtoprighttext(self.draw, powerLimit, subtextFontSize, left+width, top+groupFontSize + (subtextFontSize//2), ImageColor.getrgb(self.textColor))
        sectionHeight = groupFontSize + (subtextFontSize//2) + subtextFontSize
        return sectionHeight

    def _isMinerTempValid(self, miner, tempType, tempValue):
        if "expectations" not in miner: return True
        if "Boards" not in miner["expectations"]: return True
        if f"{tempType}Min" in miner["expectations"]["Boards"]:
            minExpected = miner["expectations"]["Boards"][f"{tempType}Min"]
            if tempValue < minExpected: return False
        if f"{tempType}Max" in miner["expectations"]["Boards"]:
            maxExpected = miner["expectations"]["Boards"][f"{tempType}Max"]
            if tempValue > maxExpected: return False
        return True

    def _renderBoards(self, miner, left, top, width):
        groupFontSize = int(self.height * 16/320)
        subtextFontSize = int(self.height * 12/320)
        subtextPadding = int(self.height * 5/320)
        boardNumber = 0
        highestTemp = 0
        highestTempColor =self.textColor
        highestY = 0
        for board in miner["data"]["Boards"]:
            boardNumber += 1
            boardID = board["ID"]
            boardTemp = board["Temp"]
            boardTempColor = self.textColor
            if not self._isMinerTempValid(miner, "Temp", boardTemp):
                boardTempColor = self.warningTextColor
                self.Status.append(f"Board {boardNumber} temp is out of expected range")
                self.StatusType = "Warning"
            chipTemp = board["ChipTemp"]
            chipTempColor = self.textColor
            if not self._isMinerTempValid(miner, "ChipTemp", chipTemp):
                chipTempColor = self.warningTextColor
                self.Status.append(f"Board {boardNumber} chip temp is out of expected range")
                self.StatusType = "Warning"
            if boardTemp > highestTemp: highestTemp = boardTemp
            if chipTemp > highestTemp: highestTemp = chipTemp
            if chipTempColor == self.warningTextColor: highestTempColor = chipTempColor
            boardTemp = str(format(boardTemp, ".2f")) + "°C"
            chipTemp = str(format(chipTemp, ".2f")) + "°C"
            y = top+groupFontSize + (subtextFontSize//2) + ((boardNumber - 1) * 2 * subtextFontSize)
            vicarioustext.drawtoplefttext(self.draw, f"{boardID}", subtextFontSize, left+subtextPadding, y, ImageColor.getrgb(self.textColor))
            vicarioustext.drawtoprighttext(self.draw, f"{boardTemp}", subtextFontSize, left+width, y, ImageColor.getrgb(boardTempColor))
            y += subtextFontSize
            vicarioustext.drawtoplefttext(self.draw, f"chip temp", subtextFontSize, left+(subtextPadding*2), y, ImageColor.getrgb(self.textColor))
            vicarioustext.drawtoprighttext(self.draw, f"{chipTemp}", subtextFontSize, left+width, y, ImageColor.getrgb(chipTempColor))
            highestY = y
        highestTemp = str(format(highestTemp, ".2f")) + "°C"
        vicarioustext.drawtoplefttext(self.draw, "Temp: ", groupFontSize, left, top, ImageColor.getrgb(self.textColor), True)
        vicarioustext.drawtoprighttext(self.draw, f"{highestTemp}", groupFontSize, left+width, top, ImageColor.getrgb(highestTempColor), True)
        sectionHeight = highestY + subtextFontSize - top
        return sectionHeight

    def _isMinerFanValid(self, miner, fanRPM):
        if "expectations" not in miner: return True
        if "Fans" not in miner["expectations"]: return True
        try:
            if str(fanRPM).upper().find("RPM") > -1: fanRPM = fanRPM.split("RPM")[0].strip()
            fanRPM = int(fanRPM)
            if "Min" in miner["expectations"]["Fans"]:
                minExpected = miner["expectations"]["Fans"]["Min"]
                if fanRPM < minExpected: return False
            if "Max" in miner["expectations"]["Fans"]:
                maxExpected = miner["expectations"]["Fans"]["Max"]
                if fanRPM > maxExpected: return False
            return True
        except Exception as e:
            self.log(f"logic error checking if fan rpm is valid. fanRPM={fanRPM}")
            return True

    def _renderFans(self, miner, left, top, width):
        groupFontSize = int(self.height * 16/320)
        subtextFontSize = int(self.height * 12/320)
        subtextPadding = int(self.height * 5/320)
        fanNumber = 0
        highestY = 0
        for fan in miner["data"]["Fans"]:
            fanNumber += 1
            fanID = fan["ID"]
            fanRPM = fan["RPM"]
            fanLabelColor = self.textColor
            if not self._isMinerFanValid(miner, fanRPM): 
                fanLabelColor = self.warningTextColor
                self.Status.append("Fan speed is out of expected range")
                self.StatusType = "Warning"
            if str(fanRPM).upper().find("RPM") == -1: fanRPM = f"{fanRPM} RPM"
            y = top+groupFontSize + (subtextFontSize//2) + ((fanNumber - 1) * subtextFontSize)
            vicarioustext.drawtoplefttext(self.draw, f"{fanID}", subtextFontSize, left+subtextPadding, y, ImageColor.getrgb(self.textColor))
            vicarioustext.drawtoprighttext(self.draw, f"{fanRPM}", subtextFontSize, left+width, y, ImageColor.getrgb(fanLabelColor))
            highestY = y
        vicarioustext.drawtoplefttext(self.draw, "Fans: ", groupFontSize, left, top, ImageColor.getrgb(self.textColor), True)
        sectionHeight = highestY + subtextFontSize - top
        return sectionHeight

    def _getMinimumHashrateExpected(self, miner):
        units=["Gh/s","Th/s","Ph/s","Eh/s","Zh/s"]
        hashrateUnit = miner["data"]["HashrateUnit"]
        if "expectations" not in miner: return 1
        if "Hashrate" not in miner["expectations"]: return 1
        if "Min" in miner["expectations"]["Hashrate"]:
            minExpected = miner["expectations"]["Hashrate"]["Min"]
            if hashrateUnit in units: minExpected /= pow(1000, units.index(hashrateUnit) + 1)
            return minExpected
        return 1

    def _isMinerHashrateValid(self, miner, hashrate, hashrateUnit):
        h = hashrate
        units=["Gh/s","Th/s","Ph/s","Eh/s","Zh/s"]
        if hashrateUnit in units: h *= pow(1000, units.index(hashrateUnit) + 1)
        if "expectations" not in miner: return True
        if "Hashrate" not in miner["expectations"]: return True
        if "Min" in miner["expectations"]["Hashrate"]:
            minExpected = miner["expectations"]["Hashrate"]["Min"]
            if h < minExpected: return False
        if "Max" in miner["expectations"]["Hashrate"]:
            maxExpected = miner["expectations"]["Hashrate"]["Max"]
            if h > maxExpected: return False
        return True

    def _renderHashrate(self, miner, left, top, width):
        groupFontSize = int(self.height * 16/320)
        tinyFontSize = int(self.height * 8/320)
        tinyPadding = int(self.height * 5/320)
        dataPointSize = int(self.height * 2/320)
        subtextPadding = int(self.height * 15/320)
        # Heading
        currentHashrate = miner["data"]["Hashrate"][-1]
        hashrateUnit = miner["data"]["HashrateUnit"]
        hashrateLabelColor = self.textColor
        if not self._isMinerHashrateValid(miner, currentHashrate, hashrateUnit): 
            hashrateLabelColor = self.warningTextColor
            self.Status.append("Hashrate is out of expected range")
            self.StatusType = "Warning"
        hashrateText = vicariousbitcoin.gethashratestring(currentHashrate, hashrateUnit)
        vicarioustext.drawtoplefttext(self.draw, "Hashrate: ", groupFontSize, left, top, ImageColor.getrgb(self.textColor), True)
        vicarioustext.drawtoprighttext(self.draw, f"{hashrateText}", groupFontSize, left+width, top, ImageColor.getrgb(hashrateLabelColor), True)
        # Chart Bounding
        chartLeft = left
        chartTop = top + groupFontSize + tinyFontSize + tinyPadding
        chartWidth = width
        chartHeight = self.getInsetHeight() // 2
        # Time Tick Marks
        timePeriodSize = 60 # pixels
        minutesPerLine = (timePeriodSize * self.interval) / 60 # minutes per hour
        timelineX = left + width - timePeriodSize - dataPointSize
        timePeriodNumber = 1
        while(timelineX > left):
            self.draw.line(xy=[(timelineX,chartTop-(subtextPadding//2)),(timelineX,chartTop+chartHeight)],fill=ImageColor.getrgb(self.hashrateBoxColor),width=1)
            timetext = str(int(timePeriodNumber * minutesPerLine)) + " mins"
            vicarioustext.drawbottomlefttext(self.draw, timetext, tinyFontSize, timelineX+2, chartTop - 1, ImageColor.getrgb(self.textColor))
            timelineX -= timePeriodSize
            timePeriodNumber += 1
        # Chart Data Plots
        minimumValueExpected = self._getMinimumHashrateExpected(miner)
        hashrateValues = miner["data"]["Hashrate"][-1 * width:]
        low, high, avg = vicariouschart.drawDotChart(draw=self.draw, left=chartLeft, top=chartTop, 
            width=chartWidth, height=chartHeight, list=hashrateValues, fieldName=None, 
            valueColor=self.hashrateValueColor, valueRadius=dataPointSize,
            movingAverageDuration=20, movingAverageColor=self.hashrateMovingAverageColor, 
            movingAverageWidth=dataPointSize,
            lowValueColor=self.hashrateLowValueColor, lowValueThreshold=minimumValueExpected)
        # Label Low, High, Avg lines
        hashrateText = "Min: " + vicariousbitcoin.gethashratestring(low, hashrateUnit)
        tw, th, _ = vicarioustext.gettextdimensions(self.draw, hashrateText, tinyFontSize, False)
        self.draw.rectangle(xy=[(chartLeft+1,chartTop+chartHeight-1),(chartLeft+tw+2,chartTop+chartHeight-th-2)],outline=ImageColor.getrgb(self.hashrateBoxColor),fill=ImageColor.getrgb(self.hashrateBoxColor),width=1)
        vicarioustext.drawbottomlefttext(self.draw, hashrateText, tinyFontSize, chartLeft+2, chartTop+chartHeight-1, ImageColor.getrgb(self.textColor))
        hashrateText = "Max: " + vicariousbitcoin.gethashratestring(high, hashrateUnit)
        tw, th, _ = vicarioustext.gettextdimensions(self.draw, hashrateText, tinyFontSize, False)
        self.draw.rectangle(xy=[(chartLeft+1,chartTop+1),(chartLeft+tw+2,chartTop+th+2)],outline=ImageColor.getrgb(self.hashrateBoxColor),fill=ImageColor.getrgb(self.hashrateBoxColor),width=1)
        vicarioustext.drawtoplefttext(self.draw, hashrateText, tinyFontSize, chartLeft+2, chartTop+1, ImageColor.getrgb(self.textColor))
        if low < minimumValueExpected and (high - low) > 0:
            hashrateText = "Low: " + vicariousbitcoin.gethashratestring(minimumValueExpected, hashrateUnit)
            tw, th, _ = vicarioustext.gettextdimensions(self.draw, hashrateText, tinyFontSize, False)
            pp = float(minimumValueExpected - low)/float(high - low)
            py = chartTop + ((1.0 - pp) * chartHeight)
            self.draw.line(xy=[(chartLeft,py),(chartLeft+chartWidth,py)],fill=ImageColor.getrgb(self.hashrateLowValueColor),width=1)
            self.draw.rectangle(xy=[(chartLeft+1,py+1),(chartLeft+tw+2,py+th+2)],outline=ImageColor.getrgb(self.hashrateLowValueColor),fill=ImageColor.getrgb(self.hashrateLowValueColor),width=1)
            vicarioustext.drawtoplefttext(self.draw, hashrateText, tinyFontSize, chartLeft+2, py+1, ImageColor.getrgb(self.hashrateLowValueTextColor))
        hashrateText = "Avg: " + vicariousbitcoin.gethashratestring(avg, hashrateUnit)
        tw, th, _ = vicarioustext.gettextdimensions(self.draw, hashrateText, tinyFontSize, False)
        pp = .5
        if high - low > 0: pp = float(avg - low)/float(high - low)
        py = chartTop + ((1.0 - pp) * chartHeight)
        self.draw.line(xy=[(chartLeft,py),(chartLeft+chartWidth,py)],fill=ImageColor.getrgb(self.hashrateBoxColor),width=1)
        if pp < .8:
            self.draw.rectangle(xy=[(chartLeft+1,py-1),(chartLeft+tw+2,py-th-2)],outline=ImageColor.getrgb(self.hashrateBoxColor),fill=ImageColor.getrgb(self.hashrateBoxColor),width=1)
            vicarioustext.drawbottomlefttext(self.draw, hashrateText, tinyFontSize, chartLeft+2, py-1, ImageColor.getrgb(self.textColor))
        else:
            self.draw.rectangle(xy=[(chartLeft+1,py+1),(chartLeft+tw+2,py+th+2)],outline=ImageColor.getrgb(self.hashrateBoxColor),fill=ImageColor.getrgb(self.hashrateBoxColor),width=1)
            vicarioustext.drawtoplefttext(self.draw, hashrateText, tinyFontSize, chartLeft+2, py+1, ImageColor.getrgb(self.textColor))
        # Box it
        self.draw.rectangle(xy=[(chartLeft,chartTop),(chartLeft+chartWidth,chartTop+chartHeight)],outline=ImageColor.getrgb(self.hashrateBoxColor),width=dataPointSize)
        # return space used
        sectionHeight = groupFontSize + tinyFontSize + tinyPadding + chartHeight
        return sectionHeight        

    def _makePoolLabel(self, poolUrl):
        o = poolUrl
        p = o.split("//")           # remove protocol
        if len(p) > 1: o = p[1]
        p = o.split(":")            # remove port
        if len(p) > 1: o = p[0]
        return o                    # ideally just fqdn

    def _isMinerPoolValid(self, miner, poolUrl, poolUser):
        if "expectations" not in miner: return True
        if "Pools" not in miner["expectations"]: return True
        for pool in miner["expectations"]["Pools"]:
            expectedPoolUrl = pool["URL"]
            expectedPoolUser = pool["User"]
            if expectedPoolUrl == poolUrl:
                if expectedPoolUser == poolUser: return True
                if str(expectedPoolUser).endswith(".*"): # check wildcard for worker name
                    if str(poolUser).startswith(expectedPoolUser.split("*")[0]): return True
        return False

    def _renderPools(self, miner, left, top, width):
        groupFontSize = int(self.height * 16/320)
        subtextFontSize = int(self.height * 12/320)
        subtextPadding = int(self.height * 5/320)
        poolNumber = 0
        highestY = 0
        for pool in miner["data"]["Pools"]:
            poolUser = pool["User"]
            poolUrl = pool["URL"]
            if len(poolUrl.strip()) == 0 or len(poolUser.strip()) == 0: continue
            poolNumber += 1
            poolLabelColor = self.textColor
            if not self._isMinerPoolValid(miner, poolUrl, poolUser): 
                poolLabelColor = self.warningTextColor
                self.Status.append("Miner has unexpected pool or user configured")
                self.StatusType = "Warning"
            poolStatus = pool["Status"]
            poolLabel = self._makePoolLabel(poolUrl)
            y = top+groupFontSize + (subtextFontSize//2) + ((poolNumber - 1) * subtextFontSize)
            vicarioustext.drawtoplefttext(self.draw, f"{poolLabel}", subtextFontSize, left+subtextPadding, y, ImageColor.getrgb(poolLabelColor))
            poolStatusColor = self.textColor
            if poolStatus != "Alive": poolStatusColor = self.warningTextColor
            vicarioustext.drawtoprighttext(self.draw, f"{poolStatus}", subtextFontSize, left+width, y, ImageColor.getrgb(poolStatusColor))
            highestY = y
        vicarioustext.drawtoplefttext(self.draw, "Pools: ", groupFontSize, left, top, ImageColor.getrgb(self.textColor), True)
        sectionHeight = highestY + subtextFontSize - top
        return sectionHeight

    def _renderStatus(self, miner, left, top, width):
        groupFontSize = int(self.height * 16/320)
        subtextFontSize = int(self.height * 12/320)
        subtextPadding = int(self.height * 5/320)
        vicarioustext.drawtoplefttext(self.draw, "Status: ", groupFontSize, left, top, ImageColor.getrgb(self.textColor), True)
        y = top + groupFontSize + subtextPadding
        y2 = y + subtextFontSize + subtextPadding
        statusColor = self.textColor
        statusText = self.Status[0]
        if self.StatusType == "Warning":
            self.draw.rectangle(xy=[(left,y),(left+width,y2)],fill=ImageColor.getrgb(self.warningStatusBackgroundColor))
            statusColor = self.warningStatusTextColor
            statusText = self.Status[1]
        vicarioustext.drawlefttext(self.draw, statusText, subtextFontSize, left, (y2+y)//2, ImageColor.getrgb(statusColor), True)
        sectionHeight = y2 + subtextFontSize - top
        return sectionHeight

    def run(self):

        borderPad = 5
        col1Width = int((self.width - (borderPad * 3)) * .35)
        col2Width = int((self.width - (borderPad * 3)) * .65)
        col1Left = borderPad
        col2Left = self.width - borderPad - col2Width

        minerNumber = 0
        minersProcessed = 0
        for miner in self.miners:
            minerNumber += 1
            if "enabled" not in miner: continue
            if not miner["enabled"]: continue
            self.Status = ["Stable"]
            self.StatusType = "Normal"
            defaultHeaderText = self.headerText
            self.pageSuffix = miner["address"] if "address" in miner else f"miner{minerNumber}"
            self.headerText = miner["headerText"] if "headerText" in miner else defaultHeaderText
            super().startImage()
            col1Top = self.getInsetTop()
            sectionHeight = self._renderPower(miner, col1Left, col1Top, col1Width)
            col1Top += sectionHeight + borderPad
            sectionHeight = self._renderBoards(miner, col1Left, col1Top, col1Width)
            col1Top += sectionHeight + borderPad
            sectionHeight = self._renderFans(miner, col1Left, col1Top, col1Width)
            col1Top += sectionHeight + borderPad
            col2Top = self.getInsetTop()
            sectionHeight = self._renderHashrate(miner, col2Left, col2Top, col2Width)
            col2Top += sectionHeight + borderPad
            sectionHeight = self._renderPools(miner, col2Left, col2Top, col2Width)
            col2Top += sectionHeight + borderPad
            statusTop = max(col1Top, col2Top)
            sectionHeight = self._renderStatus(miner, col1Left, statusTop, self.width - (borderPad*2))
            super().finishImage()
            minersProcessed += 1
            self.headerText = defaultHeaderText
        
        if minersProcessed == 0:
            self.log(f"No miners were processed")
            super()._markAsRan()

# --------------------------------------------------------------------------------------
# Entry point if running this script directly
# --------------------------------------------------------------------------------------

if __name__ == '__main__':

    p = MinerPanel()

    # If arguments were passed in, treat as a single run
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h','--help']:
            print(f"Prepares an image depicting the upcoming blocks and fees in the Mempool")
            print(f"Usage:")
            print(f"1) Call without arguments to run continuously using the configuration or defaults")
            print(f"2) Passing any arguments other then -h or --help will run once and exit")
        else:
            p.fetchData()
            p.run()
        exit(0)

    # Continuous run
    p.runContinuous()