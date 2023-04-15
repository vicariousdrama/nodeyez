#! /usr/bin/env python3
from PIL import ImageColor
from datetime import datetime
from vicariouspanel import NodeyezPanel
import math
import sys
import vicariousbitcoin
import vicarioustext

class LNDChannelFeesPanel(NodeyezPanel):

    def __init__(self):
        """Instantiates a new LND Channel Fees panel"""

        # Define which additional attributes we have
        self.configAttributes = {
            # legacy key name mappings
            "colorBackground": "backgroundColor",
            "colorNodeDead": "nodeDeadColor",
            "colorNodeOffline": "nodeOfflineColor",
            "colorRowBG1": "dataRowEvenBackgroundColor",
            "colorRowBG2": "dataRowOddBackgroundColor",
            "colorRowFG1": "dataRowEvenTextColor",
            "colorRowFG2": "dataRowOddTextColor",
            "colorTextFG": "textColor",
            "sleepInterval": "interval",
            # panel specific key names
            "dataRowEvenBackgroundColor": "dataRowEvenBackgroundColor",
            "dataRowEvenTextColor": "dataRowEvenTextColor",
            "dataRowHeaderBackgroundColor": "dataRowHeaderBackgroundColor",
            "dataRowHeaderTextColor": "dataRowHeaderTextColor",
            "dataRowOddBackgroundColor": "dataRowOddBackgroundColor",
            "dataRowOddTextColor": "dataRowOddTextColor",
            "nodeDeadColor": "nodeDeadColor",
            "nodeOfflineColor": "nodeOfflineColor",
            "nodes": "nodes",
            "pageSize": "pageSize",
        }

        # Define our defaults (all panel specific key names should be listed)
        self._defaultattr("dataRowEvenBackgroundColor", "#101010")
        self._defaultattr("dataRowEvenTextColor", "#ffffff")
        self._defaultattr("dataRowHeaderBackgroundColor", "#101020")
        self._defaultattr("dataRowHeaderTextColor", "#ffffff")
        self._defaultattr("dataRowOddBackgroundColor", "#202020")
        self._defaultattr("dataRowOddTextColor", "#ffffff")
        self._defaultattr("headerText", "Channel Usage, Fees and Earnings")
        self._defaultattr("interval", 1800)
        self._defaultattr("nodeDeadColor", "#ff0000")
        self._defaultattr("nodeOfflineColor", "#ffa500")
        self._defaultattr("nodes", [{}])
        self._defaultattr("pageSize", 8)
        self._defaultattr("watermarkAnchor", "bottom")
    
        # Initialize
        super().__init__(name="lndchannelfees")
        
        # Populate node config from rest definitions
        self.updateNodeConfigFromProfiles()

    def updateNodeConfigFromProfiles(self):
        lndRESTProfiles=vicariousbitcoin.loadJSONData("../config/lnd-rest.json")
        if "profiles" not in lndRESTProfiles: return
        if "profiles" in lndRESTProfiles: lndRESTProfiles = lndRESTProfiles["profiles"]
        nodenumber = 0
        for node in self.nodes:
            nodenumber += 1
            if "enabled" not in node: continue
            if not node["enabled"]: continue
            if "profileName" not in node: 
                self.log(f"Node #{nodenumber} has no profile configured, disabling")
                node["enabled"] = False
                continue
            pn = node["profileName"]
            found = False
            for profile in lndRESTProfiles:
                if "name" in profile and profile["name"] == pn:
                    found = True
                    if "address" in profile: node["address"] = profile["address"]
                    if "macaroon" in profile: node["macaroon"] = profile["macaroon"]
                    if "port" in profile: node["port"] = profile["port"]
                    if "useTor" in profile: node["useTor"] = profile["useTor"]
                    break
            if not found:
                self.log(f"Node #{nodenumber} has profile that is not found in lnd-rest.json, disabling")
                node["enabled"] = False
                continue

    def fetchData(self):
        """Fetches all the data needed for this panel"""

        for node in self.nodes:
            if "enabled" not in node: continue
            if not node["enabled"]: continue
            k = "channels"
            node[k] = vicariousbitcoin.lndGetNodeChannels(node)
            if k in node[k]: node[k] = node[k][k]
            for channel in node["channels"]:
                if "remote_pubkey" not in channel: continue
                remote_pubkey = channel["remote_pubkey"]
                isactive = channel["active"] if "active" in channel else False
                if isactive:
                    channel["remote_alias"] = vicariousbitcoin.lndGetNodeAliasFromPubkey(remote_pubkey, node)
                else:
                    remoteinfo = vicariousbitcoin.lndGetNodeInfo(remote_pubkey, node)
                    remote_alias = vicariousbitcoin.lndGetNodeAliasFromNodeInfo(remoteinfo)
                    vicariousbitcoin.pubkey_alias[remote_pubkey] = remote_alias
                    channel["remote_alias"] = remote_alias
                    channel["remote_updated"] = remoteinfo["node"]["last_update"]
            k = "forwarding_events"
            node[k] = vicariousbitcoin.lndGetNodeForwardingHistory(node=node)
            if k in node[k]: node[k] = node[k][k]
            k = "payments"
            node[k] = vicariousbitcoin.lndGetNodePayments(node)
            if k in node[k]: node[k] = node[k][k]

    def _getSumOfChannelEarnings(self, node, channelID):
        eventCount, eventSum = 0, 0
        for event in node["forwarding_events"]:
            if str(event["chan_id_out"]) == str(channelID):
                eventCount += 1
                eventSum += int(event["fee"])
        return eventCount, eventSum

    def _getSumOfChannelPayments(self, node, channelID):
        eventCount, eventSum = 0, 0
        for event in node["payments"]:
            if "status" not in event: continue
            if event["status"] != "SUCCEEDED": continue
            if "htlcs" not in event: continue
            for htlc in event["htlcs"]:
                if "route" not in htlc: continue
                route = htlc["route"]
                if "hops" not in route: continue
                hops = route["hops"]
                if len(hops) == 0: continue
                firsthop = hops[0]
                if "chan_id" not in firsthop: continue
                if str(firsthop["chan_id"]) == str(channelID):
                    eventCount += 1
                    if "fee" in event: eventSum += int(event["fee"])
        return eventCount, eventSum

    def run(self):

        aliasWidth = self.width // 3
        utcnow = datetime.utcnow()
        dataRowPadding = 4
        for node in self.nodes:
            if "enabled" not in node: continue
            if not node["enabled"]: continue
            if "channels" not in node: continue
            defaultHeaderText = self.headerText
            if "headerText" in node: self.headerText = node["headerText"]
            channelCount = len(node["channels"])
            self.pageSuffix = node["address"]
            self.pageCount = int(math.ceil(float(channelCount) / float(self.pageSize)))
            self.removeOldImages()
            # pages of channels for this node
            for self.pageNumber in range(1, self.pageCount+1):
                super().startImage()
                dataRowHeight = self.getInsetHeight() // (self.pageSize + 1)
                # draw headers
                self.draw.rectangle(xy=(0,self.getInsetTop(),self.width,self.getInsetTop() + dataRowHeight),fill=ImageColor.getrgb(self.dataRowHeaderBackgroundColor))
                subHeaderFontSize = int(self.height * 12/320)
                subHeaderFontSize -= subHeaderFontSize % 2
                headery = self.getInsetTop() + subHeaderFontSize//2
                headerx = 0
                vicarioustext.drawlefttext(self.draw, "Peer Alias", subHeaderFontSize, headerx, headery, ImageColor.getrgb(self.dataRowHeaderTextColor), True)
                headerx = int(self.width * .44)
                vicarioustext.drawcenteredtext(self.draw, "Ratio", subHeaderFontSize, headerx, headery, ImageColor.getrgb(self.dataRowHeaderTextColor), True)
                headerx = int(self.width * .66)
                vicarioustext.drawcenteredtext(self.draw, "Sends", subHeaderFontSize, headerx, headery, ImageColor.getrgb(self.dataRowHeaderTextColor), True)
                headerx = int(self.width * .88)
                vicarioustext.drawcenteredtext(self.draw, "Forwards", subHeaderFontSize, headerx, headery, ImageColor.getrgb(self.dataRowHeaderTextColor), True)
                headery += subHeaderFontSize
                subHeaderFontSize -= 2
                headerx = int(self.width * .385)
                vicarioustext.drawcenteredtext(self.draw, "Receive", subHeaderFontSize, headerx, headery, ImageColor.getrgb(self.dataRowHeaderTextColor), True)
                headerx = int(self.width * .495)
                vicarioustext.drawcenteredtext(self.draw, "Sent", subHeaderFontSize, headerx, headery, ImageColor.getrgb(self.dataRowHeaderTextColor), True)
                headerx = int(self.width * .605)
                vicarioustext.drawcenteredtext(self.draw, "#", subHeaderFontSize, headerx, headery, ImageColor.getrgb(self.dataRowHeaderTextColor), True)
                headerx = int(self.width * .715)
                vicarioustext.drawcenteredtext(self.draw, "Fees", subHeaderFontSize, headerx, headery, ImageColor.getrgb(self.dataRowHeaderTextColor), True)
                headerx = int(self.width * .825)
                vicarioustext.drawcenteredtext(self.draw, "#", subHeaderFontSize, headerx, headery, ImageColor.getrgb(self.dataRowHeaderTextColor), True)
                headerx = int(self.width * .935)
                vicarioustext.drawcenteredtext(self.draw, "Earned", subHeaderFontSize, headerx, headery, ImageColor.getrgb(self.dataRowHeaderTextColor), True)
                # draw node channels
                nodeFontSize = subHeaderFontSize + 2
                firstIndex = ((self.pageNumber - 1) * self.pageSize)
                lastIndex = (firstIndex + self.pageSize) - 1
                if lastIndex > channelCount - 1: lastIndex = channelCount - 1
                channelsRendered = 0
                for channelIndex in range(firstIndex, (lastIndex+1)):
                    channelsRendered += 1
                    channel = node["channels"][channelIndex]
                    chan_id = channel["chan_id"]
                    capacity = int(channel["capacity"])
                    total_satoshis_sent = int(channel["total_satoshis_sent"])
                    total_satoshis_received = int(channel["total_satoshis_received"])
                    sent_ratio = str(int((float(total_satoshis_sent) / float(capacity)) * 100)) + "%"
                    receive_ratio = str(int((float(total_satoshis_received) / float(capacity)) * 100)) + "%"
                    earncount, earnfees = self._getSumOfChannelEarnings(node, chan_id)
                    paycount, payfees = self._getSumOfChannelPayments(node, chan_id)
                    remote_alias = channel["remote_alias"]
                    dataRowTop = self.getInsetTop() + (channelsRendered * dataRowHeight)
                    dataRowBottom = dataRowTop + dataRowHeight
                    dataRowBackgroundColor = self.dataRowEvenBackgroundColor if channelsRendered % 2 == 0 else self.dataRowOddBackgroundColor
                    dataRowTextColor = self.dataRowEvenTextColor if channelsRendered % 2 == 0 else self.dataRowOddTextColor
                    nodecolor = dataRowTextColor if channel["active"] else self.nodeOfflineColor
                    if not channel["active"]:
                        remote_updated = channel["remote_updated"]
                        remote_updateddate = datetime.fromtimestamp(remote_updated)
                        csvdelay = int(channel["csv_delay"])
                        daysold = utcnow - remote_updateddate
                        csvrisk = (daysold.days * 144) > csvdelay
                        csvrisks = "-risk" if csvrisk else ""
                        remote_alias = "(" + str(daysold.days) + "d" + csvrisks + ")" + remote_alias
                        if daysold.days >= 5 or csvrisk: nodecolor = self.nodeDeadColor 
                    # background
                    self.draw.rectangle(xy=(0,dataRowTop,self.width,dataRowBottom),fill=ImageColor.getrgb(dataRowBackgroundColor))
                    # -- values
                    centery = dataRowTop + (dataRowHeight//2)
                    # alias
                    vicarioustext.drawlefttext(self.draw, remote_alias, nodeFontSize, 0, centery, ImageColor.getrgb(nodecolor))
                    self.draw.rectangle(xy=(aliasWidth-dataRowPadding,dataRowTop,self.width,dataRowBottom),fill=ImageColor.getrgb(dataRowBackgroundColor))
                    # ratio receive
                    centerx = int(self.width * .40)
                    vicarioustext.drawrighttext(self.draw, receive_ratio, nodeFontSize, centerx, centery, ImageColor.getrgb(dataRowTextColor))
                    # ratio sent
                    centerx = int(self.width * .50)
                    vicarioustext.drawrighttext(self.draw, sent_ratio, nodeFontSize, centerx, centery, ImageColor.getrgb(dataRowTextColor))
                    # send events
                    if paycount > 0:
                        centerx = int(self.width * .605)
                        vicarioustext.drawcenteredtext(self.draw, str(paycount), nodeFontSize, centerx, centery, ImageColor.getrgb(dataRowTextColor))
                    # send fees
                    if payfees > 0:
                        centerx = int(self.width * .74)
                        vicarioustext.drawrighttext(self.draw, str(payfees), nodeFontSize, centerx, centery, ImageColor.getrgb(dataRowTextColor))
                    # forward events
                    if earncount > 0:
                        centerx = int(self.width * .825)
                        vicarioustext.drawcenteredtext(self.draw, str(earncount), nodeFontSize, centerx, centery, ImageColor.getrgb(dataRowTextColor))
                    # forward earned
                    if earnfees > 0:
                        centerx = int(self.width * .98)
                        vicarioustext.drawrighttext(self.draw, str(earnfees), nodeFontSize, centerx, centery, ImageColor.getrgb(dataRowTextColor))
                # done this page of channels for this node
                super().finishImage()
            # restore header text to default
            self.headerText = defaultHeaderText               

# --------------------------------------------------------------------------------------
# Entry point if running this script directly
# --------------------------------------------------------------------------------------

if __name__ == '__main__':

    p = LNDChannelFeesPanel()

    # If arguments were passed in, treat as a single run
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h','--help']:
            print(f"Generates one or more images based on the total number of lightning channels the configured nodes have.")
            print(f"A series of images depicting the ratio of value received and sent compared to channel capacity, number of forwarding events and fees collected.")
            print(f"Usage:")
            print(f"1) Call without arguments to run continuously using the configuration or defaults")
            print(f"2) Call with an argument other then -h or --help to run once and exit")
        else:
            p.fetchData()
            p.run()
        exit(0)

    # Continuous run
    p.runContinuous()