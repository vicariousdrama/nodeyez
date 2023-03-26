---
name: Nodeyez User Setup
title: NODEYEZ Setup
layout: default
---

# Nodeyez

Now we get to specifics of the Nodeyez user and cloning this repository.

You should be logged in as a privileged user to enter these commands.

## User Home Path

When this project was first created, it was setup on a Raspberry Pi and the typical
installation approach was a MicroSD card for the OS to boot from and a larger
performant drive attached externally via USB3.

**If you are using a MicroSD card, then it is preferable to run Nodeyez from the 
external drive, and store created images and data there as well to reduce the 
potential to wear out the microsd card.**

The following script segment will determine if the default /home path is stored
on flash media, and if so create and link it on the first external hard drive
under the mount point.

```shell
DRIVECOUNT=$(df -t ext4 | grep / | awk '{print $6}' | sort | wc -l)
ISMMC=$(findmnt -n -o SOURCE --target /home | grep "mmcblk" | wc -l)
if [ $DRIVECOUNT -gt 1 ] && [ $ISMMC -gt 0 ]; then
  EXT_DRIVE_MOUNT=$(df -t ext4 | grep / | awk '{print $6}' | sort | sed -n 2p)
fi
if [ -z ${EXT_DRIVE_MOUNT+x} ]; then
  NODEYEZ_HOME=/home/nodeyez
  sudo adduser --gecos "" --disabled-password nodeyez
else
  NODEYEZ_HOME=${EXT_DRIVE_MOUNT}/nodeyez
  sudo adduser --home ${NODEYEZ_HOME} --gecos "" --disabled-password nodeyez
  sudo ln -s ${NODEYEZ_HOME} /home/nodeyez
  sudo chown -R nodeyez:nodeyez /home/nodeyez
fi
```

## Add to Tor Group

Add the user to the debian-tor group to allow it to configure tor directly

```shell
sudo adduser nodeyez debian-tor
```

## Add Bitcoin Access

Add Bitcoin configuration for nodeyez from existing configuration.

