#! /usr/bin/env python3
from PIL import Image, ImageColor, ImageDraw
from os.path import exists
from vicariouspanel import NodeyezPanel
import hashlib
import os
import qrcode
import random
import shutil
import sys
import vicariousnetwork
import vicarioustext

class GeyserFundPanel(NodeyezPanel):

    def __init__(self):
        """Instantiates a new Geyser Fund panel"""

        # Define which additional attributes we have
        self.configAttributes = {
            # legacy key name mappings
            "colorBackground": "backgroundColor",
            "colorTextFG": "textColor",
            "sleepInterval": "interval",
            # panel specific key names
            "qrCodeEnabled": "qrCodeEnabled",
            "qrCodePixelSize": "qrCodePixelSize",
            "saveUniqueFile": "saveUniqueFile",
            "tagLabelsEnabled": "tagLabelsEnabled",
            "tagRestriction": "tagRestriction",
            "useTor": "useTor",
        }

        # Define our defaults (all panel specific key names should be listed)
        self._defaultattr("interval", 300)
        self._defaultattr("qrCodeEnabled", True)
        self._defaultattr("qrCodePixelSize", 2)
        self._defaultattr("saveUniqueFile", False)
        self._defaultattr("tagLabelsEnabled", True)
        self._defaultattr("tagRestriction", "bitcoin* nostr open-source")
        self._defaultattr("useTor", False)
        self._defaultattr("watermarkAnchor", "bottom")

        # Initialize
        super().__init__(name="geyserfund")
        self.geyserprojects = {}
        self.attributionColor = "#20ECC7"

    def getTagId(self, tags):
        if len(tags) == 0: return 1
        anyTag = False | (self.tagRestriction == None)
        anyTag = anyTag | (self.tagRestriction == "")
        anyTag = anyTag | (self.tagRestriction == "*")
        anyTag = anyTag | (self.tagRestriction == "any")
        if not anyTag:
            tagRestrictions = self.tagRestriction.split()
            tagRestrictionIds = []
            for tagRestriction in tagRestrictions:
                tagRestrictionIds.append([])
                self.log(f"looking for tags matching restriction rule: {tagRestriction}")
                for tag in tags:
                    if "id" not in tag: continue
                    if "label" not in tag: continue
                    tagId = tag["id"]
                    tagLabel = tag["label"]
                    if tagRestriction == tagLabel: 
                        self.log(f"-found tag matching restriction list: {tagLabel} ({tagId})")
                        tagRestrictionIds[-1].append(tagId)
                    if tagRestriction.endswith("*"):
                        tagRestrictionPrefix = tagRestriction[:-1]
                        if tagLabel.startswith(tagRestrictionPrefix):
                            self.log(f"-found tag matching restriction list: {tagLabel} ({tagId})")
                            tagRestrictionIds[-1].append(tagId)
            tagSet = random.choice(tagRestrictionIds)
            tagId = random.choice(tagSet)
            self.log(f"chose tag with id {tagId} from the restriction list")
            return tagId
        # any tag
        tag = random.choice(tags)
        if "id" not in tag: return 1
        tagId = tag["id"]
        tagLabel = tag["label"]
        self.log(f"chose tag {tagLabel} with id {tagId} from the tag list")
        return tagId

    def getProject(self):
        ok = False
        attemptsRemaining = 10
        project = None
        projectName = "unknown"
        projectTitle = "unknown"
        while not ok and attemptsRemaining > 0:
            project = random.choice(self.geyserprojects)
            if "project" in project: project = project["project"]
            if "name" in project: projectName = project["name"]
            if "title" in project: projectTitle = project["title"]
            if "status" in project:
                projectStatus = project["status"]
                if projectStatus != "inactive": 
                    ok = True
                    self.log(f"using project: {projectName} ({projectTitle}) - {projectStatus}")
                else:
                    self.log(f"skipping inactive project: {projectName} ({projectTitle})")
            else:
                self.log(f"skipping project {projectName} ({projectTitle}) as it has no status")
            attemptsRemaining -= 1
        return project

    def fetchData(self):
        """Fetches all the data needed for this panel"""

        tags = vicariousnetwork.getgeysertags(useTor=self.useTor)
        tagId = self.getTagId(tags)
        projects = vicariousnetwork.getgeyserprojects(useTor=self.useTor, tagId=tagId)
        self.geyserprojects = projects

    def loadAndPasteImage(self, sourceFile):
        if not exists(sourceFile): return
        sourceImage=Image.open(sourceFile)
        sourceImage=sourceImage.convert("RGBA")
        sourceImage = self.resizeImageToInset(sourceImage)
        sourceWidth=int(sourceImage.getbbox()[2])
        sourceHeight=int(sourceImage.getbbox()[3])
        sourceLeft = (self.getInsetWidth() - sourceWidth) // 2
        sourceTop = self.getInsetTop() + ((self.getInsetHeight() - sourceHeight) // 2)
        self.canvas.paste(sourceImage, (sourceLeft,sourceTop))
        sourceImage.close()

    def renderImage(self, project):
        imagefile = None
        imageurl = None
        if "image" in project: imageurl = project["image"]
        if imageurl is None and "thumbnailImage" in project: imageurl = project["thumbnailImage"]
        if imageurl is not None:
            self.log(f"image url: {imageurl}")
            projectName = project["name"]
            if imageurl.startswith("https://storage.googleapis.com/geyser-images-distribution"):
                imagefile = f"{self.dataDirectory}{self.name}/images/{projectName}"
                if not exists(imagefile.rpartition("/")[0]):
                    os.makedirs(imagefile.rpartition("/")[0])
                if not exists(imagefile):
                    vicariousnetwork.getandsavefile(useTor=self.useTor, url=imageurl, savetofile=imagefile, headers=None)
                self.loadAndPasteImage(imagefile)
        else:
            self.log(f"project has no image")

    def renderDescription(self, project):
        overlay = Image.new(mode="RGBA", size=(self.width, self.height), color=(255,255,255,0))
        overlaydraw = ImageDraw.Draw(overlay)
        overlayBG = (64,64,64,128)
        texty = self.getInsetTop()
        textystop = self.height - self.getFooterHeight()
        description = project["shortDescription"]
        fontsize = int(self.height * (18/320)) 
        rwords = description.split()
        rpart, rwords = vicarioustext.getmaxtextforwidth(overlaydraw, rwords, self.width, fontsize)
        while len(rpart) > 0:
            _,sh,_ = vicarioustext.gettextdimensions(overlaydraw, rpart, fontsize)
            textyold = texty
            texty += sh
            if texty > textystop: break
            overlaydraw.rectangle(xy=((0,textyold),(self.width,texty)),fill=overlayBG)
            vicarioustext.drawbottomlefttext(overlaydraw, rpart, fontsize, 0, texty, ImageColor.getrgb(self.textColor), False)
            rpart, rwords = vicarioustext.getmaxtextforwidth(overlaydraw, rwords, self.width, fontsize)
        self.canvas.alpha_composite(overlay)
        overlay.close()

    def renderQRCode(self,project):
        if not self.qrCodeEnabled: return
        projectName = project["name"]
        projecturl = f"https://geyser.fund/project/{projectName}"
        qr = qrcode.QRCode(box_size=self.qrCodePixelSize)
        qr.add_data(projecturl)
        qr.make()
        img = qr.make_image()
        s = img.size[1]
        # right side
        pos = (self.getInsetWidth()-s,self.getInsetTop()+self.getInsetHeight()-s)
        # left side
        pos = (0,self.getInsetTop()+self.getInsetHeight()-s)
        self.canvas.paste(img, pos)
        img.close()

    def renderAttribution(self):
        fontsize = int(self.height * 12/320)
        t = "Data from Geyser.Fund"
        vicarioustext.drawbottomlefttext(self.draw, t, fontsize, 0, self.height+4, ImageColor.getrgb(self.attributionColor))

    def getColorForText(self, t):
        m = hashlib.sha256(t.encode('UTF-8')).hexdigest()
        c = ""
        while len(m) > 0 and len(c) < 6:
            p = m[0]
            if p in ['0','1','2','3','4','5','6','7']:
                c = f"{c}{p}{p}"
            m = m[1:]
        while len(c) < 6:
            c = f"{c}21"
        c = f"#{c}"
        return ImageColor.getrgb(c)

    def renderTags(self, project):
        if not self.tagLabelsEnabled: return
        fontsize = int(self.height * (12/320))
        ib = self.getInsetBottom()
        y2 = ib
        padleftright = 10
        padtopbottom = 5
        radius=5.0
        tagCount = 0
        if "tags" in project:
            for tag in project["tags"]:
                tagCount += 1
                tagValue = tag["label"]
                self.log(f"Adding tag annotation for: {tagValue}")
                sw,sh,_ = vicarioustext.gettextdimensions(self.draw, tagValue, fontsize)
                y1 = y2 - (sh + (padtopbottom))
                tagBG = self.getColorForText(tagValue)
                labelWidth = sw + (padleftright * 2)
                self.draw.rounded_rectangle(xy=((self.width - labelWidth, y1),(self.width,y2 - (padtopbottom//2))),radius=radius,fill=tagBG)
                centerx = self.width - (labelWidth//2)
                centery = y1 + ((y2 - y1) // 2)
                vicarioustext.drawcenteredtext(self.draw, tagValue, fontsize, centerx, centery)
                y2 = y1

    def copyAsUniqueFile(self, projectName):
        rFrom = f"/{self.name}."        
        rTo = f"/{self.name}-{projectName}."
        panelFileName = super().getOutputFile()
        projectFileName = panelFileName.replace(rFrom, rTo)
        self.log(f"Saving copy to {projectFileName}")
        shutil.copyfile(panelFileName, projectFileName)

    def run(self):

        # Bail if we have no projects
        if len(self.geyserprojects) == 0:
            super()._markAsRan()
            return

        # Pick random project and set the header
        project = self.getProject()
        if project is None:
            super()._markAsRan()
            return
        self.log(project)
        self.headerText = project["title"]

        super().startImage()

        # Render background image for project if exists
        self.renderImage(project)
        self.renderDescription(project)
        self.renderQRCode(project)
        self.renderTags(project)
        self.renderAttribution()

        super().finishImage()

        if self.saveUniqueFile:
            self.copyAsUniqueFile(project["name"])        

# --------------------------------------------------------------------------------------
# Entry point if running this script directly
# --------------------------------------------------------------------------------------

if __name__ == '__main__':

    p = GeyserFundPanel()

    # If arguments were passed in, treat as a single run
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h','--help']:
            print(f"Show info about a randomly chosen project from Geyser.Fund")
            print(f"Usage:")
            print(f"1) Call without arguments to run continuously using the configuration or defaults")
            print(f"2) Call with an argument other then -h or --help to run once and exit")
        else:
            p.fetchData()
            p.run()
        exit(0)

    # Continuous run
    p.runContinuous()