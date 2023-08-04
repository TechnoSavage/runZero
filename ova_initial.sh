#!/bin/bash

#Check for root privileges, exit if not run as root
if [[ $(id -u) != 0 ]]; then
    cat << EOM

This script must be run as root!
Please rerun with sudo e.g.
sudo ./initial-setup.sh

EOM
exit 1

else
    echo "Beginning initial setup..."
fi

#clear old IP addresses from interface enp0s3 and assign new IP
while [ -z "$DHCP" ]; do 
    read -p "Will this machine receive an IP address via DHCP?[y/n]: " DHCP
DHCP=$( echo $DHCP | tr '[:upper:]' '[:lower:]' )
case $DHCP in
    y | yes)    ip a flush dev enp0s3
                dhclient enp0s3
                ;;
    n | no)     read -p "Enter the IP address for this machine in CIDR notation: " NEWIP
                ip a flush dev enp0s3
                ip a add $NEWIP dev enp0s3    
                ;;
    *)          echo 'That is not a valid input, please rerun "sudo ./ova_intial.sh" and type "y" or "n" as appropriate.'
                exit 1
                ;;
esac

#Account API Key
AKEY='CTE2972652D7FFBC0CEA9A67CDBE77'
#Organization API key
OKEY='OTC78B57A7C1DA8DC30AE86D2D5E65'
#Download Token
DKEY='DT521F823BCD680C8FA8C281F1C7B6'
#Determine console IP address
CONSOLE=$(ip a | grep -i enp0s3 | grep -i inet | grep -E -o "([0-9]{1,3}[\.]){3}[0-9]{1,3}[\/]{1}" | sed 's/\///')
#SUBNET=$(ip a | grep -i enp0s3 | grep -i inet | grep -E -o "([0-9]{1,3}[\.]){3}[0-9]{1,3}[\/]{1}[0-9]{1,2}" | sed 's/\.[0-9]*\//\.0\//')

#Update console IP in /etc/rumble/config
sed -i "s/\(^RUNZERO_CONSOLE=https:\/\/\).*/RUNZERO_CONSOLE=https:\/\/$CONSOLE:443/" /etc/rumble/config

#Regenerate TLS certs for new IP
rm /etc/rumble/certs/cert.pem /etc/rumble/certs/key.pem
rumblectl generate-certificate

#restart runZero service
rumblectl restart

#Download fresh explorer
rm ruzero-explorer.bin
curl -f -o runzero-explorer.bin https://$CONSOLE:443/download/explorer/DT521F823BCD680C8FA8C281F1C7B6/64cc3552/runzero-explorer-linux-amd64.bin -k
#Install explorer
chmod u+x runzero-explorer.bin
./runzero-explorer.bin

echo "Log into the runZero console at https://$CONSOLE with username admin@test.org and password CaqGeFE+5X+PXnR6"

# echo "Creating initial superuser account..."
# read -p "Enter superuser email: " supemail
# echo "Creating initial superuser account with email $supemail..."
# init_out=$(rumblectl initial $supemail)
# pass=$(cat $init_out | cut -d ' ' -f 14)
# echo $pass