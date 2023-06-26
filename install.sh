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

echo "================================================"
echo "ENVIRONMENT:"

# Require a Debian based distro (or rather, must have access to /usr/bin/apt)
if [ ! -f "/usr/bin/apt" ]; then
  echo "This install script requires the Advanced Package Tool (apt), on Debian and derivative systems"
  exit
fi
echo "debian based environment"

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
echo "machine hardware detected as ${machine_hardware}"

# Detect raspberry pi
RASPBERRYPI=0
if [ -d "/proc/device-tree" ]; then
  RASPBERRYPI=$(grep Raspberry /proc/device-tree/model|wc -l)
  if [ $RASPBERRYPI -eq 0 ]; then
    HWPKG=$(grep Hardware /proc/cpuinfo|awk '{print $3}')
    RASPBERRYPI=$(echo "BCM2708 BCM2709 BCM2835 BCM2837" | grep $HWPKG | wc -l)
  fi
else
  RASPBERRYPI=$(grep Raspberry /proc/cpuinfo|wc -l)
fi
if [ $RASPBERRYPI -ge 1 ]; then
  echo "detected raspberry pi"
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
if [ $ISEMBASSYOS -eq 1 ]; then   # Radically different + licensing issues, needs dockerized
  INSOK=0
fi
if [ $ISNODL -eq 1 ]; then        # Need to setup environment for testing
  INSOK=0
fi
if [ $ISUMBREL -eq 1 ]; then      # Docker. Poor bitcoin-cli handling. Licensing issues, needs dockerized
  INSOK=0
fi
if [ $INSOK -eq 0 ]; then
  echo "This install script is not supported on your system at this time."
  exit
fi

# Tools
echo "================================================"
echo "TOOLS:"
echo "updating system..."
apt-get update          # without this, a few packages may fail
echo "ensuring dependent packages are installed..."
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
echo "================================================"
echo "CREATING NODEYEZ USER"
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
    echo "- creating user with home in default location"
    NODEYEZ_HOME=/home/nodeyez
    adduser --gecos "" --disabled-password nodeyez
  else
    echo "- creating user with home on external drive mount"
    NODEYEZ_HOME=${EXT_DRIVE_MOUNT}/nodeyez
    adduser --home ${NODEYEZ_HOME} --gecos "" --disabled-password nodeyez
    ln -s ${NODEYEZ_HOME} /home/nodeyez
    chown -R nodeyez:nodeyez /home/nodeyez
  fi
  CREATED_USER=1
fi

# Set permissions on nodeyez home folder so others can read
# 2023-06: no longer do this as it exposes creds to everyone. admin users can sudo
# chmod 755 /home/nodeyez

# Add user to tor group if not already
if [ $(id --name -G nodeyez | grep debian-tor | wc -l) -eq 0 ]; then
  echo "adding user to tor group"
  adduser nodeyez debian-tor
fi

