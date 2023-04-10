#!/usr/bin/env bash

# Script config for development/testing - not user config options
GITCLONEREPO="https://github.com/vicariousdrama/nodeyez.git"
GITCLONEBRANCH="main"

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
  echo "You may proceed following manual installation steps but may not be able to get all features"
  echo "Some Nodeyez scripts are capable of running on a Raspberry Pi Zero W, just slower"
  echo "For example, depending on platform, prebuilt tor or inkskape packages may not be available"
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

# Detect raspberry pi
RASPBERRYPI=0
if [ -d "/proc/device-tree" ]; then
  RASPBERRYPI=$(grep Raspberry /proc/device-tree/model|wc -l)
  if [ $RASPBERRYPI -eq 0]; then
    HWPKG=$(grep Hardware /proc/cpuinfo|awk '{print $3}')
    RASPBERRYPI=$(echo "BCM2708 BCM2709 BCM2835 BCM2837" | grep $HWPKG | wc -l)
  fi
else
  RASPBERRYPI=$(grep Raspberry /proc/cpuinfo|wc -l)
fi

# Detect common node environments 
INSOK=1
ISEMBASSYOS=0
if [ $(which embassy-cli | wc -l) -gt 0 ]; then
  echo "EMBASSYOS environment detected"
  ISEMBASSYOS=1
elif [ $(systemctl status embassyd 2>/dev/null | grep active | wc -l) -gt 0 ]; then
  echo "EMBASSYOS environment detected"
  ISEMBASSYOS=1
fi
ISMYNODE=0
if [ -d "/mnt/hdd/mynode" ]; then
  echo "MYNODEBTC environment detected"
  ISMYNODE=1
fi
ISNODL=0
if [ -d "/usr/share/nodl" ]; then
  echo "NODL environment detected"
  ISNODL=1
fi
ISRASPIBLITZ=0
if [ -f "/mnt/hdd/raspiblitz.conf" ]; then
  echo "RASPIBLITZ environment detected"
  ISRASPIBLITZ=1
fi
ISRASPIBOLT=0
if [ -f "/etc/systemd/system/bitcoind.service" ]; then
  if [ $(head -n 1 /etc/systemd/system/bitcoind.service | grep -i raspibolt | wc -l) -gt 0 ]; then
    echo "RASPIBOLT environment detected"
    ISRASPIBOLT=1
  fi
fi
ISUMBREL=0
if [ -d "/mnt/data/umbrel" ]; then
  echo "UMBREL environment detected"
  ISUMBREL=1
fi

# Some known node packages are not yet supported
# If you're a developer that can add support for this, please feel free to open a PR
# Or contact me directly if you'd like to sponsor my efforts to add support
if [ $ISEMBASSYOS -eq 1 ]; then   # Radically different + licensing issues
  INSOK=0
fi
if [ $ISNODL -eq 1 ]; then        # Need to setup environment for testing
  INSOK=0
fi
if [ $ISUMBREL -eq 1 ]; then      # Docker. Poor bitcoin-cli handling. Licensing issues
  INSOK=0
fi
if [ $INSOK -eq 0 ]; then
  echo "This install script is not supported on your system at this time."
  exit
fi

# Tools
apt-get update          # without this, a few packages will fail
apt-get -y install \
    apt-transport-tor \
    fbi \
    git \
    imagemagick \
    inkscape \
    jq \
    libjpeg-dev \
    netcat \
    python3 \
    python3-venv \
    zlib1g-dev 

# Create Nodeyez user
CREATED_USER=0
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

# Add user to tor group if not already
if [ $(id --name -G nodeyez | grep debian-tor | wc -l) -eq 0 ]; then
  adduser nodeyez debian-tor
fi

