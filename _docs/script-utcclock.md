# ![Nodeyez](../images/nodeyez.svg)
Display panels to get the most from your node

## UTC Clock

This script provides a simple rendering of the date and time

![sample image depicting the date and time](../images/utcclock.png)

* To run this script

   ```sh
   cd /home/nodeyez/nodeyez/scripts
   ./utcclock.py
   ```

   Press CTRL+C to stop the process

* To configure this script

   Override the default configuration as follows

   ```sh
   nano /home/nodeyez/nodeyez/config/utcclock.json
   ```

   | field name | description |
   | --- | --- |
   | outputFile | The path to save the generated image. Default `/home/nodeyez/nodeyez/imageoutput/utcclock.png` |
   | colorBackground | The background color of the image expressed as a hexadecimal color specifier. Default `#602060` |
   | width | The width, in pixels, to generate the image. Default `480` |
   | height | The height, in pixels, to generate the image. Default `320` |
   | sleepInterval | The amount of time, in seconds, the script should wait before data gathering and image creation again. Default `30` |
   | colorTextDayOfWeek | The color to render the day of the week expressed as a Hexadecimal color specifier. Default `#e69138` |
   | colorTextDate | The color to render the current date expressed as a Hexadecimal color specifier. Default `#f1c232` |
   | colorTextTime | The color to render the current time expressed as a Hexadecimal color specifier. Default `#6aa84f` |

   After making changes, Save (CTRL+O) and Exit (CTRL+X) nano.


---

[Home](../README.md) | 

