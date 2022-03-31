# ![Nodeyez](https://raw.githubusercontent.com/vicariousdrama/nodeyez/main/images/nodeyez.svg)
Display panels to get the most from your node

## Setting up the Nodeyez User 

Now we get to specifics of the Nodeyez user and cloning this repository.

You should be logged in as a privileged user to enter these command

### 1. Determine path for storing nodeyez files and create the user

   It is preferable to run nodeyez from an external drive and store created 
   images there as well to reduce potential to wear out the microsd card

   Determine if you have an external drive attached. List all of your
   file systems of type ext4 as follows:

   ```sh
   df -t ext4 -h
   ```

   Sample output

   ```c
   Filesystem      Size  Used Avail Use% Mounted on
   /dev/root        29G  7.0G   21G  26% /
   /dev/sda1       916G  463G  407G  54% /mnt/ext
   ```

   In the above output, there are two file systems.  The one at `/dev/root` is
   29G in size and represents the SD card mounted at the root of the system.
   The second one is `/dev/sda1`, a 1TB external drive with over 400 GB free
   having a mount point of `/mnt/ext`.  Your mount point for /dev/sda1 may
   be different.  For example, MyNodeBTC uses a mount point of /mnt/hdd. 

   Only do this next block if you have an external drive attached. Modify 
   `/dev/sda1` as desired to use a different filesystem.

   ```sh
   EXT_DRIVE_MOUNT=`df|grep /dev/sda1|awk '{print $6}'`
   NODEYEZ_HOME=${EXT_DRIVE_MOUNT}/nodeyez
   sudo adduser --home ${NODEYEZ_HOME} --gecos "" --disabled-password nodeyez
   sudo ln -s ${NODEYEZ_HOME} /home/nodeyez
   sudo chown -R nodeyez:nodeyez /home/nodeyez
   ```

   If you don't have an external drive, then you'll do this command which
   will use the default locations for the home folder and create it on the
   microsd 

   ```sh
   NODEYEZ_HOME=/home/nodeyez
   sudo adduser --gecos "" --disabled-password nodeyez
   ```

### 2. Add the user to the debian-tor group to allow it to configure tor directly

   ```sh
   sudo adduser nodeyez debian-tor
   ```

### 3. Add Bitcoin configuration for nodeyez from existing configuration.

   You can skip this step if you are not using any scripts that require Bitcoin.

   Technically we only need the rpcauth or rpcuser and rpcpassword settings to
   allow bitcoin-cli to work, but this is the easiest way to setup that I've
   found without simply adding the nodeyez user to the bitcoin group and
   linking directories.  *If you know a way to grant read only access without
   wallet to a user, please open an issue or pull request.*

   This assumes that Bitcoin was setup on your node with a dedicated user named
   bitcoin.  This is the case for MyNodeBTC and Raspibolt.  Other node types
   have not yet been verified. *If you are using Raspiblitz or Umbrel and can
   add clarity here, please open an issue or pull request.*

   ```sh
   sudo mkdir -p /home/nodeyez/.bitcoin
   sudo cp /home/bitcoin/.bitcoin/bitcoin.conf /home/nodeyeyz/.bitcoin/bitcoin.conf
   sudo cp /home/bitcoin/.bitcoin/.cookie /home/nodeyeyz/.bitcoin/.cookie
   sudo chown -R nodeyez:nodeyez /home/nodeyez/.bitcoin
   ```

### 4. Add LND tls cert and bake a macaroon specific to nodeyez

   You can skip this step if you are not using any scripts that require Lightning.

   As with the bitcoin step above, this assumes that the node is setup with an
   LND (Lightning Network Daemon) implementation under the bitcoin user.  If you
   are using C-Lightning or another implementation, you may need to alter the
   paths. *Please open an issue or pull request to provide information or help
   for others*

   ```sh
   sudo mkdir -p /home/nodeyez/.lnd
   sudo cp /home/bitcoin/.lnd/tls.cert /home/nodeyez/.lnd/tls.cert
   lncli bakemacaroon uri:/lnrpc.Lightning/GetInfo uri:/lnrpc.Lightning/GetNodeInfo uri:/lnrpc.Lightning/ListPeers uri:/lnrpc.Lightning/ListChannels uri:/lnrpc.Lightning/ChannelBalance uri:/lnrpc.Lightning/ConnectPeer uri:/lnrpc.Lightning/DisconnectPeer --save_to ${HOME}/nodeyez.macaroon
   sudo mv ${HOME}/nodeyez.macaroon /home/nodeyez/.lnd/nodeyez.macaroon
   sudo chown -R nodeyez:nodeyez /home/nodeyez/.lnd
   ```

   Whenever calling lncli with the nodeyez user, the macaroon path can now be provided as follows

   `lncli --macaroonpath=/home/nodeyez/.lnd/nodeyez.macaroon getinfo`

### 5. Change to the nodeyez user

   ```sh
   sudo su - nodeyez
   ```

