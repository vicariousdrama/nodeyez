# ![Nodeyez](../../../../raw/branch/main/images/nodeyez.svg)
Display panels to get the most from your node

[Home](../README.md) | [Back to Website Dashboard](./install-5-websitedashboard.md) 

---

## Running Services at Startup

You can run the scripts you so choose automatically at startup so that you don't
have to login and manually start them after a power outage.  To do this, copy 
the service scripts to the appropriate systemd folder

   ```sh
   sudo cp /home/nodeyez/nodeyez/scripts/systemd/*.service /etc/systemd/system/
   ```

### 1. Enable services

You don't have to enable every service, just the ones you want to run 
automatically at startup.

   ```sh
   sudo systemctl enable nodeyez-arthash.service
   sudo systemctl enable nodeyez-arthashdungeon.service
   sudo systemctl enable nodeyez-blockheight.service
   sudo systemctl enable nodeyez-channelbalance.service
   sudo systemctl enable nodeyez-compassminingstatus.service
   sudo systemctl enable nodeyez-daily-data-retrieval.service
   sudo systemctl enable nodeyez-difficultyepoch.service
   sudo systemctl enable nodeyez-f2pool.service
   sudo systemctl enable nodeyez-halving.service
   sudo systemctl enable nodeyez-ipaddress.service
   sudo systemctl enable nodeyez-mempoolblocks.service
   sudo systemctl enable nodeyez-minerbraiins.service
   sudo systemctl enable nodeyez-minermicrobt.service
   sudo systemctl enable nodeyez-rofstatus.service
   sudo systemctl enable nodeyez-satsperusd.service
   sudo systemctl enable nodeyez-slideshow.service
   sudo systemctl enable nodeyez-slushpool.service
   sudo systemctl enable nodeyez-sysinfo.service
   sudo systemctl enable nodeyez-utcclock.service
   sudo systemctl enable nodeyez-whirlpoolclimix.service
   sudo systemctl enable nodeyez-whirlpoolliquidity.service
   ```

### 2. Start services

Only issue the systemctl start command for those services you want to run.

   ```sh
   sudo systemctl start nodeyez-arthash.service
   sudo systemctl start nodeyez-arthashdungeon.service
   sudo systemctl start nodeyez-blockheight.service
   sudo systemctl start nodeyez-channelbalance.service
   sudo systemctl start nodeyez-compassminingstatus.service
   sudo systemctl start nodeyez-daily-data-retrieval.service
   sudo systemctl start nodeyez-difficultyepoch.service
   sudo systemctl start nodeyez-f2pool.service
   sudo systemctl start nodeyez-halving.service
   sudo systemctl start nodeyez-ipaddress.service
   sudo systemctl start nodeyez-mempoolblocks.service
   sudo systemctl start nodeyez-minerbraiins.service
   sudo systemctl start nodeyez-minermicrobt.service
   sudo systemctl start nodeyez-rofstatus.service
   sudo systemctl start nodeyez-satsperusd.service
   sudo systemctl start nodeyez-slideshow.service
   sudo systemctl start nodeyez-slushpool.service
   sudo systemctl start nodeyez-sysinfo.service
   sudo systemctl start nodeyez-utcclock.service
   sudo systemctl start nodeyez-whirlpoolclimix.service
   sudo systemctl start nodeyez-whirlpoolliquidity.service
   ```

### 3. List Nodeyez services and status

* For a listing of the Nodeyez services that are enabled to run automatically
  every time your system boots, use this command

   ```sh
   sudo systemctl list-unit-files --type=service --state=enabled | grep nodeyez
   ```

* More often though, you may want to see the same list, but with the running
  state as well.  You can use this command

   ```sh
   sudo systemctl list-units --type=service | grep nodeyez
   ```

Sample output

   ```c
     nodeyez-channelbalance.service                              loaded active running Image(s) for Lightning Channel Balances
     nodeyez-daily-data-retrieval.service                        loaded active running Retrieve background data for Nodeyez
     nodeyez-difficultyepoch.service                             loaded active running Image for Difficulty Epoch
   ● nodeyez-f2pool.service                                      loaded failed failed  Image for F2 Pool Mining Summary
     nodeyez-mempoolblocks.service                               loaded active running Image for Mempool Blocks
     nodeyez-minerbraiins.service                                loaded active running Image for Miner Status running Braiins
     nodeyez-satsperusd.service                                  loaded active running Image for Sats per USD
     nodeyez-slideshow.service                                   loaded active running Image Display Slideshow to Framebuffer
   ```

In the above example, we've chosen to only run some of the services, and one of
them is showing that they failed.  Viewing the logs can help when diagnosing
the cause of failure.

### 4. View logs

You can view the logs using journalctl like this

   ```sh
   sudo journalctl -fu nodeyez-sysinfo.service
   ```

And press CTRL+C to stop viewing the logs for that service


---

[Home](../README.md) | [Back to Website Dashboard](./install-5-websitedashboard.md) 

