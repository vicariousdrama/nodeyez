---
name: Setting up Regtest
title: NODEYEZ Development Environment
layout: default
---

# Regtest

It can be helpful to use a regtest bitcoin environment that is private for testing. While not going into detail about Regtest, this page will cover installing a new instance of Bitcoin or using existing for regtest with Nodeyez development.

# Check for Bitcoin

Determine if you have bitcoin 
```shell
which bitcoin-cli
```

If you have Bitcoin installed already then you can use that. Otherwise, proceed with the subsection below to install.

## Install Bitcoin

If you don't have Bitcoin installed already, then you can get setup by following these steps. For brevity, this does not perform any verification. If you want to verify, or need other releases based on your architecture, you can follow the guidance on the [Bitcoin Core](https://bitcoincore.org/en/download/) website.

### For Intel / AMD 64 Bit
```shell
cd /tmp

wget https://bitcoincore.org/bin/bitcoin-core-24.0.1/bitcoin-24.0.1-x86_64-linux-gnu.tar.gz

tar -xvf bitcoin-24.0.1-x86_64-linux-gnu.tar.gz

sudo install -m 0755 -o root -g root -t /usr/local/bin bitcoin-24.0.1/bin/*
```

### For Raspberry Pi
```shell
cd /tmp

wget https://bitcoincore.org/bin/bitcoin-core-24.0.1/bitcoin-24.0.1-aarch64-linux-gnu.tar.gz

tar -xvf bitcoin-24.0.1-aarch64-linux-gnu.tar.gz

sudo install -m 0755 -o root -g root -t /usr/local/bin bitcoin-24.0.1/bin/*
```

### Verify that Bitcoin is installed
```shell
which bitcoin-cli

bitcoin-cli --version
```

# Setup Regtest Config

Now that you have Bitcoin available, lets create configuration files for Regtest environments

## Create regtest instance folder
We'll be using the data folder. So lets make a folder for the regtest instance
```shell
mkdir -p ~/nodeyez/data/bitcoinregtest1
```

## Copy sample configuration
```shell
cp ~/nodeyez/sample-config/bitcoinregtest1.conf ~/nodeyez/config/bitcoinregtest1.conf
```

## Download and generate RPC credentials
```shell
REG1RPCUSERNAME=regtestuser1
REG1RPCPASSWORD=regtestpass1

cd /tmp

wget https://raw.githubusercontent.com/bitcoin/bitcoin/master/share/rpcauth/rpcauth.py

# Removes any existing rpcauth line
sed -i '/^rpcauth=/d' ~/nodeyez/config/bitcoinregtest1.conf

# Generates new rpcauth line and puts it into the bitcoin conf file.
python3 rpcauth.py ${REG1RPCUSERNAME} ${REG1RPCPASSWORD} | grep rpcauth >> ~/nodeyez/config/bitcoinregtest1.conf

# Removes existing data dir line
sed -i '/^datadir=/d' ~/nodeyez/config/bitcoinregtest1.conf

# Add data dir with absolute path
echo "datadir=${HOME}/nodeyez/data/bitcoinregtest1" >> ~/nodeyez/config/bitcoinregtest1.conf
```

# Starting Regtest

In a terminal window, run the following
```shell
bitcoind -conf=${HOME}/nodeyez/config/bitcoinregtest1.conf -regtest
```

You should see output reporting the Bitcoin version, using the specified data diretory and config file and reading in values. The end of the startup logs should indicate the current UpdateTip, nBestHeight etc.

Next, open another terminal instance and run the following
```shell
bitcoin-cli -conf=${HOME}/nodeyez/config/bitcoinregtest1.conf -regtest getbestblockhash
```

With no blocks yet created, example output
```
0f9188f13cb7b2c71f2a335e3a4fc328bf5beb436012afca590b1a11466e2206
```

# Generate Regtest Blocks

## Create a wallet
```shell
bitcoin-cli -conf=${HOME}/nodeyez/config/bitcoinregtest1.conf -regtest createwallet regwallet
```
## Create an address
```shell
REGADDRESS=$(bitcoin-cli -conf=${HOME}/nodeyez/config/bitcoinregtest1.conf -regtest getnewaddress)
```
The output is captured to a variable

## Generate a block
Generate a block, mining the subsidy to the address captured previously
```shell
bitcoin-cli -conf=${HOME}/nodeyez/config/bitcoinregtest1.conf -regtest generatetoaddress 1 ${REGADDRESS}
```
The output shows the blockhash of the blocks (1) generated.  Repeat the same but for 100 blocks
```shell
bitcoin-cli -conf=${HOME}/nodeyez/config/bitcoinregtest1.conf -regtest generatetoaddress 100 ${REGADDRESS}
```

There will now be 101 blocks total, 1 of which is matured and spendable in a transaction, and the remaining 100 which are not yet matured.

## Check the block height
```shell
bitcoin-cli -conf=${HOME}/nodeyez/config/bitcoinregtest1.conf -regtest getblockchaininfo
```
The output shows that 101 blocks have been created

## Loading wallet
This is handy after restarting the Regtest instance after shutdown
```shell
bitcoin-cli -conf=${HOME}/nodeyez/config/bitcoinregtest1.conf -regtest loadwallet regwallet
```

## Check balance
```shell
bitcoin-cli -conf=${HOME}/nodeyez/config/bitcoinregtest1.conf -regtest getbalance
```

## Use same output address
If you closed the terminal window where the variable was set from generating the address previously and you want to reuse the same address, you can use this command to find the address used in the most recent block's coinbase
```shell
REGADDRESS=$(bitcoin-cli -conf=${HOME}/nodeyez/config/bitcoinregtest1.conf -regtest getblock `bitcoin-cli -conf=${HOME}/nodeyez/config/bitcoinregtest1.conf -regtest getbestblockhash` 2 | jq -r .tx[0].vout[0].scriptPubKey.address)
```

# Configure Nodeyez for Regtest

To support Regtest, or alternate environments in general, edit the [~/nodeyez/config/bitcoin-cli.json](../config/bitcoin-cli.json) file, and set the activeProfile value to "regtest1".  The [vicariousbitcoin.py](../scripts/vicariousbitcoin.py) helper script
will inject the value as command options when making calls to bitcoin-cli.

# Test Nodeyez Bitcoin Scripts

With the regtest instance running, and Nodeyez configuration set to use the regtest profile, you should be able to run the bitcoin scripts using standard debugging in the IDE (F5), or running in the terminal (cd ~/nodeyez/scripts && python scriptname.py)

# Stopping Regtest

To stop the regtest instance, 

Option1: Switch to the terminal window running bitcoind, and CTRL+C to halt it.

Option2: Use the bitcoin-cli command
```shell
bitcoin-cli -conf=${HOME}/nodeyez/config/bitcoinregtest1.conf -regtest stop
```

# Resetting Regtest

To clear the regtest environment to start fresh, first Stop the instance, and then run the following
```shell
rm -rf ~/nodeyez/data/bitcoinregtest1/regtest
```

---

[Home](../) | [Back to Running and Changing Scripts]({% link _developer/2runandchange.md %})
