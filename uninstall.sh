#!/usr/bin/env bash

prompt_delete() {
  result=$OK_TO_DELETE
  if [ $PROMPT_ALL -eq 1 ]; then
    read -p "$1" promptresponse
    case "$promptresponse" in
      y|Y) result=1;;
      *) result=0;;
    esac
  fi
  echo "$result"
}

# Check that the script is started as root
if [ "$EUID" -ne 0 ]; then 
  echo "Please run as root or with sudo as follows"
  echo "   sudo bash /home/nodeyez/nodeyez/uninstall.sh"
  exit
fi

OK_TO_DELETE=0
if [[ "$NODEYEZ_DELETE_CONFIRM" == "YES" ]]; then
  OK_TO_DELETE=1
fi
if [ "$OK_TO_DELETE" -eq 0 ]; then
  echo "This script is for convenience to allow you to delete Nodeyez"
  echo "including not only its scripts and service definitions, but"
  echo "also the Nodeyez user, custom configuration, downloaded data,"
  echo "generated images and more."
  echo ""
  echo "If you want to make a backup of your configuration, data and"
  echo "images first, consider using the following command after"
  echo "cancelling this operation."
  echo "   tar -cvf /backup-of-nodeyez-`date +%Y%m%d`.tar /home/nodeyez/nodeyez{config,data,imageoutput}"
  echo ""
  read -p "Are you sure you want to uninstall Nodeyez?" promptresponse
  case "$promptresponse" in
    y|Y) OK_TO_DELETE=1;;
    *) OK_TO_DELETE=0;;
  esac
fi
if [ "$OK_TO_DELETE" -eq 0 ]; then
  echo "cancelling"
  exit
fi
PROMPT_ALL=1
if [[ "$NODEYEZ_DELETE_PROMPT" == "NO" ]]; then
  PROMPT_ALL=0
fi

# Nodeyez uninstall script
HAS_SERVICES=0
HAS_ENV=0
HAS_WEBSITE=0
HAS_UFWRULES=0
HAS_SELFCERT=0
HAS_USER=0
HAS_CONFIGTOOL=0
DELETED_SERVICES=0
DELETED_ENV=0
DELETED_WEBSITE=0
DELETED_UFWRULES=0
DELETED_SELFCERT=0
DELETED_USER=0
DELETED_CONFIGTOOL=0

# Remove Nodeyez services
systemctl reset-failed nodeyez*
HAS_SERVICES=$(systemctl --type=service | grep nodeyez | sed -n 1p | wc -l)
if [ $HAS_SERVICES -ge 1 ]; then
  section_delete=$(prompt_delete "Delete all Nodeyez services?")
  if [ "$section_delete" -eq 1 ]; then
    echo "- stopping and disabling services"
    for f in $(systemctl list-unit-files --type=service | grep nodeyez | awk '{print $1}'); do systemctl stop $f; systemctl disable $f; done
    # - service files
    if [ $(ls -la /etc/systemd/system | grep nodeyez | wc -l) -gt 0 ]; then
      echo "- deleting nodeyez service definitions"
      rm /etc/systemd/system/nodeyez-*.service
      DELETED_SERVICES=1
    fi
    # - environment file
    if [ -f "/etc/nodeyez.conf" ]; then
      HAS_ENV=1
      echo "- deleting nodeyez environment file"
      rm /etc/nodeyez.conf
      DELETED_ENV=1
    fi
  fi
fi

