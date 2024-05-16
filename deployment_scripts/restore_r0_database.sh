#!/bin/bash -x

PROGNAME=$(basename $0)

#Check for root privileges, exit if not run as root user
if [[ $(id -u) != 0 ]]; then
    cat << EOM

This script must be run as root!
Please rerun with sudo e.g.
sudo ./$PROGNAME

EOM
exit 1
else
    echo "Restoring backup..."
fi

usage () {
  echo "$PROGNAME usage: 
  $PROGNAME -f  </path/to/filesystem_archive.tar.gz> -d </path/to/database_backup.sql.gz>
  e.g. $PROGNAME -f runzero-backup-fs.tar.gz -d runzero.sql.gz
  -f | --filesystem    Filesystem backup (tar.gz file)
  -d | --database    PostgreSQL database backup (sql.gz file)"
  return
}

filesystem=
database=

while [[ -n $1 ]]; do
    case $1 in
      -f | --filesystem)  shift
                          filesystem=$( echo $1 )
                          ;;
      -d | --database)    shift
                          database=$( echo $1 )
                          ;;
      -h | --help)        usage
                          exit
                          ;;
      *)                  usage >&2
                          exit 1
                          ;;
    esac
    shift
done

if [[ ! -e $filesystem ]] || [[ ! -e $database ]]; then
    echo "Filesystem backup or database backup not found!"
    exit 1
else
    runzeroctl stop
    tar -C -zxvf $filesystem
    su -c "dropdb runzero; gzip -dc $database | psql" postgres
    runzeroctl start
    echo "Restore complete!"
fi