# Nginx - For Website Dashboard

Whether you are using a Raspberry Pi with a screen attached to GPIO pins or not, you can also setup a web based dashboard following these steps. 
This guide assumes that you don't yet have NGINX installed, but guidance is provided in later sections for [modifying existing NGINX install](#modifying-existing-nginx-setup).

![sample image of dashboard](./images/websitedashboard.png)

## Install NGINX

  💡 _Hint: NGINX is pronounced "Engine X"_

  ```sh
  $ sudo apt install -y nginx
  ```

* Create a self-signed TLS certificate (valid for 10 years)

  ```sh
  $ sudo openssl req -x509 -nodes -newkey rsa:2048 -keyout /etc/ssl/private/nginx-selfsigned.key -out /etc/ssl/certs/nginx-selfsigned.crt -subj "/CN=localhost" -days 3650
  ```

* To completely disable the NGINX webserver and configure the TCP reverse proxy for displaying the images, remove the default configuration and use the premade nginx.conf file.

  ```sh
  $ sudo mv /etc/nginx/nginx.conf /etc/nginx/nginx.conf.bak
  $ sudo cp /home/bitcoin/nodeyez/scripts/nginx/nginx.conf /etc/nginx/nginx.conf
  $ sudo cp /home/bitcoin/nodeyez/scripts/nginx/imagegallery.xslt /etc/nginx/imagegallery.xslt
  $ sudo chown root:root /etc/nginx/nginx.conf
  $ sudo chown root:root /etc/nginx/imagegallery.xslt
  ```
  
## Modifying Existing NGINX setup

If you already have nginx installed, then you really just need to add a local server listening on a port, and an upstream node for optional SSL proxying.

The premade configuration used in the prior section uses ports 907 for http, and 908 for SSL.  Why port 907? No reason other then its placement in the [BIP39 wordlist](https://github.com/bitcoin/bips/blob/master/bip-0039/english.txt).

* Edit the NGINX configuration file

  ```sh
  $ sudo nano /etc/nginx/nginx.conf
  ```
  
* Add an upstream definition inside the stream block

  ```nginx
    upstream nodeimages {
      server 127.0.0.1:907;
    }
  ```

* Add a server definition to listen as ssl

  ```nginx
    server {
      listen 908 ssl;
      proxy_pass nodeimages;
    }
  ```
  
* At the bottom of the file, create an entirely new http block

  ```nginx
  http {
    include mime.types;
    server {
      listen 907;
      root /home/bitcoin/images;
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

## Restart NGINX

* Test the NGINX configuration and restart the service.

  ```sh
  $ sudo nginx -t
  $ sudo systemctl restart nginx
  ```

## Enable Access Through Firewall

If you've setup the uncomplicated firewall to deny incoming and outgoing traffic by default, then you'll need to add a rule to allow access to the ports the web server is listening on.

* To enable SSL access

   ```sh
   $ sudo ufw allow 908 comment 'allow access to node images over ssl'
   ```
 
Now see if you can access the dashboard at https://your-node-ip:908
