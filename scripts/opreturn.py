#! /usr/bin/env python3
from PIL import ImageColor
from vicariouspanel import NodeyezPanel
import re
import sys
import vicariousbitcoin
import vicarioustext

class OPReturnPanel(NodeyezPanel):

    def __init__(self):
        """Instantiates a new OP_RETURN panel"""

        # Define which additional attributes we have
        self.configAttributes = {
            # legacy key name mappings
            "colorBackground": "backgroundColor",
            "colorTextFG": "textColor",
            "colorTextFG1": "dataRowEvenTextColor",
            "colorTextFG2": "dataRowOddTextColor",
            "sleepInterval": "interval",
            # panel specific key names
            "dataRowEvenTextColor": "dataRowEvenTextColor",
            "dataRowOddTextColor": "dataRowOddTextColor",
            "excludedPatterns": "excludedPatterns",
        }

        # Define our defaults (all panel specific key names should be listed)
        self._defaultattr("dataRowEvenTextColor", "#ff7f00")
        self._defaultattr("dataRowOddTextColor", "#dddd00")
        self._defaultattr("excludedPatterns", [
             "^[+=\-s]:(ATOM|AVAX|BCH|BNB|BTC|DOGE|ETH|GAIA|LTC|RUNE|THOR|USDC).*",
             "^.{1,5}$",
             "^.*(BERNSTEIN 2.0|HEX.com|WanChain).*",
             "^(Binance|Betnomi|Kinesis|RSK|ScytheX.io|btt|euklid|omni).*$",
             "^(OUT|REFUND):[A-F0-9]{64}.*",
             "^(DC-L5|SWAPTX|MIGRATE|inbit|ion):.*",
             "^J_(NEW_CONTRACT|WITHDRAW|REFUND).*",
             "^[A-Za-z0-9]{34}$",
             "^[A-Za-z0-9]{39}$",
             "^[A-Za-z0-9]{40}$",
             "^[A-Za-z0-9]{48}$",
             "^[A-Za-z0-9]{64}$",
             "Casper",
             "Bitzlato",
             "Describe payment",
             "Deposite",
             "Exodus Wallet",
             "Kucoin",
             "btc transfer",
             "charge",
             "consolidate",
             "donation",
             "hash payment",
             "https://trustless.computer",
             ])
        self._defaultattr("footerEnabled", False)
        self._defaultattr("interval", 540)
        self._defaultattr("watermarkAnchor", "bottomright")
        self._defaultattr("watermarkEnabled", True)

        # Initialize
        super().__init__(name="opreturn")
        self.previousblock = 0

    def fetchData(self):
        """Fetches all the data needed for this panel"""

        self.blocknumber = vicariousbitcoin.getcurrentblock()
        if self.previousblock == self.blocknumber: return
        self.opreturns = vicariousbitcoin.getblockopreturns(self.blocknumber)

    def run(self):

        if self.previousblock == self.blocknumber:
            self._markAsRan()
            return
        self.previousblock = self.blocknumber

        self.headerText = f"OP_RETURN entries for {self.blocknumber}"

        # Build up list of acceptable OP_RETURNs
        oc = len(self.opreturns)
        opreturns = []
        for opreturn in self.opreturns:
            excluded = False
            for pattern in self.excludedPatterns:
                if opreturn == pattern: 
                    excluded = True
                    break
                if re.compile(pattern).search(opreturn) is not None: 
                    excluded = True
                    break
            if not excluded and opreturn not in opreturns:
                opreturns.append(opreturn)
        if len(opreturns) == 0:
            self.log(f"Block {self.blocknumber} has no suitable OP_RETURN values (excluded {oc})")
            self._markAsRan()
            return
        self.log(f"Block {self.blocknumber} has {len(opreturns)} suitable OP_RETURN values (of {oc})")

        super().startImage()

        # Basic inits for tracking
        rowIndex = 0
        texty = self.getInsetTop()
        textystop = self.height - self.getFooterHeight()

        # Determine font size based on how many op returns to render
        fontsize = int(self.height * (20/320))
        fontsize = int(self.height * (18/320)) if len(opreturns) > 2 else fontsize
        fontsize = int(self.height * (16/320)) if len(opreturns) > 4 else fontsize
        fontsize = int(self.height * (14/320)) if len(opreturns) > 6 else fontsize
        fontsize = int(self.height * (12/320)) if len(opreturns) > 7 else fontsize

        # Render the op returns
        for opreturn in opreturns:
            rowIndex += 1
            rowTextColor = self.dataRowEvenTextColor if rowIndex % 2 == 0 else self.dataRowOddTextColor
            rwords = opreturn.split()
            rpart, rwords = vicarioustext.getmaxtextforwidth(self.draw, rwords, self.width, fontsize)
            while len(rpart) > 0:
                _,sh,_ = vicarioustext.gettextdimensions(self.draw, rpart, fontsize)
                texty += sh
                if texty > textystop: break
                vicarioustext.drawbottomlefttext(self.draw, rpart, fontsize, 0, texty, ImageColor.getrgb(rowTextColor), False)
                rpart, rwords = vicarioustext.getmaxtextforwidth(self.draw, rwords, self.width, fontsize)

        super().finishImage()

# --------------------------------------------------------------------------------------
# Entry point if running this script directly
# --------------------------------------------------------------------------------------

if __name__ == '__main__':

    p = OPReturnPanel()

    # If arguments were passed in, treat as a single run
    if len(sys.argv) > 1:
        arg1 = sys.argv[1]
        if arg1 in ['-h','--help']:
            arg0 = sys.argv[0]
            print(f"Produces an image with OP_RETURN data")
            print(f"Usage:")
            print(f"1) Call without arguments to run continuously using the configuration or defaults")
            print(f"2) Call with an argument other then -h or --help to run once and exit")
            print(f"   If a number is provided, it will be treated as a block number to look for OP_RETURNs")
            print(f"   {arg0} 722231")
        else:
            p.blocknumber = vicariousbitcoin.getcurrentblock()
            if re.match(r'^-?\d+$', arg1) is not None:
                if int(arg1) <= p.blocknumber: 
                    p.blocknumber = int(arg1)
            p.opreturns = vicariousbitcoin.getblockopreturns(p.blocknumber)
            p.run()
        exit(0)

    # Continuous run
    p.runContinuous()