#!/usr/bin/env bash

# Check that the script is started as root
if [ "$EUID" -ne 0 ]; then 
  echo "Please run as root or with sudo as follows"
  echo "wget -qO- https://nodeyez.com/install.sh | sudo bash"
  exit
fi

# Require a Debian based distro (or rather, must have access to /usr/bin/apt)
if [ ! -f "/usr/bin/apt" ]; then
  echo "This install script requires the Advanced Package Tool (apt), on Debian and derivative systems"
  exit
fi

# For now, only proceed if 64 bit
# 32 Bit raspberry pi seems to be lacking some key dependencies like 
# tor, nginx-commons, imagemagick and possibly others
if [ ! $(getconf LONG_BIT) -eq 64 ]; then
  echo "This install script requires a 64 bit operating system to satisfy dependencies"
  exit
fi

# Check for supported hardware - Intel/AMD or Raspberry Pi ARM chips
MACHINEOK=0
machine_hardware=$(uname -m)
if [ $machine_hardware == "x86_64" ]; then
  # Intel or AMD chip
  MACHINEOK=1
fi
if [ $machine_hardware == "aarch64" ]; then
  # Raspberry Pi and RockPro using ARM chip
  MACHINEOK=1
fi
if [ $MACHINEOK -eq 0 ]; then
  echo "This install script has only been tested on x86_64 and aarch64"
  exit
fi

# Initialize variables that we'll check later
CREATED_USER=0
GRANTED_BITCOIN=0
GRANTED_LND=0
CLONED_REPO=0
CREATED_PYENV=0
CREATED_WEBSITE=0
WEBURL=""
ISMYNODE=0
GITPULLRESULT=""

# Detect environment
if [ -d "/mnt/hdd/mynode" ]; then
  echo "MYNODEBTC environment detected"
  ISMYNODE=1
fi

# Tools
apt-get -y install \
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
    adduser --gecos "" --disabled-password nodeyez
  else
    NODEYEZ_HOME=${EXT_DRIVE_MOUNT}/nodeyez
    adduser --home ${NODEYEZ_HOME} --gecos "" --disabled-password nodeyez
    ln -s ${NODEYEZ_HOME} /home/nodeyez
    chown -R nodeyez:nodeyez /home/nodeyez
  fi
  CREATED_USER=1
fi

# Set permissions on nodeyez home folder so others can read
chmod 755 /home/nodeyez

# Add user to tor group
adduser nodeyez debian-tor

# Bitcoin user must exist for bitcoin and lnd setup
if id bitcoin &>/dev/null; then
  # Give bitcoin cookie and config
  echo "Granting bitcoin cookie and config"
  mkdir -p /home/nodeyez/.bitcoin
  if [ -f "/home/bitcoin/.bitcoin/bitcoin.conf" ]; then
    cp /home/bitcoin/.bitcoin/bitcoin.conf /home/nodeyez/.bitcoin/bitcoin.conf
  else
    echo "- error: unable to grant bitcoin config. File /home/bitcoin/.bitcoin/bitcoin.conf not found"
  fi
  if [ -f "/home/bitcoin/.bitcoin/.cookie" ]; then
    cp /home/bitcoin/.bitcoin/.cookie /home/nodeyez/.bitcoin/.cookie
  else
    echo "- error: unable to grant bitcoin cookie. File /home/bitcoin/.bitcoin/.cookie not found"
  fi
  chown -R nodeyez:nodeyez /home/nodeyez/.bitcoin
  GRANTED_BITCOIN=1

  # Give LND cert and macaroon if LND exists
  if [ -f "/usr/bin/lncli" ]; then
    echo "Granting LND cert and baking custom macaroon"
    mkdir -p /home/nodeyez/.lnd
    LNDCERTFILE="/home/bitcoin/.lnd/tls.cert"
    if [ -f "$LNDCERTFILE" ]; then
      cp /home/bitcoin/.lnd/tls.cert /home/nodeyez/.lnd/tls.cert
    fi
    sudo -u bitcoin /usr/bin/lncli bakemacaroon uri:/lnrpc.Lightning/GetInfo uri:/lnrpc.Lightning/GetNodeInfo uri:/lnrpc.Lightning/ListPeers uri:/lnrpc.Lightning/ListChannels uri:/lnrpc.Lightning/ChannelBalance uri:/lnrpc.Lightning/ConnectPeer uri:/lnrpc.Lightning/DisconnectPeer uri:/lnrpc.Lightning/ForwardingHistory uri:/lnrpc.Lightning/ListPayments uri:/lnrpc.Lightning/DecodePayReq uri:/lnrpc.Lightning/FeeReport --save_to /tmp/nodeyez.macaroon
    if [ -f "/home/nodeyez/.lnd/nodeyez.macaroon" ]; then
      rm /home/nodeyez/.lnd/nodeyez.macaroon
    fi
    mv /tmp/nodeyez.macaroon /home/nodeyez/.lnd/nodeyez.macaroon
    rm /tmp/nodeyez.macaroon
    chown -R nodeyez:nodeyez /home/nodeyez/.lnd
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
  chown -R nodeyez:nodeyez /home/nodeyez/nodeyez
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
if [ $(which nginx | wc -l) -eq 0 ]; then
  # nginx is not yet installed
  echo "Installing NGINX"
  apt install -y nginx nginx-common
  CREATED_WEBSITE=1