# Bitcoin user must exist for bitcoin and lnd setup
echo "================================================"
echo "Bitcoin and LND:"
GRANTED_BITCOIN=0
GRANTED_LND=0
echo ""
echo "Initially, Nodeyez leveraged bitcoin and lnd via the command line."
echo "This required bitcoin and lnd to be installed locally and accessible under a"
echo "user named 'bitcoin'. This portion of setup is maintained for backwards"
echo "compatibility and will auto-enable bitcoin related Nodeyez panels if detected"
echo ""
echo "You may also connect to bitcoin and lnd nodes via JSON-RPC REST calls. To do"
echo "this, run the nodeyez-config tool after installation to define profiles."
echo "For bitcoin, you will need to have the rpcuser and rpcpassword values in"
echo "addition to the server address and port.  For lnd, you will need to convert"
echo "the macaroon to hex format in addition to server address and port."
echo ""
mkdir -p /home/nodeyez/.bitcoin
mkdir -p /home/nodeyez/.lnd
if id bitcoin &>/dev/null; then
  echo "bitcoin user detected"
  # Give bitcoin cookie and config
  echo "granting bitcoin cookie and config to nodeyez" 
  if [ -f "/home/bitcoin/.bitcoin/bitcoin.conf" ]; then
    cp /home/bitcoin/.bitcoin/bitcoin.conf /home/nodeyez/.bitcoin/bitcoin.conf
  else
    echo "- warning: unable to grant bitcoin config. File /home/bitcoin/.bitcoin/bitcoin.conf not found"
  fi
  if [ -f "/home/bitcoin/.bitcoin/.cookie" ]; then
    cp /home/bitcoin/.bitcoin/.cookie /home/nodeyez/.bitcoin/.cookie
  else
    echo "- warning: unable to grant bitcoin cookie. File /home/bitcoin/.bitcoin/.cookie not found"
  fi
  chown -R nodeyez:nodeyez /home/nodeyez/.bitcoin
  GRANTED_BITCOIN=1

  # Give LND cert and macaroon if LND exists
  LNCLI_PATH=$(which lncli)
  if [ -z "$LNCLI_PATH" ]; then
    echo "- lncli not found. assuming LND not installed."
  else
    echo "- lncli found at ${LNCLI_PATH}"
    echo "- granting LND cert"
    LNDCERTFILE="/home/bitcoin/.lnd/tls.cert"
    if [ -f "$LNDCERTFILE" ]; then
      cp /home/bitcoin/.lnd/tls.cert /home/nodeyez/.lnd/tls.cert
    else
      echo "  warning: certificate not found"
    fi
    echo "- baking custom macaroon"
    sudo -u bitcoin ${LNCLI_PATH} bakemacaroon uri:/lnrpc.Lightning/GetInfo uri:/lnrpc.Lightning/GetNodeInfo uri:/lnrpc.Lightning/ListPeers uri:/lnrpc.Lightning/ListChannels uri:/lnrpc.Lightning/ChannelBalance uri:/lnrpc.Lightning/ConnectPeer uri:/lnrpc.Lightning/DisconnectPeer uri:/lnrpc.Lightning/ForwardingHistory uri:/lnrpc.Lightning/ListPayments uri:/lnrpc.Lightning/DecodePayReq uri:/lnrpc.Lightning/FeeReport --save_to /tmp/nodeyez.macaroon
    macaroonhex=$(xxd -ps -u -c 1000 /tmp/nodeyez.macaroon)
    if [ -f "/home/nodeyez/.lnd/nodeyez.macaroon" ]; then
      rm /home/nodeyez/.lnd/nodeyez.macaroon
    fi
    echo "- moving macaroon to nodeyez"
    mv /tmp/nodeyez.macaroon /home/nodeyez/.lnd/nodeyez.macaroon
    chown -R nodeyez:nodeyez /home/nodeyez/.lnd    
    GRANTED_LND=1
  else
    echo "lnd not installed"
  fi
else
  echo "bitcoin user not present"
fi

# Clone repository into nodeyez user space
echo "================================================"
echo "GIT REPOSITORY:"
CLONED_REPO=0
GITPULLRESULT=""
if [ ! -d "/home/nodeyez/nodeyez" ]; then
  echo "cloning Nodeyez..."
  sudo -u nodeyez git clone --single-branch --branch $GITCLONEBRANCH $GITCLONEREPO /home/nodeyez/nodeyez
  chown -R nodeyez:nodeyez /home/nodeyez/nodeyez
  CLONED_REPO=1
else
  echo "detected folder at /home/nodeyez/nodeyez"
  echo "fetching and pulling latest changes..."
  GITPULLRESULT=$(sudo -u nodeyez bash -c "cd /home/nodeyez/nodeyez && git pull")
