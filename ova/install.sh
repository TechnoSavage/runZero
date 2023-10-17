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
    echo "Beginning installation..."
fi

#Install runzero platform in offline mode using only distro packages
/home/runzero/runzero-platform.bin install --offline --distro-packages-only
# Update the console (if needed)
# For platform binaries prior to 4.0 use 'rumblectl update' instead
#runzeroctl update
# Prompt user for an email to use for the initial superuser account
read -p "Enter the email for the initial superuser account: " ACCOUNT
# Initialize the superuser; this will also print the initial login password
# For platform binaries prior to 4.0 use 'rumblectl initial $ACCOUNT' instead
runzeroctl initial $ACCOUNT


