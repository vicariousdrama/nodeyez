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

## What it Does

This will automate the same steps outlined in the following pages for

- Tools: Dependencies will be installed
- Nodeyez: User will be created, with preference to mapping to external drive if the root drive is a flash drive.  Python virtual environment will be created and dependent modules installed.  Nodeyez repository will be cloned, data folders created, and sample configuration copied.  If Bitcoin user exists, then the cookie and conf file will be copied to Nodeyez. If LND is present, the TLS cert will be copied and custom macaroon created.
- Website Dashboard: If nginx is not yet installed, then a basic nginx installation will be setup.  If nginx is already present, AND the environment is recognized as MyNodeBTC, then it will install a Nodeyez Website Dashboard as an enabled site.  Port 907 will be opened for accessing the dashboard.
- Services: Panels for ip address, utc clock, and system info will be enabled and started. If Bitcoin user exists, then Bitcoin related panels will also be enabled and started. If LND exists, then those panels will also be enabled and started.

Running the script multiple times is intended to always bring to the same state. 

## Tested On
This script has been tested on

| Architecture | Drive Count | MMC? | With Bitcoin | With LND | NGINX | MyNode |
| --- | --- | --- | --- | --- | --- | --- |
| x86_64 Laptop | 2 | No | No | No | No | No |
| x86_64 Laptop | 2 | No | No | No | Yes | No |

## Known Limitations

At present, this script does not support the following

- Auto configuring display screen
- Enabling Slideshow
- Any form of downgrades

If first pass installs Nginx, then subsquent passes will skip that, and not update templates or configuration.

---

[Home](../) | [Continue to Your Node]({% link _install_steps/1yournode.md %})