else
  echo "NGINX aleady installed"
fi
if [ ! -f "/etc/ssl/certs/nodeyez-nginx-selfsigned.crt" ]; then
  echo "Creating Nodeyez self signed cert"
  openssl req -x509 -nodes -newkey rsa:2048 -keyout /etc/ssl/private/nodeyez-nginx-selfsigned.key -out /etc/ssl/certs/nodeyez-nginx-selfsigned.crt -subj "/CN=localhost" -days 3650
  CREATED_WEBSITE=1
fi
if [ ! -f "/etc/ssl/certs/dhparam.pem" ]; then
  echo "Creating Diffie-Hellman parameters"
  openssl dhparam -dsaparam -out /etc/ssl/certs/dhparam.pem 4096
  CREATED_WEBSITE=1
fi
# get some ssl cert info from existing nginx config
echo "Getting currently referenced SSL Certificate and Key"
line_ssl_certificate=$(nginx -T 2>&1 | grep "ssl_certificate " | sed -n 1p)
line_ssl_certificate_key=$(nginx -T 2>&1 | grep "ssl_certificate_key " | sed -n 1p)
# copy xslt templates
echo "Copying in Nodeyez XSLT templates"
cp /home/nodeyez/nodeyez/scripts/nginx/nodeyez*.xslt /etc/nginx/
chown root:root /etc/nginx/nodeyez*.xslt
# nodeyez config referencing our freshly minted self signed certs
echo "Copying in Nodeyez SSL Config"
mkdir -p /etc/nginx/nodeyez
cp /home/nodeyez/nodeyez/scripts/nginx/nodeyez_ssl*.conf /etc/nginx/nodeyez
# enable xslt module if not already present
if [ $(cat /etc/nginx/modules-enabled/* | grep xslt | wc -l) -gt 0 ]; then
  echo "XSLT module already loaded for NGINX"
else
  echo "XSLT module being added by Nodeyez"
  cp /home/nodeyez/nodeyez/scripts/nginx/a_xslt.conf /etc/nginx/modules-enabled/a_xslt.conf
  chown root:root /etc/nginx/modules-enabled/a_xslt.conf
  CREATED_WEBSITE=1
fi
# site config
echo "Copying Nodeyez site configuration"
cp /home/nodeyez/nodeyez/scripts/nginx/https_nodeyez.conf /etc/nginx/sites-enabled/https_nodeyez.conf
chown root:root /etc/nginx/sites-enabled/https_nodeyez.conf
# assign back first cert and key if detected from earlier
if [ ${#line_ssl_certificate} -gt 0 ]; then
  echo "Reassigning SSL Certificate and Key"
  rm /etc/nginx/nodeyez/nodeyez_ssl_cert_key.conf
  echo $line_ssl_certificate >> /etc/nginx/nodeyez/nodeyez_ssl_cert_key.conf
  echo $line_ssl_certificate_key >> /etc/nginx/nodeyez/nodeyez_ssl_cert_key.conf
  echo "/etc/nginx/nodeyez/nodeyez_ssl_cert_key.conf:["
  cat /etc/nginx/nodeyez/nodeyez_ssl_cert_key.conf
  echo "] EOF"
  CREATED_WEBSITE=1
fi
# custom config per environment
if [ $ISMYNODE -gt 0 ]; then
  echo "Copying Nodeyez site configuration specific to MyNodeBTC"
  # mynode uses its own ssl cert
  cp /home/nodeyez/nodeyez/scripts/nginx/https_nodeyez_mynode.conf /etc/nginx/sites-enabled/https_nodeyez.conf
  chown root:root /etc/nginx/sites-enabled/https_nodeyez.conf
  CREATED_WEBSITE=1
fi
# remove our xslt enabler if there is more then 1 line in modules loading it
if [ $(cat /etc/nginx/modules-enabled/* | grep xslt | wc -l) -gt 1 ]; then
  if [ -f "/etc/nginx/modules-enabled/a_xslt.conf" ]; then
    echo "Removing XSLT from Nodeyez"
    rm /etc/nginx/modules-enabled/a_xslt.conf
  CREATED_WEBSITE=1
  fi
fi

if [ $CREATED_WEBSITE -eq 1 ]; then
  systemctl restart nginx
  # enable port 907 to the dashboard
  ufw allow 907 comment 'allow Nodeyez Dashboard HTTPS'
  ufw enable
  # restart nginx
  systemctl restart nginx
  # get weburl
  WEBURL=$(hostname -I | awk {'print "https://" $1 ":907"}')
fi

# Services
cp /home/nodeyez/nodeyez/scripts/systemd/*.service /etc/systemd/system/
cp /home/nodeyez/nodeyez/scripts/systemd/nodeyez.conf /etc/nodeyez.conf

# Initial services to enable and start
# - fearandgreed, fiatprice, ipaddress, satsperusd, sysinfo, utcclock
if [ 1 -eq 1 ]; then
systemctl enable nodeyez-fearandgreed.service
systemctl start nodeyez-fearandgreed.service
systemctl enable nodeyez-fiatprice.service
systemctl start nodeyez-fiatprice.service
systemctl enable nodeyez-ipaddress.service
systemctl start nodeyez-ipaddress.service
systemctl enable nodeyez-satsperusd.service
systemctl start nodeyez-satsperusd.service
systemctl enable nodeyez-sysinfo.service
systemctl start nodeyez-sysinfo.service
systemctl enable nodeyez-utcclock.service
systemctl start nodeyez-utcclock.service
systemctl enable nodeyez-daily-data-retrieval.service
systemctl start nodeyez-daily-data-retrieval.service
fi
# - bitcoin: arthash, arthashdungeon, blockheight, blockstats, difficultyepoch, halving, mempoolblocks
if [ $GRANTED_BITCOIN -ge 1 ]; then
  systemctl enable nodeyez-arthash.service
  systemctl start nodeyez-arthash.service
  systemctl enable nodeyez-arthashdungeon.service
  systemctl start nodeyez-arthashdungeon.service
  systemctl enable nodeyez-blockheight.service
  systemctl start nodeyez-blockheight.service
  systemctl enable nodeyez-blockstats.service
  systemctl start nodeyez-blockstats.service
  systemctl enable nodeyez-difficultyepoch.service
  systemctl start nodeyez-difficultyepoch.service
  systemctl enable nodeyez-halving.service
  systemctl start nodeyez-halving.service
  systemctl enable nodeyez-mempoolblocks.service
  systemctl start nodeyez-mempoolblocks.service
  systemctl enable nodeyez-opreturn.service
  systemctl start nodeyez-opreturn.service
  # lnd: channelbalance and channelfees
  if [ $GRANTED_LND -ge 1 ]; then
    systemctl enable nodeyez-channelbalance.service
    systemctl start nodeyez-channelbalance.service
    systemctl enable nodeyez-channelfees.service
    systemctl start nodeyez-channelfees.service
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
  echo "Nodeyez user received Bitcoin configuration and cookie"
fi
if [ $GRANTED_LND -ge 1 ]; then
  echo "Nodeyez user received LND tls cert and limited privilege macaroon"
fi
if [ $CLONED_REPO -ge 1 ]; then
  echo "Nodeyez user cloned repository from Github"
else
  echo "Nodeyez user updated repository. ${GITPULLRESULT}"
fi
if [ $CREATED_PYENV -ge 1 ]; then
  echo "Nodeyez user created python virtual environment"
else
  echo "Nodeyez user updated python virtual environment"
fi
if [ $CREATED_WEBSITE -ge 1 ]; then
  echo "Nodeyez website dashboard setup and available at ${WEBURL}"
fi
echo "Nodeyez services enabled and started"
# show service status
systemctl list-units --type=service --state=active | grep nodeyez | awk '{print "(active) " $1}'
# failed
systemctl list-units --type=service --state=failed | grep nodeyez | awk '{print "(failed) " $2}'
