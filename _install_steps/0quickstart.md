---
name: Quick Start
layout: default
---

# Quick Start

If you're on a Debian based Linux system, you can run the following command
to download and run an installation script if you're feeling #reckless

```shell
wget -qO- https://nodeyez.com/install.sh | sudo bash
```

## Known Limitations

You should be aware of the following limitations

Requires a 64 Bit operating system to be installed
- 32 bit may be missing key tools, like imagemagick and tor
- 32 bit may not have a packaged version of nginx-commons

At present, this script does not support the following
- Auto configuring display screen
- Enabling Slideshow

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

---

[Home](../) | [Continue to Your Node]({% link _install_steps/1yournode.md %})