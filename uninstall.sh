#!/usr/bin/env bash

# Nodeyez uninstall script
DELETED_SERVICES=0
DELETED_ENV=0
DELETED_WEBSITE=0
DELETED_UFWRULES=0
DELETED_SELFCERT=0
DELETED_USER=0

# Remove Nodeyez services
for f in $(systemctl list-unit-files --type=service | grep nodeyez | awk '{print $1}'); do sudo systemctl stop $f; sudo systemctl disable $f; done
# - service files
if [ $(sudo ls -la /etc/systemd/system | grep nodeyez | wc -l) -gt 0 ]; then
  sudo rm /etc/systemd/system/nodeyez-*.service
  DELETED_SERVICES=1
fi
# - environment file
if [ -f "/etc/nodeyez.conf" ]; then
  sudo rm /etc/nodeyez.conf
  DELETED_ENV=1
fi

# Remove Nodeyez dashboard
if [ $(which nginx | wc -l) -gt 0 ]; then
  # nginx is installed
  # check for our xslt module enabler
  if [ -f "/etc/nginx/modules-enabled/a_xslt.conf" ]; then
    sudo rm /etc/nginx/modules-enabled/a_xslt.conf
  fi
  # check for our templates
  if [ $(sudo ls -la /etc/nginx/ | grep xslt | grep nodeyez | wc -l) -gt 0 ]; then
    sudo rm /etc/nginx/nodeyez*.xslt
  fi    
  if [ -f "/etc/nginx/dirlistblack.xslt" ]; then
    sudo rm /etc/nginx/dirlistblack.xslt
  fi
  if [ -f "/etc/nginx/imagegallery.xslt" ]; then
    sudo rm /etc/nginx/imagegallery.xslt
  fi
  if [ -f "/etc/nginx/imagegallery128.xslt" ]; then
    sudo rm /etc/nginx/imagegallery128.xslt
  fi
  # check for our nodeyez conf folder
  if [ -d "/etc/nginx/nodeyez" ]; then
    sudo rm -rf /etc/nginx/nodeyez
  fi
  # check if using sites-enabled
  if [ -f "/etc/nginx/sites-enabled/https_nodeyez.conf" ]; then
    sudo rm /etc/nginx/sites-enabled/https_nodeyez.conf
    sudo systemctl restart nginx
    DELETED_WEBSITE=1
  fi
fi

# Remove uncomplicated firewall rules with Nodeyez comments
if [ $(sudo ufw status | grep Nodeyez | wc -l) -gt 0 ]; then
  for n in $(sudo ufw status numbered | grep Nodeyez | awk '{print $2}' | sed 's/]//' | sort -r); do sudo ufw --force delete $n; done
  DELETED_UFWRULES=1
fi

# Remove Nodeyez self-signed cert
if [ -f "/etc/ssl/certs/nodeyez-nginx-selfsigned.crt" ]; then
  sudo rm /etc/ssl/certs/nodeyez-nginx-selfsigned.crt
  DELETED_SELFCERT=1
fi
if [ -f "/etc/ssl/private/nodeyez-nginx-selfsigned.key" ]; then
  sudo rm /etc/ssl/private/nodeyez-nginx-selfsigned.key
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
    sudo deluser --remove-home nodeyez
  else
    NODEYEZ_HOME=${EXT_DRIVE_MOUNT}/nodeyez
    sudo rm ${NODEYEZ_HOME}
    sudo deluser --remove-home nodeyez
  fi
  DELETED_USER=1
fi

# show summary
echo "================================================"
echo "SUMMARY:"
if [ $DELETED_SERVICES -ge 1 ]; then
  echo "Nodeyez services removed"
fi
if [ $(sudo systemctl list-units --type=service | grep nodeyez | wc -l) -ge 1 ]; then
  echo "Remaining services"
  sudo systemctl list-units --type=service --state=active | grep nodeyez | awk '{print "(active) " $1}'
  sudo systemctl list-units --type=service --state=failed | grep nodeyez | awk '{print "(failed) " $2}'
fi
if [ $DELETED_ENV -ge 1 ]; then
  echo "Nodeyez environment variables for services removed"
fi
if [ $DELETED_WEBSITE -ge 1 ]; then
  echo "Website deleted"
fi
if [ $DELETED_UFWRULES -ge 1 ]; then
  echo "Uncomplicated Firewall Rules for Nodeyez removed"
fi
if [ $DELETED_SELFCERT -ge 1 ]; then
  echo "Nodeyez self-signed certificates removed"
fi
if [ $DELETED_USER -ge 1 ]; then
  echo "Nodeyez user deleted"
fi
echo "Uninstallation complete"
