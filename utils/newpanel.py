#! /home/nodeyez/.pyenv/nodeyez/bin/python3
from whiptail import Whiptail
from os.path import exists, dirname
import re
import sys

# Init
currentName=""
currentClass=""
currentClassLower=""
currentDescription=""
currentGroup=""

pathprefix = dirname(sys.argv[0])

# Functions
def promptTextValue(title="Value", msg="Provide a value", currentValue="", warningText=""):
    w = Whiptail(title=title, backtitle=warningText)
    r = w.inputbox(msg=msg, default=currentValue)
    # cancel, escape
    if r[1] != 0: 
        print("Panel creation cancelled")
        quit()
    # get the new value
    return r[0]

def promptGroups(currentValue="",warningText=""):
    title="Group Type"
    msg="Choose the group this panel should be associated with for documentation purposes"
    w = Whiptail(title=title, backtitle=warningText)
    choices = [
        ("Bitcoin Panels","Panels that require Bitcoin but not Lightning"),
        ("Lightning Panels","Panels that rely on the Lightning Network"),
        ("Mining Panels","Panels related to Mining Devices and Pools"),
        ("Nostr Panels","Panels about Nostr or retrieving data from Nostr"),
        ("Informational Panels","Panels about the local system resources and metrics"),
        ("Other Fun Panels","Any other info that is fun to retrieve and display"),
        ("Composite Displays","Specialized display panel layouts"),
        ]
    items = []
    for choice in choices:
        k = choice[0]
        d = choice[1]
        s = "on" if currentValue == k else "off"
        items.append((k,d,s))
    r = w.radiolist(msg=msg, items=items)
    # cancel, escape
    if r[1] != 0: 
        print("Panel creation cancelled")
        quit()
    # get the new value
    return ' '.join(r[0])

def panelExists(name):
    filename = f"../scripts/{name}.py"
    return exists(filename)

def docExists(name):
    filename = f"../_docs/script-{name}.md"
    return exists(filename)

def configExists(name):
    filename = f"../sample-config/{name}.json"
    return exists(filename)

def serviceExists(name):
    filename = f"../scripts/systemd/nodeyez-{name}.service"
    return exists(filename)

def applyTemplate(sourceFile, destinationFile):
    replacementsToPerform = [
        ("<Class>", currentClass),
        ("<ClassLower>", currentClassLower),
        ("<Name>", currentName),
        ("<Group>", currentGroup),
        ("<Description>", currentDescription)
    ]
    with open(sourceFile, "r") as sf:
        fileContent = sf.read()
    for replacements in replacementsToPerform:
        rFrom = replacements[0]
        rTo = replacements[1]
        fileContent = fileContent.replace(rFrom, rTo)
    with open(destinationFile, "w") as df:
        df.write(fileContent)
    print(f"{destinationFile} created from template")

# Get desired name from user
warningText = ""
title="Panel Name"
msg="Provide a unique name for the panel. Mixed case and spaces are allowed"
while(currentName == "" or len(warningText) > 0):
    currentName = promptTextValue(title, msg, currentName, warningText)
    currentClass = re.sub('[\W_]+', '', currentName)
    currentClassLower = currentClass.lower()
    warningText = ""
    if len(warningText) == 0 and len(currentName) == 0: warningText = "Name cannot be empty"
    if len(warningText) == 0 and len(currentClass) == 0: warningText = "Name must contain letters"
    if len(warningText) == 0 and currentClassLower[0].isdigit(): warningText = "First character of name must be a letter"
    if len(warningText) == 0 and panelExists(currentClassLower): warningText = f"A script file already exists for {currentClassLower}"
    if len(warningText) == 0 and docExists(currentClassLower): warningText = f"A document file already exists for {currentClassLower}"
    if len(warningText) == 0 and configExists(currentClassLower): warningText = f"A sample-config file already exists for {currentClassLower}"
    if len(warningText) == 0 and serviceExists(currentClassLower): warningText = f"A systemd service file already exists for {currentClassLower}"

# Prompt for Description
warningText = ""
title="Panel Description"
msg="Provide a description for this panel."
while(currentDescription == "" or len(warningText) > 0):
    currentDescription = promptTextValue(title, msg, currentDescription, warningText)
    warningText = ""
    if len(warningText) == 0 and len(currentDescription) == 0: warningText = "Description cannot be empty"

# Prompt for Type
warningText = ""
while(currentGroup == "" or len(warningText) > 0):
    currentGroup = promptGroups("Other Fun Panels", warningText)
    warningText = ""
    if len(warningText) == 0 and len(currentGroup) == 0: warningText = "Group cannot be empty"

# Copy files with replacements
templatefiles = [
    ("config.template", f"{pathprefix}/../sample-config/{currentClassLower}.json"),
    ("doc.template", f"{pathprefix}/../_docs/script-{currentClassLower}.md"),
    ("panel.template", f"{pathprefix}/../scripts/{currentClassLower}.py"),
    ("service.template", f"{pathprefix}/../scripts/systemd/nodeyez-{currentClassLower}.service")
]
for tf in templatefiles:
    sf = f"{pathprefix}/templates/{tf[0]}"
    df = tf[1]
    applyTemplate(sf,df)

# Notes to dev
print()
print(f"Your TODO list")
print(f"--------------")
print(f"1. Write your custom panel logic in ~/nodeyez/scripts/{currentClassLower}.py")
print(f"   As you add or remove configurable properties, be sure to update")
print(f"   ~/nodeyez/sample-config/{currentClassLower}.json - with property, description, type, default value")
print(f"   ~/nodeyez/_docs/script-{currentClassLower}.md - same information")
print(f"2. Run your panel. Then copy the image produced as a sample image referenced by docs.")
print(f"   cp ~/nodeyez/imageoutput/{currentClassLower}.png ~/nodeyez/images")
print(f"3. Optionally modify ~/nodeyez/_install_steps/8runatstartup.md to reference the service script in the enable and start sections")
print(f"4. Optionally modify ~/nodeyez/install.sh if this panel should be installed and optionally enabled by default")
