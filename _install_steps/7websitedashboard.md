---
name: Website Dashboard
title: NODEYEZ Website Dashboard
layout: default
---

# Website Dashboard

If you installed Nodeyez using the [Quick Start]({% link _install_steps/0quickstart.md %}), then this step is already done for you and you can skip ahead to using the 
[Nodeyez-Config]({% link _install_steps/9nodeyezconfig.md %}) tool.

Whether you are using a display screen or not, you can also make the images  viewable via website dashboard.  The dashboard included in nodeyez looks like this

![sample image of dashboard](../images/websitedashboard.png)

The dashboard view will automatically cycle through the same images at 10 second intervals, showing smaller versions at the top of the screen.  

Clicking on an image will automatically advance the view to the full size  version of that one.

There are multiple options for setting up the dashboard.  Choose the most appropriate based on your raspberry pi node

If you are currently logged in as user nodeyez, `exit` back to the privileged user.

## Installing NGINX

Check if NGINX is installed
```shell
which nginx
```

If there is no returned path for NGINX, install it
```shell
sudo apt install -y nginx nginx-common
```

## Create Self-signed Certificates

Create self-signed certificates that can be referenced in the web config.
```shell
sudo openssl req -x509 -nodes -newkey rsa:2048 -keyout /etc/ssl/private/nodeyez-nginx-selfsigned.key -out /etc/ssl/certs/nodeyez-nginx-selfsigned.crt -subj "/CN=localhost" -days 3650
```

Create Diffie-Hellman parameters if they don't already exist
```shell
if [ ! -f "/etc/ssl/certs/dhparam.pem" ]; then
  sudo openssl dhparam -dsaparam -out /etc/ssl/certs/dhparam.pem 4096
fi
```

## Capture SSL Certificate Info

Capture the existing SSL Certificate and Key.  This is primarily for previously existing NGINX instances.  In the case of installing on a MyNodeBTC instance, the intent is to be able to use the same SSL certificate that is used for other subsites in that instance

```shell
line_ssl_certificate=$(sudo nginx -T 2>&1 | grep "ssl_certificate " | sed -n 1p)
line_ssl_certificate_key=$(sudo nginx -T 2>&1 | grep "ssl_certificate_key " | sed -n 1p)
```

## Copy XSLT Templates

Drop in the Nodeyez XSLT Templates used for building directory listings
```shell
sudo cp /home/nodeyez/nodeyez/scripts/nginx/nodeyez*.xslt /etc/nginx/
```

If the above statement fails with a cannot stat error, use this

```shell
sudo cp /home/nodeyez/nodeyez/scripts/nginx/nodeyez_dirlistblack.xslt /etc/nginx/

sudo cp /home/nodeyez/nodeyez/scripts/nginx/nodeyez_imagegallery128.xslt /etc/nginx/

sudo cp /home/nodeyez/nodeyez/scripts/nginx/nodeyez_imagegallery.xslt /etc/nginx/
```

## Copy Nodeyez SSL Config

The prebuilt SSL configuration files include references to the cert and key, common parameters, and proxy definitions.

```shell
sudo mkdir -p /etc/nginx/nodeyez
sudo cp /home/nodeyez/nodeyez/scripts/nginx/nodeyez_ssl*.conf /etc/nginx/nodeyez
```

Check if there were certificates in existing config
```shell
echo $line_ssl_certificate
echo $line_ssl_certificate_key
```

If the above outputed values, then assign back into configuration as follows
```shell
sudo rm /etc/nginx/nodeyez/nodeyez_ssl_cert_key.conf
sudo echo $line_ssl_certificate >> /etc/nginx/nodeyez/nodeyez_ssl_cert_key.conf
sudo echo $line_ssl_certificate_key >> /etc/nginx/nodeyez/nodeyez_ssl_cert_key.conf
```

## Ensure XSLT enabled

Check for whether XSLT modules are included already
```shell
sudo cat /etc/nginx/modules-enabled/* | grep xslt
```

If there are no values returned, copy in the configuration to enable it
```shell
sudo cp /home/nodeyez/nodeyez/scripts/nginx/a_xslt.conf /etc/nginx/modules-enabled/a_xslt.conf
```

## Copy Nodeyez Site

Now we deploy the site definition for the dashboard itself

__MyNodeBTC Only__ : If you are deploying on a __MyNodeBTC__ instance, use the following
```shell
sudo cp /home/nodeyez/nodeyez/scripts/nginx/https_nodeyez_mynode.conf /etc/nginx/sites-enabled/https_nodeyez.conf
```

__Raspibolt Only__ : If you are deploying on a __Raspibolt__ instance, use the following
```shell
sudo cp /home/nodeyez/nodeyez/scripts/nginx/http_nodeyez_raspibolt.conf /etc/nginx/nodeyez/http_nodeyez_raspibolt.conf

sudo cp /home/nodeyez/nodeyez/scripts/nginx/https_nodeyez_raspibolt.conf /etc/nginx/streams-enabled/https_nodeyez_raspibolt.conf

if [ ! -f "/etc/nginx/modules-enabled/http_nodeyez_raspibolt.conf" ]; then
  sudo ln -s /etc/nginx/nodeyez/http_nodeyez_raspibolt.conf /etc/nginx/modules-enabled/http_nodeyez_raspibolt.conf
fi
```

For other instances, use the following
```shell
sudo cp /home/nodeyez/nodeyez/scripts/nginx/https_nodeyez.conf /etc/nginx/sites-enabled/https_nodeyez.conf
```

Once complete, set the ownership
```shell
sudo chown root:root -R /etc/nginx/
```

## Grant Group and Execute permission

This will assign group to nginx, and also give it execute permission to the
group so that members can traverse the folders of nodeyez

```shell
sudo gpasswd -a www-data nodeyez
sudo chmod g+x /home/nodeyez 
sudo chmod g+x /home/nodeyez/nodeyez 
sudo chmod g+x /home/nodeyez/nodeyez/imageoutput
```

## Configure Firewall rules

The Nodeyez website dashboard uses port 907.  Enable access to view it.
```shell
sudo ufw allow 907 comment 'allow Nodeyez Dashboard HTTPS'
sudo ufw enable
```

You can find the IP address to access via
```shell
hostname -I
```

## Restart NGINX

First, test the configuration
```shell
sudo nginx -t
```

If there are errors, review the configuration files and correct.

If you receive an error about module "ngx_http_xslt_filer_module" already being loaded, then you can remove the XSLT dropin:
```shell
sudo rm /etc/nginx/modules-enabled/a_xslt.conf
```

If there are no failures from testing configuration, then restart nginx
```shell
sudo systemctl restart nginx
```

## View Dashboard

Using a web browser, see if you can access the dashboard at

    https://your-node-ip:907

You can also get to lists of files in the data directory at 

    https://your-node-ip:907/data/

And view a specific subfolder of data as a photo album at 

    https://your-node-ip:907/album/

---

[Home](../) | [Back to Slideshow]({% link _install_steps/6slideshow.md %}) | [Continue to Running Services at Startup]({% link _install_steps/8runatstartup.md %})