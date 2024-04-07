#!/bin/bash -x

#Check for root privileges, exit if not run as root user
if [[ $(id -u) != 0 ]]; then
    cat << EOM

This script must be run as root!
Please rerun with sudo e.g.
sudo ./backup_r0_database.sh

EOM
exit 1
else
    echo "Beginning backup..."
fi

tar zcvf runzero-backup-fs.tar.gz /etc/runzero/ /opt/runzero/ /lib/systemd/system/runzero-console.service /etc/systemd/system/multi-user.target.wants/runzero-console.service /usr/bin/runzeroctl
su -c "pg_dumpall -f /var/lib/postgresql/runzero.sql && gzip /var/lib/postgresql/runzero.sql" postgres
mv /var/lib/postgresql/runzero.sql.gz $(pwd)

echo "Backup complete!"