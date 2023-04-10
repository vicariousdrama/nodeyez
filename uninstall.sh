#!/usr/bin/env bash

# Check that the scritp is started as root
if [ "$EUID" -ne 0 ]; then 
  echo "Please run as root or with sudo as follows"
  echo "wget -qO- https://nodeyez.com/uninstall.sh | sudo bash"
  exit
fi

# Nodeyez uninstall script
DELETED_SERVICES=0
DELETED_ENV=0
DELETED_WEBSITE=0
DELETED_UFWRULES=0
DELETED_SELFCERT=0
DELETED_USER=0
DELETED_CONFIGTOOL=0

# Remove Nodeyez services
for f in $(systemctl list-unit-files --type=service | grep nodeyez | awk '{print $1}'); do systemctl stop $f; systemctl disable $f; done
# - service files
if [ $(ls -la /etc/systemd/system | grep nodeyez | wc -l) -gt 0 ]; then
  rm /etc/systemd/system/nodeyez-*.service
  DELETED_SERVICES=1
fi
# - environment file
if [ -f "/etc/nodeyez.conf" ]; then
  rm /etc/nodeyez.conf
  DELETED_ENV=1
fi

# Remove Nodeyez dashboard
if [ $(which nginx | wc -l) -gt 0 ]; then
  # nginx is installed
  # check for our xslt module enabler
  if [ -f "/etc/nginx/modules-enabled/a_xslt.conf" ]; then
    rm /etc/nginx/modules-enabled/a_xslt.conf
  fi
  # check for our templates
  if [ $(ls -la /etc/nginx/ | grep xslt | grep nodeyez | wc -l) -gt 0 ]; then
    rm /etc/nginx/nodeyez*.xslt
  fi    
  if [ -f "/etc/nginx/dirlistblack.xslt" ]; then
    rm /etc/nginx/dirlistblack.xslt
  fi
  if [ -f "/etc/nginx/imagegallery.xslt" ]; then
    rm /etc/nginx/imagegallery.xslt
  fi
  if [ -f "/etc/nginx/imagegallery128.xslt" ]; then
    rm /etc/nginx/imagegallery128.xslt
  fi
  # check for our nodeyez conf folder
  if [ -d "/etc/nginx/nodeyez" ]; then
    rm -rf /etc/nginx/nodeyez
  fi
  # check if using sites-enabled (generic, mynode, raspiblitz)
  if [ -f "/etc/nginx/sites-enabled/https_nodeyez.conf" ]; then
    rm /etc/nginx/sites-enabled/https_nodeyez.conf
    DELETED_WEBSITE=1
  fi
  # check if using streams-enabled
  if [ -f "/etc/nginx/streams-enabled/https_nodeyez_raspibolt.conf" ]; then
    rm /etc/nginx/streams-enabled/https_nodeyez_raspibolt.conf
    DELETED_WEBSITE=1
  fi
  # check for http for raspibolt in  modules-enabled
  if [ -f "/etc/nginx/modules-enabled/http_nodeyez_raspibolt.conf" ]; then
    unlink /etc/nginx/modules-enabled/http_nodeyez_raspibolt.conf
    DELETED_WEBSITE=1
  fi
  # remove any lines from nginx.conf that reference http_nodeyez_raspibolt.conf
  sed -i '/http_nodeyez_raspibolt/d' /etc/nginx/nginx.conf
  # reload nginx
  if [ $DELETED_WEBSITE -gt 0 ]; then
    systemctl reload nginx
  fi
fi

# Remove uncomplicated firewall rules with Nodeyez comments
if [ $(ufw status | grep Nodeyez | wc -l) -gt 0 ]; then
  for n in $(ufw status numbered | grep Nodeyez | awk '{print $2}' | sed 's/]//' | sort -r); do ufw --force delete $n; done
  DELETED_UFWRULES=1
fi

# Remove Nodeyez self-signed cert
if [ -f "/etc/ssl/certs/nodeyez-nginx-selfsigned.crt" ]; then
  rm /etc/ssl/certs/nodeyez-nginx-selfsigned.crt
  DELETED_SELFCERT=1
fi
if [ -f "/etc/ssl/private/nodeyez-nginx-selfsigned.key" ]; then
  rm /etc/ssl/private/nodeyez-nginx-selfsigned.key
  DELETED_SELFCERT=1
fi

# Remove Nodeyez user
if id nodeyez &>/dev/null; then
  DRIVECOUNT=$(df -t ext4 | grep / | awk '{print $6}' | sort | wc -l)
  ISMMC=$(findmnt -n -o SOURCE --target /home | grep "mmcblk" | wc -l)
  if [ $DRIVECOUNT -gt 1 ] && [ $ISMMC -gt 0 ]; then
    EXT_DRIVE_MOUNT=$(df -t ext4 | grep / | awk '{print $6}' | sort | sed -n 2p)
  fi
  if [ -z ${EXT_DRIVE_MOUNT+x} ]; then
    deluser --remove-home nodeyez
  else
    deluser --remove-home nodeyez
    unlink /home/nodeyez
  fi
  DELETED_USER=1
fi

# Remove Nodeyez configuration tool
if [ -f "/usr/local/bin/nodeyez-config" ]; then
  rm /usr/local/bin/nodeyez-config
  DELETED_CONFIGTOOL=1
fi

# show summary
echo "================================================"
echo "SUMMARY:"
if [ $DELETED_SERVICES -ge 1 ]; then
  echo "Nodeyez services removed"
fi
if [ $(systemctl list-units --type=service | grep nodeyez | wc -l) -ge 1 ]; then
  echo "Remaining services"
  systemctl list-units --type=service --state=active | grep nodeyez | awk '{print "(active) " $1}'
  systemctl list-units --type=service --state=failed | grep nodeyez | awk '{print "(failed) " $2}'
fi
if [ $DELETED_ENV -ge 1 ]; then
  echo "Nodeyez environment variables for services removed"
fi
if [ $DELETED_WEBSITE -ge 1 ]; then
  echo "Nodeyez website deleted"
  echo "NGINX is still installed"
  if [ $(nginx -T 2>/dev/null | grep "listen" | grep -v "#" | xargs | wc -l) -gt 0 ]; then
    echo "Listening ports of remaining sites"
    nginx -T 2>/dev/null | grep "listen" | grep -v "#" | xargs
  else
    echo "No 'listen' directives found in nginx configuration"
  fi
  echo "If you have no other websites you can remove via"
  echo "     sudo apt-get -y purge nginx nginx-common"
fi
if [ $DELETED_UFWRULES -ge 1 ]; then
  echo "Nodeyez uncomplicated firewall rules for port 907 removed"
fi
if [ $DELETED_SELFCERT -ge 1 ]; then
  echo "Nodeyez self-signed certificates removed"
fi
if [ $DELETED_USER -ge 1 ]; then
  echo "Nodeyez user deleted"
fi
if [ $DELETED_CONFIGTOOL -ge 1 ]; then
  echo "Nodeyez configuration tool deleted"
fi
echo "Uninstallation complete"