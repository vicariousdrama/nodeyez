# ![Nodeyez](https://raw.githubusercontent.com/vicariousdrama/nodeyez/main/images/nodeyez.svg)
Display panels to get the most from your node

## Art Hash Dungeon

This script produces a maze reminiscent of legacy videogame systems based on the
Bitcoin Blockhash.  The maze is rendered semi deterministically and features
custom tilesets for the maze floor and walls, and logos of popular entities in
the Bitcoin ecosystem.  The script is installed at 
[/home/nodeyez/nodeyez/scripts/arthashdungeon.py](../scripts/arthashdungeon.py). 
It depends on a bitcoin node running locally and fully synched.

![sample image depicting a sample generated maze](../images/arthashdungeon.png)

* To run this script

   ```sh
   cd /home/nodeyez/nodeyez/scripts
   ./arthashdungeon.py
   ```

   Press CTRL+C to stop the process

* To configure this script

   Override the default configuration as follows

   ```sh
   nano /home/nodeyez/nodeyez/config/arthash.json
   ```

   | field name | description |
   | --- | --- |
   | outputFile | The path to save the generated image. Default `/home/nodeyez/nodeyez/imageoutput/arthashdungeon.png` |
   | bitcoinLogosFile | The path to a file containing tiles of logos to overlay on the maze with dimensions 32x32 pixels, 16 icons wide. Default `/home/nodeyez/nodeyez/images/arthash-dungeon-bitcoin-logos.png` |
   | bitcoinTilesFile | The path to a file containing tiles with dimensions 32x32 arranged in sets of 8 tiles per theme, two themes wide, and 11 themes high. Default `/home/nodeyez/nodeyez/images/arthash-dungeon-bitcoin-tiles.png` |
   | colorTextFG | The color of the text expressed as a Hexadecimal color specifier. Default `#ffffff` |
   | colorBackground | The background color of the image expressed as a hexadecimal color specifier. Default `#000000` |
   | sleepInterval | The amount of time, in seconds, the script should wait before data gathering and image creation again. Default `300` |

   After making changes, Save (CTRL+O) and Exit (CTRL+X) nano.


---

[Home](../README.md) | 

