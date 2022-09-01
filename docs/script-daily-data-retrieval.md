# ![Nodeyez](https://raw.githubusercontent.com/vicariousdrama/nodeyez/main/images/nodeyez.svg)
Display panels to get the most from your node

## Daily Data Retrieval

This script is purely used to gather information from remote resources on a
periodic basis.  While its named daily data retrieval, in truth it runs
continuously and different data sets being retrieved can happen at differing
intervals.

Most current scripts are still working off of a snapshot type basis where
they report on a point in time when they are run.  Going forward there will
be a push to transition to using the data collected from this script which
will also allow for more graphing trends.

The script is installed at [/home/nodeyez/nodeyez/scripts/daily-data-retrieval.py](../scripts/daily-data-retrieval.py).

* Before running this script you must have met dependencies

  - beautifulsoup4 is required for compass mining scripts to parse HTML

  ```sh
  python3 -m pip install beautifulsoup4
  ```

  - pandas is required for luxor scripts to use the client library for data retrieval

  ```sh
  python3 -m pip install pandas
  ```

* To run this script

   ```sh
   cd /home/nodeyez/nodeyez/scripts
   /home/nodeyez/nodeyez/scripts/daily-data-retrieval.py
   ```

   Press CTRL+C to stop the process

* To configure this script

   Currently there is no external configuration file.  Within the __main__ part
   of the script are the defaults.  The following data sets are all set to be
   retrieved, at varying intervals.

   | Data Set | Interval | Config File | Configuration Documentation |
   | --- | --- | --- | --- |
   | Bisq | 1 hour | [/home/nodeyez/nodeyez/config/satsperusd.json](../sample-config/satsperusd.json) | [doc](./script-satsperusd.md) |
   | CollectAPI | 24 hours | [/home/nodeyez/nodeyez/config/collectapi.json](../sample-config/collectapi.json) | [doc](./config-collectapi.md) |
   | Compass Hardware | 1 hour | [/home/nodeyez/nodeyez/config/compassmininghardware.json](../sample-config/compassmininghardware.json) | [doc](./script-compassmininghardware.md) |
   | Compass Status | 23 hours | [/home/nodeyez/nodeyez/config/compassminingstatus.json](../sample-config/compassminingstatus.json) | [doc](./script-compassminingstatus.md) |
   | F2 Pool | 23 hours | [/home/nodeyez/nodeyez/config/f2pool.json](../sample-config/f2pool.json) | [doc](./script-f2pool.md) |
   | Luxor | 23 hours | [/home/nodeyez/nodeyez/config/luxor.json](../sample-config/luxor.json) | [doc](./script-luxor-mining-hashrate.md) |
   | Slushpool | 23 hours | [/home/nodeyez/nodeyez/config/slushpool.json](../sample-config/slushpool.json) | [doc](./script-slushpool.md) |


   Until this file is externalized, you are strongly encouraged to only make
   changes to whether a data set is enabled or not.  Any future updates may
   overwrite your customizations to the script.

---

[Home](../README.md) | 

