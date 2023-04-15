#! /usr/bin/env python3
from PIL import ImageColor
from datetime import datetime
from vicariouspanel import NodeyezPanel
import json
import math
import redis
import sys
import vicarioustext

class LNDHubPanel(NodeyezPanel):

    def __init__(self):
        """Instantiates a new LND Hub panel"""

        # Define which additional attributes we have
        self.configAttributes = {
            # legacy key name mappings
            "colorAttribution": "attributionColor",
            "colorBackground": "backgroundColor",
            "colorLine": "lineColor",
            "colorTextDark": "userDetailsTextColor",
            "colorTextFG": "textColor",
            "enableLogDetails": "logDetailsEnabled",
            "enableUserDetails": "userDetailsEnabled",
            "sleepInterval": "interval",
            # panel specific key names
            "attributionColor": "attributionColor",
            "lineColor": "lineColor",
            "logDetailsEnabled": "logDetailsEnabled",
            "redisDb": "redisDb",
            "redisPort": "redisPort",
            "redisServer": "redisServer",
            "userAccounts": "userAccounts",
            "userDetailsEnabled": "userDetailsEnabled",
            "userDetailsTextColor": "userDetailsTextColor",
        }

        # Define our defaults (all panel specific key names should be listed)
        self._defaultattr("attributionColor", "#80cef2")
        self._defaultattr("headerText", "LNDHub Account Balances")
        self._defaultattr("interval", 86400)
        self._defaultattr("lineColor", "#4040ff")
        self._defaultattr("logDetailsEnabled", True)
        self._defaultattr("pageSize", 12)
        self._defaultattr("redisDb", 0)
        self._defaultattr("redisPort", 6379)
        self._defaultattr("redisServer", "localhost")
        self._defaultattr("userAccounts", [{"userid":"f9095b00b85802c6ff9cc674231858af03a24a75353aa7c0","name":"Samantha"}])
        self._defaultattr("userDetailsEnabled", True)
        self._defaultattr("userDetailsTextColor", "#808080")
        self._defaultattr("watermarkAnchor", "bottomleft")
    
        # Initialize
        super().__init__(name="lndhub")
        self.redis = redis.Redis(host=self.redisServer, port=self.redisPort, db=self.redisDb)

    def _getlndhubusers(self):
        return self.redis.keys("user_*")

    def _getlndhubuser(self, k):
        return self.redis.get(k)

    def _getlndhubispaids(self):
        return self.redis.keys("ispaid_*")

    def _islndhubpaymentforuser(self, s, u):
        v = self.redis.get("payment_hash_" + s)
        return False if v is None else v.decode("utf-8") == u

    def _getlndhubpaymentamount(self, k):
        return self.redis.get(k)

    def _getlndhubusertx(self, k):
        min = 0
        max = 10000
        return self.redis.lrange("txs_for_" + k, min, max)

    def _getuseralias(self, k):
        l = k
        a = None
        if "userAccounts" in self.config:
            for ua in self.config["userAccounts"]:
                if all(key in ua for key in ["name","accountid"]):
                    if ua["accountid"].lower() == l:
                        a = ua["name"]
        # deprecated field based approach
        elif l in self.config:
            a = self.config[l]
        if a is not None:
            if self.logDetailsEnabled:
                self.log(f"configured alias: {a}")
            return a
        f8l8 = l[:8]+".."+l[-8:]
        if self.logDetailsEnabled:
            self.log(f"calculated alias: {f8l8}")
            self.log("---")
            self.log(f"There was no configured alias found for '{l}'")
            self.log(f"You may use the nodeyez-config tool to set a name for this account by")
            self.log(f"adding a userAccount in the lndhub configuration and setting the")
            self.log(f"accountid property to {l}")
            self.log("---")
        return f8l8

    def _getusermetadata(self, u):
        return self.redis.get("metadata_for_" + u)

    def fetchData(self):
        """Fetches all the data needed for this panel"""

        self.lndhubusers = self._getlndhubusers()
        self.lndhubispaids = self._getlndhubispaids()
        
    def run(self):

        userCount = len(self.lndhubusers)
        if userCount == 0:
            self.log("There are no user accounts in LND Hub. Skipping")
            self._markAsRan()
            return

        textRowsPerUser = 4 if self.userDetailsEnabled else 2
        usersPerPage = self.pageSize // textRowsPerUser
        self.pageCount = int(math.ceil((userCount * textRowsPerUser) / self.pageSize))
        for self.pageNumber in range(1, self.pageCount+1):
            firstIndex = ((self.pageNumber - 1) * usersPerPage)
            lastIndex = (firstIndex + usersPerPage) - 1
            super().startImage()
            rowHeight = self.getInsetHeight() // (self.pageSize + 2) # 2: header,attribution
            # subheader row
            fs = int(self.height * 16/320)
            ypos = self.getInsetTop() + (rowHeight // 2)
            subxaccount = 3
            subxreceived = int(self.width * .6)
            subxspent = int(self.width * .8)
            subxbalance = int(self.width - 3)
            vicarioustext.drawlefttext(self.draw,  "Account",  fs, subxaccount,  ypos)
            vicarioustext.drawrighttext(self.draw, "Received", fs, subxreceived, ypos)
            vicarioustext.drawrighttext(self.draw, "Spent",    fs, subxspent,    ypos)
            vicarioustext.drawrighttext(self.draw, "Balance",  fs, subxbalance,  ypos)
            self.draw.line(xy=[3,self.getInsetTop() + rowHeight,self.width-3,self.getInsetTop() + rowHeight],fill=ImageColor.getrgb(self.lineColor),width=1)
            # users
            for userIndex in range(firstIndex, lastIndex + 1):
                if userIndex > len(self.lndhubusers) -1:
                    break
                user = self.lndhubusers[userIndex]
                if self.logDetailsEnabled:
                    usercred = user.decode("utf-8")
                    self.log(f"credential user record key: {usercred}")
                uservalue = self._getlndhubuser(user).decode("utf-8") # this is the internal mapped user
                if self.logDetailsEnabled:
                    self.log(f"maps to internal user account {uservalue}")
                useralias = self._getuseralias(uservalue) # this is a configurable alias
                usermetadata = self._getusermetadata(uservalue)
                usercreated = "unknown"
                try:
                    j = json.loads(usermetadata)
                    usercreated = j["created_at"][0:10]
                except Exception as e:
                    self.log(f"error loading user metadata as json: {e}")
                if self.logDetailsEnabled:
                    self.log(f"  created on {usercreated}")
                # get funds received by user
                userreceived = 0
                userreceivedcount = 0
                for paid in self.lndhubispaids:
                    suffix = paid.decode("utf-8").replace("ispaid_","")
                    if self._islndhubpaymentforuser(suffix, uservalue):
                        userreceivedcount = userreceivedcount + 1
                        receivedamount = int(self._getlndhubpaymentamount(paid))
                        userreceived = userreceived + receivedamount
                if self.logDetailsEnabled:
                    self.log(f"+ received ({userreceivedcount} transactions): {userreceived}")
                # get funds spent by user
                usertxs = self._getlndhubusertx(uservalue)
                userspent = 0
                userspentcount = 0
                userhubfees = 0
                for tx in usertxs:
                    try:
                        j = json.loads(tx)
                        j = j["payment_route"]
                        total_amt_msat = j["total_amt_msat"]
                        total_fees = j["total_fees"]
                        txsum = math.ceil(int(total_amt_msat) / 1000) + int(total_fees)
                        userspent = userspent + txsum
                        userspentcount = userspentcount + 1
                        userhubfees = userhubfees + int(total_fees)
                    except Exception as e:
                        self.log(f"error loading as json: {e}")
                if self.logDetailsEnabled:
                    self.log(f"- spent ({userspentcount} transactions): {userspent}")
                userbalance = userreceived - userspent
                if self.logDetailsEnabled:
                    self.log(f"= current balance: {userbalance}")
                # create text for user
                fs = int(self.height * 14/320)
                userrowheight = rowHeight * textRowsPerUser
                ypos = self.getInsetTop() + rowHeight + ((userIndex - firstIndex) * userrowheight) + (rowHeight // 2)
                vicarioustext.drawlefttext(self.draw,  useralias,         fs, subxaccount,  ypos)
                vicarioustext.drawrighttext(self.draw, str(userreceived), fs, subxreceived, ypos)
                vicarioustext.drawrighttext(self.draw, str(userspent),    fs, subxspent,    ypos)
                vicarioustext.drawrighttext(self.draw, str(userbalance),  fs, subxbalance,  ypos)
                if self.userDetailsEnabled:
                    ypos += rowHeight
                    userdesc = f"created: {usercreated}, hub fees paid: {userhubfees}"
                    vicarioustext.drawlefttext(self.draw, userdesc, fs, subxaccount, ypos, ImageColor.getrgb(self.userDetailsTextColor))
                    ypos += rowHeight
                    userdesc = f"# funding tx: {userreceivedcount}, # spend tx: {userspentcount}"
                    vicarioustext.drawlefttext(self.draw, userdesc, fs, subxaccount, ypos, ImageColor.getrgb(self.userDetailsTextColor))
            # Attribution
            fs = int(self.height * 16/320)
            xpos = self.width // 2
            ypos = self.getInsetTop() + self.getInsetHeight() - (rowHeight//2)
            attributionLine = "Data from local LNDhub instance"
            vicarioustext.drawcenteredtext(self.draw, attributionLine, fs, xpos, ypos, ImageColor.getrgb(self.attributionColor))
            super().finishImage()

# --------------------------------------------------------------------------------------
# Entry point if running this script directly
# --------------------------------------------------------------------------------------

if __name__ == '__main__':

    p = LNDHubPanel()

    # If arguments were passed in, treat as a single run
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h','--help']:
            print(f"Prepares images for LND Hub Account Balances")
            print(f"Usage:")
            print(f"1) Call without arguments to run continuously using the configuration or defaults")
            print(f"2) Passing any arguments other then -h or --help will run once and exit")
        else:
            p.fetchData()
            p.run()
        exit(0)

    # Continuous run
    p.runContinuous()