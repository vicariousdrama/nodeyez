---
name: Running Nodeyez Services at Startup
title: NODEYEZ Running at Startup
layout: default
---

# Running Services at Startup

If you installed Nodeyez using the [Quick Start]({% link _install_steps/0quickstart.md %}), then this step is already done for you and you can skip ahead to using the [Nodeyez-Config]({% link _install_steps/9nodeyezconfig.md %}) tool to toggle and view services.

You can run the scripts you so choose automatically at startup so that you don't have to login and manually start them after a power outage or system reboot.  To do this, copy the service scripts to the appropriate systemd folder

```shell
sudo cp /home/nodeyez/nodeyez/scripts/systemd/*.service /etc/systemd/system/
sudo cp /home/nodeyez/nodeyez/scripts/systemd/nodeyez.conf /etc/nodeyez.conf
```

## Enable services

You don't have to enable every service, just the ones you want to run automatically at startup.

```shell
sudo systemctl enable nodeyez-arthash.service
sudo systemctl enable nodeyez-blockhashdungeon.service
sudo systemctl enable nodeyez-blockheight.service
sudo systemctl enable nodeyez-blockstats.service
sudo systemctl enable nodeyez-daily-data-retrieval.service
sudo systemctl enable nodeyez-difficultyepoch.service
sudo systemctl enable nodeyez-fearandgreed.service
sudo systemctl enable nodeyez-feeestimates.service
sudo systemctl enable nodeyez-fiatprice.service
sudo systemctl enable nodeyez-geyserfund.service
sudo systemctl enable nodeyez-halving.service
sudo systemctl enable nodeyez-inscriptionmempool.service
sudo systemctl enable nodeyez-inscriptionparser.service
sudo systemctl enable nodeyez-ipaddresses.service
sudo systemctl enable nodeyez-lndchannelbalance.service
sudo systemctl enable nodeyez-lndchannelfees.service
sudo systemctl enable nodeyez-lndhub.service
sudo systemctl enable nodeyez-lndmessages.service
sudo systemctl enable nodeyez-lndringoffire.service
sudo systemctl enable nodeyez-mempoolspace.service
sudo systemctl enable nodeyez-miner.service
sudo systemctl enable nodeyez-miningpool-braiinspool.service
sudo systemctl enable nodeyez-miningpool-f2pool.service
sudo systemctl enable nodeyez-miningpool-luxorpool.service
sudo systemctl enable nodeyez-nodeyezdual.service
sudo systemctl enable nodeyez-nostrbandstats.service
sudo systemctl enable nodeyez-opreturn.service
sudo systemctl enable nodeyez-satsperfiatunit.service
sudo systemctl enable nodeyez-slideshow.service
sudo systemctl enable nodeyez-sysinfo.service
sudo systemctl enable nodeyez-utcclock.service
sudo systemctl enable nodeyez-whirlpoolclimix.service
sudo systemctl enable nodeyez-whirlpoolliquidity.service
```

## Start services

Only issue the systemctl start command for those services you want to run.

```shell
sudo systemctl start nodeyez-arthash.service
sudo systemctl start nodeyez-blockhashdungeon.service
sudo systemctl start nodeyez-blockheight.service
sudo systemctl start nodeyez-blockstats.service
sudo systemctl start nodeyez-daily-data-retrieval.service
sudo systemctl start nodeyez-difficultyepoch.service
sudo systemctl start nodeyez-fearandgreed.service
sudo systemctl start nodeyez-feeestimates.service
sudo systemctl start nodeyez-fiatprice.service
sudo systemctl start nodeyez-geyserfund.service
sudo systemctl start nodeyez-halving.service
sudo systemctl start nodeyez-inscriptionmempool.service
sudo systemctl start nodeyez-inscriptionparser.service
sudo systemctl start nodeyez-ipaddresses.service
sudo systemctl start nodeyez-lndchannelbalance.service
sudo systemctl start nodeyez-lndchannelfees.service
sudo systemctl start nodeyez-lndhub.service
sudo systemctl start nodeyez-lndmessages.service
sudo systemctl start nodeyez-lndringoffire.service
sudo systemctl start nodeyez-mempoolspace.service
sudo systemctl start nodeyez-miner.service
sudo systemctl start nodeyez-miningpool-braiinspool.service
sudo systemctl start nodeyez-miningpool-f2pool.service
sudo systemctl start nodeyez-miningpool-luxorpool.service
sudo systemctl start nodeyez-nodeyezdual.service
sudo systemctl start nodeyez-nostrbandstats.service
sudo systemctl start nodeyez-opreturn.service
sudo systemctl start nodeyez-satsperfiatunit.service
sudo systemctl start nodeyez-slideshow.service
sudo systemctl start nodeyez-sysinfo.service
sudo systemctl start nodeyez-utcclock.service
sudo systemctl start nodeyez-whirlpoolclimix.service
sudo systemctl start nodeyez-whirlpoolliquidity.service
```

## List Nodeyez Services

For a listing of the Nodeyez services that are enabled to run automatically
every time your system boots, use this command

```shell
sudo systemctl list-unit-files --type=service --state=enabled | grep nodeyez
```

More often though, you may want to see the same list, but with the running
state as well.  You can use this command

```shell
sudo systemctl list-units --type=service | grep nodeyez
```

Sample output

```c
  nodeyez-lndchannelbalance.service      loaded active running LND Channel Balances
  nodeyez-daily-data-retrieval.service   loaded active running Background data retrieval
  nodeyez-difficultyepoch.service        loaded active running Difficulty Epoch
  nodeyez-mempoolspace.service           loaded active running Mempool Blocks and Fee Estimates
  nodeyez-miner.service                  loaded active running Miner Status
● nodeyez-miningpool-f2pool.service      loaded failed failed  F2 Pool Mining Summary
  nodeyez-satsperfiatunit.service        loaded active running Sats per Fiat Unit
  nodeyez-slideshow.service              loaded active running Nodeyez Slideshow Runner
```

In the above example, we've chosen to only run some of the services, and one of them is showing that they failed.  Viewing the logs can help when diagnosing the cause of failure.

## Viewing Logs

You can view the logs using journalctl like this

```shell
sudo journalctl -fu nodeyez-sysinfo.service
```

And press CTRL+C to stop viewing the logs for that service


## Stopping a Service

Stopping a service is just as easy as starting one.

```shell
sudo systemctl stop nodeyez-fearandgreed.service
```

## Disabling a Service

If you desire to disable a service so it does not automatically start you can issue a command structured like this

```shell
sudo systemctl disable nodeyez-fearandgreed.service
```

---

[Home](../) | [Back to Website Dashboard]({% link _install_steps/7websitedashboard.md %}) | [Continue to Nodeyez-Config Tool]({% link _install_steps/9nodeyezconfig.md %})