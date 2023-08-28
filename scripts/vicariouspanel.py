# import packages
from PIL import Image, ImageDraw, ImageColor
from datetime import datetime
import glob
import json
import math
import os
import time
import vicarioustext
import vicariouswatermark

class NodeyezPanel:
    """
    A class used as the base class for Nodeyez Panel scripts
    """

    def __init__(self,
                 name: str = None,
                 ):
        """Instantiates a new panel

        Parameters
        ----------
        name : str
            The name to distinguish this panel type. Used in
            referencing configuration files and forms the basis of
            output file names. This value should be unique across
            panel definitions and is recommended to be named the same
            as the script file.
        """

        self.name = name
        self.logprefix = name
        # Establish the last time this panel was run
        self.lastRan = 0
        # Other initializations
        self.canvas = None
        self.draw = None
        self.minimumInterval = 30
        self._defaultattr("backgroundColor", "#000000")
        self._defaultattr("blockclockAddress", "21.21.21.21")
        self._defaultattr("blockclockEnabled", False)
        self._defaultattr("blockclockPassword", "")
        self._defaultattr("dataDirectory", "../data/")
        self._defaultattr("enabled", True)
        self._defaultattr("footerEnabled", True)
        self._defaultattr("headerColor", "#ffffff")
        self._defaultattr("headerEnabled", True)
        self._defaultattr("headerText", self.name)
        self._defaultattr("height", 320)
        self._defaultattr("interval", 600)
        self._defaultattr("pagingEnabled", True)
        self._defaultattr("pageNumber", None)
        self._defaultattr("pageCount", None)
        self._defaultattr("textColor", "#ffffff")
        self._defaultattr("watermarkEnabled", True)
        self._defaultattr("watermarkAnchor", "bottomleft")
        self._defaultattr("width", 480)
        # Load config
        self.setConfig()

        # Ensure directory exists
        if not os.path.exists(self.dataDirectory):
            os.makedirs(self.dataDirectory)


    def log(self, s):
        print(f"{self.logprefix}: {s}")

    def _defaultattr(self, attributeName: str, attributeValue: any):
        if not hasattr(self, attributeName):
            self.__setattr__(attributeName, attributeValue)

    def setConfig(self, config = None):
        """Sets configuration for this panel
        
        Parameters
        ----------
        config : (dict,str), optional
            If this parameter is provided, then the configuration will
            be set based upon the parameter type. If it is a dictionary
            then it will be assigned. If it is a string, then the path
            will be checked for existence, and attempted to be loaded
            as JSON. If not provided, then the default configuration
            path based upon the instance's shortName will be tried.
        """

        configDict = None
        configFile = None
        # Assignment from passed in variables
        if config is not None:
            if type(config) is dict:
                configDict = config
            if type(config) is str:
                configFile = config
        # Set file to default config path if none was passed in
        if configFile is None:
            configFile = f"../config/{self.name}.json"
        # If we dont yet have a dict, load from the configFile
        if config is None:
            if os.path.exists(configFile):
                with open(configFile) as f:
                    config = json.load(f)
        # If we still don't have a config, then initialize to empty
        if config is None:
            config = {}
        # See if our config is nested in the config or top level
        if self.name in config:
            self.config = config[self.name]
        else:
            self.config = config
        # Update common attributes
        configAttributes = ["backgroundColor", "blockclockAddress", "blockclockEnabled",
            "blockclockPassword", "enabled", "header", "headerColor", "height",
            "interval", "name", "footerEnabled", "headerEnabled", "pagingEnabled",
            "watermarkEnabled", "textColor", "width"]
        for attrName in configAttributes:
            if attrName in self.config:
                self.__setattr__(attrName, self.config[attrName])
        # Update attributes defined in configattrs
        if self.configAttributes is not None:
            if type(self.configAttributes) is list:
                for attrName in self.configAttributes:
                    if attrName in self.config:
                        self.__setattr__(attrName, self.config[attrName])
            # support for mapping attributes
            if type(self.configAttributes) is dict:
                for attrName in self.configAttributes.keys():
                    if attrName in self.config:
                        self.__setattr__(self.configAttributes[attrName], self.config[attrName])

    def secondsUntilNextRun(self):
        """Returns the number of seconds before we run again"""

        self.interval = self.minimumInterval if self.interval < self.minimumInterval else self.interval
        return (self.lastRan + self.interval) - int(time.time())

    def isTimeToRun(self):
        """Indicates if the panel is elligible to run

        The panel is elligible to run based on when it was last run,
        the current time, and the setting of its interval.
        """

        # Only if this panel is enabled
        if not self.enabled:
            return False
        # Compare to when we last ran
        return self.secondsUntilNextRun() < 0

    def startImage(self, 
                   pageSuffix: str = None, 
                   pageNumber: int = None,
                   pageCount: int = None):
        """Initializes new image and draw object

        Begins creation of a new image and draw object based upon the
        width and height dimensions, background color and assigning as
        the canvas

        Parameters
        ----------
        pageSuffix : str, optional
            Defines a suffix that will be used in building the output
            filename, dominant to pageNumber. (default is None)
        pageNumber : int, optional
            Defines a suffix that will be used in building the output
            filename, subordinate to a pageSuffix. (default is None)
        pageCount : int, optional
            Defines the total pages of images expected to be generated
            as output
        """

        # Must not yet be initialized (use multiple instance for parallel image creation)
        if self.canvas is not None:
            raise Exception(f"{self.name}: Unable to start Image. Canvas already exists")
        # Initialize canvas
        backgroundColor = ImageColor.getrgb(self.backgroundColor)
        self.canvas = Image.new(mode="RGBA", size=(self.width, self.height), color=backgroundColor)
        # Initialize draw object
        self.draw = ImageDraw.Draw(self.canvas)
        # Setup for file name
        if pageSuffix is not None:
            self.pageSuffix = pageSuffix
        if pageNumber is not None:
            self.pageNumber = pageNumber
        if pageCount is not None:
            self.pageCount = pageCount
        # Set drawn state
        self.headerDrawn = False
        self.footerDrawn = False
        self.pagingDrawn = False
        self.watermarkDrawn = False

    def getOutputFile(self, fileExt: str = "png"):
        """Generates output filename with suffixes
        
        Derives a name for the output file based on the shortname
        assigned to this panel instance.  If a page suffix or page
        number has been previously established, that information 
        is concatenated with a hyphen as delimiter before the
        file extension

        Parameters
        ----------
        fileExt : str, optional
            The file extension to use for the output file. (default is 
            png)
        """

        baseFile = f"../imageoutput/{self.name}.{fileExt}"
        l = []
        if hasattr(self, "pageSuffix"):
            if self.pageSuffix is not None:
                l.append(self.pageSuffix)
        if hasattr(self, "pageNumber"):
            if self.pageNumber is not None:
                l.append(str(self.pageNumber))
        for v in l:
            if v is not None and len(v) > 0:
                p = baseFile.rpartition(".")
                baseFile = f"{p[0]}-{v}{p[1]}{p[2]}"
        return baseFile
    
    def finishImage(self):
        """Performs common finishing tasks for the image

        Renders the header if there is one, along with the footer and
        watermark, saves the file and frees up associated resources to
        reset the canvas and draw state
        """

        # Must have a canvas to work with
        if self.canvas is None:
            raise Exception(f"{self.name}: Unable to finish image. Canvas is not initialized")
        # Add the header
        if self.headerEnabled:
            if len(self.headerText) > 0:
                self._renderHeader()
        # Add the footer
        if self.footerEnabled:
            self._renderFooter()
        # Add the paging info
        pagingRendered = False
        if self.pagingEnabled:
            pagingRendered = self._renderPaging()
            if pagingRendered and self.watermarkAnchor == "bottomleft":
                self.watermarkAnchor = "bottom"
        # Add the watermark
        if self.watermarkEnabled:
            self._renderWatermark(anchor=self.watermarkAnchor)
        # Save image
        self._saveImage()
        # Cleanup resources
        self._cleanupResources()
        # Set last ran time
        self._markAsRan()

    def _markAsRan(self):
        self.lastRan = int(time.time())

    def _renderHeader(self):
        """Renders the header at the top of the canvas, sized to fit"""

        # Noop if not enabled
        if self.headerEnabled is False:
            return
        # Noop if no header
        if self.headerText is None or len(self.headerText) == 0:
            return
        # Noop if header already drawn
        if self.headerDrawn is not None and self.headerDrawn:
            return
        # Must have a canvas to work with
        if self.canvas is None:
            raise Exception(f"{self.name}: Unable to render header. Canvas is not initialized")
        # Set the color
        textColor = ImageColor.getrgb(self.textColor)
        if hasattr(self, "headerColor"):
            textColor = ImageColor.getrgb(self.headerColor)
        if not hasattr(self, "headerHeight"):
            maxHeight = self.canvas.height // 10
        else:
            maxHeight = self.headerHeight
        maxWidth = self.canvas.width
        maxFontSize = maxHeight
        minFontSize = 8
        # Start with standard size header and find largest that can fit
        fs,sw,sh = vicarioustext.getmaxfontsize(self.draw, self.headerText, maxWidth, maxHeight, True, maxFontSize, minFontSize)
        textFits = fs >= minFontSize
        ltext = ""
        ctext = self.headerText
        rtext = ""
        headerparts = self.headerText.split("|")
        if len(headerparts) > 1:
            ltext = headerparts[0]
            ctext = ""
            rtext = headerparts[1]
        if len(headerparts) > 2:
            ctext = headerparts[1]
            rtext = headerparts[2]
        if len(ltext) > 0:
            if textFits:
                vicarioustext.drawlefttext(draw=self.draw, s=ltext, fontsize=fs, x=0, y=maxHeight//2, textcolor=textColor, isbold=True)
            else:
                vicarioustext.drawtoplefttext(draw=self.draw, s=ltext, fontsize=fs, x=0, y=0, textcolor=textColor, isbold=True)
        if len(rtext) > 0:
            if textFits:
                vicarioustext.drawrighttext(draw=self.draw, s=rtext, fontsize=fs, x=self.width, y=maxHeight//2, textcolor=textColor, isbold=True)
            else:
                vicarioustext.drawbottomrighttext(draw=self.draw, s=rtext, fontsize=fs, x=self.width, y=maxHeight, textcolor=textColor, isbold=True)
        # centered considered most important and will be drawn last to overlap as needed
        if len(ctext) > 0:
            vicarioustext.drawcenteredtext(draw=self.draw, s=ctext, fontsize=fs, x=self.width//2, y=maxHeight//2, textcolor=textColor, isbold=True)                    

        self.headerDrawn = True

    def _renderFooter(self):
        """Renders current date and time at bottomright of canvas"""

        # Noop if footer already drawn
        if self.footerDrawn is not None and self.footerDrawn:
            return
        if self.footerEnabled is False:
            return
        # Must have a canvas to work with
        if self.canvas is None:
            raise Exception(f"{self.name}: Unable to render footer. Canvas is not initialized")
        isoDate = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        textToDisplay = f"as of {isoDate}"
        # Set the color
        textColor = ImageColor.getrgb(self.textColor)
        if hasattr(self, "footerColor"):
            textColor = ImageColor.getrgb(self.headerColor)
        fontSize = self.canvas.height // 26
        vicarioustext.drawbottomrighttext(self.draw, s=textToDisplay, fontsize=fontSize, x=self.canvas.width, y=self.canvas.height, textcolor=textColor, isbold=False)
        self.footerDrawn = True

    def _renderPaging(self):
        """Renders the paging information at the bottomleft of canvas

        Paging information will only be rendered if marked to do so
        via the showPaging attribute, and there is a setting for
        pageNumber and pageCount where pageNumber must be greater than
        zero, and pageCount must be greater than one.
        
        Returns
        -------
        bool:
            indicates whether paging information was rendered
        """
        
        # Must have a canvas to work with
        if self.canvas is None:
            raise Exception(f"{self.name}: Unable to render paging. Canvas is not initialized")
        if self.pagingEnabled is False or \
            self.pageCount is None or \
            self.pageCount <= 1 or \
            self.pageNumber is None or \
            self.pageNumber <= 0:
            return False
        else:
            # Noop if paging already drawn
            if self.pagingDrawn is not None and self.pagingDrawn:
                return True
            textToDisplay = f"PAGE {self.pageNumber} of {self.pageCount}"
            textColor = ImageColor.getrgb(self.textColor)
            fontSize = self.canvas.height // 26
            vicarioustext.drawbottomlefttext(self.draw, s=textToDisplay, fontsize=fontSize, x=0, y=self.canvas.height, textcolor=textColor, isbold=False)
            self.pagingDrawn = True
            return True

    def _renderWatermark(self, anchor="bottomleft", width=100):
        """Renders the Nodeyez watermark based on anchor position

        Parameters
        ----------
        anchor : str, optional
            The anchor position to render the watermark. Valid values
            are `bottomleft`, `bottom`, `bottomright`, `right`,
            `topright`, `top`, `topleft`, `left`. (default is 
            bottomleft)
        width : int, optional
            The width to make the watermark in pixels.  The height will
            be scaled accordingly. (default is 100)
        """

        # Noop if watermark already drawn
        if self.watermarkDrawn is not None and self.watermarkDrawn:
            return
        if self.watermarkEnabled is False:
            return
        # Must have a canvas to work with
        if self.canvas is None:
            raise Exception(f"{self.name}: Unable to render watermark. Canvas is not initialized")
        ratioWidthHeight = 8 # approximate, based on the svg file
        # determine top and left by anchor position
        if anchor == "bottom":      # typically safe
            left = (self.canvas.width//2)-(width//2)
            top = self.canvas.height - (width//ratioWidthHeight)
        elif anchor == "bottomright": # will typically interfere with footer
            left = self.canvas.width - width
            top = self.canvas.height - (width//ratioWidthHeight)
            top -= self.getFooterHeight()
        elif anchor == "right":       # will interfere with most images
            left = self.canvas.width - width
            top = self.canvas.height//2 - ((width//ratioWidthHeight)//2)
        elif anchor == "topright":    # may be free of header
            left = self.canvas.width - width
            top = 0
        elif anchor == "top":         # will typically interfere with header
            left = (self.canvas.width//2)-(width//2)
            top = 0
        elif anchor == "topleft":     # may be free of header
            left = 0
            top = 0
        elif anchor == "left":        # will interfere with most images
            left = 0
            top = self.canvas.height//2 - ((width//ratioWidthHeight)//2)
        else: # default bottomleft is generally best (recommended)
            left = 0
            top = self.canvas.height - (width//ratioWidthHeight)
        # apply it
        vicariouswatermark.do(canvas=self.canvas, width=width, box=(left,top))
        self.watermarkDrawn = True

    def _saveImage(self, outputFile: str = None):
        """Saves the current state of the canvas an image file

        Parameters
        ----------
        outputFile : str, optional
            An optional alternate filename to save the image. If no
            value is provided, then the calculated outputFile will be
            used based upon the shortName and pageNumber established
            when the class was instantiated and the image initialized.
        """

        saveAsFilePath = self.getOutputFile() if outputFile is None else outputFile
        # Must have a canvas to work with
        if self.canvas is None:
            raise Exception(f"{self.name}: Unable to save image. Canvas is not initialized")
        self.log(f"Saving file to {saveAsFilePath}")
        self.canvas.save(saveAsFilePath)

    def _cleanupResources(self):
        """Cleans up canvas and draw objects"""

        if self.canvas is not None:
            self.canvas.close()
            self.canvas = None
        self.draw = None
        self.headerDrawn = False
        self.footerDrawn = False
        self.pagingDrawn = False
        self.watermarkDrawn = False
    
    def runContinuous(self):
        """The basic logic to run continuously.
        
        This is a blocking call

        If the panel is not enabled, it will return immediately.

        While enabled, it will check if its time to run based on the
        interval set.  Once ready, the latest data is retrieved and
        the panel is run creating an image.  Finally, the process
        will sleep until ready for the next run.
        """

        sleptSinceRun = False
        while self.enabled:
            if self.isTimeToRun():
                self.fetchData()
                self.run()
                sleptSinceRun = False
            sleepTime = self.secondsUntilNextRun()
            sleepTime = 1 if sleepTime <= 0 and not sleptSinceRun else sleepTime
            if sleepTime > 0:
                self.log(f"sleeping for {sleepTime} seconds")
                time.sleep(sleepTime)
                sleptSinceRun = True

    def run(self):
        """Runs the panel one time, based on existing data gathered
        
        An inheriting class should override this method
        """

        self.startImage()
        # An inheriting class should call super().startImage(), perform
        # its customized rendering logic, and end with super().finishImage()
        self.finishImage()

        if self.blockclockEnabled:
            self.blockclockReport()

    def blockclockReport(self):
        """Placeholder to perform blockclock reporting
        
        An inheriting class should override this method
        """

        pass

    def fetchData(self):
        """Placeholder to retrieve any additional data
        
        An inheriting class should override this method
        """

        pass

    def getInsetBottom(self):
        """Returns the avaialble bottom

        Accounts for potential rendering of footer        
        """

        return self.getInsetTop() + self.getInsetHeight()

    def getInsetHeight(self):
        """Returns the available height
        
        Accounts for potential rendering of header and footer
        """

        # Must have a canvas to work with
        if self.canvas is None:
            raise Exception(f"{self.name}: Unable to calculate inset width. Canvas is not initialized")
        availHeight = self.height
        availHeight -= self.getInsetTop()
        footerHeight = self.getFooterHeight()
        pagingHeight = self.getPagingHeight()
        watermarkHeight = self.getWatermarkHeight() if "bottom" in self.watermarkAnchor else 0
        bottomHeight = 0
        bottomHeight = footerHeight if footerHeight > bottomHeight else bottomHeight
        bottomHeight = pagingHeight if pagingHeight > bottomHeight else bottomHeight
        bottomHeight = watermarkHeight if watermarkHeight > bottomHeight else bottomHeight
        availHeight -= bottomHeight
        return availHeight

    def getInsetTop(self):
        """Returns the available top
        
        Accounts for potential rendering of header
        """
        return self.getHeaderHeight()

    def getInsetWidth(self):
        """Returns the available width
        
        Accounts for potential rendering of header and footer
        """

        # Must have a canvas to work with
        if self.canvas is None:
            raise Exception(f"{self.name}: Unable to calculate inset width. Canvas is not initialized")
        return self.width

    def getHeaderHeight(self):
        """Returns the height of the header
        
        Accounts for sizing the header to fit, down to minimum font
        size. This will return the bottom pixel of the header from
        the top (0). If no header, then 0 is returned.
        """

        # Must have a canvas to work with
        if self.canvas is None:
            raise Exception(f"{self.name}: Unable to calculate header height. Canvas is not initialized")
        if self.headerEnabled is False or self.headerText is None or len(self.headerText) == 0:
            return 0
        if not hasattr(self, "headerHeight"):
            maxHeight = self.canvas.height // 10
        else:
            maxHeight = self.headerHeight
        maxWidth = self.canvas.width
        maxFontSize = maxHeight
        minFontSize = 8
        fs,sw,sh = vicarioustext.getmaxfontsize(self.draw, self.headerText, maxWidth, maxHeight, True, maxFontSize, minFontSize)
        if fs < minFontSize and self.headerText("|") > -1:
            # split left aligned and right aligned will use available height
            return maxHeight
        # whether fits or not, when single part, its always vertically centered
        return (maxHeight//2) + (sh//2)

    def getFooterHeight(self):
        """Returns the height of the footer, if shown"""

        # Must have a canvas to work with
        if self.canvas is None:
            raise Exception(f"{self.name}: Unable to calculate footer height. Canvas is not initialized")
        if self.footerEnabled is False:
            return 0
        isoDate = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        textToDisplay = f"as of {isoDate}"
        fontSize = self.canvas.height // 26
        _,sh,_ = vicarioustext.gettextdimensions(self.draw, s=textToDisplay, fontsize=fontSize, isbold=False)
        return sh
    
    def getFooterWidth(self):
        """Returns the width of the footer, if shown"""

        # Must have a canvas to work with
        if self.canvas is None:
            raise Exception(f"{self.name}: Unable to calculate footer height. Canvas is not initialized")
        if self.footerEnabled is False:
            return 0
        isoDate = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        textToDisplay = f"as of {isoDate}"
        fontSize = self.canvas.height // 26
        sw,_,_ = vicarioustext.gettextdimensions(self.draw, s=textToDisplay, fontsize=fontSize, isbold=False)
        return sw

                
    def getPagingHeight(self):
        """Returns the height of paging information, if shown"""

        # Must have a canvas to work with
        if self.canvas is None:
            raise Exception(f"{self.name}: Unable to calculate paging height. Canvas is not initialized")
        if self.pagingEnabled is False or \
            self.pageCount is None or \
            self.pageCount <= 1 or \
            self.pageNumber is None or \
            self.pageNumber <= 0:
            return 0
        else:
            textToDisplay = f"PAGE {self.pageNumber} of {self.pageCount}"
            fontSize = self.canvas.height // 26
            _,sh,_ = vicarioustext.gettextdimensions(self.draw, s=textToDisplay, fontsize=fontSize, isbold=False)
            return sh

    def getWatermarkHeight(self, width=100):
        """Renders the height of the watermark, if shown

        Parameters
        ----------
        width : int, optional
            The width that the watermark will be in pixels. The height
            is calculated accordingly. (default is 100)
        """

        # Must have a canvas to work with
        if self.canvas is None:
            raise Exception(f"{self.name}: Unable to calculate watermark height. Canvas is not initialized")
        if self.watermarkEnabled is False:
            return 0
        ratioWidthHeight = 8 # approximate, based on the svg file
        return math.ceil(width/ratioWidthHeight)

    def removeOldImages(self, fileExt: str = "png"):
        globPattern = f"../imageoutput/{self.name}"
        if hasattr(self, "pageSuffix"):
            if len(self.pageSuffix) > 0:
                globPattern = f"{globPattern}-{self.pageSuffix}"
        globPattern = f"{globPattern}*.{fileExt}"
        files = glob.glob(globPattern)
        for file in files:
            os.remove(file)

    def resizeImageToInset(self, im):
        im = self.resizeImageToWidth(im)
        ih = self.getInsetHeight()
        if im.height <= ih: return im
        irh = float(im.width)/float(im.height)
        im2 = im.resize((int(ih*irh),ih),resample=Image.NEAREST) #,Image.Resampling.LANCZOS)
        im.close()
        return im2

    def resizeImageToWidth(self, im):
        width = im.width
        if width == self.width: return im
        height = im.height
        ratio = self.width / width
        newwidth = int(width*ratio)
        newheight = int(height*ratio)
        im2 = im.resize((newwidth,newheight),resample=Image.NEAREST) #,Image.Resampling.LANCZOS)
        im.close()
        return im2

