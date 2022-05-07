# ![Nodeyez](https://raw.githubusercontent.com/vicariousdrama/nodeyez/main/images/nodeyez.svg)
Display panels to get the most from your node

![case](./images/case-lightningshell.jpg)

This repository contains simple [scripts](./scripts) used to generate images 
representing different state about your node, market rates, mining and more.

The images can be displayed via simple slideshow to attached screen, or to a
website dashboard.  The installation steps below will guide you through setting
up both options.  Some scripts also have support for reporting data to a local [Blockclock Mini](https://blockclockmini.com/).
For convenice, systemd service scripts are also available to allow for running
them at startup automatically.


<img src="./images/arthash-719360.png" width=196 /><img src="./images/arthashdungeon.png" width=196 /><img src="./images/blockheight.png" width=196 /><img src="./images/channelbalance.png" width=196 /><img src="./images/compassmininghardware.png" width=196 /><img src="./images/compassminingstatus.png" width=196 /><img src="./images/difficultyepoch.png" width=196 /><img src="./images/f2pool.png" width=196 /><img src="./images/gasprice.png" width=196 /><img src="./images/ipaddress.png" width=196 /><img src="./images/logo.png" width=196 /><img src="./images/luxor-mining-hashrate-2021-12.png" width=196 /><img src="./images/mempoolblocks.png" width=196 /><img src="./images/minerbraiins.png" width=196 /><img src="./images/raretoshi.png" width=196 /><img src="./images/rof-sample.png" width=196 /><img src="./images/satsperusd.png" width=196 /><img src="./images/slushpool.png" width=196 /><img src="./images/sysinfo.png" width=196 /><img src="./images/utcclock.png" width=196 />

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
2. [Python and Dependencies](./docs/install-2-pythondeps.md)
3. [Display Screen](./docs/install-3-displayscreen.md)
4. [Nodeyez User and this Git Repository](./docs/install-4-nodeyez.md)
5. [Website Dashboard](./docs/install-5-websitedashboard.md)
6. [Running Services at Startup](./docs/install-6-runatstartup.md)


