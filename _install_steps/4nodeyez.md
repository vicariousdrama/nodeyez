---
name: Creating the Nodeyez User and Environment
title: NODEYEZ User Setup
layout: default
---

# Nodeyez

If you installed Nodeyez using the [Quick Start]({% link _install_steps/0quickstart.md %}), then this step is already done for you and you can skip ahead to setting up the [Slideshow]({% link _install_steps/6slideshow.md %}) or using the [Nodeyez-Config]({% link _install_steps/9nodeyezconfig.md %}) tool.

Now we get to specifics of the Nodeyez user and cloning this repository.

You should be logged in as a privileged user to enter these commands.

## User Home Path

When this project was first created, it was setup on a Raspberry Pi and the typical installation approach was a MicroSD card for the OS to boot from and a larger performant drive attached externally via USB3.

**If you are using a MicroSD card, then it is preferable to run Nodeyez from the  external drive, and store created images and data there as well to reduce the  potential to wear out the microsd card.**

The following script segment will determine if the default /home path is stored on flash media, and if so create and link it on the first external hard drive under the mount point.

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

## Optional: Prepare Bitcoin Access

**You can [skip this step](#optional-prepare-lnd-access) if you are not using any scripts that require Bitcoin.**

NOTE: If you are installing Nodeyez on popular node packages, changing the RPC Authentiation approach can break usage by other apps that rely on cookie based authentication. For now, JSON-RPC REST based access is primarily beneficial in scenarios where you want to run Nodeyez on a machine different from that which has Bitcoin running on it. 

Proceed to one of the following two sections depending on whether you are setting up for [CLI](#grant-bitcoin-cli-access) or [REST](#setup-bitcoin-rest-access) access.

### Grant Bitcoin-CLI Access

Add Bitcoin configuration for nodeyez from existing configuration.

Technically we only need the rpcauth or rpcuser and rpcpassword settings to allow bitcoin-cli to work, but this is the easiest way to setup that I've found without simply adding the nodeyez user to the bitcoin group and linking directories.  *If you know a way to grant read only access without wallet to a user, please open an issue or pull request.*

This assumes that Bitcoin was setup on your node with a dedicated user named `bitcoin`.  This is the case for MyNodeBTC and Raspibolt.  Other node types have not yet been verified. *If you are using Raspiblitz or Umbrel and can add clarity here, please open an issue or pull request.*

```shell
sudo mkdir -p /home/nodeyez/.bitcoin

sudo cp /home/bitcoin/.bitcoin/bitcoin.conf /home/nodeyez/.bitcoin/bitcoin.conf

sudo cp /home/bitcoin/.bitcoin/.cookie /home/nodeyez/.bitcoin/.cookie

sudo chown -R nodeyez:nodeyez /home/nodeyez/.bitcoin
```

Proceed to [prepare LND access](#optional-prepare-lnd-access) or [switch to Nodeyez user](#switch-to-nodeyez-user).

### Setup Bitcoin-REST Access

Note that if you are using a prepackaged node like an Umbrel, it may already have settings for rpcauth.  If you change an existing rpcauth line, it may break other applications on that node. You are strongly encouraged to make backups before changing anything so that you can revert to known good configurations if you break something.

By default, newer installations of Bitcoin will use the cookie authorization if no `rpcuser` and `rpcpassword` is provided. The config values of `rpcuser` and  `rpcpassword` are deprecated, and in their place, you should use `rpcauth`. You can download the rpcauth.py script from the Bitcoin repository at

https://github.com/bitcoin/bitcoin/blob/master/share/rpcauth/rpcauth.py

Once downloaded, run the script with python, specifying the username to use, and optionally, a password (if no password is provided, one will be generated)

```sh
python3 rpcauth.py mybitcoinrpcusername
```

Sample output
```sh
$ python3 rpcauth.py mybitcoinrpcusername
String to be appended to bitcoin.conf:
rpcauth=mybitcoinrpcusername:66736ea48233dba1492222baed2b7922$d467d157346b42185cf371df20dea11e82f45f7d142679b979efc4dc12d0521c
Your password:
C4xkKLa4YII62Z_4BkiNhXsO2E_q5X8jJcYQ3uT2ATs=
```

Make note of the username and password as you will need to specify them when configuring the bitcoin-rest.json file for the Nodeyez user later.

Modify the Bitcoin configuration file to use RPC Auth and allow IP addresses that should be able to access

```sh
sudo nano /home/bitcoin/.bitcoin/bitcoin.conf
```

Add the `rpcauth` line generated by rpcauth.py, and for each machine's IP address that you want to be able to access RPC, add an entry for `rpcallowip`. For example, the localhost (127.0.0.1) and another machine on the network  (10.10.21.21) would appear as follows

```ini
rpcauth=mybitcoinrpcusername:66736ea48233dba1492222baed2b7922$d467d157346b42185cf371df20dea11e82f45f7d142679b979efc4dc12d0521c
rpcbind=0.0.0.0
rpcallowip=127.0.0.1
rpcallowip=10.10.21.21
```

Save (CTRL+O) and Exit (CTRL+X).

Restart the Bitcoin deamon to activate the changes

```sh
sudo systemctl restart bitcoind
```

## Optional: Prepare LND Access

**You can [skip this step](#switch-to-nodeyez-user) if you are not using any scripts that require Lightning.**

Bake a macaroon for Nodeyez with only the permissions needed for scripts.

```sh
lncli bakemacaroon uri:/lnrpc.Lightning/GetInfo uri:/lnrpc.Lightning/GetNodeInfo uri:/lnrpc.Lightning/ListPeers uri:/lnrpc.Lightning/ListChannels uri:/lnrpc.Lightning/ChannelBalance uri:/lnrpc.Lightning/ConnectPeer uri:/lnrpc.Lightning/DisconnectPeer uri:/lnrpc.Lightning/ForwardingHistory uri:/lnrpc.Lightning/ListPayments uri:/lnrpc.Lightning/DecodePayReq uri:/lnrpc.Lightning/FeeReport uri:/lnrpc.Lightning/ListInvoices --save_to ${HOME}/nodeyez.macaroon
```

Proceed to one of the following two sections depending on whether you are setting up for [CLI](#grant-lnd-cli-access) or [REST](#setup-lnd-rest-access) access.

### Grant LND-CLI Access

Add LND tls cert and macaroon specific to nodeyez

```shell
sudo mkdir -p /home/nodeyez/.lnd

# Copy the TLS Cert
sudo cp /home/bitcoin/.lnd/tls.cert /home/nodeyez/.lnd/tls.cert

# Copy the macaroon
sudo cp ${HOME}/nodeyez.macaroon /home/nodeyez/.lnd/nodeyez.macaroon

sudo chown -R nodeyez:nodeyez /home/nodeyez/.lnd
```

Whenever calling lncli with the nodeyez user, the macaroon path can now be provided as follows

`lncli --macaroonpath=/home/nodeyez/.lnd/nodeyez.macaroon getinfo`

Proceed to [switch to Nodeyez user](#switch-to-nodeyez-user)

### Setup LND-REST Access

Convert the LND tls certificate to a hex format. You will need this later to configure the lnd-rest.json file for the Nodeyez user.

```sh
sudo xxd -ps -u -c 1000 /home/bitcoin/.lnd/tls.cert
```

Convert the macaroon to hex format. You will need this later to configure the lnd-rest.json file for the Nodeyez user.

```sh
xxd -ps -u -c 1000 ${HOME}/nodeyez.macaroon
```

## Switch to Nodeyez User

Change to the nodeyez user

```shell
sudo su - nodeyez
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

cp ~/nodeyez/sample-config/*.json ~/nodeyez/config
```

## Create Python Environment

A virtual environment will be used for the Nodeyez user when running scripts to help isolate versions from other uses of Python on the system

```shell
python3 -m venv ~/.pyenv/nodeyez
```

Activate the new virtual environment

```shell
source ~/.pyenv/nodeyez/bin/activate
```

Install modules used by scripts into the virtual environment

```shell
python3 -m pip install --upgrade Pillow beautifulsoup4 pandas psutil qrcode Wand exifread urllib3 requests redis pysocks whiptail-dialogs
```

- Pillow - Python Imaging Library
- beatifulsoup4 - For screenscraping extracting data from HTML and XML files. Within Nodeyez, it is used by the Compass Mining Status script and the Daily Data Retrieval script.
- pandas - Data analysis library. Within Nodeyez, it is used by the Luxor GraphQL client for transforming/mapping results from API calls
- psutil - psutil is a cross-platform library for retrieving information on running processes and system utilization (CPU, memory, disks, network, sensors) in Python
- qrcode - For creating qrcodes based on text input and is used by Nodeyez as part of the Raretoshi script.
- Wand - Binding to ImageMagick for Python. It is used by Nodeyez for handling filetypes that pillow is unable to such as scalable vector graphics (SVG)
- exifread - For parsig out EXIF data from Image files
- urllib3 - Handy wrappers to act as an HTTP client when making requests
- requests - Higher level api for HTTP clients
- redis - Redis client that is used by the LNDHub script
- pysocks - SOCKS proxy client for python, used when making remote requests


## Optional: Configure Bitcoin Access

Nodeyez supports accessing Bitcoin either using the command line interface (CLI) defined in the next section, or over REST calls, which may be to a node on the same computer, or another reachable on the network.

**You can skip this step and [continue to Panel Index]({% link _install_steps/5panels.md %}) if you are not using any scripts that require Bitcoin or Lightning.**

Proceed to one of the following two sections depending on whether you are finishing setup for [CLI](#test-bitcoin-cli-access) or [REST](#grant-and-test-bitcoin-rest-access) access.

### Test Bitcoin-CLI Access

Test that the nodeyez user has access to bitcoin-cli

Lets get a simple output of mining info which yields the block height, difficulty, estimated hashrate per second, chain, and some other details

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

**If you get an error, please report as a new issue.  You will not be able to run scripts requiring access to bitcoin until this is resolved.**

### Grant and Test Bitcoin-REST Access

You will need the following information to setup rest based access

- IP address of bitcoin node (e.g. 127.0.0.1 if local)
- The rpc port the node is listening for requests on.  (e.g. 8332)
- The rpc user name
- The rpc password

In the Nodeyez config folder, locate the bitcoin-rest.json file and edit it

```sh
nano ~/nodeyez/config/bitcoin-rest.json
```

Set the appropriate field values for the profile named `default`, which assumes a local Bitcoin node. Or copy the structure creating a new profile. Finally, set the name of the profile to use as the value for the `activeProfile` field.  

Save (CTRL+O) and Exit (CTRL+X).

To test the setup, open a python terminal using the environment

```sh
cd ~/nodeyez/scripts
~/.pyenv/nodeyez/bin/python
```

Paste in these commands

```python
from vicariousbitcoin import *
bitcoinMode
getcurrentblock()
exit()
```
If successful, it should report the Bitcoin mode as REST and a valid block height.

## Optional: Configure LND Access

Nodeyez supports accessing LND either using the command line interface (CLI) defined in the next section, or over REST calls, which may be to a node on the same computer, or another reachable on the network.

**You can skip this step and [continue to Panel Index]({% link _install_steps/5panels.md %}) if you are not using any scripts that require Lightning.**

Proceed to one of the following two sections depending on whether you are finishing setup for [CLI](#test-lnd-cli-access) or [REST](#grant-and-test-lnd-rest-access) access.

### Test LND-CLI Access

For lightning, first we will get the nodes public key

```shell
lncli --macaroonpath=/home/nodeyez/.lnd/nodeyez.macaroon getinfo | jq .identity_pubkey
```

**If you get an error, please report as a new issue.  You will not be able to run scripts requiring access to lightning until this is resolved.**
  
You can also verify that the nodeyez macaroon for lncli does not allow any actions that aren't in its permission set.  For example, getting a new wallet address will fail

```shell
lncli --macaroonpath=/home/nodeyez/.lnd/nodeyez.macaroon newaddress p2wkh
```
For this you should have gotten the following error

`[lncli] rpc error: code = Unknown desc = permission denied`

You can list the permissions that the macaroon has by using the `printmacaroon` operation

```shell
lncli --macaroonpath=/home/nodeyez/.lnd/nodeyez.macaroon printmacaroon --macaroon_file /home/nodeyez/.lnd/nodeyez.macaroon
```

The output should appear as follows. These are the only calls that the  nodeyez scripts make at this time.

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
    "uri:/lnrpc.Lightning/ListInvoices",
    "uri:/lnrpc.Lightning/ListPayments",
    "uri:/lnrpc.Lightning/ListPeers"
  ],
  "caveats": null
}
```

### Grant and Test LND-REST Access

You will need the following information to setup rest based access

- IP address of lnd node (e.g. 127.0.0.1 if local)
- The listening port for REST calls (e.g. 10080)
- The hex encoded macaroon info
- The hex encoded tls certificate info

In the Nodeyez config folder, locate the lnd-rest.json file and edit it

```sh
nano ~/nodeyez/config/lnd-rest.json
```

Set the appropriate field values for the profile named `default`, which assumes a local LND node.  Alternatively you can copy the structure to setup a new profile if you need to access multiple Lightning Nodes.  Set one of the profiles as the value for the `activeProfile` field.  

Save (CTRL+O) and Exit (CTRL+X).

To test the setup, open a python terminal using the environment

```sh
cd ~/nodeyez/scripts
~/.pyenv/nodeyez/bin/python
```

Paste in these commands

```python
from vicariousbitcoin import *
lndMode
lndGetNodeChannels(lndRESTOptions)
exit()
```
If successful, it should report the LND mode as REST and report any current channels.

---

[Home](../) | [Back to Tools]({% link _install_steps/3tools.md %}) | [Continue to Panel Index]({% link _install_steps/5panels.md %})
