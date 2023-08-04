#!/bin/bash

#Check for root privileges, exit if not run as root user
if [[ $(id -u) != 0 ]]; then
    cat << EOM

This script must be run as root!
Please rerun with sudo e.g.
sudo ./ova_intial.sh

EOM
exit 1

else
    echo "Beginning initial setup..."
fi

USERNAME='admin@test.org'    #These creds mean nothing
PASSWORD='CaqGeFE+5X+PXnR6'  

#Get interface name (different virtualization platforms change the interface name; this retrieves the non-loopback interface)
INTERFACE=$(ip a | grep -i ^[1-9]\: | grep -v lo\: | cut -d ' ' -f 2 | sed s/\://)

#Clear old IP addresses from interface and assign new IP
while [ -z "$DHCP" ]; do 
    read -p "Will this appliance receive an IP address via DHCP? [y/n]: " DHCP
done
DHCP=$( echo $DHCP | tr '[:upper:]' '[:lower:]' )
case $DHCP in
    y | yes)    ip a flush dev $INTERFACE
                dhclient $INTERFACE
                ;;
    n | no)     read -p "Enter the IP address for this machine with CIDR notation: " NEWIP
                ip a flush dev $INTERFACE
                ip a add $NEWIP dev $INTERFACE 
                ;;
    *)          echo 'That is not a valid input, please rerun and type "y" or "n" as appropriate.'
                exit 1
                ;;
esac

#Account API Key
AKEY='CTE2972652D7FFBC0CEA9A67CDBE77' #These keys also mean nothing...sorry
#Organization API key
OKEY='OTC78B57A7C1DA8DC30AE86D2D5E65'
#Download Token
DKEY='DT521F823BCD680C8FA8C281F1C7B6'
#Determine console IP address
CONSOLE=$(ip a | grep -i $INTERFACE | grep -i inet | grep -E -o "([0-9]{1,3}[\.]){3}[0-9]{1,3}[\/]{1}" | sed 's/\///')

#Update console IP in /etc/rumble/config
sed -i "s/\(^RUNZERO_CONSOLE=https:\/\/\).*/RUNZERO_CONSOLE=https:\/\/$CONSOLE:443/" /etc/rumble/config

#Regenerate TLS certs
rm /etc/rumble/certs/cert.pem /etc/rumble/certs/key.pem
rumblectl generate-certificate

#Restart runZero service
rumblectl restart

#Download fresh explorer
rm ruzero-explorer.bin
curl -f -o runzero-explorer.bin https://$CONSOLE:443/download/explorer/DT521F823BCD680C8FA8C281F1C7B6/64cc3552/runzero-explorer-linux-amd64.bin -k
#Install explorer
chmod u+x runzero-explorer.bin
./runzero-explorer.bin

echo -e "\nYou may now log into the runZero console at https://$CONSOLE with username $USERNAME and password $PASSWORD\n"


#Half-baked ideas and unneeded lines below:

#SUBNET=$(ip a | grep -i $INTERFACE | grep -i inet | grep -E -o "([0-9]{1,3}[\.]){3}[0-9]{1,3}[\/]{1}[0-9]{1,2}" | sed 's/\.[0-9]*\//\.0\//')

# echo "Creating initial superuser account..."
# read -p "Enter superuser email: " supemail
# echo "Creating initial superuser account with email $supemail..."
# init_out=$(rumblectl initial $supemail)
# pass=$(cat $init_out | cut -d ' ' -f 14)
# echo $pass