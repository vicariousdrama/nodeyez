---
name: Python and Dependencies
title: Setting up Python and Dependencies
---

# Setting up Python and Dependencies

You will need to be logged into your system with a privileged user that can perform super user operations.

If you are using a Raspberry Pi setup, you can login as these user names

    - MyNodeBTC: ssh as admin
    - Raspiblitz ssh as admin
    - Raspibolt: ssh as admin
    - Umbrel: ssh as umbrel
    - Default Raspbian: ssh as pi

## Install Python3

For Raspberry Pi it'll normally come with Python 2.7, but the scripts require Python 3.  

You can esure you have Python 3 by running the following

```shell
sudo apt-get install python3
```

## Install Git

In future steps you'll use Git to clone this repo.


```shell
sudo apt install git
```

## Install Torify

Torify is optionally used by some scripts that retrieve data from external sources in a privacy preserving way.

```shell
sudo apt-get install apt-transport-tor
```

## Install the Pillow Library

This library is a key python library used by the scripts for working with and rendering 2D graphics.

```shell
sudo apt-get install libjpeg-dev zlib1g-dev
python3 -m pip install --upgrade Pillow
```

## Install ImageMagic and Inkscape

These libraries are used for some of the image file type conversions

```shell
sudo apt-get install imagemagick inkscape
```

---

[Home](../README.md) | [Back to Display Screen](./install-2-displayscreen.md) | [Continue to Nodeyez](./install-4-nodeyez.md)
