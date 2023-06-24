#! /usr/bin/env python3
from PIL import Image, ImageColor
from vicariouspanel import NodeyezPanel
import math
import random
import sys
import vicariousbitcoin

class BlockHashDungeonPanel(NodeyezPanel):

    def __init__(self):
        """Instantiates a new Blockhash Dungeon panel"""

        # Define additional configuration attributes we have
        self.configAttributes = {
            # legacy key name mappings
            "colorBackground": "backgroundColor",           
            "colorTextFG": "textColor",
            "sleepInterval": "interval",
            # panel specific key names
            "bitcoinLogosFile": "bitcoinLogosFile",
            "bitcoinTilesFile": "bitcoinTilesFile",
        }

        # Define our defaults (all panel specific key names should be listed)
        self._defaultattr("bitcoinLogosFile", "../images/blockhash-dungeon-bitcoin-logos.png")
        self._defaultattr("bitcoinTilesFile", "../images/blockhash-dungeon-bitcoin-tiles.png")
        self._defaultattr("footerEnabled", False)
        self._defaultattr("interval", 540)
        self._defaultattr("pagingEnabled", False)
        self._defaultattr("watermarkAnchor", "bottom")

        # Initialize
        super().__init__(name="blockhashdungeon")

    def fetchData(self):
        """Fetches all the data needed for this panel"""

        self.blocknumber = vicariousbitcoin.getcurrentblock()
        self.blockhash = vicariousbitcoin.getblockhash(self.blocknumber)

    def _dfsBuildMaze(self, maze, x, y, d, t):
        n = maze[x][y]
        if not n['v']:
            n['v'] = True
            r = t + (int(random.random() * 3) - 1)  # -1, 0, 1 for floor tile change
            r = 0 if r < 0 else r
            r = 6 if r > 6 else r                   # 6 is floorPerTheme
            n['t'] = r                              # sets floor tile number to use
            n[d + 'o'] = True       # its open where we came from
            n[d + 'a'] = False      # and no longer available to try
            # determine availability based on border walls in direction
            availDef = {"na": y>0, "ea": x < len(maze) -1, "wa": x>0, "sa": y < len(maze[x])-1}
            availDirs = []
            for k in availDef.keys():
                if n[k]:
                    if availDef[k]:
                        availDirs.append(k)
                    else:
                        n[k] = False
            dirDef = {"na": [x, y-1, "s"], "ea": [x+1,y,"w"], "wa": [x-1,y,"e"], "sa": [x,y+1,"n"]}
            while len(availDirs):
                slot = int(random.random() * len(availDirs))    # pick a direction at random
                dir = availDirs[slot]
                del availDirs[slot]
                n[dir] = False
                if not maze[dirDef[dir][0]][dirDef[dir][1]]["v"]:
                    n[dir[0:1] + "o"] = True
                    maze = self._dfsBuildMaze(maze, dirDef[dir][0], dirDef[dir][1], dirDef[dir][2], r)
            maze[x][y] = n
        return maze

    def run(self):

        self.headerText = f"Blockhash Dungeon|Level {self.blocknumber}"
        super().startImage()

        # Load tile and logo files
        iconsize = 32
        tiles  = Image.open(self.bitcoinTilesFile)
        tileIconsWide = tiles.getbbox()[2] // iconsize
        tileIconsHigh = tiles.getbbox()[3] // iconsize
        logos  = Image.open(self.bitcoinLogosFile)
        logoIconsWide = logos.getbbox()[2] // iconsize
        logoIconsHigh = logos.getbbox()[3] // iconsize

        # Determine maximum tiles for our image width and height
        headerIconsHigh = math.ceil((self.height//10)/iconsize)
        imageIconsWide = self.width//iconsize
        imageIconsHigh = self.height//iconsize - headerIconsHigh
        imageIconsWide = imageIconsWide - 1 if (imageIconsWide % 2) == 0 else imageIconsWide # must be odd
        imageIconsHigh = imageIconsHigh - 1 if (imageIconsHigh % 2) == 0 else imageIconsHigh # must be odd

        # Determine the offset for generating the maze
        artLeft = (self.width - (imageIconsWide * iconsize))//2
        artTop = (headerIconsHigh * iconsize) + \
              (((self.height - (headerIconsHigh * iconsize)) - (imageIconsHigh * iconsize))//2)

        # Get tile theme to use
        floorPerTheme = 6
        wallsPerTheme = 2
        tilesPerTheme = floorPerTheme + wallsPerTheme        
        bhIdx = len(self.blockhash)
        bhIdx -= 2
        theme = int(self.blockhash[bhIdx:bhIdx+2],16) % (tileIconsWide * tileIconsHigh / tilesPerTheme)
        themeX = iconsize * tilesPerTheme if theme % 2 == 1 else 0
        themeY = (theme//2) * iconsize
        # Get starting floor tile (0..5)
        bhIdx -= 2
        floorTile = int(self.blockhash[bhIdx:bhIdx+2],16) % floorPerTheme
        floorTileX = themeX + (floorTile * iconsize)
        floorTileImage = tiles.crop((floorTileX, themeY, floorTileX + iconsize, themeY + iconsize))
        # Get the wall tile (0..1)
        bhIdx -= 2
        wallTile = int(self.blockhash[bhIdx:bhIdx+2],16) % wallsPerTheme
        wallTileX = themeX + ((floorPerTheme + wallTile) * iconsize)
        wallTileImage = tiles.crop((wallTileX, themeY, wallTileX + iconsize, themeY + iconsize))
        # Get randomization for the maze
        bhIdx -= 6
        random.seed(int(self.blockhash[bhIdx:bhIdx+6],16))

        # Initialize floor of the maze and itemMap
        itemMap = [] # tracks positions where we've put things
        for c in range(imageIconsWide):
            itemMap.append([])
            for r in range(imageIconsHigh):
                itemMap[c].append(0)
                # paste in the floor
                self.canvas.paste(floorTileImage, (artLeft+(c * iconsize), artTop+(r * iconsize)))
        # Initialize the maze itself
        maze = []
        for c in range(imageIconsWide//2):
            maze.append([])
            for r in range(imageIconsHigh//2):
                maze[c].append({'v':False, \
                                'no':False,'eo':False,'wo':False,'so':False, \
                                'na':True, 'ea':True, 'wa':True, 'sa':True, \
                                't':0})
        maze = self._dfsBuildMaze(maze, 0, 0, 'w', floorTile)

        # Draw the walls and floor of the maze to the canvas
        changeFloorTiles = True
        for r in range(imageIconsHigh//2):
            for c in range(imageIconsWide//2):
                if changeFloorTiles:
                    # new floor tile
                    floorTile = maze[c][r]['t'] % floorPerTheme
                    floorTileX = themeX + (floorTile * iconsize)
                    floorTileImage.close()
                    floorTileImage = tiles.crop((floorTileX, themeY, floorTileX + iconsize, themeY + iconsize))
                    self.canvas.paste(floorTileImage, (artLeft+(((c*2)+1)*iconsize), artTop+(((r*2)+0)*iconsize)))
                    self.canvas.paste(floorTileImage, (artLeft+(((c*2)+0)*iconsize), artTop+(((r*2)+1)*iconsize)))
                    self.canvas.paste(floorTileImage, (artLeft+(((c*2)+1)*iconsize), artTop+(((r*2)+1)*iconsize)))
                # wall tiles
                # - base position
                self.canvas.paste(wallTileImage, (artLeft+(((c*2)+0)*iconsize), artTop+(((r*2)+0)*iconsize)))
                itemMap[(c*2)+0][(r*2)+0]=1
                if not maze[c][r]['no']:                            # draw wall if north closed (also top border)
                    self.canvas.paste(wallTileImage, (artLeft+(((c*2)+1)*iconsize), artTop+(((r*2)+0)*iconsize)))
                    itemMap[(c*2)+1][(r*2)+0]=1
                if not maze[c][r]['wo']:                            # draw wall if west closed (also left border)
                    self.canvas.paste(wallTileImage, (artLeft+(((c*2)+0)*iconsize), artTop+(((r*2)+1)*iconsize)))
                    itemMap[(c*2)+0][(r*2)+1]=1
                if c == (imageIconsWide//2) - 1:                    # draw right border when on last column of row
                    # draw right side border of maze
                    rightBorderX = artLeft+(((c*2)+2)*iconsize)
                    rightBorderY = artTop +(((r*2)+0)*iconsize)
                    self.canvas.paste(wallTileImage, (rightBorderX, rightBorderY))
                    itemMap[(c*2)+2][(r*2)+0]=1
                    rightBorderY += iconsize
                    tmy = 1
                    if r == (imageIconsHigh//2) - 1:                # check if last row
                        rightBorderY += iconsize                    # leave open for exit, advance to bottom
                        tmy = 2
                    self.canvas.paste(wallTileImage, (rightBorderX, rightBorderY))
                    itemMap[(c*2)+2][(r*2)+tmy]=1
                if r == (imageIconsHigh//2) - 1:                    # draw bottom border when on last row
                    # draw bottom border of maze
                    bottomBorderX = artLeft+(((c*2)+0)*iconsize)
                    bottomBorderY = artTop +(((r*2)+2)*iconsize)
                    self.canvas.paste(wallTileImage, (bottomBorderX, bottomBorderY))
                    itemMap[(c*2)+0][(r*2)+2]=1
                    bottomBorderX += iconsize
                    self.canvas.paste(wallTileImage, (bottomBorderX, bottomBorderY))
                    itemMap[(c*2)+1][(r*2)+2]=1

        # Add some logos
        logostodraw = imageIconsHigh//2
        logostotry = 1000
        logosused = []
        while logostodraw > 0 and logostotry > 0:
            logostotry -= 1
            # get random position
            bhIdx = bhIdx-4 if bhIdx-4 >= 20 else len(self.blockhash)-(4+int(random.random()*7))
            c = int(self.blockhash[bhIdx:bhIdx+4],16) % imageIconsWide
            bhIdx = bhIdx-4 if bhIdx-4 >= 20 else len(self.blockhash)-(4+int(random.random()*8))
            r = int(self.blockhash[bhIdx:bhIdx+4],16) % imageIconsHigh
            # see if the area is clear
            if itemMap[c][r] == 0:
                # get random logo
                bhIdx = bhIdx-2 if bhIdx-2 >= 0 else len(self.blockhash)-(2+int(random.random()*3))
                logoTileX = int(self.blockhash[bhIdx:bhIdx+2],16) % logoIconsWide
                bhIdx = bhIdx-2 if bhIdx-2 >= 0 else len(self.blockhash)-(2+int(random.random()*4))
                logoTileY = int(self.blockhash[bhIdx:bhIdx+2],16) % logoIconsHigh
                # check for dupes
                i = (logoTileY * iconsize) + logoTileX    # id
                if i in logosused:              # disallow dupes
                    continue
                logoTileImage = logos.crop((logoTileX*iconsize,logoTileY*iconsize,(logoTileX+1)*iconsize,(logoTileY+1)*iconsize))
                # put into the image
                self.canvas.paste(logoTileImage, (artLeft+(c*iconsize),artTop+(r*iconsize)), logoTileImage)
                # mark as spot in use
                itemMap[c][r] = 1
                logostodraw -= 1
                logosused.append(i)

        # Close tile and logo files
        floorTileImage.close()
        wallTileImage.close()
        tiles.close()
        logos.close()
        super().finishImage()

# --------------------------------------------------------------------------------------
# Entry point if running this script directly
# --------------------------------------------------------------------------------------

if __name__ == '__main__':
    p = BlockHashDungeonPanel()

    # If arguments were passed in, treat as a single run
    if len(sys.argv) > 1:
        arg0 = sys.argv[0]
        if sys.argv[1] in ['-h','--help']:
            print(f"Produces a retro gaming style maze based on Bitcoin Blockhash values")
            print(f"Usage:")
            print(f"1) Call without arguments to run continuously using configured defaults")
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