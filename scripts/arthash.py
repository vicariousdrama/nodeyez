#! /usr/bin/env python3
from PIL import ImageColor
from vicariouspanel import NodeyezPanel
import math
import random
import sys
import vicariousbitcoin

class ArtHashPanel(NodeyezPanel):

    def __init__(self):
        """Instantiates a new Art Hash panel"""

        # Define which additional attributes we have
        self.configAttributes = {
            # legacy key name mappings
            "colorBackground": "backgroundColor",
            "colorShapeOutline": "shapeOutlineColor",
            "colorTextFG": "textColor",
            "sleepInterval": "interval",
            # panel specific key names
            "shapeOutlineColor": "shapeOutlineColor",
        }

        # Define our defaults (all panel specific key names should be listed)
        self._defaultattr("shapeOutlineColor", "#ffffff")

        # Initialize
        super().__init__(name="arthash")

    def fetchData(self):
        """Fetches all the data needed for this panel"""

        self.blocknumber = vicariousbitcoin.getcurrentblock()
        self.blockhash = vicariousbitcoin.getblockhash(self.blocknumber)

    def setArtPosition(self):
        """Calculates the Top, Left, Height, and Width of the art
        
        A calculation of the bounding box area for the art that will be
        generated will be constrained to the largest square that can fit
        within the canvas while allowing for the the header and footer.
        """

        # Act like a singleton, only calculate this the first time
        if hasattr(self, "artHeight"):
            return
        artPadding = 5
        insetTop = self.getInsetTop()
        insetWidth = self.getInsetWidth() - artPadding * 2
        insetHeight = self.getInsetHeight() - artPadding * 2
        self.artHeight = insetHeight if insetWidth > insetHeight else insetWidth
        self.artWidth = self.artHeight
        self.artTop = insetTop + (insetHeight//2) - (self.artHeight//2)
        self.artLeft = (insetWidth//2) - (self.artWidth//2)

    def run(self):

        self.headerText = f"Blockhash Art|Block {self.blocknumber}"
        super().startImage()
        self.setArtPosition()

        pwidth=1  # line width for polygons defining the triangles
        cwidth=2  # line width for chords
        outlinecolor=ImageColor.getrgb(self.shapeOutlineColor)
        # basic pythagoras theorem math
        triclen=self.artWidth/4  # hypotenuese
        triblen=self.artWidth/8  # base
        trialen=int(math.sqrt((triclen*triclen)-(triblen*triblen))) # height
        # iterate over last 24 bytes of the blockhash
        for i in range(24):
            s = ((8+i)*2)   # jump ahead 8 bytes (16 characters)
            e = s+2         # 2 characters per each hexadecimal color part
            c = self.blockhash[s:e]  # get the actual color
            if i%3 == 0:             # capture as red component
                r = c
            if i%3 == 1:             # capture as blue component
                g = c
            if i%3 == 2:             # capture as green component
                b = c
            # adjust y offset for top/bottom row based on how many read so far
            j = i
            y = 0
            if j > 11:
                j = j - 12
                y = triclen*2
            # first three (0-2) are top triangles from left to right of the left hexagon
            if j == 0: # red
                self.draw.polygon(((self.artLeft+triblen,y+self.artTop+triclen-trialen),(self.artLeft,y+self.artTop+triclen),(self.artLeft+triclen,y+self.artTop+triclen)),fill=ImageColor.getrgb("#" + c + "0000"),outline=outlinecolor,width=pwidth)
            elif j == 1: # green
                self.draw.polygon(((self.artLeft+triblen,y+self.artTop+triclen-trialen),(self.artLeft+triclen,y+self.artTop+triclen),(self.artLeft+triblen+triclen,y+self.artTop+triclen-trialen)),fill=ImageColor.getrgb("#00" + c + "00"),outline=outlinecolor,width=pwidth)
            elif j == 2: # blue
                self.draw.polygon(((self.artLeft+triclen,y+self.artTop+triclen),(self.artLeft+triblen+triclen,y+self.artTop+triclen-trialen),(self.artLeft+(triclen*2),y+self.artTop+triclen)),fill=ImageColor.getrgb("#0000" + c),outline=outlinecolor,width=pwidth)
                # draw the top half circle with the combined color
                self.draw.chord(((self.artLeft+triblen,y+self.artTop+triblen),(self.artLeft+triclen+triblen,y+self.artTop+triclen+triblen)),start=180,end=360,fill=ImageColor.getrgb("#"+r+g+b),outline=outlinecolor,width=cwidth)
            # second three (3-5) are top triangles from left to right of the right hexagon
            elif j == 3: # red
                self.draw.polygon(((self.artLeft+(triclen*2)+triblen,y+self.artTop+triclen-trialen),(self.artLeft+(triclen*2),y+self.artTop+triclen),(self.artLeft+(triclen*3),y+self.artTop+triclen)),fill=ImageColor.getrgb("#" + c + "0000"),outline=outlinecolor,width=pwidth)
            elif j == 4: # green
                self.draw.polygon(((self.artLeft+(triclen*2)+triblen,y+self.artTop+triclen-trialen),(self.artLeft+(triclen*3),y+self.artTop+triclen),(self.artLeft+(triclen*3)+triblen,y+self.artTop+triclen-trialen)),fill=ImageColor.getrgb("#00" + c + "00"),outline=outlinecolor,width=pwidth)
            elif j == 5: # blue
                self.draw.polygon(((self.artLeft+(triclen*3)+triblen,y+self.artTop+triclen-trialen),(self.artLeft+(triclen*3),y+self.artTop+triclen),(self.artLeft+(triclen*4),y+self.artTop+triclen)),fill=ImageColor.getrgb("#0000" + c),outline=outlinecolor,width=pwidth)
                # draw the top half circle with the combined color
                self.draw.chord(((self.artLeft+triblen+(triclen*2),y+self.artTop+triblen),(self.artLeft+triclen+triblen+(triclen*2),y+self.artTop+triclen+triblen)),start=180,end=360,fill=ImageColor.getrgb("#"+r+g+b),outline=outlinecolor,width=cwidth)
            # third three (6-8) are bottom triangles from left to right of the left hexagon
            elif j == 6: # red
                self.draw.polygon(((self.artLeft,y+self.artTop+triclen),(self.artLeft+triclen,y+self.artTop+triclen),(self.artLeft+triblen,y+self.artTop+triclen+trialen)),fill=ImageColor.getrgb("#" + c + "0000"),outline=outlinecolor,width=pwidth)
            elif j == 7: # green
                self.draw.polygon(((self.artLeft+triclen,y+self.artTop+triclen),(self.artLeft+triblen,y+self.artTop+triclen+trialen),(self.artLeft+triclen+triblen,y+self.artTop+triclen+trialen)),fill=ImageColor.getrgb("#00" + c + "00"),outline=outlinecolor,width=pwidth)
            elif j == 8: # blue
                self.draw.polygon(((self.artLeft+triclen,y+self.artTop+triclen),(self.artLeft+triclen+triblen,y+self.artTop+triclen+trialen),(self.artLeft+(triclen*2),y+self.artTop+triclen)),fill=ImageColor.getrgb("#0000" + c),outline=outlinecolor,width=pwidth)
                # draw bottom half circle with combined color
                self.draw.chord(((self.artLeft+triblen,y+self.artTop+triblen),(self.artLeft+triclen+triblen,y+self.artTop+triclen+triblen)),start=0,end=180,fill=ImageColor.getrgb("#"+r+g+b),outline=outlinecolor,width=cwidth)
            # fourth three (9-11) are bottom triangles from left to right of the right hexagon
            elif j == 9: # red
                self.draw.polygon(((self.artLeft+(triclen*2),y+self.artTop+triclen),(self.artLeft+(triclen*2)+triblen,y+self.artTop+triclen+trialen),(self.artLeft+(triclen*3),y+self.artTop+triclen)),fill=ImageColor.getrgb("#" + c + "0000"),outline=outlinecolor,width=pwidth)
            elif j == 10: # green
                self.draw.polygon(((self.artLeft+(triclen*3),y+self.artTop+triclen),(self.artLeft+(triclen*2)+triblen,y+self.artTop+triclen+trialen),(self.artLeft+(triclen*3)+triblen,y+self.artTop+triclen+trialen)),fill=ImageColor.getrgb("#00" + c + "00"),outline=outlinecolor,width=pwidth)
            elif j == 11: # blue
                self.draw.polygon(((self.artLeft+(triclen*3),y+self.artTop+triclen),(self.artLeft+(triclen*3)+triblen,y+self.artTop+triclen+trialen),(self.artLeft+(triclen*4),y+self.artTop+triclen)),fill=ImageColor.getrgb("#0000" + c),outline=outlinecolor,width=pwidth)
                # draw bottom half circle with combined color
                self.draw.chord(((self.artLeft+triblen+(triclen*2),y+self.artTop+triblen),(self.artLeft+triclen+triblen+(triclen*2),y+self.artTop+triclen+triblen)),start=0,end=180,fill=ImageColor.getrgb("#"+r+g+b),outline=outlinecolor,width=cwidth)
        super().finishImage()


# --------------------------------------------------------------------------------------
# Entry point if running this script directly
# --------------------------------------------------------------------------------------

if __name__ == '__main__':
    p = ArtHashPanel()

    # If arguments were passed in, treat as a single run
    if len(sys.argv) > 1:
        arg0 = sys.argv[0]
        if sys.argv[1] in ['-h','--help']:
            print(f"Produces artwork deterministically based on Bitcoin blockhash values")
            print(f"Usage:")
            print(f"1) Call without arguments to run continuously using the configuration or defaults")
            print(f"2) Pass the desired block number as an argument as follows")
            print(f"   {arg0} 722231")
            print(f"3) Pass the desired block number, width and height as arguments")
            print(f"   {arg0} 722231 1920 1080")
            exit(0)
        p.blocknumber = int(sys.argv[1])
        p.blockhash = vicariousbitcoin.getblockhash(p.blocknumber)
        if len(sys.argv) > 3:
            p.width = int(sys.argv[2])
            p.height = int(sys.argv[3])
        p.pageSuffix = str(p.blocknumber)
        p.run()
        exit(0)

    # Continuous run
    p.runContinuous()