#!/bin/bash -x

#Check for root privileges, exit if not run as root user
if [[ $(id -u) != 0 ]]; then
    cat << EOM

This script must be run as root!
Please rerun with sudo e.g.
sudo ./explorer.sh

EOM
exit 1
else
    echo "Beginning backup..."
fi

tar zcvf runzero-backup-fs.tar.gz /etc/runzero/ /opt/runzero/ /lib/systemd/system/runzero-console.service /etc/systemd/system/multi-user.target.wants/runzero-console.service /usr/bin/runzeroctl
su - postgres
pg_dumpall -f runzero.sql && gzip runzero.sql

echo "Backup complete!"