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
    echo "Beginning installation..."
fi

usage () {
  echo "$PROGNAME usage: 
  $PROGNAME -t  <download token> -u <console URL> -b <binary architecture>
  e.g. $PROGNAME -t xxxxxxxxxxxxxxx -c console.runzero.com -b runzero-explorer-linux-amd64
  -t | --token      Download token of Organization
  -u | --url        URL of runZero console
  -b | --binary     Explorer binary architecture"
  return
}

dltok=
console='console.runzero.com'
bin='runzero-explorer-linux-amd64'

while [[ -n $1 ]]; do
    case $1 in
      -t | --token)  shift
                          dltok=$( echo $1 )
                          ;;
      -u | --url)    shift
                          console=$( echo $1 )
                          ;;
      -b | --binary) shift
                          bin=$( echo $1 )
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

curl -f -o runzero-explorer.bin "https://$console/download/explorer/$dltok/rzer0123/$bin"
chmod + x runzero-explorer.bin
./runzero-explorer.bin
