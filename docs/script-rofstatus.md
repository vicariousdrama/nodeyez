# ![Nodeyez](../../../../raw/branch/main/images/nodeyez.svg)
Display panels to get the most from your node

## Ring of Fire Status

The Ring of Fire script provides renderings of configured Lightning Ring of Fire
groups.  If you have a lightning node and participate in a Ring of Fire, you can
configure the pubkeys for each node in the preordained sequence and the script 
will provide a useful image showing its present state.  

Offline nodes may be colored differently and have rings around them to draw 
attention.  Node operator contact list appears to the right of the ring.  You 
can define as many ring of fire configurations as you want, and each can have 
unique colors, labels, and fonts. To avoid spamming the lightning network with
connection attempts, there is a delay between each ring being processed.

The script is installed at [/home/nodeyez/nodeyez/scripts/rofstatus.py](../scripts/rofstatus.py)

![sample ring of fire rendering showing 5 nodes](../images/rof-sample.png)


* To run this script

   ```sh
   cd /home/nodeyez/nodeyez/scripts
   /home/nodeyez/nodeyez/scripts/rofstatus.py
   ```

   Press CTRL+C to stop the process

* To configure this script

   Override the default configuration as follows

   ```sh
   nano /home/nodeyez/nodeyez/config/rofstatus.json
   ```

   | field name    | description                             |
   | ------------- |---------------------------------------- |
   | width | The width, in pixels, to generate the image. Default `480` |
   | height | The height, in pixels, to generate the image. Default `320` |
   | sleepInterval | The amount of time, in seconds, the script should wait before data gathering and image creation again. Default `900` |
   | imagesettings | The default settings to apply to images generated unless overridden within a ring. The structure is defined below. |
   | rings | An array collection of defined rings to monitor and produce images for. The structure is defined below. |


   __imagesettings__

   | field name | description |
   | --- | --- |
   | colors | A structure of the color settings to apply to image generated. The structure is defined below |


   __colors__

   | field name | description |
   | --- | --- |
   | circle | The default color of the outer circle of the ring expressed as a Hexadecimal color specifier. Default `#404040` |
   | offline | The default color of a node when its offline expressed as a Hexadecimal color specifier. Default `#ff4040` |
   | online | The default color of a node when its online expressed as a Hexadecimal color specifier. Default `#40ff40` |
   | offlinetext | The default color of the text for an offline node expressed as a Hexadecimal color specifier. Default `#ffffff` |
   | onlinetext | The default color of the text for an online node expressed as a Hexadecimal color specifier. Default `#000000` |
   | text | The default color of the text for the ring name expressed as a Hexadecimal color specifier. Default `#ffffff` |
   | textshadow | The default color of the text shadow for the ring name expressed as a Hexadecimal color specifier. Default `#000000` |
   | background | The background color of the image expressed as a Hexadecimal color specifier. Default `#000000` |


   __rings__

   | field name | description |
   | --- | --- |
   | name | The name of the ring. Not used in image renderings. Default `Sample Ring` |
   | shortlabel | A short label for the ring to be displayed on the generated image. Default `Sample` |
   | imagefilename | The path to save the generated image fo this ring.  Each defined ring should have a unique value. Default `/home/nodeyez/nodeyez/imageoutput/rof-sample.png` |
   | telegramgroup | An arbitrary field value for information about the ring.  Not used in image renderings. Default is unset |
   | telegramadmin | An arbitrary field value specifying the coordinator of the ring. Not used in image renderings. Default is unset |
   | imagesettings | The settings to apply to the image generated from this ring. The structure is defined above |
   | nodes | An array of node objects where each represents a lightning node participant in this ring, in order. The structure is defined below |


   __node__

   | field name | description |
   | --- | --- |
   | pubkey | The public key to the node |
   | operator | A short label to identify the node |


   After making changes, Save (CTRL+O) and Exit (CTRL+X) nano.


---

[Home](../README.md) | 

