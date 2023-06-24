#! /usr/bin/env python3
from PIL import ImageColor
from vicariouspanel import NodeyezPanel
import sys
import vicariousbitcoin
import vicariouschart
import vicariouslookup
import vicariousnetwork
import vicarioustext

class <Template Class>Panel(NodeyezPanel):

    def __init__(self):
        """Instantiates a new <Template Name> panel"""

        # Define which additional attributes we have
        self.configAttributes = {
            # legacy key name mappings
            "colorBackground": "backgroundColor",
            "colorTextFG": "textColor",
            "sleepInterval": "interval",
            # panel specific key names
        }

        # Define our defaults (all panel specific key names should be listed)
        self._defaultattr("headerText", "<Template Name>")
        self._defaultattr("interval", 120)

        # Initialize
        super().__init__(name="<Template Class Lower>")

    def fetchData(self):
        """Fetches all the data needed for this panel"""

        pass

    def run(self):

        super().startImage()

        # Your image logic here

        super().finishImage()

# --------------------------------------------------------------------------------------
# Entry point if running this script directly
# --------------------------------------------------------------------------------------

if __name__ == '__main__':

    p = <Template Class>Panel()

    # If arguments were passed in, treat as a single run
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h','--help']:
            print(f"Creates a summary image of <Template Name>")
            print(f"Usage:")
            print(f"1) Call without arguments to run continuously using the configuration or defaults")
            print(f"2) Call with an argument other then -h or --help to run once and exit")
        else:
            p.fetchData()
            p.run()
        exit(0)

    # Continuous run
    p.runContinuous()