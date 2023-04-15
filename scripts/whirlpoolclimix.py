#! /usr/bin/env python3
from PIL import ImageColor
from datetime import timedelta
from vicariouspanel import NodeyezPanel
import sys
import vicariousnetwork
import vicarioustext

class WhirlpoolCLIMixPanel(NodeyezPanel):

    def __init__(self):
        """Instantiates a new Whirlpool CLI Mix panel"""

        # Define which additional attributes we have
        self.configAttributes = {
            # legacy key name mappings
            "colorBackground": "backgroundColor",
            "colorDataLabel": "labelColor",
            "colorDataOff": "offColor",
            "colorDataOn": "onColor",
            "colorDataValue": "valueColor",
            "colorHeader": "headerColor",
            "colorTextFG": "textColor",
            "sleepInterval": "interval",
            "whirlpoolurl": "whirlpoolUrl",
            # panel specific key names
            "apiKey": "apiKey",
            "attributionColor": "attributionColor",
            "labelColor": "labelColor",
            "offColor": "offColor",
            "onColor": "onColor",
            "useTor": "useTor",
            "valueColor": "valueColor",
            "whirlpoolUrl": "whirlpoolUrl",
        }

        # Define our defaults (all panel specific key names should be listed)
        self._defaultattr("apiKey", "NOT_SET")
        self._defaultattr("attributionColor", "#aa2222")
        self._defaultattr("headerText", "Whirlpool CLI + MIX Status")
        self._defaultattr("interval", 300)
        self._defaultattr("labelColor", "#aa2222")
        self._defaultattr("offColor", "#ff4040")
        self._defaultattr("onColor", "#40ff40")
        self._defaultattr("useTor", False)
        self._defaultattr("valueColor", "#bbbbbb")
        self._defaultattr("watermarkAnchor", "bottomright")
        self._defaultattr("whirlpoolUrl", "https://127.0.0.1:8899")

        # Initialize
        super().__init__(name="whirlpoolclimix")

    def convertBTCtoSats(self, i):
        return str(int(float(i.replace("btc","")) * 100000000)) + " sats"

    def isDependenciesMet(self):

        # Verify apikey set
        if len(self.apiKey) == 0 or self.apiKey.find("NOT_SET") > -1:
            self.log(f"apiKey not configured")
            return False

        # Verify local whirlpool
        if self.isWhirlpoolCoordinator():
            self.log(f"You must specify the url to your local whirlpool instance as whirlpoolurl")
            return False

        return True
    
    def isWhirlpoolCoordinator(self):
        if "udkmfc5j6zvv3ysavbrwzhwji4hpyfe3apqa6yst7c7l32mygf65g4ad.onion" in self.whirlpoolUrl:
            return True
        if "pool.whirl.mx" in self.whirlpoolUrl:
            return True
        return False

    def fetchData(self):
        """Fetches all the data needed for this panel"""

        if not self.isDependenciesMet():
            return

        self.cliStatus = vicariousnetwork.getwhirlpoolcliconfig(self.useTor, self.whirlpoolUrl, self.apiKey)
        self.mixStatus = vicariousnetwork.getwhirlpoolmix(self.useTor, self.whirlpoolUrl, self.apiKey)

    def getHumanTime(self, timeinms, partcount=1):
        d = timedelta(milliseconds=timeinms)
        seconds = int(d.total_seconds() // 1)
        o = ""
        if partcount > 0 and (seconds // 86400) > 0:
            days = seconds // 86400
            o = o + ", " if len(o) > 0 else o
            o = o + str(days) + " day"
            o = o + "s" if days > 1 else ""
            partcount = partcount - 1
            seconds -= (days * 86400)
        if partcount > 0 and (seconds // 3600) > 0:
            hours = seconds // 3600
            o = o + ", " if len(o) > 0 else o
            o = o + str(hours) + " hour"
            o = o + "s" if hours > 1 else ""
            partcount = partcount - 1
            seconds -= (hours * 3600)
        if partcount > 0 and (seconds // 60) > 0:
            minutes = seconds // 60
            o = o + ", " if len(o) > 0 else o
            o = o + str(minutes) + " minute"
            o = o + "s" if minutes > 1 else ""
            partcount = partcount - 1
        if partcount > 0 and seconds > 0:
            o = o + ", " if len(o) > 0 else o
            o = o + str(seconds) + " second"
            o = o + "s" if seconds > 1 else ""
            partcount = partcount - 1
        if o == "":
            o = "now"
        else:
            o += " ago"
        return o

    def getStepStatus(self, s):
        if s == "CONNECTING": return "connecting..."
        if s == "CONNECTED": return "connected"
        if s == "REGISTERED_INPUT": return "input registered"
        if s == "CONFIRMING_INPUT": return "waiting for mix"
        if s == "CONFIRMED_INPUT": return "joined a mix!"
        if s == "REGISTERING_OUTPUT": return "registering output"
        if s == "REGISTERED_OUTPUT": return "output registered"
        if s == "SIGNING": return "signing tx"
        if s == "SIGNED": return "tx signed"
        if s == "REVEALED_OUTPUT": return "round aborted"
        if s == "SUCCESS": return "mix success!"
        if s == "FAIL": return "mix failed"
        return s

    def getUnicodeBool(self, b):
        return u"✓" if b else u"✗"

    def renderAttribution(self):
        fontsize = int(self.height * 16/320)
        t = "Data from Whirlpool Client"
        vicarioustext.drawbottomlefttext(self.draw, t, fontsize, 0, self.height, ImageColor.getrgb(self.attributionColor))

    def renderErrors(self):
        if len(self.errors) == 0: return
        errorColor = ImageColor.getrgb(self.offColor)
        fontsize = int(self.height * 20/320)
        buf = 5
        x = buf
        y = self.height // 2
        for error in self.errors:
            fs, w, h = vicarioustext.getmaxfontsize(self.draw, error, self.width - (buf * 2), self.height//10, True, fontsize)
            vicarioustext.drawtoplefttext(self.draw, error, fs, x, y, errorColor, True)
            y = y + h + buf

    def renderFieldValue(self, label, value, left, top, right, bottom):
        centerh = left + ((right-left)//2)
        centerv = top + ((bottom-top)//2)
        valueColor = self.valueColor
        labelFontSize = int(self.height * 16/320)
        valueFontSize = int(self.height * 14/320)
        fontBold = False
        if value == self.getUnicodeBool(True):
            valueColor = self.onColor
            valueFontSize = int(self.height * 32/320)
            fontBold = True
        if value == self.getUnicodeBool(False):
            valueColor = self.offColor
            valueFontSize = int(self.height * 32/320)
            fontBold = True        
        vicarioustext.drawcenteredtext(self.draw, label, labelFontSize, centerh, centerv - 10, ImageColor.getrgb(self.labelColor), True)
        vicarioustext.drawcenteredtext(self.draw, value, valueFontSize, centerh, centerv + 10, ImageColor.getrgb(valueColor), fontBold)

    def renderFields(self):
        errors = []
        if not self.cliStatus.keys() & {'cliStatus','network','tor','dojo','loggedIn','version'}:
            errors.append("CLI Status not in correct format")
            network = "unknown"
            tor = False
            dojo = False
            loggedIn = False
            version = "unknown"
        else:
            status = self.cliStatus["cliStatus"]
            if status == "ERROR": errors.append("Error accessing CLI. Is Whirlpool running?")
            network = self.cliStatus["network"]
            tor = self.cliStatus["tor"]
            dojo = self.cliStatus["dojo"]
            loggedIn = self.cliStatus["loggedIn"]
            version = self.cliStatus["version"]
        started = self.mixStatus["started"] if "started" in self.mixStatus else False
        mixCount = self.mixStatus["nbMixing"] if "nbMixing" in self.mixStatus else 0
        mixQueued = self.mixStatus["nbQueued"] if "nbQueued" in self.mixStatus else 0
        mixMessage = self.mixStatus["message"] if "message" in self.mixStatus else ""
        if len(mixMessage) > 0: self.log(f"mix status message: {mixMessage}")
        if "No wallet opened" in mixMessage: errors.append(mixMessage)
        if "error" in self.mixStatus:
            if self.mixStatus["error"] != None: errors.append(self.mixStatus["error"])
        self.errors = errors
        qw = self.width//4
        qh = self.getInsetHeight() // 5
        qt = self.getInsetTop()
        self.renderFieldValue("Tor",       self.getUnicodeBool(tor),      qw*0, qt+(qh*0), qw*1, qt+(qh*1))
        self.renderFieldValue("Dojo",      self.getUnicodeBool(dojo),     qw*1, qt+(qh*0), qw*2, qt+(qh*1))
        self.renderFieldValue("Logged In", self.getUnicodeBool(loggedIn), qw*2, qt+(qh*0), qw*3, qt+(qh*1))
        self.renderFieldValue("Started",   self.getUnicodeBool(started),  qw*3, qt+(qh*0), qw*4, qt+(qh*1))
        self.renderFieldValue("Network",   network,                       qw*0, qt+(qh*1), qw*1, qt+(qh*2))
        self.renderFieldValue("Version",   version,                       qw*1, qt+(qh*1), qw*2, qt+(qh*2))
        self.renderFieldValue("Mixing",    f"{mixCount}",                 qw*2, qt+(qh*1), qw*3, qt+(qh*2))
        self.renderFieldValue("Queued",    f"{mixQueued}",                qw*3, qt+(qh*1), qw*4, qt+(qh*2))

    def renderMixing(self):
        if "threads" not in self.mixStatus: return
        qh = self.getInsetHeight() // 5
        qt = self.getInsetTop()
        tc = 0
        tw = self.width//3
        threadheads = ["Pool", "Mix Step", "Last Activity"]
        for t in self.mixStatus["threads"]:
            if not t.keys() & {'poolId','mixStep','lastActivityElapsed'}: continue
            if tc > 0: threadheads = ["","",""]
            yt = qt+int(qh*(2.5 + float(tc) * 0.3)) - 16
            yb = qt+int(qh*(3.0 + float(tc) * 0.3)) - 16
            sats = self.convertBTCtoSats(t["poolId"])
            stepstatus = self.getStepStatus(t["mixStep"])
            humantime = self.getHumanTime(t["lastActivityElapsed"])
            self.renderFieldValue(threadheads[0], f"{sats}",       tw*0, yt, tw*1, yb)
            self.renderFieldValue(threadheads[1], f"{stepstatus}", tw*1, yt, tw*2, yb)
            self.renderFieldValue(threadheads[2], f"{humantime}",  tw*2, yt, tw*3, yb)
            tc = tc + 1

    def run(self):

        super().startImage()

        self.renderFields()
        self.renderErrors()
        self.renderMixing()
        self.renderAttribution()

        super().finishImage()

# --------------------------------------------------------------------------------------
# Entry point if running this script directly
# --------------------------------------------------------------------------------------

if __name__ == '__main__':

    p = WhirlpoolCLIMixPanel()

    # If arguments were passed in, treat as a single run
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h','--help']:
            print(f"Creates a summary image of Whirlpool Mix Status.")
            print(f"Usage:")
            print(f"1) Call without arguments to run continuously using the configuration or defaults")
            print(f"2) Pass with an argument other than -h or --help to run once and exit.")
        else:
            if not p.isDependenciesMet():
                exit(1)
            p.fetchData()
            p.run()
        exit(0)

    # Continuous run
    p.runContinuous()