---
name: Running the Slideshow
title: Running the Slideshow
layout: default
---

# Running the Slideshow

If you have a screen attached to your raspberry pi, you can display the
generated images to the screen using the slideshow script 

## Script Location

The script is installed at
[/home/nodeyez/nodeyez/scripts/slideshow.sh](../scripts/slideshow.sh)

## Run Diretly

If you are currently logged in as nodeyez, `exit` back to the priviledged user

```shell
if [ "`whoami`" == "nodeyez" ]; then
exit
fi
```

Then run the following

```shell
cd /home/nodeyez/nodeyez/scripts
sudo ./slideshow.sh &
```

A process ID (PID) number will be displayed as output to the console for the
background process. You may also find this process ID with this command:

```shell
ps aux | grep slideshow | grep -v grep | awk '{print $2}'
```

You should start seeing images display on your screen.  


If you dont see any images, then edit the slideshow script file

```shell
nano /home/nodeyez/nodeyez/scripts/slideshow.sh
```

Locate the line that initiates the fbi commmand (around line 12) which looks like this

```
fbi --vt 1 --autozoom --timeout ${timeperimage} --device /dev/fb0 --noreadahead --cachemem 0 --noverbose --norandom ${globtodisplay} > /dev/null 2>&1
```

Comment the part at the end that redirects to stdout and stderr to /dev/null.

You can do this by placing a `#` right before this at the end of the line `> /dev/null 2>&1`.

Save (Press CTRL+O) and exit (Press CTRL+X)

Terminate any existing background process before restarting the slideshow script

```shell
for p in `ps aux | grep slideshow | grep -v grep | awk '{print $2}'`; do sudo kill $p; done
sudo /home/nodeyez/nodeyez/scripts/slideshow.sh &
```

Now any errors will be reported to the console.

You may need to change the parameters of the fbi command to

- Use a different virtual terminal (Try 0 or 1 as the value for `--vt`)
- Use a different device for output (Try /dev/fb0 or /dev/fb1 as the value for `--device`)


## Run at Startup

To enable the script to run at startup, as the privileged user run the following

```shell
sudo systemctl enable nodeyez-slideshow.service
sudo systemctl start nodeyez-slideshow.service
```

[Home](../) | [Back to Panel Index]({% link _install_steps/5panels.md %}) | [Continue to Website Dashboard]({% link _install_steps/7websitedashboard.md %})