# Remove Nodeyez dashboard
if [ $(which nginx | wc -l) -gt 0 ]; then
  # nginx is installed, check for config
  if [ -d "/etc/nginx/nodeyez" ]; then
    section_delete=$(prompt_delete "Delete the Nodeyez Dashboard (website)?")
    if [ "$section_delete" -eq 1 ]; then
      # check for our xslt module enabler
      if [ -f "/etc/nginx/modules-enabled/a_xslt.conf" ]; then
        HAS_WEBSITE=1
        echo "- deleting custom xslt module enabler"
        rm /etc/nginx/modules-enabled/a_xslt.conf
      fi
      # check for our templates
      if [ $(ls -la /etc/nginx/ | grep xslt | grep nodeyez | wc -l) -gt 0 ]; then
        HAS_WEBSITE=1
        echo "- deleting nodeyez templates"
        rm /etc/nginx/nodeyez*.xslt
      fi    
      if [ -f "/etc/nginx/dirlistblack.xslt" ]; then
        HAS_WEBSITE=1
        echo "- deleting dirlistblack.xslt"
        rm /etc/nginx/dirlistblack.xslt
      fi
      if [ -f "/etc/nginx/imagegallery.xslt" ]; then
        HAS_WEBSITE=1
        echo "- deleting imagegallery.xslt"
        rm /etc/nginx/imagegallery.xslt
      fi
      if [ -f "/etc/nginx/imagegallery128.xslt" ]; then
        HAS_WEBSITE=1
        echo "- deleting imagegallery128.xslt"
        rm /etc/nginx/imagegallery128.xslt
      fi
      # check for our nodeyez conf folder
      if [ -d "/etc/nginx/nodeyez" ]; then
        HAS_WEBSITE=1
        echo "- deleting nginx nodeyez folder"
        rm -rf /etc/nginx/nodeyez
      fi
      # check if using sites-enabled (generic, mynode, raspiblitz)
      if [ -f "/etc/nginx/sites-enabled/https_nodeyez.conf" ]; then
        HAS_WEBSITE=1
        echo "- removing nodeyez from nginx sites-enabled"
        rm /etc/nginx/sites-enabled/https_nodeyez.conf
        DELETED_WEBSITE=1
      fi
      # check if using streams-enabled
      if [ -f "/etc/nginx/streams-enabled/https_nodeyez_raspibolt.conf" ]; then
        HAS_WEBSITE=1
        echo "- removing nodeyez from nginx streams-enabled"
        rm /etc/nginx/streams-enabled/https_nodeyez_raspibolt.conf
        DELETED_WEBSITE=1
      fi
      # check for http for raspibolt in  modules-enabled
      if [ -f "/etc/nginx/modules-enabled/http_nodeyez_raspibolt.conf" ]; then
        HAS_WEBSITE=1
        echo "- removing link for nodeyez raspibolt conf in modules-enabled"
        unlink /etc/nginx/modules-enabled/http_nodeyez_raspibolt.conf
        DELETED_WEBSITE=1
      fi
      # remove any lines from nginx.conf that reference http_nodeyez_raspibolt.conf
      nginx_reference_nodeyez_for_raspibolt=$(cat /etc/nginx/nginx.conf | grep http_nodeyez_raspibolt | wc -l)
      if [ $nginx_reference_nodeyez_for_raspibolt -gt 0 ]; then
        HAS_WEBSITE=1
        echo "- removing any lines in nginx.conf that reference http_nodeyez_raspibolt"
        sed -i '/http_nodeyez_raspibolt/d' /etc/nginx/nginx.conf
      fi
      # reload nginx
      if [ $DELETED_WEBSITE -gt 0 ]; then
        echo "- restarting nginx"
        systemctl reload nginx
      fi
    fi
  fi
fi

# Remove uncomplicated firewall rules with Nodeyez comments
if [ $(ufw status | grep Nodeyez | wc -l) -gt 0 ]; then
  section_delete=$(prompt_delete "Delete firewall rules for Nodeyez?")
  if [ "$section_delete" -eq 1 ]; then
    HAS_UFWRULES=1
    echo "- removing uncomplicated firewall rules that reference Nodeyez"
    for n in $(ufw status numbered | grep Nodeyez | awk '{print $2}' | sed 's/]//' | sort -r); do ufw --force delete $n; done
    DELETED_UFWRULES=1
  fi
fi

# Remove Nodeyez self-signed cert
if [ -f "/etc/ssl/certs/nodeyez-nginx-selfsigned.crt" ]; then
  HAS_SELFCERT=1
fi
if [ -f "/etc/ssl/private/nodeyez-nginx-selfsigned.key" ]; then
  HAS_SELFCERT=1
fi
if [ $HAS_SELFCERT -ge 1 ]; then
  section_delete=$(prompt_delete "Delete self-signed certificate?")
  if [ "$section_delete" -eq 1 ]; then
    if [ -f "/etc/ssl/certs/nodeyez-nginx-selfsigned.crt" ]; then
      echo "- removing public self-signed certificate file"
      rm /etc/ssl/certs/nodeyez-nginx-selfsigned.crt
      DELETED_SELFCERT=1
    fi
    if [ -f "/etc/ssl/private/nodeyez-nginx-selfsigned.key" ]; then
      echo "- removing private key for self-signed certificate"
      rm /etc/ssl/private/nodeyez-nginx-selfsigned.key
      DELETED_SELFCERT=1
    fi
  fi
