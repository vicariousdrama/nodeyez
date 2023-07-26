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
            "renderActivePubkeysPerDay": "renderActivePubkeysPerDay",
            "renderBadgeDefinitionsPerDay": "renderBadgeDefinitionsPerDay",
            "renderZapsPerDay": "renderZapsPerDay",
            "statsUrl": "statsUrl",
            "useTor": "useTor",
        }

        # Define our defaults (all panel specific key names should be listed)
        self._defaultattr("attributionColor", "#A020A0")
        self._defaultattr("attributionLine", "Data from Nostr.Band")
        self._defaultattr("graphAverageColor", "#8888ff")
        self._defaultattr("graphBorderColor", "#888888")
        self._defaultattr("graphDataColors", ["#A020A0", "#0000ff", "#00ff00", "#D0C000", "#ff0000", "#00ffff", "#800000", "#808080", "#008000", "#800080", "#ff00ff", "#008080"])
        self._defaultattr("headerText", "Nostr.Band Stats")
        self._defaultattr("interval", 86400)
        self._defaultattr("renderActivePubkeysPerDay", True)
        self._defaultattr("renderBadgeDefinitionsPerDay", True)
        self._defaultattr("renderZapsPerDay", True)
        self._defaultattr("statsUrl", "https://stats.nostr.band/stats_api?method=stats&options=")
        self._defaultattr("useTor", True)
        self._defaultattr("watermarkAnchor", "bottom")

        # Initialize
        super().__init__(name="nostrbandstats")

    def fetchData(self):
        """Fetches all the data needed for this panel"""

        self.nostrStats = vicariousnetwork.getnostrstats(self.useTor, self.statsUrl)

        # transform it to format more native to our charting functions
        self.transformData()

        # set date range for charts based on data
        activeRelays, _ = vicariouschart.getNestedField(self.transformStats, "daily.datasets.active_relays")
        self.dateBegin = activeRelays[0]["d"]
        self.dateEnd = activeRelays[-1]["d"]

    def transformData(self):
        # make a copy to work with
        tstats = dict(self.nostrStats)
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
        self.transformStats = tstats

    def renderChart(self, pageSuffix, headerText, baseKey, colorIndex):
        attributionSize = int(self.height * 14/320)
        labelSize = int(self.height * 12/320)
        self.headerText = headerText
        self.pageSuffix = pageSuffix
        super().startImage()
        nestedField = f"daily.datasets.{baseKey}_flat"
        chartStats, _ = vicariouschart.getNestedField(self.transformStats, nestedField)
        vicariouschart.drawBarChart(draw=self.draw, left=0, top=self.getInsetTop(), 
            width=self.width, height=self.getInsetHeight(), 
            theList=chartStats, fieldName=None, 
            showLabels=True, chartLabel="", grouping=1, 
            valueColor=self.graphDataColors[colorIndex], 
            showAverage=True, averageColor=self.graphAverageColor, 
            movingAverageDuration=7, movingAverageColor="#33ff33", movingAverageWidth=2,
            borderColor=self.graphBorderColor)
        vicariouschart.drawLabel(self.draw, self.dateBegin, labelSize, "tl", 0 + 2, self.getInsetTop()+2 )
        vicariouschart.drawLabel(self.draw, self.dateEnd, labelSize, "tr", self.width - 3, self.getInsetTop()+2)
        vicarioustext.drawbottomlefttext(self.draw, self.attributionLine, attributionSize, 0, self.height, ImageColor.getrgb(self.attributionColor))
        super().finishImage()

    def run(self):

        # render zaps per day chart
        if self.renderZapsPerDay:
            self.renderChart("zapsperday", "Nostr Zaps per Day", "kind_9735", 3)

        # render badge definitions per day chart
        if self.renderBadgeDefinitionsPerDay:
            self.renderChart("badgescreatedperday", "Nostr Badges Created per day", "kind_30009", 1)

        # render active pubkeys chart
        if self.renderActivePubkeysPerDay:
            self.renderChart("activepubkeysperday", "Nostr Pubkeys Active per Day", "active_pubkeys", 0)

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