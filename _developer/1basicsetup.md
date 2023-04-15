---
name: Python and IDE Setup
title: NODEYEZ Development Environment
layout: default
---

# Developing Enhancements

If you want to make improvements to Nodeyez, it's strongly recommended to have a code environment independent of the Nodeyez user.  This section will guide you through setting up development using Visual Studio Code as an IDE.  This guide assumes that the user is working on an Ubuntu or Debian based platform.

# Install Tools

```shell
sudo apt-get install python3 python3-venv git apt-transport-tor libjpeg-dev zlib1g-dev imagemagick inkspace -y
```

# Python Environment

Create an environment for Nodeyez, activate it, and install modules referenced

```shell
python3 -m venv ~/.pyenv/nodeyez

source ~/.pyenv/nodeyez/bin/activate

python3 -m pip install --upgrade beautifulsoup4 exifread pandas psutil pysocks qrcode redis requests urllib3 whiptail-dialogs Pillow Wand
```

# Clone the Project

Just as we did for the Nodeyez user, we'll clone the repository and setup initial folders

```shell
cd ~ 

git clone https://github.com/vicariousdrama/nodeyez.git

cd ~/nodeyez

mkdir -p ./{config,data,imageoutput,temp}

cp ./sample-config/*.json ./config
```

# Setup Visual Studio IDE

## Download and Install

For more details, follow the guidance available on the [Visual Studio Code on Linux](https://code.visualstudio.com/docs/setup/linux) installation details.

```shell
cd /tmp

wget "https://code.visualstudio.com/sha/download?build=stable&os=linux-deb-x64" -O vscode.deb

sudo dpkg -i vscode.deb
```

## Launch Visual Studio Code

By default, installing the .deb package should have created shortcuts to Visual Studio Code under the Programming menu.
From the command line, you can launch Visual Code from any path via the following:

```shell
cd ~/nodeyez

code .
```

## Install Extensions

While not required, Extensions for Visual Studio Code make the IDE a much more helpful tool.

Access the Extensions view by either the shortcut (CTRL+SHIFT+X), or from expanding the File menu, choosing Preferences, and finally Extensions.

From the Search bar, look for and install the following extensions:

- Python [from Microsoft]: IntelliSense (Pylance), Linting, Debugging (multi-threaded, remote), Jupyter Notebooks, code formatting, refactoring, unit tests, and more.

- Pylance [from Microsoft]: A performant, feature-rich language server for Python ins VS Code

- systemd-unit-file [from coolbear]: Language support for systemd unit files

## Choose Python Interpreter

When in Visual Studio Code, we want to make sure that we're using the environment that we setup previously.  Access the command palette by either the shortcut (CTRL+SHIFT+P) or from the View menu.

Type in `Python: Select Interpreter` and press [ENTER].

From the options that appear, choose the one that corresponds to `~/.pyenv/nodeyez/bin/python`.

---

[Home](../) | [Back to Nodeyez Architecture]({% link _developer/0architecture.md %}) | [Continue to Running and Changing Scripts]({% link _developer/2runandchange.md %})