fi
# create folders that dont yet exist
echo "================================================"
echo "NODEYEZ CONFIG FILES:"
echo "ensuring folders exist..."
sudo -u nodeyez mkdir -p /home/nodeyez/nodeyez/{config,data,imageoutput,temp}
# copy sample configs that aren't yet in user config
echo "creating config files from sample-config where missing..."
sudo -u nodeyez cp -n /home/nodeyez/nodeyez/sample-config/*.json /home/nodeyez/nodeyez/config
# rename user config to new names if they exist
echo "renaming old config files..."
if [ -f "/home/nodeyez/nodeyez/config/braiinspool.json" ]; then
  echo "- braiinspool -> miningpool-braiinspool"
  sudo -u nodeyez mv /home/nodeyez/nodeyez/config/braiinspool.json /home/nodeyez/nodeyez/config/miningpool-braiinspool.json 2>/dev/null
fi
if [ -f "/home/nodeyez/nodeyez/config/f2pool.json" ]; then
  echo "- f2pool -> miningpool-f2pool"
  sudo -u nodeyez mv /home/nodeyez/nodeyez/config/f2pool.json /home/nodeyez/nodeyez/config/miningpool-f2pool.json 2>/dev/null
fi
if [ -f "/home/nodeyez/nodeyez/config/ipaddress.json" ]; then
  echo "- ipaddress -> ipaddresses"
  sudo -u nodeyez mv /home/nodeyez/nodeyez/config/ipaddress.json /home/nodeyez/nodeyez/config/miningpool-ipaddresses.json 2>/dev/null
fi
if [ -f "/home/nodeyez/nodeyez/config/mempool.json" ]; then
  echo "- mempool -> mempoolspace"
  sudo -u nodeyez mv /home/nodeyez/nodeyez/config/mempool.json /home/nodeyez/nodeyez/config/mempoolspace.json 2>/dev/null
fi
if [ -f "/home/nodeyez/nodeyez/config/mempoolblocks.json" ]; then
  echo "- mempoolblocks -> mempoolspace"
  sudo -u nodeyez mv /home/nodeyez/nodeyez/config/mempoolblocks.json /home/nodeyez/nodeyez/config/mempoolspace.json 2>/dev/null
fi
if [ -f "/home/nodeyez/nodeyez/config/ordinals.json" ]; then
  echo "- ordinals -> inscriptionparser"
  sudo -u nodeyez mv /home/nodeyez/nodeyez/config/ordinals.json /home/nodeyez/nodeyez/config/inscriptionparser.json 2>/dev/null
fi
if [ -f "/home/nodeyez/nodeyez/config/rofstatus.json" ]; then
  echo "- rofstatus -> lndringoffire"
  sudo -u nodeyez mv /home/nodeyez/nodeyez/config/rofstatus.json /home/nodeyez/nodeyez/config/lndringoffire.json 2>/dev/null
fi
if [ -f "/home/nodeyez/nodeyez/config/satsperusd.json" ]; then
  echo "- satsperusd -> satsperfiatunit"
  sudo -u nodeyez mv /home/nodeyez/nodeyez/config/satsperusd.json /home/nodeyez/nodeyez/config/satsperfiatunit.json 2>/dev/null
fi
if [ -f "/home/nodeyez/nodeyez/config/slushpool.json" ]; then
  echo "- slushpool -> miningpool-braiinspool"
  sudo -u nodeyez mv /home/nodeyez/nodeyez/config/slushpool.json /home/nodeyez/nodeyez/config/miningpool-braiinspool.json 2>/dev/null
fi
# set macaroon into lnd-rest config if not defined
if [ $GRANTED_LND -ge 1 ]; then
  hasdefaultprofile=$(cat /home/nodeyez/nodeyez/config/lnd-rest.json | jq -r '.profiles[]|select(.name=="default").name'|wc -l)
  if [ $hasdefaultprofile -ge 1 ]; then
    configmacaroon=$(cat /home/nodeyez/nodeyez/config/lnd-rest.json | jq -r '.profiles[]|select(.name=="default").macaroon')
    setmacaroon=0
    # if empty
    if [ -n $configmacaroon ]; then
      setmacaroon=1
    fi
    # if short from sample-config
    if [ $configmacaroon == "23972973293A876dCF236D2..." ]; then
      setmacaroon=1
    fi
    if [ $setmacaroon -ge 1 ]; then
      jq '.profiles[]|select(.name=="default").macaroon = "'$macaroonhex'"' /home/nodeyez/nodeyez/config/lnd-rest.json
    fi
  fi
fi

# Create python virtual environment in nodeyez user space
echo "================================================"
echo "PYTHON ENVIRONMENT:"
CREATED_PYENV=0
if [ ! -d "/home/nodeyez/.pyenv/nodeyez" ]; then
  echo "creating python virtual environment"
  sudo -u nodeyez python3 -m venv /home/nodeyez/.pyenv/nodeyez
  CREATED_PYENV=1
else
  echo "detected existing python virtual environment"
fi
# ensure python modules we depend on are present in the virtual environment
echo "ensuring required modules..."
sudo -u nodeyez -s source /home/nodeyez/.pyenv/nodeyez/bin/activate && /home/nodeyez/.pyenv/nodeyez/bin/python3 -m pip install --upgrade \
    beautifulsoup4 exifread pandas psutil pysocks qrcode redis requests urllib3 whiptail-dialogs Pillow Wand

# Website dashboard
echo "================================================"
echo "WEBSITE DASHBOARD:"
CREATED_WEBSITE=0
if [ $(which nginx | wc -l) -eq 0 ]; then
  # nginx is not yet installed
  echo "installing nginx"
  apt install -y nginx nginx-common
  CREATED_WEBSITE=1
else
  echo "nginx is aleady installed"
fi
if [ ! -f "/etc/ssl/certs/nodeyez-nginx-selfsigned.crt" ]; then
  echo "- creating Nodeyez self signed cert"
  openssl req -x509 -nodes -newkey rsa:2048 -keyout /etc/ssl/private/nodeyez-nginx-selfsigned.key -out /etc/ssl/certs/nodeyez-nginx-selfsigned.crt -subj "/CN=localhost" -days 3650
  CREATED_WEBSITE=1
fi
echo "configuring..."
if [ ! -f "/etc/ssl/certs/dhparam.pem" ]; then
  echo "- creating Diffie-Hellman parameters"
  openssl dhparam -dsaparam -out /etc/ssl/certs/dhparam.pem 4096
  CREATED_WEBSITE=1
fi
# get some ssl cert info from existing nginx config
echo "- getting currently referenced SSL certificate and key"
line_ssl_certificate=$(nginx -T 2>&1 | grep "ssl_certificate " | sed -n 1p)
line_ssl_certificate_key=$(nginx -T 2>&1 | grep "ssl_certificate_key " | sed -n 1p)
# copy xslt templates
echo "- copying in Nodeyez XSLT templates"
cp /home/nodeyez/nodeyez/scripts/nginx/nodeyez*.xslt /etc/nginx/
# nodeyez config referencing our freshly minted self signed certs
echo "- copying in Nodeyez SSL config"
mkdir -p /etc/nginx/nodeyez
cp /home/nodeyez/nodeyez/scripts/nginx/nodeyez_ssl*.conf /etc/nginx/nodeyez
# enable xslt module if not already present
if [ $(cat /etc/nginx/modules-enabled/* | grep xslt | wc -l) -gt 0 ]; then
  echo "- XSLT module already loaded for NGINX"
else
  echo "- XSLT module being added by Nodeyez"
  cp /home/nodeyez/nodeyez/scripts/nginx/a_xslt.conf /etc/nginx/modules-enabled/a_xslt.conf
  CREATED_WEBSITE=1
fi
# assign back first cert and key if detected from earlier
if [ ${#line_ssl_certificate} -gt 0 ]; then
  echo "- reassigning SSL Certificate and Key"
  rm /etc/nginx/nodeyez/nodeyez_ssl_cert_key.conf
  echo $line_ssl_certificate >> /etc/nginx/nodeyez/nodeyez_ssl_cert_key.conf
  echo $line_ssl_certificate_key >> /etc/nginx/nodeyez/nodeyez_ssl_cert_key.conf
  echo "- contents of /etc/nginx/nodeyez/nodeyez_ssl_cert_key.conf:"
  cat -n /etc/nginx/nodeyez/nodeyez_ssl_cert_key.conf
  CREATED_WEBSITE=1
fi
# custom config per environment
if [ $ISMYNODE -gt 0 ]; then
  echo "- copying Nodeyez site configuration specific to MyNodeBTC"
  # mynode uses its own ssl cert
  cp /home/nodeyez/nodeyez/scripts/nginx/https_nodeyez_mynode.conf /etc/nginx/sites-enabled/https_nodeyez.conf
  CREATED_WEBSITE=1
elif [ $ISRASPIBLITZ -gt 0 ]; then
  echo "- copying Nodeyez site configuration specific to Raspiblitz"
  # mynode uses its own ssl cert
  cp /home/nodeyez/nodeyez/scripts/nginx/https_nodeyez_raspiblitz.conf /etc/nginx/sites-enabled/https_nodeyez.conf
  CREATED_WEBSITE=1
elif [ $ISRASPIBOLT -gt 0 ]; then
  # ensure no sites-enabled
  if [ $(cat /etc/nginx/nginx.conf | grep -i "sites-enabled" | wc -l) -eq 0 ]; then
    # ensure streams-enabled
    if [ $(cat /etc/nginx/nginx.conf | grep -i "streams-enabled" | wc -l) -gt 0 ]; then
      echo "- copy Nodeyez http configuration specific to Raspibolt"
      cp /home/nodeyez/nodeyez/scripts/nginx/http_nodeyez_raspibolt.conf /etc/nginx/nodeyez/http_nodeyez_raspibolt.conf
      if [ ! -f "/etc/nginx/modules-enabled/http_nodeyez_raspibolt.conf" ]; then
        ln -s /etc/nginx/nodeyez/http_nodeyez_raspibolt.conf /etc/nginx/modules-enabled/http_nodeyez_raspibolt.conf
      fi
      echo "- copying Nodeyez stream configuration specific to Raspibolt"
      cp /home/nodeyez/nodeyez/scripts/nginx/https_nodeyez_raspibolt.conf /etc/nginx/streams-enabled/https_nodeyez_raspibolt.conf
      CREATED_WEBSITE=1
    fi
  fi
else
  # generic site config
  echo "- copying Nodeyez site configuration as generic sites-enabled"
  cp /home/nodeyez/nodeyez/scripts/nginx/https_nodeyez.conf /etc/nginx/sites-enabled/https_nodeyez.conf
  CREATED_WEBSITE=1
fi
# remove our xslt enabler if there is more then 1 line in modules loading it
if [ $(cat /etc/nginx/modules-enabled/* | grep xslt | wc -l) -gt 1 ]; then
  if [ -f "/etc/nginx/modules-enabled/a_xslt.conf" ]; then
    echo "- removing XSLT from Nodeyez as multiple lines load it"
    rm /etc/nginx/modules-enabled/a_xslt.conf
  CREATED_WEBSITE=1
  fi
fi

WEBURL=""
if [ $CREATED_WEBSITE -eq 1 ]; then
  # enable port 907 to the dashboard
  if [ $(ufw status | grep 907 | grep Nodeyez | wc -l) -eq 0 ]; then
    echo "granting port 907 via uncomplicated firewall to access"
    ufw allow 907 comment 'allow Nodeyez Dashboard HTTPS'
    ufw --force enable
  fi
  # restart nginx
  echo "restarting nginx"
  systemctl restart nginx
  # get weburl
  WEBURL=$(hostname -I | awk {'print "https://" $1 ":907"}')
fi

# TODO: Prompt for Bitcoin REST config
# TODO: Prompt for LND REST config

# Services
echo "================================================"
echo "SERVICES:"
echo "installing..."
cp /home/nodeyez/nodeyez/scripts/systemd/*.service /etc/systemd/system/
cp /home/nodeyez/nodeyez/scripts/systemd/nodeyez.conf /etc/nodeyez.conf
echo "removing or renaming any older services..."
# braiinspool -> miningpool-braiinspool
if [ -f "/etc/systemd/system/nodeyez-braiinspool.service" ]; then
  if [ $(systemctl is-enabled nodeyez-braiinspool) == "enabled" ]; then
    echo "- changing nodeyez-braiinspool to nodeyez-miningpool-braiinspool"
    systemctl enable nodeyez-miningpool-braiinspool
    if [ $(systemctl is-active nodeyez-braiinspool) == "active" ]; then
      systemctl stop nodeyez-braiinspool
      systemctl start nodeyez-miningpool-braiinspool
    fi
    systemctl disable nodeyez-braiinspool
  fi
  rm /etc/systemd/system/nodeyez-braiinspool.service
fi
# compassmininghardware [remove]
if [ -f "/etc/systemd/system/nodeyez-compassmininghardware.service" ]; then
  if [ $(systemctl is-enabled nodeyez-compassmininghardware) == "enabled" ]; then
    echo "- removing compassmininghardware service"
    if [ $(systemctl is-active nodeyez-compassmininghardware) == "active" ]; then
      systemctl stop nodeyez-compassmininghardware
    fi
    systemctl disable nodeyez-compassmininghardware
  fi
  rm /etc/systemd/system/nodeyez-compassmininghardware.service
fi
# f2pool -> miningpool-f2pool
if [ -f "/etc/systemd/system/nodeyez-f2pool.service" ]; then
  if [ $(systemctl is-enabled nodeyez-f2pool) == "enabled" ]; then
    echo "- changing nodeyez-f2pool to nodeyez-miningpool-f2pool"
    systemctl enable nodeyez-miningpool-f2pool
    if [ $(systemctl is-active nodeyez-f2pool) == "active" ]; then
      systemctl stop nodeyez-f2pool
      systemctl start nodeyez-miningpool-f2pool
    fi
    systemctl disable nodeyez-f2pool
  fi
  rm /etc/systemd/system/nodeyez-f2pool.service
fi
# ipaddress -> ipaddresses
if [ -f "/etc/systemd/system/nodeyez-ipaddress.service" ]; then
  if [ $(systemctl is-enabled nodeyez-ipaddress) == "enabled" ]; then
    echo "- changing nodeyez-ipaddress to nodeyez-ipaddresses"
    systemctl enable nodeyez-ipaddresses
    if [ $(systemctl is-active nodeyez-ipaddress) == "active" ]; then
      systemctl stop nodeyez-ipaddress
      systemctl start nodeyez-ipaddresses
    fi
    systemctl disable nodeyez-ipaddress
  fi
  rm /etc/systemd/system/nodeyez-ipaddress.service
fi
# mempoolblocks -> mempoolspace
if [ -f "/etc/systemd/system/nodeyez-mempoolblocks.service" ]; then
  if [ $(systemctl is-enabled nodeyez-mempoolblocks) == "enabled" ]; then
    echo "- changing nodeyez-mempoolblocks to nodeyez-mempoolspace"
    systemctl enable nodeyez-mempoolspace
    if [ $(systemctl is-active nodeyez-mempoolblocks) == "active" ]; then
      systemctl stop nodeyez-mempoolblocks
      systemctl start nodeyez-mempoolspace
    fi
    systemctl disable nodeyez-mempoolblocks
  fi
  rm /etc/systemd/system/nodeyez-mempoolblocks.service
fi
# minerbraiins [remove]
if [ -f "/etc/systemd/system/nodeyez-minerbraiins.service" ]; then
  if [ $(systemctl is-enabled nodeyez-minerbraiins) == "enabled" ]; then
    echo "- removing nodeyez-minerbraiins. you need to reconfigure using nodeyez-config"
    if [ $(systemctl is-active nodeyez-minerbraiins) == "active" ]; then
      systemctl stop nodeyez-minerbraiins
    fi
    systemctl disable nodeyez-minerbraiins
  fi
  rm /etc/systemd/system/nodeyez-minerbraiins.service
fi
# minermicrobt [remove]
if [ -f "/etc/systemd/system/nodeyez-minermicrobt.service" ]; then
  if [ $(systemctl is-enabled nodeyez-minermicrobt) == "enabled" ]; then
    echo "- removing nodeyez-minermicrobt. you need to reconfigure using nodeyez-config"
    if [ $(systemctl is-active nodeyez-minermicrobt) == "active" ]; then
      systemctl stop nodeyez-minermicrobt
    fi
    systemctl disable nodeyez-minermicrobt
  fi
  rm /etc/systemd/system/nodeyez-minermicrobt.service
fi
# ordinals -> inscriptionparser
if [ -f "/etc/systemd/system/nodeyez-ordinals.service" ]; then
  if [ $(systemctl is-enabled nodeyez-ordinals) == "enabled" ]; then
    echo "- changing nodeyez-ordinals to nodeyez-inscriptionparser"
    systemctl enable nodeyez-inscriptionparer
    if [ $(systemctl is-active nodeyez-ordinals) == "active" ]; then
      systemctl stop nodeyez-ordinals
      systemctl start nodeyez-inscriptionparser
    fi
    systemctl disable nodeyez-ordinals
  fi
  rm /etc/systemd/system/nodeyez-ordinals.service
fi
# rofstatus -> lndringoffire
if [ -f "/etc/systemd/system/nodeyez-rofstatus.service" ]; then
  if [ $(systemctl is-enabled nodeyez-rofstatus) == "enabled" ]; then
    echo "- changing nodeyez-rofstatus to nodeyez-lndringoffire. you will need to redefine rings using nodeyez-config"
    systemctl enable nodeyez-lndringoffire
    if [ $(systemctl is-active nodeyez-rofstatus) == "active" ]; then
      systemctl stop nodeyez-rofstatus
      systemctl start nodeyez-lndringoffire
    fi
    systemctl disable nodeyez-rofstatus
  fi
  rm /etc/systemd/system/nodeyez-rofstatus.service
fi
# satsperusd -> satsperfiatunit
if [ -f "/etc/systemd/system/nodeyez-satsperusd.service" ]; then
  if [ $(systemctl is-enabled nodeyez-satsperusd) == "enabled" ]; then
    echo "- changing nodeyez-satsperusd to nodeyez-satsperfiatunit"
    systemctl enable nodeyez-satsperfiatunit
    if [ $(systemctl is-active nodeyez-satsperusd) == "active" ]; then
      systemctl stop nodeyez-satsperusd
      systemctl start nodeyez-satsperfiatunit
    fi
    systemctl disable nodeyez-satsperusd
  fi
  rm /etc/systemd/system/nodeyez-satsperusd.service
fi
# slushpool -> miningpool-braiinspool
if [ -f "/etc/systemd/system/nodeyez-slushpool.service" ]; then
  if [ $(systemctl is-enabled nodeyez-slushpool) == "enabled" ]; then
    echo "- changing nodeyez-slushpool to nodeyez-miningpool-braiinspool"
    systemctl enable nodeyez-miningpool-braiinspool
    if [ $(systemctl is-active nodeyez-slushpool) == "active" ]; then
      systemctl stop nodeyez-slushpool
      systemctl start nodeyez-miningpool-braiinspool
    fi
    systemctl disable nodeyez-slushpool
  fi
  rm /etc/systemd/system/nodeyez-slushpool.service
fi

# Remove older images
rm /home/nodeyez/nodeyez/imageoutput/braiinspool.png 2>/dev/null
rm /home/nodeyez/nodeyez/imageoutput/f2pool.png 2>/dev/null
rm /home/nodeyez/nodeyez/imageoutput/ipaddress.png 2>/dev/null
rm /home/nodeyez/nodeyez/imageoutput/luxor-mining-hashrate*.png 2>/dev/null
rm /home/nodeyez/nodeyez/imageoutput/mempoolblocks.png 2>/dev/null
rm /home/nodeyez/nodeyez/imageoutput/minerbraiins*.png 2>/dev/null
rm /home/nodeyez/nodeyez/imageoutput/minermicrobt*.png 2>/dev/null
rm /home/nodeyez/nodeyez/imageoutput/ordinals.png 2>/dev/null
rm /home/nodeyez/nodeyez/imageoutput/rofstatus*.png 2>/dev/null
rm /home/nodeyez/nodeyez/imageoutput/satsperusd.png 2>/dev/null
rm /home/nodeyez/nodeyez/imageoutput/slushpool.png 2>/dev/null

# Initial services to enable and start
# - fearandgreed, fiatprice, ipaddresses, mempoolspace, satsperfiatunit, sysinfo, utcclock
if [ 1 -eq 1 ]; then
systemctl enable nodeyez-fearandgreed.service
systemctl start nodeyez-fearandgreed.service
systemctl enable nodeyez-fiatprice.service
systemctl start nodeyez-fiatprice.service
systemctl enable nodeyez-ipaddresses.service
systemctl start nodeyez-ipaddresses.service
systemctl enable nodeyez-mempoolspace.service
systemctl start nodeyez-mempoolspace.service
systemctl enable nodeyez-satsperfiatunit.service
systemctl start nodeyez-satsperfiatunit.service
systemctl enable nodeyez-sysinfo.service
systemctl start nodeyez-sysinfo.service
systemctl enable nodeyez-utcclock.service
systemctl start nodeyez-utcclock.service
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
echo "================================================"
echo "CONFIGURATION TOOL:"
UPDATED_CONFIGTOOL=0
if [ -f "/usr/local/bin/nodeyez-config" ]; then
  echo "updating..."
  UPDATED_CONFIGTOOL=1
else
  echo "installing..."
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
echo ""
if [ $UPDATED_CONFIGTOOL -ge 1 ]; then
  echo "Nodeyez configuration tool updated. Run it with: sudo nodeyez-config"
else
  echo "Nodeyez configuration tool installed. Run it with: sudo nodeyez-config"
fi
echo ""
echo "The nodeyez-config tool can help you quickly setup Bitcoin and LND profiles,"
echo "review and toggle services that generate images, and set the configuration"
echo "for those services. Nodeyez panels that require some form of authentication"
echo "such as api keys, usernames and passwords need to be configured before"
echo "running those services. Those that call Bitcoin and LND nodes will use the"
echo "active profile or named profiles that you define using the nodeyez-config tool."
# raspberry pi guidance
if [ $RASPBERRYPI -ge 1 ]; then
  echo ""
  echo "You appear to be running a Raspbery Pi."
  echo "If you want to attach an LCD or DSI screen, be sure to follow the steps at"
  echo "   https://nodeyez.com/install_steps/2displayscreen"
  echo "For convenience, the framebuffer imageviewer tool has already been installed."
fi