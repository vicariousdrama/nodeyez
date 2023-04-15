---
name: Daily Data Retrieval
title: Daily Data Retrieval script
layout: default
---

# Daily Data Retrieval

This script is purely used to gather information from remote resources on a
periodic basis.  While its named daily data retrieval, in truth it runs
continuously and different data sets being retrieved can happen at differing
intervals.

Most current scripts are still working off of a snapshot type basis where
they report on a point in time when they are run.  Going forward there will
be a push to transition to using the data collected from this script which
will also allow for more graphing trends.

## Script Location

The script is installed at 
[~/nodeyez/scripts/daily-data-retrieval.py](../scripts/daily-data-retrieval.py).

## Configuration

Currently there is no external configuration file.  Within the __main__ part
of the script are the defaults.  The following data sets are all set to be
retrieved, at varying intervals.

| Data Set | Interval | Config File | Configuration Documentation |
| --- | --- | --- | --- |
| Bisq | 1 hour | [../config/satsperfiatunit.json](../sample-config/satsperusd.json) | [doc](./script-satsperfiatunit.md) |
| CollectAPI | 24 hours | [../config/collectapi.json](../sample-config/collectapi.json) | [doc](./config-collectapi.md) |
| Compass Hardware | 1 hour | [../config/compassmininghardware.json](../sample-config/compassmininghardware.json) | [doc](./script-compassmininghardware.md) |
| Compass Status | 23 hours | [../config/compassminingstatus.json](../sample-config/compassminingstatus.json) | [doc](./script-compassminingstatus.md) |
| F2 Pool | 23 hours | [../config/f2pool.json](../sample-config/miningpool-f2pool.json) | [doc](./script-miningpool-f2pool.md) |
| Fear and Greed | 12 hours | [../config/fearandgreed.json](../sample/config/fearandgreed.json) | [doc](./script-fearandgreed.md) |
| Luxor | 23 hours | [../config/miningpool-luxorpool.json](../sample-config/miningpool-luxorpool.json) | [doc](./script-miningpool-luxorpool.md) |
| Braiinspool | 23 hours | [../config/miningpool-braiinspool.json](../sample-config/miningpool-braiinspool.json) | [doc](./script-miningpool-braiinspool.md) |

Until this file is externalized, you are strongly encouraged to only make
changes to whether a data set is enabled or not.  Any future updates will
overwrite your customizations to the script.

## Run Directly

Ensure the virtual environment is activated
```shell
source ~/.pyenv/nodeyez/bin/activate
```

Change to the scripts folder
```shell
cd ~/nodeyez/scripts
```

Run it
```shell
python daily-data-retrieval.py
```

Press CTRL+C to stop the process

## Run at Startup

To enable the script to run at startup, as the privileged user run the following

```shell
sudo systemctl enable nodeyez-daily-data-retrieval.service

sudo systemctl start nodeyez-daily-data-retrieval.service
```