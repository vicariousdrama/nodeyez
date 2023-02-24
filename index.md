---
title: NODEYEZ - Display panels to get the most from your node
---
# About Nodeyez

Nodeyez is a project that contains a variety of python [scripts](./scripts) to produce images based on your Bitcoin Node

Images can be displayed
* to video output such as an attached screen on a Raspberry Pi
* in a website dashboard for browser based acess

In addition, some scripts have support for reporting data to a local [Blockclock Mini](https://blockclockmini.com/).

Scripts can be run on their own, or run continuously in the background as a service on system startup.

## Sample Panels Created by Nodeyez

<div class="slider">
  <div class="slide"><img src="./images/arthash-719360.png" width=196 /></div>
  <div class="slide"><img src="./images/arthashdungeon.png" width=196 /></div>
  <div class="slide"><img src="./images/blockheight.png" width=196 /></div>
  <div class="slide"><img src="./images/channelbalance.png" width=196 /></div>
  <div class="slide"><img src="./images/channelfees.png" width=196 /></div>
  <div class="slide"><img src="./images/compassminingstatus.png" width=196 /></div>
  <div class="slide"><img src="./images/difficultyepoch.png" width=196 /></div>
  <div class="slide"><img src="./images/f2pool.png" width=196 /></div>
  <div class="slide"><img src="./images/fearandgreed.png" width=196 /></div>
  <div class="slide"><img src="./images/fiatprice.png" width=196 /></div>
  <div class="slide"><img src="./images/inscriptionmempool.png" width=196 /></div>
  <div class="slide"><img src="./images/ipaddress.png" width=196 /></div>
  <div class="slide"><img src="./images/lndhub.png" width=196 /></div>
  <div class="slide"><img src="./images/logo.png" width=196 /></div>
  <div class="slide"><img src="./images/luxor-mining-hashrate-2021-12.png" width=196 /></div>
  <div class="slide"><img src="./images/mempoolblocks.png" width=196 /></div>
  <div class="slide"><img src="./images/minerbraiins.png" width=196 /></div>
  <div class="slide"><img src="./images/opreturn.png" width=196 /></div>
  <div class="slide"><img src="./images/ordinals.png" width=196 /></div>
  <div class="slide"><img src="./images/rof-sample.png" width=196 /></div>
  <div class="slide"><img src="./images/satsperusd.png" width=196 /></div>
  <div class="slide"><img src="./images/slushpool.png" width=196 /></div>
  <div class="slide"><img src="./images/sysinfo.png" width=196 /></div>
  <div class="slide"><img src="./images/utcclock.png" width=196 /></div>
  <div class="slide"><img src="./images/whirlpoolclimix.png" width=196 /></div>
  <div class="slide"><img src="./images/whirlpoolliquidity.png" width=196 /></div>
  <button class="btn btn-next">&gt;</button>
  <button class="btn btn-prev">&lt;</button>
</div>

## Informational Panels

* [IP Address]({% link _docs/script-ipaddress.md %})
* [System Metrics]({% link _docs/script-sysinfo.md %})
* [UTC Clock]({% link _docs/script-utcclock.md %})

## Bitcoin Panels

All of these panels can work with a local Bitcoin node. At this time, information is accessed via bitcoin-cli RPC calls.

* [Art Hash]({% link _docs/script-arthash.md %})
* [Blockhash Dungeon]({% link _docs/script-arthashdungeon.md %})
* [Block Height]({% link _docs/script-blockheight.md %})
* [Difficulty Epoch]({% link _docs/script-difficultyepoch.md %})
* [Halving Countdown]({% link _docs/script-halving.md %})
* [Inscription Mempool]({% link _docs/script-inscriptionmempool.md %})
* [Mempool Blocks]({% link _docs/script-mempoolblocks.md %})
* [OP_RETURN]({% link _docs/script-opreturn.md %})
* [Ordinal Inscriptions]({% link _docs/script-ordinals.md %})

## Lighting (LND) Panels

These panels can be configured to report on local LND based nodes, as well as remote ones over REST.

* [Channel Balance]({% link _docs/script-channelbalance.md %})
* [Channel Fees]({% link _docs/script-channelfees.md %})
* [LND Hub Account Balances]({% link _docs/script-lndhub.md %})
* [Ring of Fire]({% link _docs/script-rofstatus.md %})

## Mining Panels

* [F2 Pool]({% link _docs/script-f2pool.md %})
* [Luxor Pool]({% link _docs/script-luxor-mining-hashrate.md %})
* [Miner - Braiins]({% link _docs/script-minerbraiins.md %})
* [Miner - MicroBT]({% link _docs/script-minermicrobt.md %})
* [Braiins Pool]({% link _docs/script-slushpool.md %})

## Other Fun Panels

* [Dual Image Display]({% link _docs/script-nodeyezdual.md %})
* [Fear and Greed Index]({% link _docs/script-fearandgreed.md %})
* [Price of Bitcoin]({% link _docs/script-fiatprice.md %})
* [Sats per USD]({% link _docs/script-satsperusd.md %})
* [Whirlpool CLI Mix Status]({% link _docs/script-whirlpoolclimix.md %})
* [Whirlpool Liquidity]({% link _docs/script-whirlpoolliquidity.md %})

## No Longer Supported

The scripts are still available, but may not properly function as the data providers have changed from open standards or charge exhorbitant fees.

* [Compass Mining Hardware]({% link _docs/script-compassmininghardware.md %})
* [Compass Mining Status]({% link _docs/script-compassminingstatus.md %})
* [Gas Price]({% link _docs/script-gasprice.md %})
* [Raretoshi]({% link _docs/script-raretoshi.md %})

