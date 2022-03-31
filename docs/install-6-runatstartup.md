# ![Nodeyez](https://raw.githubusercontent.com/vicariousdrama/nodeyez/main/images/nodeyez.svg)
Display panels to get the most from your node

## Running Services at Startup

You can run the scripts you so choose automatically at startup so that you don't
have to login and manually start them after a power outage.  To do this, copy 
the service scripts to the appropriate systemd folder

   ```sh
   sudo cp /home/nodeyez/nodeyez/scripts/systemd/*.service /etc/systemd/system/
   ```

And enable them.  You don't have to enable every service, just the ones you want 
to run automatically at startup

   ```sh
   sudo systemctl enable nodeyez-arthash.service
   sudo systemctl enable nodeyez-arthashdungeon.service
   sudo systemctl enable nodeyez-blockheight.service
   sudo systemctl enable nodeyez-channelbalance.service
   sudo systemctl enable nodeyez-compassmininghardware.service
   sudo systemctl enable nodeyez-compassminingstatus.service
   sudo systemctl enable nodeyez-daily-data-retrieval.service
   sudo systemctl enable nodeyez-difficultyepoch.service
   sudo systemctl enable nodeyez-f2pool.service
   sudo systemctl enable nodeyez-gasprice.service
   sudo systemctl enable nodeyez-ipaddress.service
   sudo systemctl enable nodeyez-mempoolblocks.service
   sudo systemctl enable nodeyez-minerbraiins.service
   sudo systemctl enable nodeyez-raretoshi.service
   sudo systemctl enable nodeyez-rofstatus.service
   sudo systemctl enable nodeyez-satsperusd.service
   sudo systemctl enable nodeyez-slideshow.service
   sudo systemctl enable nodeyez-slushpool.service
   sudo systemctl enable nodeyez-sysinfo.service
   sudo systemctl enable nodeyez-utcclock.service
   ```

And then start them. As above, only issue the systemctl start command for those 
services you want to run.

   ```sh
   sudo systemctl start nodeyez-arthash.service
   sudo systemctl start nodeyez-arthashdungeon.service
   sudo systemctl start nodeyez-blockheight.service
   sudo systemctl start nodeyez-channelbalance.service
   sudo systemctl start nodeyez-compassmininghardware.service
   sudo systemctl start nodeyez-compassminingstatus.service
   sudo systemctl start nodeyez-daily-data-retrieval.service
   sudo systemctl start nodeyez-difficultyepoch.service
   sudo systemctl start nodeyez-f2pool.service
   sudo systemctl start nodeyez-gasprice.service
   sudo systemctl start nodeyez-ipaddress.service
   sudo systemctl start nodeyez-mempoolblocks.service
   sudo systemctl start nodeyez-minerbraiins.service
   sudo systemctl start nodeyez-raretoshi.service
   sudo systemctl start nodeyez-rofstatus.service
   sudo systemctl start nodeyez-satsperusd.service
   sudo systemctl start nodeyez-slideshow.service
   sudo systemctl start nodeyez-slushpool.service
   sudo systemctl start nodeyez-sysinfo.service
   sudo systemctl start nodeyez-utcclock.service
   ```

You can view the logs using journalctl like this

   ```sh
   sudo journalctl -fu nodeyez-sysinfo.service
   ```

And press CTRL+C to stop viewing the logs


---

[Home](../README.md) | [Back to Website Dashboard](./install-5-websitedashboard.md) 

