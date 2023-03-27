---
name: Configuring CollectAPI
title: Configuring for Collectapi
---

# Configuration for collectapi.json

This configuration file is used for defining resources to be retrieved from the
https://collectapi.com site.  It is used in conjuction with the 
[../scripts/daily-data-retrieval.py](./script-daily-data-retrieval.md)
script.

To make use of this configuration in the daily-data-retrieval script, you will
need to establish an account on collectapi.com, subscribe to the free tier, and
then create an API Token.

To configure this file

```shell
nano ../config/collectapi.json
```

Definitions to support the [../scripts/gasprice.py](./script-gasprice.md) script

Assuming an apikey of `thIsIsAsamPleAPIkey:aNd4Del1n3at3dValue`

```json
{
  "dailyretrieve": [
    {
      "enabled": false,
      "url": "https://api.collectapi.com/gasPrice/allUsaPrice",
      "headers": [
        "authorization: apikey thIsIsAsamPleAPIkey:aNd4Del1n3at3dValue",
        "content-type: application/json"
      ],
      "saveToSubfolder": "gasprice/allusaprice"
    },
    {
      "enabled": false,
      "url": "https://api.collectapi.com/gasPrice/canada",
      "headers": [
        "authorization: apikey thIsIsAsamPleAPIkey:aNd4Del1n3at3dValue",
        "content-type: application/json"
      ],
      "saveToSubfolder": "gasprice/canada"
    }
  ]
}
```

Additional definitions may be added in the dailyretrieve field array if there
are other data sets on collectapi that you want to have retrieved periodically.

---

[Home](../) | 

