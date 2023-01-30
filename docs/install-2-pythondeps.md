# ![Nodeyez](../images/nodeyez.svg)
Display panels to get the most from your node

[Home](../README.md) | [Back to Raspberry Pi Node](./install-1-raspberrypinode.md) | [Continue to Display Screen](./install-3-displayscreen.md)

---

## Python and Dependencies

### 1.  Login to your node with a privileged user that can sudo.
    - MyNodeBTC: ssh as admin
    - Raspiblitz ssh as admin
    - Raspibolt: ssh as admin
    - Umbrel: ssh as umbrel
    - Default Raspbian: ssh as pi

### 2. Install Python3.  The Raspberry Pi comes with Python 2.7, but the 
   scripts require Python 3. 

   ```sh
   sudo apt-get install python3
   ```

### 3. Install the Python Pillow library. 

   ```sh
   sudo apt-get install libjpeg-dev zlib1g-dev
   pip list | grep --ignore-case pi
   ```

   Sample output

   ```c
   googleapis-common-protos 1.52.0
   Pillow                   8.3.1
   pip                      21.2.1
   pipenv                   2020.6.2
   RPi.GPIO                 0.7.0
   typing-extensions        3.7.4.2
   ```

   If neither PIL or Pillow is installed, then go ahead with the install as 
   follows:

   ```sh
   pip install Pillow
   ```

   You can upgrade Pillow to the latest using the following command:

   ```sh
   python3 -m pip install --upgrade Pillow
   ```

   Some scripts make use of rounded_rectangle, which requires Pillow 8.2 or 
   above.

### 4. Install git and torify as follows

   ```sh
   sudo apt install git
   sudo apt-get install apt-transport-tor
   ```

### 5. Install ImageMagic libraries as follows

   ```sh
   sudo apt-get install imagemagick
   ```

---

[Home](../README.md) | [Back to Raspberry Pi Node](./install-1-raspberrypinode.md) | [Continue to Display Screen](./install-3-displayscreen.md)

