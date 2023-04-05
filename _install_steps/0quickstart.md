---
name: Quick Start
layout: default
---

# Quick Start

If you're on a Debian based Linux system, you can get started quickly by
running an installation script if you're feeling #reckless.

## Install

To insall via the script, download and pipe to bash with sudo
```shell
wget -qO- https://nodeyez.com/install.sh | sudo bash
```

## Known Limitations

You should be aware of the following limitations

It requires a 64 Bit operating system to be installed and has only been
tested on MyNodeBTC and Raspibolt environments.

At present, this script does not support auto configuring an attached
display screen, or enabling the slideshow.

Only a subset of available Nodeyez panel scripts will be enabled.

## What it Does

This will automate the same steps outlined in the following pages for

- Tools: Dependencies will be installed
- Nodeyez: User will be created, with preference to mapping to external drive if the root drive is a flash drive.  Python virtual environment will be created and dependent modules installed.  Nodeyez repository will be cloned, data folders created, and sample configuration copied.  
  - If Bitcoin user exists, then the cookie and conf file will be copied to Nodeyez. 
  - If LND is present, the TLS cert will be copied and custom macaroon created.
- Website Dashboard: Installs NGINX if not yet installed. Creates certificates and diffie-hellman parameters along with dropping in templates and site configs.  If MyNodeBTC
is present, then custom site config using the existing certificate will be used. Port 907 
will be opened for accessing the dashboard.
- Services: Panels for ip address, utc clock, and system info will be enabled and started. If Bitcoin user exists, then Bitcoin related panels will also be enabled and started. If LND exists, then those panels will also be enabled and started.

Running the script multiple times is intended to always bring to the same state. 

A configuration tool is also deployed to review Nodeyez services, toggle their status,
and make configuration changes for each panel.  You may access this from the terminal
by running `sudo nodeyez-config`

If you are attaching a screen, check out steps that cover
[Display Screen]({% link _install_steps/2displayscreen.md %}) and 
[Slideshow]({% link _install_steps/6slideshow.md %})]

Otherwise, you can jump ahead to using the [Nodeyez-Config]({% link _install_steps/9nodeyezconfig.md %}) tool

## Uninstall

Uninstalling is similar, simply run the following
```shell
wget -qO- https://nodeyez.com/uninstall.sh | sudo bash
```

An existing NGINX instance will be left running after Nodeyez is removed.

---

[Home](../) | [Continue to Your Node]({% link _install_steps/1yournode.md %})