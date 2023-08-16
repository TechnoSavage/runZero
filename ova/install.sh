#!/bin/bash

#Check for root privileges, exit if not run as root user
if [[ $(id -u) != 0 ]]; then
    cat << EOM

This script must be run as root!
Please rerun with sudo e.g.
sudo ./install.sh

EOM
exit 1

else
    echo "Beginning initial setup..."
fi

#Install runzero platform using only distro packages
./rumble-platform.bin install --distro-packages-only
#Update the console (if needed)
rumblectl update
#Prompt user for an email to use for the initial superuser account
read -p "\nEnter the email for the initial superuser account: " ACCOUNT
#Initialize the superuser; this will also print the initial login password
rumblectl initial $ACCOUNT


