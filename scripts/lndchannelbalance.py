#! /usr/bin/env python3
from PIL import ImageColor
from datetime import datetime
from vicariouspanel import NodeyezPanel
import math
import sys
import vicariousbitcoin
import vicarioustext

class LNDChannelBalancePanel(NodeyezPanel):

    def __init__(self):
        """Instantiates a new LND Channel Balance panel"""

        # Define which additional attributes we have
        self.configAttributes = {
            # legacy key name mappings
            "colorBackground": "backgroundColor",
            "colorBarEmpty": "barEmptyColor",
            "colorBarFilled": "barFilledColor",
            "colorBarOutline": "barOutlineColor",
            "colorNodeDead": "nodeDeadColor",
            "colorNodeOffline": "nodeOfflineColor",
            "colorTextFG": "textColor",
            "displayBalances": "displayBalancesEnabled",
            "sleepInterval": "interval",
            # panel specific key names
            "barEmptyColor": "barEmptyColor",
            "barFilledColor": "barFilledColor",
            "barOutlineColor": "barOutlineColor",
            "displayBalancesEnabled": "displayBalancesEnabled",
            "nodeDeadColor": "nodeDeadColor",
            "nodeOfflineColor": "nodeOfflineColor",
            "nodes": "nodes",
            "pageSize": "pageSize",
        }

        # Define our defaults (all panel specific key names should be listed)
        self._defaultattr("barEmptyColor", "#ffa500")
        self._defaultattr("barFilledColor", "#008000")
        self._defaultattr("barOutlineColor", "#808080")
        self._defaultattr("displayBalancesEnabled", True)
        self._defaultattr("headerText", "Lightning Channel Balance")
        self._defaultattr("interval", 1800)
        self._defaultattr("nodeDeadColor", "#ff0000")
        self._defaultattr("nodeOfflineColor", "#ffa500")
        self._defaultattr("nodes", [{}])
        self._defaultattr("pageSize", 8)
        self._defaultattr("watermarkAnchor", "bottom")
    
        # Initialize
        super().__init__(name="lndchannelbalance")

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

    def run(self):

        aliasWidth = self.width // 3
        utcnow = datetime.utcnow()
        dataRowPadding = 4
        outlineWidth = 2
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
                subHeaderFontSize = int((dataRowHeight / 3 * 2) - 2)
                subHeaderFontSize -= subHeaderFontSize % 2
                y = self.getInsetTop() + (dataRowHeight // 2)
                vicarioustext.drawlefttext(self.draw, "Peer Alias", subHeaderFontSize, 0, y, ImageColor.getrgb(self.textColor), True)
                vicarioustext.drawlefttext(self.draw, "Local Balance", subHeaderFontSize, aliasWidth, y, ImageColor.getrgb(self.textColor), True)
                vicarioustext.drawrighttext(self.draw, "Remote Balance", subHeaderFontSize, self.width, y, ImageColor.getrgb(self.textColor), True)
                # draw node channels
                nodeFontSize = int(subHeaderFontSize * .90)
                nodeFontSize -= nodeFontSize % 2
                firstIndex = ((self.pageNumber - 1) * self.pageSize)
                lastIndex = (firstIndex + self.pageSize) - 1
                if lastIndex > channelCount - 1: lastIndex = channelCount - 1
                channelsRendered = 0
                if lastIndex > -1:
                    for channelIndex in range(firstIndex, (lastIndex+1)):
                        channelsRendered += 1
                        channel = node["channels"][channelIndex]
                        capacity = int(channel["capacity"])
                        local_balance = int(channel["local_balance"])
                        remote_balance = int(channel["remote_balance"])
                        remote_alias = channel["remote_alias"]
                        nodecolor = self.textColor if channel["active"] else self.nodeOfflineColor
                        if not channel["active"]:
                            remote_updated = channel["remote_updated"]
                            remote_updateddate = datetime.fromtimestamp(remote_updated)
                            csvdelay = int(channel["csv_delay"])
                            daysold = utcnow - remote_updateddate
                            csvrisk = (daysold.days * 144) > csvdelay
                            csvrisks = "-risk" if csvrisk else ""
                            remote_alias = "(" + str(daysold.days) + "d" + csvrisks + ")" + remote_alias
                            if daysold.days >= 5 or csvrisk: nodecolor = self.nodeDeadColor
                        dataRowTop = self.getInsetTop() + (channelsRendered * dataRowHeight)
                        dataRowBottom = dataRowTop + dataRowHeight
                        # alias
                        vicarioustext.drawlefttext(self.draw, remote_alias, nodeFontSize, 0, dataRowTop + (dataRowHeight//2), ImageColor.getrgb(nodecolor))
                        # capacity bar
                        self.draw.rounded_rectangle(xy=(aliasWidth, dataRowTop+dataRowPadding, self.width-outlineWidth, dataRowBottom), radius=4, fill=ImageColor.getrgb(self.barEmptyColor), outline=ImageColor.getrgb(self.barOutlineColor), width=outlineWidth)
                        # local balance is filled portion
                        percentage = float(local_balance)/float(capacity)
                        barWidth = int(float(self.width - aliasWidth - outlineWidth) * percentage)
                        self.draw.rounded_rectangle(xy=(aliasWidth + outlineWidth, dataRowTop + dataRowPadding + outlineWidth, aliasWidth + outlineWidth + barWidth, dataRowBottom - outlineWidth), radius=3, fill=ImageColor.getrgb(self.barFilledColor))
                        # labels
                        if self.displayBalancesEnabled:
                            vicarioustext.drawlefttext(self.draw, str(local_balance), nodeFontSize, aliasWidth+outlineWidth+1, dataRowTop + (dataRowHeight//2) + outlineWidth + 1, ImageColor.getrgb(self.backgroundColor))
                            vicarioustext.drawlefttext(self.draw, str(local_balance), nodeFontSize, aliasWidth+outlineWidth,   dataRowTop + (dataRowHeight//2) + outlineWidth,     ImageColor.getrgb(self.textColor))
                            vicarioustext.drawrighttext(self.draw, str(remote_balance), nodeFontSize, self.width-outlineWidth-outlineWidth,   dataRowTop + (dataRowHeight//2) + outlineWidth + 1, ImageColor.getrgb(self.backgroundColor))
                            vicarioustext.drawrighttext(self.draw, str(remote_balance), nodeFontSize, self.width-outlineWidth-outlineWidth-1, dataRowTop + (dataRowHeight//2) + outlineWidth,     ImageColor.getrgb(self.textColor))
                # draw a line separating alias if it bleeds under balance bar
                self.draw.rectangle(xy=(aliasWidth-dataRowPadding,self.getInsetTop(),aliasWidth-1,self.getInsetTop()+self.getInsetHeight()),fill=ImageColor.getrgb(self.backgroundColor))
                # done this page of channels for this node
                super().finishImage()
            # restore header text to default
            self.headerText = defaultHeaderText

# --------------------------------------------------------------------------------------
# Entry point if running this script directly
# --------------------------------------------------------------------------------------

if __name__ == '__main__':

    p = LNDChannelBalancePanel()

    # If arguments were passed in, treat as a single run
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h','--help']:
            print(f"Generates one or more images based on the total number of lightning channels the configured node(s) have.")
            print(f"A series of images depicting the balance on each side of the channel for local and remote.")
            print(f"Usage:")
            print(f"1) Call without arguments to run continuously using the configuration or defaults")
            print(f"2) Call with an argument other then -h or --help to run once and exit")
        else:
            p.fetchData()
            p.run()
        exit(0)

    # Continuous run
    p.runContinuous()
