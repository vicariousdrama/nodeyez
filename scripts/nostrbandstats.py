#! /usr/bin/env python3
from PIL import ImageColor
from vicariouspanel import NodeyezPanel
import sys
import vicariouschart
import vicariousnetwork
import vicarioustext

class NostrBandStatsPanel(NodeyezPanel):

    def __init__(self):
        """Instantiates a new Nostr.Band Stats panel"""

        # Define which additional attributes we have
        self.configAttributes = {
            # panel specific key names
            "attributionColor": "attributionColor",
            "graphAverageColor": "graphAverageColor",
            "graphBorderColor": "graphBorderColor",
            "graphDataColors": "graphDataColors",
            "statsUrl": "statsUrl",
            "useTor": "useTor",
        }

        # Define our defaults (all panel specific key names should be listed)
        self._defaultattr("attributionColor", "#A020A0")
        self._defaultattr("graphAverageColor", "#8888ff")
        self._defaultattr("graphBorderColor", "#888888")
        self._defaultattr("graphDataColors", ["#A020A0", "#0000ff", "#00ff00", "#808000", "#ff0000", "#00ffff", "#800000", "#808080", "#008000", "#800080", "#ff00ff", "#008080"])
        self._defaultattr("headerText", "Nostr.Band Stats")
        self._defaultattr("interval", 86400)
        self._defaultattr("statsUrl", "https://stats.nostr.band/stats_api?method=stats&options=")
        self._defaultattr("useTor", True)
        self._defaultattr("watermarkAnchor", "bottom")

        # Initialize
        super().__init__(name="nostrbandstats")

    def fetchData(self):
        """Fetches all the data needed for this panel"""

        self.nostrstats = vicariousnetwork.getnostrstats(self.useTor, self.statsUrl)

    def transformData(self):
        # make a copy to work with
        tstats = dict(self.nostrstats)
        # create simple lists from datasets
        for tlk in tstats.keys():
            tlko = tstats[tlk]
            if type(tlko) is not dict: continue
            if "datasets" in tlko:
                datasets = tlko["datasets"]
                keynames = list(datasets.keys())
                for k in keynames:
                    flatk = f"{k}_flat"
                    listk = []
                    valueAdded = False
                    if type(datasets[k]) is list:
                        for o in datasets[k]:
                            if "c" in o:
                                listk.append(o["c"])
                                valueAdded = True
                    if valueAdded: datasets[flatk] = listk
        return tstats

    def run(self):

        attributionLine = "Data from Nostr.Band"
        attributionSize = int(self.height * 14/320)
        labelSize = int(self.height * 12/320)

        # transform data to our generalized format for charting
        tstats = self.transformData()

        # get date range
        activeRelays, _ = vicariouschart.getNestedField(tstats, "daily.datasets.active_relays")
        dateBegin = activeRelays[0]["d"]
        dateEnd = activeRelays[-1]["d"]

        # render zaps per day chart
        self.headerText = "Zaps per Day"
        self.pageSuffix = "zapsperday"
        super().startImage()
        kind9735stats, _ = vicariouschart.getNestedField(tstats, "daily.datasets.kind_9735_flat")
        vicariouschart.drawBarChart(self.draw, 0, self.getInsetTop(), self.width, self.getInsetHeight(), kind9735stats, None, True, "", 1, self.graphDataColors[0], self.graphAverageColor, self.graphBorderColor)
        vicariouschart.drawLabel(self.draw, dateBegin, labelSize, "tl", 0 + 2, self.getInsetTop()+2 )
        vicariouschart.drawLabel(self.draw, dateEnd, labelSize, "tr", self.width - 3, self.getInsetTop()+2)
        vicarioustext.drawbottomlefttext(self.draw, attributionLine, attributionSize, 0, self.height, ImageColor.getrgb(self.attributionColor))
        super().finishImage()

# --------------------------------------------------------------------------------------
# Entry point if running this script directly
# --------------------------------------------------------------------------------------

if __name__ == '__main__':

    p = NostrBandStatsPanel()

    # If arguments were passed in, treat as a single run
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h','--help']:
            print(f"Prepares an image of recent Nostr statistics per Nostr.band")
            print(f"Usage:")
            print(f"1) Call without arguments to run continuously using the configuration or defaults")
            print(f"2) Call with an argument other then -h or --help to run once and exit")
        else:
            p.fetchData()
            p.run()
        exit(0)

    # Continuous run
    p.runContinuous()