fi

# Remove Nodeyez user
if id nodeyez &>/dev/null; then
  HAS_USER=1
  section_delete=$(prompt_delete "Delete the Nodeyez user, downloaded data and configs?")
  if [ "$section_delete" -eq 1 ]; then
    DRIVECOUNT=$(df -t ext4 | grep / | awk '{print $6}' | sort | wc -l)
    ISMMC=$(findmnt -n -o SOURCE --target /home | grep "mmcblk" | wc -l)
    if [ $DRIVECOUNT -gt 1 ] && [ $ISMMC -gt 0 ]; then
      EXT_DRIVE_MOUNT=$(df -t ext4 | grep / | awk '{print $6}' | sort | sed -n 2p)
    fi
    if [ -z ${EXT_DRIVE_MOUNT+x} ]; then
      echo "- deleting Nodeyez user and home folder"
      deluser --remove-home nodeyez
    else
      echo "- deleting Nodeyez user and home folder mapped to external drive"
      deluser --remove-home nodeyez
      echo "- removing link for /home/nodeyez to external drive"
      unlink /home/nodeyez
    fi
    DELETED_USER=1
  fi
fi

# Remove Nodeyez configuration tool
if [ -f "/usr/local/bin/nodeyez-config" ]; then
  HAS_CONFIGTOOL=1
  section_delete=$(prompt_delete "Delete the nodeyez-config tool?")
  if [ "$section_delete" -eq 1 ]; then
    echo "- removing nodeyez-config tool"
    rm /usr/local/bin/nodeyez-config
    DELETED_CONFIGTOOL=1
  fi
fi

# show summary
echo "================================================"
echo "SUMMARY:"
if [ $HAS_SERVICES -ge 1 ]; then
  if [ $DELETED_SERVICES -ge 1 ]; then
    echo "Nodeyez services removed"
  else
    echo "Nodeyez services were found, but deletion was skipped"
  fi
fi
if [ $(systemctl list-units --type=service | grep nodeyez | wc -l) -ge 1 ]; then
  echo "Remaining Nodeyez services"
  systemctl list-units --type=service --state=active | grep nodeyez | awk '{print "(active) " $1}'
  systemctl list-units --type=service --state=failed | grep nodeyez | awk '{print "(failed) " $2}'
else
  echo "No services for Nodeyez were found"
fi
if [ $HAS_ENV -ge 1 ]; then
  if [ $DELETED_ENV -ge 1 ]; then
    echo "Nodeyez environment variables for services removed"
  else
    echo "Nodeyez environment variables for services was found, but deletion was skipped"
  fi
else
  echo "No environment variables file for Nodeyez was found"
fi
if [ $HAS_WEBSITE -ge 1 ]; then
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
  else
    echo "Nodeyez website dashboard was found, but deletion was skipped"
  fi
else
  echo "No website dashboard for Nodeyez was found"
fi
if [ $HAS_UFWRULES -ge 1 ]; then
  if [ $DELETED_UFWRULES -ge 1 ]; then
    echo "Nodeyez uncomplicated firewall rules for port 907 removed"
  else
    echo "Nodeyez uncomplicated firewall rules was found, but deletion was skipped"
  fi
else
  echo "No uncomplicated firewall rules for Nodeyez were found"
fi
if [ $HAS_SELFCERT -ge 1 ]; then
  if [ $DELETED_SELFCERT -ge 1 ]; then
    echo "Nodeyez self-signed certificates removed"
  else
    echo "Nodeyez self-signed certificates were found, but deletion was skipped"
  fi
else
  echo "No self-signed certificates for Nodeyez were found"
fi
if [ $HAS_USER -ge 1 ]; then
  if [ $DELETED_USER -ge 1 ]; then
    echo "Nodeyez user deleted"
  else
    echo "Nodeyez user was found, but deletion was skipped"
  fi
else
  echo "No user for Nodeyez was found"
fi
if [ $HAS_CONFIGTOOL -ge 1 ]; then
  if [ $DELETED_CONFIGTOOL -ge 1 ]; then
    echo "Nodeyez configuration tool deleted"
  else
    echo "Nodeyez configuration tool was found, but deletion was skipped"
  fi
else
  echo "No nodeyez-config tool was found"
fi

