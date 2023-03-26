#!/usr/bin/env bash

# Nodeyez installation script (these are not user settable flags, do not change)
CREATED_USER=0
GRANTED_BITCOIN=0
GRANTED_LND=0
CLONED_REPO=0
CREATED_PYENV=0
CREATED_WEBSITE=0
WEBURL=""
ISMYNODE=0
GITPULLRESULT=""

# Tools
sudo apt-get -y install \
    apt-transport-tor \
    fbi \
    git \
    imagemagick \
    inkscape \
    jq \
    libjpeg-dev \
    python3 \
    python3-venv \
    zlib1g-dev

# Create Nodeyez user
if id nodeyez &>/dev/null; then
  echo "Nodeyez user already exists"
else
  echo "Creating Nodeyez user"
  DRIVECOUNT=$(df -t ext4 | grep / | awk '{print $6}' | sort | wc -l)
  ISMMC=$(findmnt -n -o SOURCE --target /home | grep "mmcblk" | wc -l)
  if [ $DRIVECOUNT -gt 1 ] && [ $ISMMC -gt 0 ]; then
    EXT_DRIVE_MOUNT=$(df -t ext4 | grep / | awk '{print $6}' | sort | sed -n 2p)
  fi
  if [ -z ${EXT_DRIVE_MOUNT+x} ]; then
    NODEYEZ_HOME=/home/nodeyez
    sudo adduser --gecos "" --disabled-password nodeyez
  else
    NODEYEZ_HOME=${EXT_DRIVE_MOUNT}/nodeyez
    sudo adduser --home ${NODEYEZ_HOME} --gecos "" --disabled-password nodeyez
    sudo ln -s ${NODEYEZ_HOME} /home/nodeyez
    sudo chown -R nodeyez:nodeyez /home/nodeyez
  fi
  CREATED_USER=1
fi

# Add user to tor group
sudo adduser nodeyez debian-tor

# Bitcoin user must exist for bitcoin and lnd setup
if id bitcoin &>/dev/null; then
  # Give bitcoin cookie and config
  echo "Granting bitcoin cookie and config"
  sudo mkdir -p /home/nodeyez/.bitcoin
  if [ -f "/home/bitcoin/.bitcoin/bitcoin.conf" ]; then
    sudo cp /home/bitcoin/.bitcoin/bitcoin.conf /home/nodeyez/.bitcoin/bitcoin.conf
  else
    echo "- error: unable to grant bitcoin config. File /home/bitcoin/.bitcoin/bitcoin.conf not found"
  fi
  if [ -f "/home/bitcoin/.bitcoin/.cookie" ]; then
    sudo cp /home/bitcoin/.bitcoin/.cookie /home/nodeyez/.bitcoin/.cookie
  else
    echo "- error: unable to grant bitcoin cookie. File /home/bitcoin/.bitcoin/.cookie not found"
  fi
  sudo chown -R nodeyez:nodeyez /home/nodeyez/.bitcoin
  GRANTED_BITCOIN=1

  # Give LND cert and macaroon if LND exists
  if [ $(which lncli | wc -l) -gt 0 ]; then
    echo "Granting LND cert and baking custom macaroon"
    sudo mkdir -p /home/nodeyez/.lnd
    LNDCERTFILE="/home/bitcoin/.lnd/tls.cert"
    if [ -f "$LNDCERTFILE" ]; then
      sudo cp /home/bitcoin/.lnd/tls.cert /home/nodeyez/.lnd/tls.cert
    fi
    lncli bakemacaroon uri:/lnrpc.Lightning/GetInfo uri:/lnrpc.Lightning/GetNodeInfo uri:/lnrpc.Lightning/ListPeers uri:/lnrpc.Lightning/ListChannels uri:/lnrpc.Lightning/ChannelBalance uri:/lnrpc.Lightning/ConnectPeer uri:/lnrpc.Lightning/DisconnectPeer uri:/lnrpc.Lightning/ForwardingHistory uri:/lnrpc.Lightning/ListPayments uri:/lnrpc.Lightning/DecodePayReq uri:/lnrpc.Lightning/FeeReport --save_to /tmp/nodeyez.macaroon
    if [ -f "/home/nodeyez/.lnd/nodeyez.macaroon" ]; then
      sudo rm /home/nodeyez/.lnd/nodeyez.macaroon
    fi
    sudo mv /tmp/nodeyez.macaroon /home/nodeyez/.lnd/nodeyez.macaroon
    sudo rm /tmp/nodeyez.macaroon
    sudo chown -R nodeyez:nodeyez /home/nodeyez/.lnd
    GRANTED_LND=1
  else
    echo "LND not installed"
  fi
