---
name: Website Dashbaord
title: NODEYEZ Website Dashboard
---

# Website Dashboard

Whether you are using a display screen or not, you can also make the images 
viewable via website dashboard.  The dashboard included in nodeyez looks like
this

![sample image of dashboard](../images/websitedashboard.png)

The dashboard view will automatically cycle through the same images at 10 second
intervals, showing smaller versions at the top of the screen.  

Clicking on an image will automatically advance the view to the full size 
version of that one.

There are multiple options for setting up the dashboard.  Choose the most
appropriate based on your raspberry pi node

Before beginning, make sure you are logged in as the privileged user.  If you
continued here from the previous section logged in as `nodeyez`, then issue
the following to return back to the privileged user

```shell
exit
```

## Choose ONE (1) of the following

- [Install for MyNodeBTC](#install-for-mynodebtc)
- [New Install of NGINX](#new-install-of-nginx)
- [Modifying Existing NGINX Setup](#modifying-existing-nginx-setup)

## Install for MyNodeBTC

<mash-accordion markdown="1" key="nbcweb1" resource="549a2981-ae65-41e3-b620-6b22bec143cd" button-horizontal-align="center" button-vertical-align="bottom" button-text="Read More" button-variant="solid" button-size="md" loading-indicator-size="14">

<div markdown="1">

If you are using [MyNodeBTC](https://mynodebtc.com/), then you can follow 
this section.  MyNodeBTC already comes with NGINX and will update over top of 
configuration files. Thankfully, it also makes use of the sites-enabled and 
[reverse-proxy](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/) 
features to make this a little easier.

* Copy necessary files for NGINX

We want to enable the XSLT module, create a definition for the Nodeyez 
dashboard on port 907, and our template that generates the dashboard view.

```shell
sudo cp /home/nodeyez/nodeyez/scripts/nginx/a_xslt.conf /etc/nginx/modules-enabled/a_xslt.conf
sudo cp /home/nodeyez/nodeyez/scripts/nginx/https_nodeyez.conf /etc/nginx/sites-enabled/https_nodeyez.conf
sudo cp /home/nodeyez/nodeyez/scripts/nginx/*.xslt /etc/nginx/
sudo chown root:root /etc/nginx/modules-enabled/a_xslt.conf
sudo chown root:root /etc/nginx/sites-enabled/https_nodeyez.conf
sudo chown root:root /etc/nginx/*.xslt
```

* Test the NGINX configuration and restart the service.

There should be no errors when running the test with the first command.

```shell
sudo nginx -t
sudo systemctl restart nginx
```
  
* Enable Access Through Firewall

```shell
sudo ufw allow 907 comment 'allow access to nodeyez images over ssl'
```
 
Now see if you can access the dashboard at https://your-node-ip:907

[Continue to Running Services at Startup](./install-6-runatstartup.md)

</div>

</mash-accordion>




## New Install of NGINX

<mash-accordion markdown="1" key="nbcweb2" resource="549a2981-ae65-41e3-b620-6b22bec143cd" button-horizontal-align="center" button-vertical-align="bottom" button-text="Read More" button-variant="solid" button-size="md" loading-indicator-size="14">

<div markdown="1">

If you dont yet have nginx setup, the steps here will guide you for the installation
and basic configuration of the web server.

```shell
sudo apt install -y nginx
```

* Create a self-signed TLS certificate (valid for 10 years)

```shell
sudo openssl req -x509 -nodes -newkey rsa:2048 -keyout /etc/ssl/private/nginx-selfsigned.key -out /etc/ssl/certs/nginx-selfsigned.crt -subj "/CN=localhost" -days 3650
```

* To completely disable the NGINX webserver and configure the TCP reverse proxy
  for displaying the images, remove the default configuration and use the 
  premade nginx.conf file.

```shell
sudo mv /etc/nginx/nginx.conf /etc/nginx/nginx.conf.bak
sudo cp /home/nodeyez/nodeyez/scripts/nginx/nginx.conf /etc/nginx/nginx.conf
sudo cp /home/nodeyez/nodeyez/scripts/nginx/imagegallery.xslt /etc/nginx/imagegallery.xslt
sudo chown root:root /etc/nginx/nginx.conf
sudo chown root:root /etc/nginx/imagegallery.xslt
```

* Test the NGINX configuration and restart the service.

```shell
sudo nginx -t
sudo systemctl restart nginx
```

* Enable Access Through Firewall

```shell
sudo ufw allow 907 comment 'allow access to nodeyez images over ssl'
```
 
Now see if you can access the dashboard at https://your-node-ip:907

You can also get to lists of files in the data directory at https://your-node-ip:907/data/

And view a specific subfolder of data as a photo album at https://your-node-ip:907/album/

[Continue to Running Services at Startup](./install-6-runatstartup.md)

</div>

</mash-accordion>




## Modifying Existing NGINX setup

<mash-accordion markdown="1" key="nbcweb3" resource="549a2981-ae65-41e3-b620-6b22bec143cd" button-horizontal-align="center" button-vertical-align="bottom" button-text="Read More" button-variant="solid" button-size="md" loading-indicator-size="14">

<div markdown="1">

If you already have nginx installed, then you really just need to add a local 
server listening on a port, and an upstream node for optional SSL proxying.  

* Copy in the stylesheet and set ownership

```shell
sudo cp /home/nodeyez/nodeyez/scripts/nginx/imagegallery.xslt /etc/nginx/imagegallery.xslt
sudo chown root:root /etc/nginx/imagegallery.xslt
```

* Edit the NGINX configuration file

```shell
sudo nano /etc/nginx/nginx.conf
```
  
* Add an upstream definition inside the stream block

```nginx
upstream nodeyez {
   server 127.0.0.1:906;
}
```

* Add a server definition to listen as ssl

```nginx
server {
   listen 907 ssl;
   proxy_pass nodeyez;
}
```
  
* At the bottom of the file, create an entirely new http block

```nginx
http {
  include mime.types;
  server {
    listen 906;
    root /home/nodeyez/nodeyez/imageoutput;
    default_type text/html;
    location / {
      autoindex on;
      autoindex_format xml;
      xslt_string_param title $1;
      xslt_stylesheet /etc/nginx/imagegallery.xslt;
      try_files $uri $uri/ =404;
    }
  }
}
```
  
* Save (CTRL+O) and exit (CTRL+X) the file

* Test the NGINX configuration and restart the service.

```shell
sudo nginx -t
sudo systemctl restart nginx
```

* Enable Access Through Firewall

```shell
sudo ufw allow 907 comment 'allow access to nodeyez images over ssl'
```
 
Now see if you can access the dashboard at https://your-node-ip:907

[Continue to Running Services at Startup](./install-6-runatstartup.md)

</div>

</mash-accordion>



---

[Home](../README.md) | [Back to Nodeyez User](./install-4-nodeyez.md) | [Continue to Running Services at Startup](./install-6-runatstartup.md)

