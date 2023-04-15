#! /usr/bin/env python3
from PIL import ImageColor
from vicariouspanel import NodeyezPanel
import math
import sys
import vicariousbitcoin
import vicarioustext

class LNDRingOfFirePanel(NodeyezPanel):

    def __init__(self):
        """Instantiates a new LND Ring of Fire panel"""

        # Define which additional attributes we have
        self.configAttributes = {
            # legacy key name mappings
            "colorBackground": "backgroundColor",
            "colorTextFG": "textColor",
            "sleepInterval": "interval",
            # panel specific key names
            "node": "node",
            "nodeOfflineBackgroundColor": "nodeOfflineBackgroundColor",
            "nodeOfflineTextColor": "nodeOfflineTextColor",
            "nodeOnlineBackgroundColor": "nodeOnlineBackgroundColor",
            "nodeOnlineTextColor": "nodeOnlineTextColor",
            "ringColor": "ringColor",
            "rings": "rings",
        }

        # Define our defaults (all panel specific key names should be listed)
        self._defaultattr("headerText", "Lightning Ring of Fire")
        self._defaultattr("interval", 900)
        self._defaultattr("nodeOfflineBackgroundColor", "#ff1010")  # coloroffline
        self._defaultattr("nodeOfflineTextColor", "#ffffff")        # colorofflinetext
        self._defaultattr("nodeOnlineBackgroundColor", "#20ff20")   # coloronline
        self._defaultattr("nodeOnlineTextColor", "#000000")         # coloronlinetext
        self._defaultattr("ringColor", "#202020")                   # colorcircle
        self._defaultattr("rings", [])
        self._defaultattr("watermarkAnchor", "bottomleft")

        if vicariousbitcoin.lndMode == "REST":
            self.node = vicariousbitcoin.lndRESTOptions
        else:
            self.node = None

        # Initialize
        super().__init__(name="lndringoffire")

    def fetchData(self):
        """Fetches all the data needed for this panel"""

        for ring in self.rings:
            if "enabled" not in ring: continue
            if not ring["enabled"]: continue
            if "nodes" not in ring: continue
            for node in ring["nodes"]:
                remotePubkey = node["pubkey"]
                node["nodeinfo"] = vicariousbitcoin.lndGetNodeInfo(remotePubkey, self.node)

    def _getRingConfigValue(self, ring, key):
        if key in ring:
            return ring[key]
        else:
            return self.__getattribute__(key)

    def _getXYByNodeNumber(self, nodeNumber, totalNodes, center, radius):
        degrees=360/totalNodes
        degreeso=-90+(degrees/2)
        angle=nodeNumber*degrees-degreeso
        x = center[0] + radius * math.cos(angle * math.pi / 180)
        y = center[1] + radius * math.sin(angle * math.pi / 180)
        return x, y

    def _getNodeNumberForPubKey(self, ring, pubKey):
        if "nodes" not in ring:
            return -1
        nodeNumber = 0
        for node in ring["nodes"]:
            nodeNumber += 1
            # check in config
            if "pubkey" in node:
                if pubKey == node["pubkey"]:
                    return nodeNumber
            # iterate live return data (why would this differ?)
            if "nodeinfo" not in node:
                continue
            nodeinfo = node["nodeinfo"]
            if "node" not in nodeinfo:
                continue
            nodePubKey = nodeinfo["node"]["pub_key"]
            if pubKey == nodePubKey:
                return nodeNumber
        return -1
        
    def _getConnectedNodes(self, ring):
        connections = []
        if "nodes" not in ring:
            return connections
        nodeNumber = 0
        nodeCount = len(ring["nodes"])
        for node in ring["nodes"]:
            nodeNumber += 1
            if "nodeinfo" not in node:
                continue
            nodeinfo = node["nodeinfo"]
            if "channels" not in nodeinfo:
                continue
            if "node" not in nodeinfo:
                continue
            nodePubKey = nodeinfo["node"]["pub_key"]
            channels = nodeinfo["channels"]
            for channel in channels:
                pub1 = channel["node1_pub"]
                pub2 = channel["node2_pub"]
                otherPubKey = pub2 if pub1 == nodePubKey else pub1
                otherNodeNumber = self._getNodeNumberForPubKey(ring, otherPubKey)
                if otherNodeNumber > 0 and otherNodeNumber != nodeNumber:
                    connections.append([nodeNumber,otherNodeNumber])
        return connections

    def run(self):

        ringNumber = 0
        for ring in self.rings:
            ringNumber += 1
            if "enabled" not in ring: continue
            if not ring["enabled"]: continue
            if "nodes" not in ring: continue

            # start this ring image
            defaultHeaderText = self.headerText
            headerText = self._getRingConfigValue(ring, "headerText")
            self.headerText = headerText
            ringID = ring["id"] if "id" in ring else ringNumber
            self.pageSuffix = f"{ringID}"
            super().startImage()

            # set ring colors
            nodeOfflineBackgroundColor = self._getRingConfigValue(ring, "nodeOfflineBackgroundColor")
            nodeOfflineTextColor = self._getRingConfigValue(ring, "nodeOfflineTextColor")
            nodeOnlineBackgroundColor = self._getRingConfigValue(ring, "nodeOnlineBackgroundColor")
            nodeOnlineTextColor = self._getRingConfigValue(ring, "nodeOnlineTextColor")
            ringColor = self._getRingConfigValue(ring, "ringColor")

            # draw the main ring
            ringPadding = self.getInsetHeight() // 10
            ringThickness = int(self.height * 10/320)
            ringTop = self.getInsetTop() + ringPadding - ringThickness//2
            ringBottom = self.getInsetTop() + self.getInsetHeight() - ringPadding + ringThickness//2
            ringHeight = ringBottom - ringTop
            ringLeft = (self.width - ringHeight) // 2
            ringRight = ringLeft + ringHeight
            ringRadius = ringHeight / 2
            ringCenterX = ringLeft + ringRadius
            ringCenterY = ringTop + ringRadius
            ringCenter = (ringCenterX, ringCenterY)
            self.draw.ellipse(xy=(ringLeft, ringTop, ringRight, ringBottom), outline=ImageColor.getrgb(ringColor), width=ringThickness)

            # draw the connected nodes
            connections = self._getConnectedNodes(ring)
            nodeCount = len(ring["nodes"])
            for connection in connections:
                node0X, node0Y = self._getXYByNodeNumber(connection[0], nodeCount, ringCenter, ringRadius)
                node1X, node1Y = self._getXYByNodeNumber(connection[1], nodeCount, ringCenter, ringRadius)                
                self.draw.line(xy=(node0X,node0Y,node1X,node1Y),fill=ImageColor.getrgb(nodeOnlineBackgroundColor),width=ringThickness//2)

            # draw the nodes and their online status
            nodeNumber = 0
            nodeRadius = (ringPadding*4)//5
            for node in ring["nodes"]:
                nodeNumber += 1
                nodeinfo = node["nodeinfo"]
                nodealias = vicariousbitcoin.lndGetNodeAliasFromNodeInfo(nodeinfo)
                if nodealias == "":
                    if "operator" in node: 
                        nodealias = node["operator"]
                    else:
                        nodealias = vicariousbitcoin.lndCreateMockAliasForPubkey(node["pubkey"])
                nodeOnline = False
                lastUpdated = 0
                if "node" in nodeinfo:
                    if "last_update" in nodeinfo["node"]:
                        lastUpdated = nodeinfo["node"]["last_update"]
                nodeOnline = lastUpdated > 0
                nodeBackgroundColor = nodeOnlineBackgroundColor if nodeOnline else nodeOfflineBackgroundColor
                nodeTextColor = nodeOnlineTextColor if nodeOnline else nodeOfflineTextColor
                node0X, node0Y = self._getXYByNodeNumber(nodeNumber, nodeCount, ringCenter, ringRadius)
                fs = int(self.height * 16/320)
                # node circle
                self.draw.ellipse(xy=(node0X-nodeRadius,node0Y-nodeRadius,node0X+nodeRadius,node0Y+nodeRadius), fill=ImageColor.getrgb(nodeBackgroundColor), outline=ImageColor.getrgb(ringColor), width=1)
                # node number
                vicarioustext.drawcenteredtext(self.draw, f"{nodeNumber}", fs, node0X, node0Y, ImageColor.getrgb(nodeTextColor), True)
                # node alias label (left or right side)
                if nodeNumber <= nodeCount // 2:
                    vicarioustext.drawrighttext(self.draw, nodealias, fs, node0X-ringPadding, node0Y, ImageColor.getrgb(self.textColor), False)
                else:
                    vicarioustext.drawlefttext(self.draw, nodealias, fs, node0X+ringPadding, node0Y, ImageColor.getrgb(self.textColor), False)

            # close out the ring image
            super().finishImage()
            self.headerText = defaultHeaderText

# --------------------------------------------------------------------------------------
# Entry point if running this script directly
# --------------------------------------------------------------------------------------

if __name__ == '__main__':

    p = LNDRingOfFirePanel()

    # If arguments were passed in, treat as a single run
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h','--help']:
            print(f"Prepares images depicting the status of Lightning Ring of Fire setups")
            print(f"Usage:")
            print(f"1) Call without arguments to run continuously using the configuration or defaults")
            print(f"2) Passing any arguments other then -h or --help will run once and exit")
        else:
            p.fetchData()
            p.run()
        exit(0)

    # Continuous run
    p.runContinuous()