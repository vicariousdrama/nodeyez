# ![Nodeyez](https://raw.githubusercontent.com/vicariousdrama/nodeyez/main/images/nodeyez.svg)
Display panels to get the most from your node

![image strip](./images/nodeyez-4x4-layout.png)

This repository contains simple [scripts](./scripts) used to generate images 
representing different state about your node, market rates, mining and more.

The images can be displayed via simple slideshow to attached screen, or to a
website dashboard.  The installation steps below will guide you through setting
up both options.  Some scripts also have support for reporting data to a local [Blockclock Mini](https://blockclockmini.com/).
For convenice, systemd service scripts are also available to allow for running
them at startup automatically.

STATUS: BETA.  Scripts are functional, but there may be bugs, or unhandled 
exceptions may cause the script or wrapper services to terminate.  Please
consider reviewing, testing, and providing feedback as a github issue.

## Quick Menu of Info Panels

| Panel Name | Requires Bitcoin Node | Requires Lightning Service | Makes Remote Calls |
| --- | --- | --- | --- |
|                **_Local Only_** |
| [ip address](./docs/script-ipaddress.md) | | | |
| [system info](./docs/script-sysinfo.md) | | | |
| [utc clock](./docs/script-utcclock.md) | | | |
|                **_Bitcoin Dependent_** |
| [art hash](./docs/script-arthash.md) | Yes | | |
| [art hash dungeon](./docs/script-arthashdungeon.md) | Yes | | |
| [block height](./docs/script-blockheight.md) | Yes | | |
| [difficulty epoch](./docs/script-difficultyepoch.md) | Yes | | |
| [mempool blocks](./docs/script-mempoolblocks.md) | Optional | | Yes |
|                **_Lightning Dependent_** |
| [channel balance](./docs/script-channelbalance.md) | | Yes | |
| [ring of fire](./docs/script-rofstatus.md) | | Yes | Yes |
|                **_Mining Related_** |
| [f2 pool](./docs/script-f2pool.md) | | | Yes |
| [luxor pool](./docs/script-luxor-mining-hashrate.md) | | | Yes |
| [miner - braiins](./docs/script-minerbraiins.md) | | | |
| [slushpool](./docs/script-slushpool.md) | | | Yes |
|                **_Other Fun Stuff_** |
| [compass mining hardware](./docs/script-compassmininghardware.md) | | | Yes |
| [compass mining status](./docs/script-compassminingstatus.md) | | | Yes |
| [gas price](./docs/script-gasprice.md) | | | Yes |
| [raretoshi](./docs/script-raretoshi.md) | | | Yes |
| [sats per usd](./docs/script-satsperusd.md) | | | Yes |

## Installation Steps

1. [Raspberry Pi Node](./docs/install-1-raspberrypinode.md)
2. [Python and Library Dependencies](./docs/install-2-pythonlibs.md)
3. [Display Screen](./docs/install-3-displayscreen.md)
4. [Nodeyez User and this Git Repository](./docs/install-4-nodeyez.md)
5. [Website Dashboard](./docs/install-5-websitedashboard.md)
6. [Running Services at Startup](./docs/install-6-runatstartup.md)


