---
name: Tools
title: NODEYEZ Common Tools
layout: default
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

## Install JPEG Development Library

This library is referenced by Pillow, a python module we'll install in the next section used by the scripts for working with and rendering 2D graphics.

```shell
sudo apt-get install libjpeg-dev zlib1g-dev
```

## Install ImageMagic and Inkscape

These libraries are used for some of the image file type conversions

```shell
sudo apt-get install imagemagick inkscape
```

## Install JQ

This provides for JSON processing
```shell
sudo apt-get insall jq
```

---

[Home](../) | [Back to Display Screen]({% link _install_steps/2displayscreen.md %}) | [Continue to Nodeyez]({% link _install_steps/4nodeyez.md %})
