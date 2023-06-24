---
name: Your Node
title: NODEYEZ General Node Guidance
layout: default
---

# Your Node

To use some of the the scripts in this project, you'll need a Bitcoin Node.

Consider following the helpful guidance at [node.guide](https://node.guide)  on different options available.  

An easy low cost option is a Raspberry Pi based node. Before the supply shortage of Raspberry Pi boards, this was a very common choice because of its small form factor, and low power demands (15 watt).  

Another common option is to use an older desktop or laptop.  Anything made in the past few years is likely to be powerful enough.  From a hardware specification standpoint, consider the following to be a reasonable minimum
- Multicore processor (4+ cores)
- 4GB of RAM or more
- 1TB SSD or larger

If you are brand new to Linux then I would recommend the following

- If you want to learn more about the command line, and verify everything that you install and using a Raspberry Pi, then consider [Raspibolt](https://raspibolt.org)
- If you prefer to primarily work from a graphical user interface, and want to toggle on apps from a web interface, then consider [MyNodeBTC](https://mynodebtc.org). It is well suited to running on a Raspberry Pi, an Intel/AMD64 based system, or even in a virtual machine

Many of the scripts can be run without a Bitcoin node though, so if you're just looking to setup the display of the current date, the sats per usd, or price of Bitcoin or the Mempool Blocks getting its data from an external resource, then you just need a basic computer already setup with the Linux operating system.

The remainder of this guide assumes that you will be doing the commands on a Linux operating system that uses systemd and is Debian based. 

---

[Home](../) | [Continue to Display Screen]({% link _install_steps/2displayscreen.md %})

