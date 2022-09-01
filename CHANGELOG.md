# ![Nodeyez](https://raw.githubusercontent.com/vicariousdrama/nodeyez/main/images/nodeyez.svg)
Display panels to get the most from your node

# CHANGELOG

## Unreleased main branch

New Panels and Enhancements
- New panel: Miner Status for MicroBT Whatsminer
- New panel: Channel Fees (requires updated macaroon)
- New Panel: Halving Countdown - Progress to Next Subsidy Halving
- New Panel: Whirlpool Liquidity - Show Premixer and Remixer state for the pools
- Enhanced Mempool - show sumary of tx in mempool, block count and time

General
- Updated macaroon creation to allow querying ForwardingHistory
- Dimensions for any panel can be set via "width" and "height" in config file
- Updated Compass Facilities list
- Improved resource management for images, closing to free memory
- Encapsulated network calls, default to using torify for most scripts
- Changed documentation to call scripts from full path to workaround common mount issues

## 1.0.0

- Released 2022-05-07
- Tagged Commit: [290fb01c39cef84ab77155eea437439825a304ca](https://github.com/vicariousdrama/nodeyez/commit/290fb01c39cef84ab77155eea437439825a304ca)

New Panels and Enhancements
- New panel: Raretoshi
- New panel: Compass Mining Hardware
- New panel: Gas Price
- Renamed panel: Miner - Braiins (replaces Miner Status panel)
- Enhanced Compass Mining Status - now supports minor status level
- Enhanced Miner Brains - support multiple miners, new look and feel
- Enhanced Raretoshi - Set download timeout to 5 seconds
- Enhanced Daily Data Retrieval - support for slushpool data 
- Enhanced Raretoshi panel to allow for traversing user randomly
- Enhanced Raretoshi panel to support QR code hyperlink
- Enhanced Mempool panel to show fee histogram as a bar and improve config

General
- Externalized configuration from scripts to json files
- New script to retrieve/parse compass mining historical status
- Added rudimentary mock-data support for Bitcoin and LND calls
- Added support for colorBackground in panels via config
- Improve guidance for different node types (Raspibolt, Raspiblitz, MyNodeBTC, Umbrel)
- Setup now using dedicated nodeyez user with preference to external hard drive for home folder
- Lots of new documentation
- Systemd service scripts now all use /usr/bin/env to force execution path as mounted drive may disallow

Bugfixes
- Fixed some loop timeouts
- Fixed f2pool crashing if account info could not be retrieved
- Fixed daily data retrieval eixsts checks
- Fixed extension and urls for IPFS resources only available on raretoshi
- Fixed bottomrighttext handler to allow specifying color
- Fixed Miner Status panel support for password
- Fixed ring of fire panel handling of background color
- Fixed difficulty epoch failing if blocknum was last in a difficulty epoch
- Fixed bitcoin dependent services to get updated bitcoin cookie before start

## 1.0.0-beta

- Released: 2022-02-06
- Tagged Commit: [e7571c06acd68f0ee58e228d294137b09a103d2a](https://github.com/vicariousdrama/nodeyez/commit/e7571c06acd68f0ee58e228d294137b09a103d2a)

### Features
- Added Github-pages at https://vicariousdrama.github.io/nodeyez/
- Add/update sample images
- Added guidance for screen to put on Raspberry Pi
- General organization/refactoring to improve maintainability
- Added service scripts
- Added web dashboard capability with NGINX
- Some torification
- Existing panels all get font normalization and assorted cleanup
- New panel: IP Address to show all exposed IPs
- New panel: Channel Balance for lightning nodes
- New panel: Miner Status for S9 home miners
- New panel: Slushpool Mining Summary - 30 day
- New panel: F2Pool 24 Hour Hashrate summary
- New panel: Compass Mining Status for facilities
- New panel: Luxor Mining Hashrate by calendar month
- New panel: Art Hash geometric art based on blockhash
- New panel: Blockhash Dungeon deterministic from blockhash
- New panel: Logo with scaling and optional V/H fill

## 1.0.0-alpha

- Released: 2021-07-29
- Tagged Commit: [81073d0d8720f6ae77bd209d20fa3d7db59e33a4](https://github.com/vicariousdrama/nodeyez/commit/81073d0d8720f6ae77bd209d20fa3d7db59e33a4)

### Features
- New panel: Block Height
- New panel: Difficulty Epoch
- New panel: Mempool Blocks
- New panel: Ring of Fire
- New panel: SATS per Fiat
- New panel: System Info
- New panel: UTC Clock
- Slideshow
