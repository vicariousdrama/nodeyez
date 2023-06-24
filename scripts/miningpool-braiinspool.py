#! /usr/bin/env python3
from PIL import ImageColor
from vicariouspanel import NodeyezPanel
import math
import sys
import time
import vicariousbitcoin
import vicariousnetwork
import vicarioustext

class BraiinsPoolPanel(NodeyezPanel):

    def __init__(self):
        """Instantiates a new Braiins Pool panel"""

        # Define which additional attributes we have
        self.configAttributes = {
            # legacy key name mappings
            "colorBackground": "backgroundColor",
            "colorBOSReward": "miningBOSRewardColor",
            "colorBreakEvenGood": "breakEvenGoodColor",
            "colorBreakEvenMiss": "breakEvenMissColor",
            "colorDataValue": "dataValueColor",
            "colorGraphLineDark": "graphLineDarkColor",
            "colorGraphLineLight": "graphLineLightColor",
            "colorHeader": "headerColor",
            "colorMiningReward": "miningRewardColor",
            "colorMovingAverage": "movingAverageColor",
            "colorReferralReward": "miningReferralRewardColor",
            "colorTextFG": "textColor",
            "priceurl": "priceUrl",
            "sleepInterval": "interval",
            # panel specific key names
            "authtoken": "authtoken",
            "miningBOSRewardColor": "miningBOSRewardColor",
            "breakEvenGoodColor": "breakEvenGoodColor",
            "breakEvenMissColor": "breakEvenMissColor",
            "dataValueColor": "dataValueColor",
            "graphLineDarkColor": "graphLineDarkColor",
            "graphLineLightColor": "graphLineLightColor",
            "headerColor": "headerColor",
            "miningRewardColor": "miningRewardColor",
            "movingAverageColor": "movingAverageColor",
            "miningReferralRewardColor": "miningReferralRewardColor",
            "fiatUnit": "fiatUnit",
            "kwhPrice": "kwhPrice",
            "kwhUsed": "kwhUsed",
            "priceCheckInterval": "priceCheckInterval",
            "priceUrl": "priceUrl",
            "useTor": "useTor",
        }

        # Define our defaults (all panel specific key names should be listed)
        self._defaultattr("authtoken", "NOT_SET")
        self._defaultattr("breakEvenDaily", 9999999)
        self._defaultattr("breakEvenGoodColor", "#00ff00")
        self._defaultattr("breakEvenMissColor", "#ff0000")
        self._defaultattr("dataValueColor", "#4040ff")
        self._defaultattr("graphLineDarkColor", "#606060")
        self._defaultattr("graphLineLightColor", "#a0a0a0")
        self._defaultattr("fiatUnit", "USD")
        self._defaultattr("headerColor", "#ffffff")
        self._defaultattr("kwhPrice", .12)
        self._defaultattr("kwhUsed", 1.100)
        self._defaultattr("miningBOSRewardColor", "#fb82a8")
        self._defaultattr("miningReferralRewardColor", "#00bac5")
        self._defaultattr("miningRewardColor", "#6b50ff")
        self._defaultattr("movingAverageColor", "#d69f06")
        self._defaultattr("interval", 3600)
        self._defaultattr("priceCheckInterval", 10800)
        self._defaultattr("priceCheckTimeRemaining", 0)
        self._defaultattr("priceHigh", 1)
        self._defaultattr("priceLast", 1)
        self._defaultattr("priceLow", 1)
        self._defaultattr("priceUrl", "https://bisq.markets/bisq/api/markets/ticker")
        self._defaultattr("satsPerBTC", 100000000)
        self._defaultattr("useTor", True)
        
        # Initialize
        super().__init__(name="miningpool-braiinspool")

    def isDependenciesMet(self):

        # Verify token set
        if len(self.authtoken) == 0 or self.authtoken.find("NOT_SET") > -1:
            self.log(f"authtoken not configured")
            return False
        return True

    def fetchData(self):
        """Fetches all the data needed for this panel"""

        if not self.isDependenciesMet():
            return

        # Braiins data
        self.log("Getting account profile information from Braiins")
        self.accountprofile = vicariousnetwork.getbraiinspoolaccountprofile(True, self.authtoken)
        time.sleep(6)
        self.log("Getting account rewards information from Braiins")
        self.accountrewards = vicariousnetwork.getbraiinspoolaccountrewards(True, self.authtoken)
        time.sleep(6)
        self.log("Getting pool stats information from Braiins")
        self.poolstats = vicariousnetwork.getbraiinspoolstats(True, self.authtoken)

        # Price data
        if self.priceCheckTimeRemaining <= 0:
            self.log("Getting updated prices")
            self.priceLast, self.priceHigh, self.priceLow, fiatkeyname = vicariousnetwork.getpriceinfo(True, self.priceUrl, self.priceLast, self.priceHigh, self.priceLow, self.fiatUnit)
            if fiatkeyname != f"btc_{self.fiatUnit}".lower():
                self.fiatUnit = fiatkeyname.split("_")[1].upper()
            self.priceCheckTimeRemaining = self.priceCheckInterval
        else:
            self.priceCheckTimeRemaining = self.priceCheckTimeRemaining - self.interval

    def _getbraiinsaccounthashrate(self, accountprofile):
        hashrate = accountprofile["btc"]["hash_rate_5m"]
        hashdesc = accountprofile["btc"]["hash_rate_unit"]
        return vicariousbitcoin.gethashratestring(hashrate, hashdesc)

    def _gethighestreward(self, accountrewards):
        highestreward = 0.00
        days = 0
        for reward in accountrewards["btc"]["daily_rewards"]:
            days = days + 1
            currenttotal = float(reward["total_reward"])
            if currenttotal > highestreward:
                highestreward = currenttotal
        return highestreward

    def _getlowestreward(self, accountrewards):
        lowestreward = 0.00
        days = 0
        for reward in accountrewards["btc"]["daily_rewards"]:
            days = days + 1
            currenttotal = float(reward["total_reward"])
            if days == 1:
                lowestreward = currenttotal
            else:
                if currenttotal < lowestreward:
                    lowestreward = currenttotal
        return lowestreward


    def run(self):

        if not self.isDependenciesMet():
            self._markAsRan()
            return

        self.headerText = "Braiins Pool Mining Summary"
        super().startImage()
        
        # Hashrate -Area Labels ---------------------------------------------
        hashAreaHeight = self.getInsetHeight() * .4
        hashAreaLabelSize = int(self.height * (16/320))
        hashAreaValueSize = int(self.height * (24/320))
        earningspad = int(self.height * (24/320))
        hashrateLabel = "Hashrate"
        hashrateValue = self._getbraiinsaccounthashrate(self.accountprofile)
        vicarioustext.drawcenteredtext(self.draw, hashrateLabel, hashAreaLabelSize, self.width//4, (self.getInsetTop() + hashAreaHeight//2 - hashAreaValueSize), ImageColor.getrgb(self.textColor))
        vicarioustext.drawcenteredtext(self.draw, hashrateValue, hashAreaValueSize, self.width//4, (self.getInsetTop() + hashAreaHeight//2), ImageColor.getrgb(self.dataValueColor))
        # Yesterday and Today value
        value_last_day = "0 sats"
        value_today = "0 sats"
        if len(self.accountrewards["btc"]["daily_rewards"]) > 0:
            since_date = self.accountrewards["btc"]["daily_rewards"][0]["date"]
            sattally = 0
            for key in self.poolstats["btc"]["blocks"]:
                block = self.poolstats["btc"]["blocks"][key]
                if block["date_found"] > since_date:
                    if block["user_reward"] is not None:
                        sattally = sattally + int(float(block["user_reward"]) * self.satsPerBTC)
                else:
                    break
            sattally2 = sattally
            since_date = since_date + 86400
            sattally = 0
            for key in self.poolstats["btc"]["blocks"]:
                block = self.poolstats["btc"]["blocks"][key]
                if block["date_found"] > since_date:
                    if block["user_reward"] is not None:
                        sattally = sattally + int(float(block["user_reward"]) * self.satsPerBTC)
                else:
                    break
            value_last_day = f"{sattally2 - sattally} sats"
            value_today = f"{sattally} sats"
        vicarioustext.drawcenteredtext(self.draw, "Earnings Yesterday", hashAreaLabelSize, self.width//4*3, (self.getInsetTop() + hashAreaHeight//2 - hashAreaValueSize - earningspad), ImageColor.getrgb(self.textColor))
        vicarioustext.drawcenteredtext(self.draw, value_last_day,       hashAreaValueSize, self.width//4*3, (self.getInsetTop() + hashAreaHeight//2 - earningspad), ImageColor.getrgb(self.dataValueColor))
        vicarioustext.drawcenteredtext(self.draw, "Earnings Today",     hashAreaLabelSize, self.width//4*3, (self.getInsetTop() + hashAreaHeight//2 - hashAreaValueSize + earningspad), ImageColor.getrgb(self.textColor))
        vicarioustext.drawcenteredtext(self.draw, value_today,          hashAreaValueSize, self.width//4*3, (self.getInsetTop() + hashAreaHeight//2 + earningspad), ImageColor.getrgb(self.dataValueColor))

        # 30 Days Rewards Chart ---------------------------------------------
        yAxisLabelSize = int(self.height * (12/320))
        chartLabelSize = int(self.height * (16/320))
        highestreward = self._gethighestreward(self.accountrewards)
        lowestreward = self._getlowestreward(self.accountrewards)
        labelwidth = self.width//5
        graphedge = 3
        charttop = self.getInsetTop() + hashAreaHeight + (chartLabelSize * 2)
        chartleft = labelwidth + graphedge
        chartright = self.width - graphedge
        chartbottom = self.getInsetTop() + self.getInsetHeight() - graphedge
        # - chart border
        self.draw.line(xy=[chartleft,  charttop,    chartleft,  chartbottom],fill=ImageColor.getrgb(self.graphLineLightColor),width=1)
        self.draw.line(xy=[chartleft,  chartbottom, chartright, chartbottom],fill=ImageColor.getrgb(self.graphLineLightColor),width=1)
        self.draw.line(xy=[chartleft,  charttop,    chartright, charttop],   fill=ImageColor.getrgb(self.graphLineDarkColor),width=1)
        self.draw.line(xy=[chartright, charttop,    chartright, chartbottom],fill=ImageColor.getrgb(self.graphLineDarkColor),width=1)
        # - dashed line background
        chart25 = int(math.floor(charttop + ((chartbottom - charttop)/4*1)))
        chart50 = int(math.floor(charttop + ((chartbottom - charttop)/4*2)))
        chart75 = int(math.floor(charttop + ((chartbottom - charttop)/4*3)))
        for i in range(chartleft, chartright, 10):
            self.draw.line(xy=[i,chart25,i+1,chart25],fill=ImageColor.getrgb(self.graphLineDarkColor),width=1)
            self.draw.line(xy=[i,chart50,i+1,chart50],fill=ImageColor.getrgb(self.graphLineDarkColor),width=1)
            self.draw.line(xy=[i,chart75,i+1,chart75],fill=ImageColor.getrgb(self.graphLineDarkColor),width=1)
        # - left labels
        reward25 = int(math.floor((lowestreward + ((highestreward - lowestreward)/4*3)) * self.satsPerBTC))
        reward50 = int(math.floor((lowestreward + ((highestreward - lowestreward)/4*2)) * self.satsPerBTC))
        reward75 = int(math.floor((lowestreward + ((highestreward - lowestreward)/4*1)) * self.satsPerBTC))
        vicarioustext.drawrighttext(self.draw, str(reward25) + " sats", yAxisLabelSize, labelwidth, chart25, ImageColor.getrgb(self.textColor))
        vicarioustext.drawrighttext(self.draw, str(reward50) + " sats", yAxisLabelSize, labelwidth, chart50, ImageColor.getrgb(self.textColor))
        vicarioustext.drawrighttext(self.draw, str(reward75) + " sats", yAxisLabelSize, labelwidth, chart75, ImageColor.getrgb(self.textColor))
        # - 30 days of bars
        totaldays = 31
        days = 0
        daystoskip = 1
        daywidth = int(math.floor((chartright - chartleft) / totaldays))
        barwidth = daywidth - 2
        overalltotal = 0
        masize = 14 # days of simple moving average.
        maoldx = -1
        maoldy = -1
        for reward in self.accountrewards["btc"]["daily_rewards"]:
            days = days + 1
            # skip the first day entry, something not right, and it doesnt show on pool.braiins.com
            if days < (daystoskip + 1):
                continue
            if days > totaldays + 1:
                break
            currenttotal = 0
            if reward["total_reward"] is not None:
                currenttotal = float(reward["total_reward"])
            overalltotal = overalltotal + currenttotal
            dayx = chartright - ((days - daystoskip) * daywidth)
            barpct = 0 if highestreward <= lowestreward else (currenttotal-lowestreward)/(highestreward-lowestreward)
            bartop = chartbottom - int(math.floor((chartbottom-charttop)*barpct))
            self.draw.rectangle(xy=[dayx,bartop,dayx+barwidth,chartbottom-1],fill=ImageColor.getrgb(self.miningRewardColor))
            if reward["bos_plus_reward"] is not None:
                bosreward = float(reward["bos_plus_reward"])
                bospct = 0 if highestreward <= lowestreward else bosreward/(highestreward-lowestreward)
                bosbottom = bartop + int(math.floor((chartbottom-charttop)*bospct))
                if bosbottom > chartbottom:
                    bosbottom = chartbottom
                self.draw.rectangle(xy=[dayx,bartop,dayx+barwidth,bosbottom],fill=ImageColor.getrgb(self.miningBOSRewardColor))
            # referral_bonus, referral_reward also available, but i dont know what they would look like yet
            # moving average line
            max = dayx + int(barwidth/2)
            matotal = 0
            for maidx in range(masize):
                marewardidx = days + maidx
                if len(self.accountrewards["btc"]["daily_rewards"]) > marewardidx:
                    mareward = self.accountrewards["btc"]["daily_rewards"][marewardidx]
                    marewardtotal = float(mareward["total_reward"])
                    matotal = matotal + marewardtotal
            maavg = (matotal / masize)
            mapct = 0
            if highestreward > lowestreward:
                mapct = (maavg-lowestreward)/(highestreward-lowestreward)
            may = chartbottom - int(math.floor((chartbottom-charttop)*mapct))
            if maoldx != -1:
                self.draw.line(xy=[(max,may),(maoldx,maoldy)],fill=ImageColor.getrgb(self.movingAverageColor),width=2)
            maoldx = max
            maoldy = may
        overalltotal = overalltotal * self.satsPerBTC
        # Chart header
        if days > 0:
            dailyavg = (overalltotal / days)
            # Warn if missing breakeven. 
            hoursPerDay = 24
            breakevendaily = int((self.satsPerBTC / self.priceLast) * (hoursPerDay * self.kwhUsed * self.kwhPrice))
            breakevencolor = ImageColor.getrgb(self.breakEvenGoodColor)
            if dailyavg < breakevendaily:
                breakevencolor = ImageColor.getrgb(self.breakEvenMissColor)
                vicarioustext.drawtoplefttext(self.draw, "Warning: Mining at a loss",           chartLabelSize, 0, (self.getInsetTop() + hashAreaHeight + chartLabelSize), breakevencolor)
            vicarioustext.drawtoplefttext(self.draw, f"Last 30 days {int(overalltotal)} sats",  chartLabelSize, 0, (self.getInsetTop() + hashAreaHeight), ImageColor.getrgb(self.textColor))
            vicarioustext.drawtoprighttext(self.draw, f"Daily avg {int(dailyavg)} sats",        chartLabelSize, self.width, (self.getInsetTop() + hashAreaHeight), ImageColor.getrgb(self.textColor))
            vicarioustext.drawtoprighttext(self.draw, f"Break even {int(breakevendaily)} sats", chartLabelSize, self.width, (self.getInsetTop() + hashAreaHeight + chartLabelSize), breakevencolor)
        else:
            vicarioustext.drawcenteredtext(self.draw, "Rewards will be graphed below once earnings are recorded"  , chartLabelSize, self.width//2, (self.getInsetTop() + hashAreaHeight))

        super().finishImage()

# --------------------------------------------------------------------------------------
# Entry point if running this script directly
# --------------------------------------------------------------------------------------

if __name__ == '__main__':

    p = BraiinsPoolPanel()

    # If arguments were passed in, treat as a single run
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h','--help']:
            print(f"Creates a summary image of Braiins pool account with the current hashrate, and the")
            print(f"account earnings depicted for yesterday and today, and a graph of past 30 days")
            print(f"Usage:")
            print(f"1) Call without arguments to run continuously using the configuration or defaults")
            print(f"2) Pass with an argument other than -h or --help to run once and exit.")
            print(f"You must specify authtoken in the config file")
        else:
            if not p.isDependenciesMet():
                exit(1)
            p.fetchData()
            p.run()
        exit(0)

    # Continuous run
    if not p.isDependenciesMet():
        exit(1)
    p.runContinuous()