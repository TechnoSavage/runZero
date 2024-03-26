#!/bin/bash -x

#Check for root privileges, exit if not run as root user
if [[ $(id -u) != 0 ]]; then
    cat << EOM

This script must be run as root!
Please rerun with sudo e.g.
sudo ./explorer.sh

EOM
exit 1

dltok=
console='console.runzero.com'
bin='runzero-explorer-linux-amd64'
curl -f -o runzero-explorer.bin "https://$console/download/explorer/$dltok/rzer0123/$bin"
chmod + x runzero-explorer.bin
./runzero-explorer.bin