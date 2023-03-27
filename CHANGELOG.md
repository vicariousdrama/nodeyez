---
title: NODEYEZ Change Log
---
# CHANGELOG

## Main Branch

**New Panels and Enhancements**

**General**

- Linking tagged commits back to Github as a public mirror
- Add guidance for Developers, including setting up Regtest
- Add missing dependencies Pysocks and JQ
- Set temp folder for image magick
- Establish EnvironmentFile for services
- Normalized NGINX Configurations
- Added Install and Uninstall scripts

**Bugfixes**

- Fix System Info drive icons if only one drive
- Fix Blockstats handling of 0 fee and negative block numbers
- Fix Ring of Fire error when LND attempt to connect to nodes

## 23.03

Released: 2023-03-13

Tagged Commit: [e8c0f38c6c1035bcaae88d9d629e75fe17483223](https://github.com/vicariousdrama/nodeyez/commit/e8c0f38c6c1035bcaae88d9d629e75fe17483223)

**New Panels and Enhancements**

- New panel: Miner Status for MicroBT Whatsminer
- New panel: Channel Fees (requires updated macaroon)
- New Panel: Halving Countdown - Progress to Next Subsidy Halving
- New Panel: Whirlpool Liquidity - Show Premixer and Remixer state for the pools
- New Panel: Whirlpool CLI+Mix Status - Shows your whirlpool CLI status and pools you are mixing in
- New Panel: Fear and Greed Index - Shows data from alternative.me
- New Panel: LND Hub Account Balances - Relies on local redis backing store to show account info
- New Panel: OP_RETURN - Renders text from OP_RETURN values
- New Panel: Price of Bitcoin - Shows the price of 1 BTC in fiat terms based on the US dollar valuation
- New Panel: Dual Image Display - Creates a composite of multiple images suitable for screens in portrait orientation. Based around 800x480 5" LCD screens.
- New Panel: Ordinals - Displays images that have been embedded as inscriptions with optional blocklist
- New Panel: Inscription Mempool - Display recent inscriptions in the mempool that are not yet mined into a block
- New Panel: Block Stats - Renders an image of stats for the current block height including inputs, outputs, transaction count, percentage of segwit, the size of the block and utxo set change, fee rates and fees for transactions. Optionally renders time series data for fee rates and segwit
- Enhanced Channel Balances - Cleaner lines, new default colors, option to display amounts and support remote LND hosts
- Enhanced Mempool - show sumary of tx in mempool, block count and time, fix for timeout, add renderStyle
- Enhanced Sats Per USD - dynamically scale size of sat grid based on current total
- Enhanced System Info - Cleaner lines, better thermometer bulb alignment, improved scaling for temperature, pie storage and cpu load icons

**General**

- Updated macaroon creation to allow querying ForwardingHistory
- Dimensions for any panel can be set via "width" and "height" in config file
- Updated Compass Facilities list
- Improved resource management for images, closing to free memory
- Encapsulated network calls, default to using tor for most scripts
- Changed documentation to call scripts from full path to workaround common mount issues
- Migrated repository to local gitea service. Github is now only a mirror.
- Deprecated support for Compass Mining Hardware, Gas Prices, Raretoshi
- Improved Mock data for testing renderings
- Added watermarks to renders
- Updated the markdown and jekyll themes for website, now available at https://nodeyez.com
- Slushpool renamed to Braiins pool

**Bugfixes**

- Fixed Blockhash Dungeon seeder and perpetual growth bug
- Fixed floortiles bug in Blockhash Dungeon
- Daily Data Retrieval has url corrections for Braiins pool

## 1.0.0

Released 2022-05-07

Tagged Commit: [290fb01c39cef84ab77155eea437439825a304ca](https://github.com/vicariousdrama/nodeyez/commit/290fb01c39cef84ab77155eea437439825a304ca)

**New Panels and Enhancements**

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

**General**

- Externalized configuration from scripts to json files
- New script to retrieve/parse compass mining historical status
- Added rudimentary mock-data support for Bitcoin and LND calls
- Added support for colorBackground in panels via config
- Improve guidance for different node types (Raspibolt, Raspiblitz, MyNodeBTC, Umbrel)
- Setup now using dedicated nodeyez user with preference to external hard drive for home folder
- Lots of new documentation
- Systemd service scripts now all use /usr/bin/env to force execution path as mounted drive may disallow

**Bugfixes**

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

Released: 2022-02-06

Tagged Commit: [e7571c06acd68f0ee58e228d294137b09a103d2a](https://github.com/vicariousdrama/nodeyez/commit/e7571c06acd68f0ee58e228d294137b09a103d2a)

**Features**

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

Released: 2021-07-29

Tagged Commit: [81073d0d8720f6ae77bd209d20fa3d7db59e33a4](https://github.com/vicariousdrama/nodeyez/commit/81073d0d8720f6ae77bd209d20fa3d7db59e33a4)

**Features**

- New panel: Block Height
- New panel: Difficulty Epoch
- New panel: Mempool Blocks
- New panel: Ring of Fire
- New panel: SATS per Fiat
- New panel: System Info
- New panel: UTC Clock
- Slideshow
