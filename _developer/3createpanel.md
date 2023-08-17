---
name: Creating New Panel
title: NODEYEZ Development Environment
layout: default
---

# Creating a New Panel

## Create a temporary branch for your new panel. 

Using the Terminal
```shell
git checkout -b helloworld
```

## Run the panel creation script

Using the Terminal
```shell
cd ~/nodeyez/utils
~/.pyenv/nodeyez/bin/python3 newpanel.py
```

When prompted for the Name, type in the name you want for the panel.  This should be kept relatively short.  For example `Hello World`

For the description, you can add a little more context, but its not intended for a lengthy paragraph of text. This embeds in documentation, usage guidance, service description and even the initial sample output.  For example `This is my first Nodeyez panel`.

On the Group Type screen, select the group that most matches the intent of your panel.  Use the arrow keys, and press the space bar to mark the selection before pressing the Enter key.  For example `Other Fun Panels`

After this final selection, 4 files will be created in their respective directories based on the name given in the first prompt.  You'll also be presented with a TODO list for further actions.

```output
Your TODO list
--------------
1. Write your custom panel logic in ~/nodeyez/scripts/helloworld.py
   As you add or remove configurable properties, be sure to update
   ~/nodeyez/sample-config/helloworld.json - with property, description, type, default value
   ~/nodeyez/_docs/script-helloworld.md - same information
2. Run your panel. Then copy the image produced as a sample image referenced by docs.
   cp ~/nodeyez/imageoutput/helloworld.png ~/nodeyez/images
3. Optionally modify ~/nodeyez/_install_steps/8runatstartup.md to reference the service script in the enable and start sections
4. Optionally modify ~/nodeyez/install.sh if this panel should be installed and optionally enabled by default
```

## Run the panel

Using the Terminal
```shell
cd ~nodeyez/scripts
~/.pyenv/nodeyez/bin/python3 helloworld.py
```

press CTRL+C to stop the panel running continuously.

If using the IDE, you can select the generated file in the scripts folder and begin running it immediately by pressing F5.

Review the image in the imageoutput folder.



---

[Home](../) | [Back to Running and Changing Scripts]({% link _developer/2runandchange.md %}) | [Continue to Setting up Regtest]({% link _developer/4regtest.md %})