**You can [skip this step](#switch-to-nodeyez-user) if you are not using any scripts that require Bitcoin.**

Technically we only need the rpcauth or rpcuser and rpcpassword settings to
allow bitcoin-cli to work, but this is the easiest way to setup that I've found
without simply adding the nodeyez user to the bitcoin group and linking
directories.  *If you know a way to grant read only access without wallet to a
user, please open an issue or pull request.*

This assumes that Bitcoin was setup on your node with a dedicated user named
`bitcoin`.  This is the case for MyNodeBTC and Raspibolt.  Other node types have
not yet been verified. *If you are using Raspiblitz or Umbrel and can add
clarity here, please open an issue or pull request.*

```shell
sudo mkdir -p /home/nodeyez/.bitcoin

sudo cp /home/bitcoin/.bitcoin/bitcoin.conf /home/nodeyez/.bitcoin/bitcoin.conf

sudo cp /home/bitcoin/.bitcoin/.cookie /home/nodeyez/.bitcoin/.cookie

sudo chown -R nodeyez:nodeyez /home/nodeyez/.bitcoin
```

## Add LND Access

Add LND tls cert and bake a macaroon specific to nodeyez

**You can [skip this step](#switch-to-nodeyez-user) if you are not using any scripts that require Lightning.**

As with the bitcoin step above, this assumes that the node is setup with an LND
(Lightning Network Daemon) implementation under the bitcoin user.  If you are
using C-Lightning or another implementation, you may need to alter the paths.
*Please open an issue or pull request to provide information or help for others*

```shell
sudo mkdir -p /home/nodeyez/.lnd

sudo cp /home/bitcoin/.lnd/tls.cert /home/nodeyez/.lnd/tls.cert

lncli bakemacaroon uri:/lnrpc.Lightning/GetInfo uri:/lnrpc.Lightning/GetNodeInfo uri:/lnrpc.Lightning/ListPeers uri:/lnrpc.Lightning/ListChannels uri:/lnrpc.Lightning/ChannelBalance uri:/lnrpc.Lightning/ConnectPeer uri:/lnrpc.Lightning/DisconnectPeer uri:/lnrpc.Lightning/ForwardingHistory uri:/lnrpc.Lightning/ListPayments uri:/lnrpc.Lightning/DecodePayReq uri:/lnrpc.Lightning/FeeReport --save_to ${HOME}/nodeyez.macaroon

sudo mv ${HOME}/nodeyez.macaroon /home/nodeyez/.lnd/nodeyez.macaroon

sudo chown -R nodeyez:nodeyez /home/nodeyez/.lnd
```

Whenever calling lncli with the nodeyez user, the macaroon path can now be provided as follows

`lncli --macaroonpath=/home/nodeyez/.lnd/nodeyez.macaroon getinfo`

## Switch to Nodeyez User

Change to the nodeyez user

```shell
sudo su - nodeyez
```

## Test Access

Test that the nodeyez user has access to bitcoin-cli and lncli

You can [skip to the next section](#clone-the-repository) if you didn't setup bitcoin or lightning for the
Nodeyez user in the sections above.

For bitcoin, lets get a simple output of mining info which yields the block
height, difficulty, estimated hashrate per second, chain, and some other details

```shell
bitcoin-cli getmininginfo
```

Example output:
```json
{
  "blocks": 729586,
  "difficulty": 27452707696466.39,
  "networkhashps": 2.043741869269852e+20,
  "pooledtx": 12524,
  "chain": "main",
  "warnings": ""
}
```

**If you get an error, please report as a new issue.  You will not be able
to run scripts requiring access to bitcoin until this is resolved.**

For lightning, first we will get the nodes public key

```shell
lncli --macaroonpath=/home/nodeyez/.lnd/nodeyez.macaroon getinfo | jq .identity_pubkey
```

**If you get an error, please report as a new issue.  You will not be able
to run scripts requiring access to lightning until this is resolved.**
  
You can also verify that the nodeyez macaroon for lncli does not allow any
actions that aren't in its permission set.  For example, getting a new
wallet address will fail

```shell
lncli --macaroonpath=/home/nodeyez/.lnd/nodeyez.macaroon newaddress p2wkh
```
For this you should have gotten the following error

`[lncli] rpc error: code = Unknown desc = permission denied`

You can list the permissions that the macaroon has by using the printmacaroon
operation

```shell
lncli --macaroonpath=/home/nodeyez/.lnd/nodeyez.macaroon printmacaroon --macaroon_file /home/nodeyez/.lnd/nodeyez.macaroon
```

The output should appear as follows. These are the only calls that the 
nodeyez scripts make at this time.

```json
{
  "version": 2,
  "location": "lnd",
  "root_key_id": "0",
  "permissions": [
    "uri:/lnrpc.Lightning/ChannelBalance",
    "uri:/lnrpc.Lightning/ConnectPeer",
    "uri:/lnrpc.Lightning/DecodePayReq",
    "uri:/lnrpc.Lightning/DisconnectPeer",
    "uri:/lnrpc.Lightning/FeeReport",
    "uri:/lnrpc.Lightning/ForwardingHistory",
    "uri:/lnrpc.Lightning/GetInfo",
    "uri:/lnrpc.Lightning/GetNodeInfo",
    "uri:/lnrpc.Lightning/ListChannels",
    "uri:/lnrpc.Lightning/ListPayments",
    "uri:/lnrpc.Lightning/ListPeers"
  ],
  "caveats": null
}
```

## Clone the Repository

Again, this step should be done as the nodeyez user

```shell
cd ~

git clone https://github.com/vicariousdrama/nodeyez.git
```

## Create folders

Create folders and copy sample configuration files

```shell
mkdir -p ~/nodeyez/{config,data,imageoutput,temp}

mkdir -p ~/nodeyez/imageoutput/ordinals

cp ~/nodeyez/sample-config/*.json ~/nodeyez/config
```

## Create Python Environment

A virtual environment will be used for the Nodeyez user when
running scripts to help isolate versions from other uses of
Python on the system

```shell
python3 -m venv ~/.pyenv/nodeyez
```

Activate the new virtual environment

```shell
source ~/.pyenv/nodeyez/bin/activate
```

Finally, install modules used by scripts into the virtual environment

```shell
python3 -m pip install --upgrade Pillow beautifulsoup4 pandas qrcode Wand exifread urllib3 requests redis pysocks
```

- beatifulsoup4 - For screenscraping extracting data from HTML and XML files. Within Nodeyez, it is used by the Compass Mining Status script and the Daily Data Retrieval script.
- pandas - Data analysis library. Within Nodeyez, it is used by the Luxor GraphQL client for transforming/mapping results from API calls
- qrcode - For creating qrcodes based on text input and is used by Nodeyez as part of the Raretoshi script.
- Wand - Binding to ImageMagick for Python. It is used by Nodeyez for handling filetypes that pillow is unable to such as scalable vector graphics (SVG)
- exifread - For parsig out EXIF data from Image files
- urllib3 - Handy wrappers to act as an HTTP client when making requests
- requests - Higher level api for HTTP clients
- redis - Redis client that is used by the LNDHub script
- pysocks - SOCKS proxy client for python, used when making remote requests

---

[Home](../) | [Back to Tools]({% link _install_steps/3tools.md %}) | [Continue to Panel Index]({% link _install_steps/5panels.md %})