# Bitcoin user must exist for bitcoin and lnd setup
GRANTED_BITCOIN=0
GRANTED_LND=0
mkdir -p /home/nodeyez/.bitcoin
mkdir -p /home/nodeyez/.lnd
if id bitcoin &>/dev/null; then
  # Give bitcoin cookie and config
  echo "Granting bitcoin cookie and config" 
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
CLONED_REPO=0
GITPULLRESULT=""
if [ ! -d "/home/nodeyez/nodeyez" ]; then
  echo "Cloning Nodeyez"
  sudo -u nodeyez git clone --single-branch --branch $GITCLONEBRANCH $GITCLONEREPO /home/nodeyez/nodeyez
  chown -R nodeyez:nodeyez /home/nodeyez/nodeyez
  CLONED_REPO=1
else
  echo "Folder for nodeyez repository already exists at /home/nodeyez/nodeyez"
  GITPULLRESULT=$(sudo -u nodeyez bash -c "cd /home/nodeyez/nodeyez && git pull")
fi
# create folders that dont yet exist
sudo -u nodeyez mkdir -p /home/nodeyez/nodeyez/{config,data,imageoutput,temp}
sudo -u nodeyez mkdir -p /home/nodeyez/nodeyez/imageoutput/ordinals
# copy sample configs that aren't yet in user config
sudo -u nodeyez cp -n /home/nodeyez/nodeyez/sample-config/*.json /home/nodeyez/nodeyez/config

# Create python virtual environment in nodeyez user space
CREATED_PYENV=0
if [ ! -d "/home/nodeyez/.pyenv/nodeyez" ]; then
  echo "Creating python virtual environment"
  sudo -u nodeyez python3 -m venv /home/nodeyez/.pyenv/nodeyez
  CREATED_PYENV=1
else
  echo "Python virtual environment already exists"
fi
# ensure python modules we depend on are present in the virtual environment
sudo -u nodeyez -s source /home/nodeyez/.pyenv/nodeyez/bin/activate && /home/nodeyez/.pyenv/nodeyez/bin/python3 -m pip install --upgrade \
    beautifulsoup4 exifread pandas pysocks qrcode redis requests urllib3 whiptail-dialogs Pillow Wand

# Website dashboard
CREATED_WEBSITE=0
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
  CREATED_WEBSITE=1
fi
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
  CREATED_WEBSITE=1
elif [ $ISRASPIBLITZ -gt 0 ]; then
  echo "Copying Nodeyez site configuration specific to Raspiblitz"
  # mynode uses its own ssl cert
  cp /home/nodeyez/nodeyez/scripts/nginx/https_nodeyez_raspiblitz.conf /etc/nginx/sites-enabled/https_nodeyez.conf
  CREATED_WEBSITE=1
elif [ $ISRASPIBOLT -gt 0 ]; then
  # ensure no sites-enabled
  if [ $(cat /etc/nginx/nginx.conf | grep -i "sites-enabled" | wc -l) -eq 0 ]; then
    # ensure streams-enabled
    if [ $(cat /etc/nginx/nginx.conf | grep -i "streams-enabled" | wc -l) -gt 0 ]; then
      echo "Copy Nodeyez http configuration specific to Raspibolt"
      cp /home/nodeyez/nodeyez/scripts/nginx/http_nodeyez_raspibolt.conf /etc/nginx/nodeyez/http_nodeyez_raspibolt.conf
      if [ ! -f "/etc/nginx/modules-enabled/http_nodeyez_raspibolt.conf" ]; then
        ln -s /etc/nginx/nodeyez/http_nodeyez_raspibolt.conf /etc/nginx/modules-enabled/http_nodeyez_raspibolt.conf
      fi
      echo "Copying Nodeyez stream configuration specific to Raspibolt"
      cp /home/nodeyez/nodeyez/scripts/nginx/https_nodeyez_raspibolt.conf /etc/nginx/streams-enabled/https_nodeyez_raspibolt.conf
      CREATED_WEBSITE=1
    fi
  fi
else
  # generic site config
  echo "Copying Nodeyez site configuration as generic sites-enabled"
  cp /home/nodeyez/nodeyez/scripts/nginx/https_nodeyez.conf /etc/nginx/sites-enabled/https_nodeyez.conf
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

WEBURL=""
if [ $CREATED_WEBSITE -eq 1 ]; then
  # enable port 907 to the dashboard
  if [ $(ufw status | grep 907 | grep Nodeyez | wc -l) -eq 0 ]; then
    ufw allow 907 comment 'allow Nodeyez Dashboard HTTPS'
    ufw --force enable
  fi
  # restart nginx
  systemctl restart nginx
  # get weburl
  WEBURL=$(hostname -I | awk {'print "https://" $1 ":907"}')
fi

# Services
cp /home/nodeyez/nodeyez/scripts/systemd/*.service /etc/systemd/system/
cp /home/nodeyez/nodeyez/scripts/systemd/nodeyez.conf /etc/nodeyez.conf

# Initial services to enable and start
# - fearandgreed, fiatprice, ipaddress, mempoolblocks, satsperusd, sysinfo, utcclock
if [ 1 -eq 1 ]; then
systemctl enable nodeyez-fearandgreed.service
systemctl start nodeyez-fearandgreed.service
systemctl enable nodeyez-fiatprice.service
systemctl start nodeyez-fiatprice.service
systemctl enable nodeyez-ipaddress.service
systemctl start nodeyez-ipaddress.service
systemctl enable nodeyez-mempoolblocks.service
systemctl start nodeyez-mempoolblocks.service
systemctl enable nodeyez-satsperusd.service
systemctl start nodeyez-satsperusd.service
systemctl enable nodeyez-sysinfo.service
systemctl start nodeyez-sysinfo.service
systemctl enable nodeyez-utcclock.service
systemctl start nodeyez-utcclock.service
systemctl enable nodeyez-daily-data-retrieval.service
systemctl start nodeyez-daily-data-retrieval.service
fi
# - bitcoin: arthash, blockhashdungeon, blockheight, blockstats, difficultyepoch, halving, opreturn
if [ $GRANTED_BITCOIN -ge 1 ]; then
  systemctl enable nodeyez-arthash.service
  systemctl start nodeyez-arthash.service
  systemctl enable nodeyez-blockhashdungeon.service
  systemctl start nodeyez-blockhashdungeon.service
  systemctl enable nodeyez-blockheight.service
  systemctl start nodeyez-blockheight.service
  systemctl enable nodeyez-blockstats.service
  systemctl start nodeyez-blockstats.service
  systemctl enable nodeyez-difficultyepoch.service
  systemctl start nodeyez-difficultyepoch.service
  systemctl enable nodeyez-halving.service
  systemctl start nodeyez-halving.service
  systemctl enable nodeyez-opreturn.service
  systemctl start nodeyez-opreturn.service
  # lnd: channelbalance and channelfees
  if [ $GRANTED_LND -ge 1 ]; then
    systemctl enable nodeyez-lndchannelbalance.service
    systemctl start nodeyez-lndchannelbalance.service
    systemctl enable nodeyez-lndchannelfees.service
    systemctl start nodeyez-lndchannelfees.service
  fi
fi

# Config tool
UPDATED_CONFIGTOOL=0
if [ -f "/usr/local/bin/nodeyez-config" ]; then
  UPDATED_CONFIGTOOL=1
fi
cp /home/nodeyez/nodeyez/scripts/nodeyez-config /usr/local/bin

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
# report config tool
if [ $UPDATED_CONFIGTOOL -ge 1 ]; then
  echo "Nodeyez configuration tool updated. Run it with: sudo nodeyez-config"
else
  echo "Nodeyez configuration tool installed. Run it with: sudo nodeyez-config"
fi
# raspberry pi guidance
if [ $RASPBERRYPI -ge 1 ]; then
  echo "You appear to be running a Raspbery Pi."
  echo "If you want to attach an LCD or DSI screen, be sure to follow the steps at"
  echo "   https://nodeyez.com/install_steps/2displayscreen"
  echo "For convenience, the framebuffer imageviewer tool has already been installed."
fi