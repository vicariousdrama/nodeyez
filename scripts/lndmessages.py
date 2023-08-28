#! /usr/bin/env python3
from PIL import ImageColor
from datetime import datetime
from vicariouspanel import NodeyezPanel
import base64
import math
import qrcode
import sys
import time
import vicariousbitcoin
import vicarioustext

class LNDMessagesPanel(NodeyezPanel):

    def __init__(self):
        """Instantiates a new LND Messages panel"""

        # Define which additional attributes we have
        self.configAttributes = {
            # legacy key name mappings
            "colorBackground": "backgroundColor",
            "colorTextFG": "textColor",
            "sleepInterval": "interval",
            # panel specific key names
            "dataRowEvenBackgroundColor": "dataRowEvenBackgroundColor",
            "dataRowEvenTextColor": "dataRowEvenTextColor",
            "dataRowHeaderBackgroundColor": "dataRowHeaderBackgroundColor",
            "dataRowHeaderTextColor": "dataRowHeaderTextColor",
            "dataRowOddBackgroundColor": "dataRowOddBackgroundColor",
            "dataRowOddTextColor": "dataRowOddTextColor",
            "nodes": "nodes",
            "renderNewestFirst": "renderNewestFirst",
            "renderQRCodesForInvoices": "renderQRCodesForInvoices",
            "renderQRCodesForURLs": "renderQRCodesForURLs",
            "renderMode": "renderMode",
            "restrictToDaysAgo": "restrictToDaysAgo",
            "pageSize": "pageSize",
        }

        # Define our defaults (all panel specific key names should be listed)
        self._defaultattr("dataRowEvenBackgroundColor", "#101010")
        self._defaultattr("dataRowEvenTextColor", "#ffffff")
        self._defaultattr("dataRowHeaderBackgroundColor", "#101020")
        self._defaultattr("dataRowHeaderTextColor", "#ffffff")
        self._defaultattr("dataRowOddBackgroundColor", "#202020")
        self._defaultattr("dataRowOddTextColor", "#ffffff")
        self._defaultattr("headerText", "LND Messages Received")
        self._defaultattr("interval", 120)
        self._defaultattr("nodes", [{}])
        self._defaultattr("renderImages", 0)             # NYI not yet implemented
        self._defaultattr("renderMode", "proportional")
        self._defaultattr("renderNewestFirst", True)
        self._defaultattr("renderQRCodesForInvoices", 0) # NYI if 0 dont render as image
        self._defaultattr("renderQRCodesForURLs", 0)     # NYI else render if amount > value
        self._defaultattr("restrictToDaysAgo", 30)
        self._defaultattr("pageSize", 8)
        self._defaultattr("watermarkAnchor", "bottom")

        # Initialize
        super().__init__(name="lndmessages")

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

        timestampSince = 0
        if self.restrictToDaysAgo > 0:
            timestampSince = int(time.time()) - (self.restrictToDaysAgo * 86400)

        nodenumber = 0
        for node in self.nodes:
            nodenumber += 1
            if "enabled" not in node: continue
            if not node["enabled"]: continue
            k = "invoices"
            invoices = vicariousbitcoin.lndGetNodeInvoices(node=node,creationDateStart=timestampSince)
            if k in invoices: invoices = invoices[k]
            if "message" in invoices and invoices["message"] == "permission denied":
                self.log(f"Permission denied retrieving invoices for node number {nodenumber}. Skipping and disabling.")
                node["enabled"] = False
                continue
            messages = []
            for invoice in invoices:
                if "htlcs" not in invoice: continue
                htlcs = invoice["htlcs"]
                for htlc in htlcs:
                    if int(htlc["resolve_time"]) <= timestampSince: continue
                    if "custom_records" not in htlc: continue
                    if "34349334" not in htlc["custom_records"]: continue
                    msgBase64 = htlc["custom_records"]["34349334"]
                    msgText = base64.b64decode(msgBase64.encode("utf-8")).decode("utf-8")
                    amount = int(float(htlc["amt_msat"]) / 1000.0)
                    state = htlc["state"]
                    receiveTime = htlc["resolve_time"]
                    msg = {"text": msgText, 
                           "amount": amount, 
                           "state": state, 
                           "received": receiveTime}
                    messages.append(msg)
            if self.renderNewestFirst: messages.reverse()
            node["messages"] = messages

    def getFormattedDate(self, epochdate):
        e = int(epochdate)
        return datetime.fromtimestamp(e).strftime("%Y-%m-%d")

    def getQRCode(self, data):
        qr = qrcode.QRCode(box_size=1)
        qr.add_data(data)
        qr.make()
        img = qr.make_image()
        return img

    def renderMessagesByFixedPageSize(self, address, messages):
        messageCount = len(messages)
        self.pageSuffix = address
        self.pageCount = int(math.ceil(float(messageCount) / float(self.pageSize)))
        self.removeOldImages()
        subHeaderFontSize = int(self.height * 14/320)
        subHeaderFontSize -= subHeaderFontSize % 2
        messageFontSize = int(self.height * 12/320)
        messageFontSize -= messageFontSize % 2
        for self.pageNumber in range(1, self.pageCount+1):
            super().startImage()
            insetHeight = self.getInsetHeight()
            insetTop = self.getInsetTop()
            dataRowHeight = insetHeight // (self.pageSize + 1)
            # draw headers
            self.draw.rectangle(xy=(0,insetTop,self.width,insetTop + dataRowHeight),fill=ImageColor.getrgb(self.dataRowHeaderBackgroundColor))
            ypos = insetTop + (dataRowHeight//2)
            xpos = 0
            vicarioustext.drawlefttext(self.draw, "Date", subHeaderFontSize, xpos, ypos, ImageColor.getrgb(self.dataRowHeaderTextColor), True)
            xpos = int(self.width * .20)
            vicarioustext.drawcenteredtext(self.draw, "Sats", subHeaderFontSize, xpos, ypos, ImageColor.getrgb(self.dataRowHeaderTextColor), True)
            xpos = int(self.width * .625)
            vicarioustext.drawcenteredtext(self.draw, "Message", subHeaderFontSize, xpos, ypos, ImageColor.getrgb(self.dataRowHeaderTextColor), True)
            # draw messages
            stepping = 1
            firstIndex = ((self.pageNumber - 1) * self.pageSize)
            lastIndex = (firstIndex + self.pageSize) - 1
            if lastIndex > messageCount - 1: lastIndex = messageCount - 1
            messagesRendered = 0
            for messageIndex in range(firstIndex, (lastIndex+1), stepping):
                messagesRendered += 1
                message = messages[messageIndex]
                sDate = self.getFormattedDate(message["received"])
                amount = message["amount"]
                text = message["text"]
                dataRowTop = insetTop + (messagesRendered * dataRowHeight)
                dataRowBottom = dataRowTop + dataRowHeight
                dataRowBackgroundColor = self.dataRowEvenBackgroundColor if messagesRendered % 2 == 0 else self.dataRowOddBackgroundColor
                dataRowTextColor = self.dataRowEvenTextColor if messagesRendered % 2 == 0 else self.dataRowOddTextColor
                # background
                self.draw.rectangle(xy=(0,dataRowTop,self.width,dataRowBottom),fill=ImageColor.getrgb(dataRowBackgroundColor))
                # -- values
                ypos = dataRowTop + (dataRowHeight//2)
                xpos = 0
                vicarioustext.drawlefttext(self.draw, sDate, messageFontSize, xpos, ypos, ImageColor.getrgb(dataRowTextColor))
                xpos = int(self.width * .20)
                vicarioustext.drawcenteredtext(self.draw, f"{amount}", messageFontSize, xpos, ypos, ImageColor.getrgb(dataRowTextColor))
                amountspace = " " * (len(str(amount)) + 2) # cheap hack
                vicarioustext.drawcenteredtext(self.draw, f"{amountspace}⚡", messageFontSize+6, xpos, ypos, ImageColor.getrgb("#FFC300"), True)
                xpos = int(self.width * .25)
                vicarioustext.drawlefttext(self.draw, f"{text}", messageFontSize, xpos, ypos, ImageColor.getrgb(dataRowTextColor))
            if messageCount == 0:
                nomsg = "No messages received"
                if self.restrictToDaysAgo > 0: nomsg += f" in past {self.restrictToDaysAgo} days"
                vicarioustext.drawcenteredtext(self.draw, nomsg, messageFontSize, self.width//2, self.height//2, ImageColor.getrgb(self.textColor))                
                super().finishImage()

            # done this page of messages for this node
            super().finishImage()

    def renderMessagesByProportionalSize(self, address, messages):
        self.pageSuffix = address
        messageCount = len(messages)
        fieldHeaderFontSize = int(self.height * 14/320)
        fieldHeaderFontSize -= fieldHeaderFontSize % 2
        messageFontSize = int(self.height * 12/320)
        messageFontSize -= messageFontSize % 2
        dateFieldWidth = int(self.width * .15)
        amountFieldWidth = int(self.width * .10)
        messageFieldWidth = int(self.width * .75)

        # calculate page count
        self.pageCount = 2
        self.pageNumber = 1
        super().startImage()
        insetHeight = self.getInsetHeight()
        insetTop = self.getInsetTop()
        pageCount = 1
        pageHeaderHeight = int(fieldHeaderFontSize * 1.5)
        pageDataMaxHeight = insetHeight - pageHeaderHeight
        pageDataHeightAvailable = pageDataMaxHeight
        for message in messages:
            text = message["text"]
            wrappedText = vicarioustext.getwrappedtextatwidth(self.draw, text, messageFieldWidth, messageFontSize, False)
            wrappedTextWidth, wrappedTextHeight, _ = vicarioustext.gettextdimensions(self.draw, wrappedText, messageFontSize, False)
            wrappedTextHeight = max(wrappedTextHeight, 16)
            message["text"] = wrappedText
            message["width"] = wrappedTextWidth
            message["height"] = wrappedTextHeight
            if pageDataHeightAvailable >= wrappedTextHeight:
                # use space on current page
                pageDataHeightAvailable -= wrappedTextHeight
                message["page"] = pageCount
            else:
                # new page
                pageCount += 1
                pageDataHeightAvailable = pageDataMaxHeight
                message["page"] = pageCount
                # check if fits
                if wrappedTextHeight > pageDataMaxHeight:
                    # it will take whole page
                    pageCount += 1
                else:
                    # use space on the new page
                    pageDataHeightAvailable -= wrappedTextHeight
        self.pageCount = pageCount
        self._cleanupResources()
        self.removeOldImages()

        # render the pages
        for self.pageNumber in range(1, self.pageCount+1):
            super().startImage()
            # draw headers
            self.draw.rectangle(xy=(0,insetTop,self.width,insetTop + pageHeaderHeight),fill=ImageColor.getrgb(self.dataRowHeaderBackgroundColor))
            ypos = insetTop + (pageHeaderHeight//2)
            xpos = dateFieldWidth // 2
            vicarioustext.drawcenteredtext(self.draw, "Date", fieldHeaderFontSize, xpos, ypos, ImageColor.getrgb(self.dataRowHeaderTextColor), True)
            xpos = dateFieldWidth + (amountFieldWidth // 2)
            vicarioustext.drawcenteredtext(self.draw, "Sats", fieldHeaderFontSize, xpos, ypos, ImageColor.getrgb(self.dataRowHeaderTextColor), True)
            xpos = dateFieldWidth + amountFieldWidth + (messageFieldWidth // 2)
            vicarioustext.drawcenteredtext(self.draw, "Message", fieldHeaderFontSize, xpos, ypos, ImageColor.getrgb(self.dataRowHeaderTextColor), True)
            # draw messages
            ypos = insetTop + pageHeaderHeight
            messageNumber = 0
            for message in messages:
                messageNumber += 1
                if message["page"] < self.pageNumber: 
                    # not yet on the page we're rendering
                    continue
                if message["page"] > self.pageNumber: 
                    # all messages from this point on will be on future pages.
                    # finish the image and stop checking messages
                    super().finishImage()
                    break
                messageHeight = message["height"]
                sDate = self.getFormattedDate(message["received"])
                amount = message["amount"]
                text = message["text"]
                dataRowTop = ypos
                dataRowBottom = ypos + messageHeight
                dataRowBackgroundColor = self.dataRowEvenBackgroundColor if messageNumber % 2 == 0 else self.dataRowOddBackgroundColor
                dataRowTextColor = self.dataRowEvenTextColor if messageNumber % 2 == 0 else self.dataRowOddTextColor
                # background
                self.draw.rectangle(xy=(0,dataRowTop,self.width,dataRowBottom),fill=ImageColor.getrgb(dataRowBackgroundColor))
                # -- values
                xpos = 0
                vicarioustext.drawtoplefttext(self.draw, f"{sDate}", messageFontSize, xpos, ypos, ImageColor.getrgb(dataRowTextColor))
                xpos = dateFieldWidth + (amountFieldWidth // 2)
                vicarioustext.drawtoptext(self.draw, f"{amount}", messageFontSize, xpos, ypos, ImageColor.getrgb(dataRowTextColor))
                amountspace = " " * (len(str(amount)) + 2) # cheap hack
                vicarioustext.drawtoptext(self.draw, f"{amountspace}⚡", messageFontSize+2, xpos, ypos, ImageColor.getrgb("#FFC300"), True)
                xpos = dateFieldWidth + amountFieldWidth
                vicarioustext.drawtoplefttext(self.draw, f"{text}", messageFontSize, xpos, ypos, ImageColor.getrgb(dataRowTextColor))
                ypos += messageHeight
                # last message, finish the image
                if messageNumber == messageCount: super().finishImage()
            if messageNumber == 0:
                nomsg = "No messages received"
                if self.restrictToDaysAgo > 0: nomsg += f" in past {self.restrictToDaysAgo} days"
                vicarioustext.drawcenteredtext(self.draw, nomsg, messageFontSize, self.width//2, self.height//2, ImageColor.getrgb(self.textColor))                
                super().finishImage()

    def run(self):
        for node in self.nodes:
            if "enabled" not in node: continue
            if not node["enabled"]: continue
            if "messages" not in node: continue
            defaultHeaderText = self.headerText
            if "headerText" in node: self.headerText = node["headerText"]
            if self.renderMode == "fixedheight":
                self.renderMessagesByFixedPageSize(node["address"], node["messages"])
            else: # default
                self.renderMessagesByProportionalSize(node["address"], node["messages"])
            self.headerText = defaultHeaderText

# --------------------------------------------------------------------------------------
# Entry point if running this script directly
# --------------------------------------------------------------------------------------

if __name__ == '__main__':

    p = LNDMessagesPanel()

    # If arguments were passed in, treat as a single run
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h','--help']:
            print(f"Displays messages received via invoices or keysend payments")
            print(f"Usage:")
            print(f"1) Call without arguments to run continuously using the configuration or defaults")
            print(f"2) Call with an argument other then -h or --help to run once and exit")
        else:
            p.fetchData()
            p.run()
        exit(0)

    # Continuous run
    p.runContinuous()