else
  echo "Bitcoin user not present"
fi

# Clone repository into nodeyez user space
if [ ! -d "/home/nodeyez/nodeyez" ]; then
  echo "Cloning Nodeyez"
  sudo -u nodeyez git clone https://github.com/vicariousdrama/nodeyez.git /home/nodeyez/nodeyez
  sudo -u nodeyez mkdir -p /home/nodeyez/nodeyez/{config,data,imageoutput,temp}
  sudo -u nodeyez mkdir -p /home/nodeyez/nodeyez/imageoutput/ordinals
  sudo -u nodeyez cp /home/nodeyez/nodeyez/sample-config/*.json /home/nodeyez/nodeyez/config
  sudo chown -R nodeyez:nodeyez /home/nodeyez/nodeyez
  CLONED_REPO=1
else
  echo "Folder for nodeyez repository already exists at /home/nodeyez/nodeyez"
  GITPULLRESULT=$(sudo -u nodeyez bash -c "cd /home/nodeyez/nodeyez && git pull")
fi

# Create python virtual environment in nodeyez user space
if [ ! -d "/home/nodeyez/.pyenv/nodeyez" ]; then
  echo "Creating python virtual environment"
  sudo -u nodeyez python3 -m venv /home/nodeyez/.pyenv/nodeyez
  CREATED_PYENV=1
else
  echo "Python virtual environment already exists"
fi
# ensure python modules we depend on are present in the virtual environment
sudo -u nodeyez -s source /home/nodeyez/.pyenv/nodeyez/bin/activate && /home/nodeyez/.pyenv/nodeyez/bin/python3 -m pip install --upgrade \
    beautifulsoup4 exifread pandas pysocks qrcode redis requests urllib3 Pillow Wand

# Website dashboard
if [ $(which nginx | wc -l) -gt 0 ]; then
  # nginx is already installed
  if [ -d "/mnt/hdd/mynode" ]; then
    # we are installing on a mynode environment
    echo "Configuring Nodeyez Dashboard in NGINX"
    # enable xslt module
    sudo cp /home/nodeyez/nodeyez/scripts/nginx/a_xslt.conf /etc/nginx/modules-enabled/a_xslt.conf
    sudo chown root:root /etc/nginx/modules-enabled/a_xslt.conf
    # copy xslt templates
    sudo cp /home/nodeyez/nodeyez/scripts/nginx/nodeyez*.xslt /etc/nginx/
    sudo chown root:root /etc/nginx/nodeyez*.xslt
    # site config
    sudo cp /home/nodeyez/nodeyez/scripts/nginx/https_nodeyez_mynode.conf /etc/nginx/sites-enabled/https_nodeyez.conf
    sudo chown root:root /etc/nginx/sites-enabled/https_nodeyez.conf
    ISMYNODE=1
    CREATED_WEBSITE=1
  else
    # Generic NGINX
    # get some ssl cert info
    line_ssl_certificate=$(sudo nginx -T 2>&1 | grep "ssl_certificate " | sed -n 1p)
    line_ssl_certificate_private=$(sudo nginx -T 2>&1 | grep "ssl_certificate_private " | sed -n 1p)
    # drop in our base config
    # determine if xslt module is loaded
    if [ $(nginx -V 2>&1 | tr ' ' '\n' | egrep -i 'xslt' | wc -l) -gt 0 ]; then
      echo "XSLT module is loaded for NGINX"
    else
      echo "Configuring NGINX to load XSLT module"
      sudo cp /home/nodeyez/nodeyez/scripts/nginx/a_xslt.conf /etc/nginx/modules-enabled/a_xslt.conf
      sudo chown root:root /etc/nginx/modules-enabled/a_xslt.conf
    fi
    # copy xslt templates
    sudo cp /home/nodeyez/nodeyez/scripts/nginx/nodeyez*.xslt /etc/nginx/
    sudo chown root:root /etc/nginx/nodeyez*.xslt
    # site config
    sudo cp /home/nodeyez/nodeyez/scripts/nginx/https_nodeyez.conf /etc/nginx/sites-enabled/https_nodeyez.conf
    sudo chown root:root /etc/nginx/sites-enabled/https_nodeyez.conf
    # ssl config
    sudo mkdir -p /etc/nginx/nodeyez
    sudo cp /home/nodeyez/scripts/nginx/nodeyez_ssl*.conf /etc/nginx/nodeyez
    # assign back first cert and key if detected from earlier
    if [ ${#line_ssl_certificate} -gt 0 ]; then
      sudo rm /etc/nginx/nodeyez/nodeyez_ssl_cert_key.conf
      sudo echo $line_ssl_certificate >> /etc/nginx/nodeyez/nodeyez_ssl_cert_key.conf
      sudo echo $line_ssl_certificate_private >> /etc/nginx/nodeyez/nodeyez_ssl_cert_key.conf
    else
      sudo openssl req -x509 -nodes -newkey rsa:2048 -keyout /etc/ssl/private/nodeyez-nginx-selfsigned.key -out /etc/ssl/certs/nodeyez-nginx-selfsigned.crt -subj "/CN=localhost" -days 3650
    fi
    sudo chown root:root -R /etc/nginx/nodeyez
    CREATED_WEBSITE=1 
  fi
else
  # nginx is not yet installed
  sudo apt install -y nginx
  # make a self signed cert
  sudo openssl req -x509 -nodes -newkey rsa:2048 -keyout /etc/ssl/private/nodeyez-nginx-selfsigned.key -out /etc/ssl/certs/nodeyez-nginx-selfsigned.crt -subj "/CN=localhost" -days 3650
  # enable xslt module
  sudo cp /home/nodeyez/nodeyez/scripts/nginx/a_xslt.conf /etc/nginx/modules-enabled/a_xslt.conf
  sudo chown root:root /etc/nginx/modules-enabled/a_xslt.conf
  # templates
  sudo cp /home/nodeyez/nodeyez/scripts/nginx/nodeyez*.xslt /etc/nginx/
  sudo chown root:root /etc/nginx/nodeyez*.xslt
  # nodeyez config referencing our freshly minted self signed certs
  sudo mkdir -p /etc/nginx/nodeyez
  sudo cp /home/nodeyez/scripts/nginx/nodeyez_ssl*.conf /etc/nginx/nodeyez
  # site config
  sudo cp /home/nodeyez/nodeyez/scripts/nginx/https_nodeyez.conf /etc/nginx/sites-enabled/https_nodeyez.conf
  sudo chown root:root /etc/nginx/sites-enabled/https_nodeyez.conf
  CREATED_WEBSITE=1
fi
if [ $CREATED_WEBSITE -eq 1 ]; then
  # enable port 907 to the dashboard
  sudo ufw allow 907 comment 'allow Nodeyez Dashboard HTTPS'
  sudo ufw enable
  # restart nginx
  sudo systemctl restart nginx
  # get weburl
  WEBURL=$(hostname -I | awk {'print "https://" $1 ":907"}')
fi

# Services
sudo cp /home/nodeyez/nodeyez/scripts/systemd/*.service /etc/systemd/system/
sudo cp /home/nodeyez/nodeyez/scripts/systemd/nodeyez.conf /etc/nodeyez.conf

# Initial services to enable and start
# - fearandgreed, fiatprice, ipaddress, satsperusd, sysinfo, utcclock
sudo systemctl enable nodeyez-fearandgreed.service
sudo systemctl start nodeyez-fearandgreed.service
sudo systemctl enable nodeyez-fiatprice.service
sudo systemctl start nodeyez-fiatprice.service
sudo systemctl enable nodeyez-ipaddress.service
sudo systemctl start nodeyez-ipaddress.service
sudo systemctl enable nodeyez-satsperusd.service
sudo systemctl start nodeyez-satsperusd.service
sudo systemctl enable nodeyez-sysinfo.service
sudo systemctl start nodeyez-sysinfo.service
sudo systemctl enable nodeyez-utcclock.service
sudo systemctl start nodeyez-utcclock.service
sudo systemctl enable nodeyez-daily-data-retrieval.service
sudo systemctl start nodeyez-daily-data-retrieval.service
# - bitcoin: arthash, arthashdungeon, blockheight, blockstats, difficultyepoch, halving, mempoolblocks
if [ $GRANTED_BITCOIN -ge 1 ]; then
  sudo systemctl enable nodeyez-arthash.service
  sudo systemctl start nodeyez-arthash.service
  sudo systemctl enable nodeyez-arthashdungeon.service
  sudo systemctl start nodeyez-arthashdungeon.service
  sudo systemctl enable nodeyez-blockheight.service
  sudo systemctl start nodeyez-blockheight.service
  sudo systemctl enable nodeyez-blockstats.service
  sudo systemctl start nodeyez-blockstats.service
  sudo systemctl enable nodeyez-difficultyepoch.service
  sudo systemctl start nodeyez-difficultyepoch.service
  sudo systemctl enable nodeyez-halving.service
  sudo systemctl start nodeyez-halving.service
  sudo systemctl enable nodeyez-mempoolblocks.service
  sudo systemctl start nodeyez-mempoolblocks.service
  sudo systemctl enable nodeyez-opreturn.service
  sudo systemctl start nodeyez-opreturn.service
  # lnd: channelbalance and channelfees
  if [ $GRANTED_LND -ge 1 ]; then
    sudo systemctl enable nodeyez-channelbalance.service
    sudo systemctl start nodeyez-channelbalance.service
    sudo systemctl enable nodeyez-channelfees.service
    sudo systemctl start nodeyez-channelfees.service
  fi
fi

# show summary
echo "================================================"
echo "SUMMARY:"
if [ $CREATED_USER -ge 1 ]; then
  echo "Nodeyez user created"
else
  echo "Nodeyez user already exists"
fi
if [ $GRANTED_BITCOIN -ge 1 ]; then
  echo "Bitcoin configuration and cookie copied to Nodeyez"
fi
if [ $GRANTED_LND -ge 1 ]; then
  echo "LND TLS certificate copied to Nodeyez, and custom macaroon created"
fi
if [ $CLONED_REPO -ge 1 ]; then
  echo "Nodeyez repository cloned from github"
else
  echo "Nodeyez repository already exists. ${GITPULLRESULT}"
fi
if [ $CREATED_PYENV -ge 1 ]; then
  echo "Python virtual environment created"
else
  echo "Python virtual environment already exists"
fi
if [ $CREATED_WEBSITE -ge 1 ]; then
  echo "Website Dashboard setup and available at ${WEBURL}"
fi
echo "Services enabled and started"
# show service status
sudo systemctl list-units --type=service --state=active | grep nodeyez | awk '{print "(active) " $1}'
# failed
sudo systemctl list-units --type=service --state=failed | grep nodeyez | awk '{print "(failed) " $2}'