### 6. Test that the nodeyez user has access to bitcoin-cli and lncli

   You can skip the portions below if you didn't setup bitcoin or lightning
   for the nodeyez user in steps 3 and 4 above.  Continue with step 7 below.

   For bitcoin, lets get a simple output of mining info which yields the block
   height, difficulty, estimated hashrate per second, chain, and some other details

   ```sh
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

   **If you get an error, please report as a github issue.  You will not be able
   to run scripts requiring access to bitcoin until this is resolved.**

   For lightning, first we will get the nodes public key

   ```sh
   lncli --macaroonpath=/home/nodeyez/.lnd/nodeyez.macaroon getinfo | jq .identity_pubkey
   ```

   **If you get an error, please report as a github issue.  You will not be able
   to run scripts requiring access to lightning until this is resolved.**
  
   You can also verify that the nodeyez macaroon for lncli does not allow any
   actions that aren't in its permission set.  For example, getting a new
   wallet address will fail

   ```sh
   lncli --macaroonpath=/home/nodeyez/.lnd/nodeyez.macaroon newaddress p2wkh
   ```
   For this you should have gotten the following error
   `[lncli] rpc error: code = Unknown desc = permission denied`

   You can list the permissions that the macaroon has by using the printmacaroon
   operation

   ```sh
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
         "uri:/lnrpc.Lightning/DisconnectPeer",
         "uri:/lnrpc.Lightning/GetInfo",
         "uri:/lnrpc.Lightning/GetNodeInfo",
         "uri:/lnrpc.Lightning/ListChannels",
         "uri:/lnrpc.Lightning/ListPeers"
      ],
      "caveats": null
   }
   ```

### 7. Clone the repository as nodeyez user

   ```sh
   if [ "`whoami`" == "nodeyez" ]; then
   cd /home/nodeyez ; git clone https://github.com/vicariousdrama/nodeyez.git
   fi
   ```

### 8. Create folders and set scripts as executable as the nodeyez user

   ```sh
   if [ "`whoami`" == "nodeyez" ]; then
   mkdir -p /home/nodeyez/nodeyez/config
   mkdir -p /home/nodeyez/nodeyez/data
   mkdir -p /home/nodeyez/nodeyez/imageoutput
   cp /home/nodeyez/nodeyez/sample-config/*.json /home/nodeyez/nodeyez/config
   fi
   ```

## Configuring and Running Nodeyez Scripts

The nodeyez user and scripts are now available locally.  Individual scripts
can be configured with their respective config file.  View the documentation
on each script for more information.  You may want to open these in a
separate tab or window for convenience.

**Local Only**
- [ip address](./script-ipaddress.md)
- [system info](./script-sysinfo.md)
- [utc clock](./script-utcclock.md)

**Bitcoin Dependent**
- [art hash](./script-arthash.md)
- [art hash dungeon](./script-arthashdungeon.md)
- [block height](./script-blockheight.md)
- [difficulty epoch](./script-difficultyepoch.md)
- [mempool blocks](./script-mempoolblocks.md)

**Lightning Dependent**
- [channel balance](./script-channelbalance.md)
- [ring of fire](./script-rofstatus.md)

**Mining Related**
- [f2pool](./script-f2pool.md)
- [luxor](./script-luxor-mining-hashrate.md)
- [slushpool](./script-slushpool.md)
- [miner - braiins](./script-minerbraiins.md)

**Other Fun Stuff**
- [compass mining hardware](./script-compassmininghardware.md)
- [compass mining status](./script-compassminingstatus.md)
- [gas prices](./script-gasprice.md)
- [raretoshi](./script-raretoshi.md)
- [sats per usd](./script-satsperusd.md)

## Running the Slideshow

If you have a screen attached to your raspberry pi, you can display the 
generated images to the screen using the slideshow script installed at
[/home/nodeyez/nodeyez/scripts/slideshow.sh](../scripts/slideshow.sh)

If you are currently logged in as nodeyez, `exit` back to the priviledged user,
then run the following

   ```sh
   cd /home/nodeyez/nodeyez/scripts
   sudo ./slideshow.sh &
   ```

A process ID (PID) number will be displayed as output to the console for the
background process. You may also find this process ID with this command:

   ```sh
   ps aux | grep slideshow | grep -v grep | awk '{print $2}'
   ```

You should start seeing images display on your screen.  If you dont see any
images, then edit the `/home/nodeyez/nodeyez/scripts/slideshow.sh` file, and 
remove the part at the end `> /dev/null 2>&1`, and save the file.  When you run
the script again it will now show any errors to the console.

Terminate any existing background process before restarting the slideshow script

   ```sh
   for p in `ps aux | grep slideshow | grep -v grep | awk '{print $2}'`; do sudo kill $p; done
   sudo /home/nodeyez/nodeyez/scripts/slideshow.sh &
   ```

---

[Home](../README.md) | [Back to Display Screen](./install-3-displayscreen.md) | [Continue to Website Dashboard](./install-5-websitedashboard.md)

