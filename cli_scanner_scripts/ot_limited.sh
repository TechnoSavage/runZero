#!/bin/bash

PROGNAME=$(basename $0)

#Check for root privileges, exit if not run as root user
if [[ $(id -u) != 0 ]]; then
    cat << EOM

This script must be run as root!
Please rerun with sudo e.g.
sudo ./ot_limited.sh

EOM
exit 1
fi

usage () {
  echo "$PROGNAME usage: $PROGNAME -i  </path/to/scan_targets_file> [ -c <snmp,community,strings> ]
  -i | --input_list   Text file with list of targets to scan
  -c | --communities  Additional SNMP community strings (comma separated, no spaces)"
  return
}

input_list=
comms="public,private"
ports="21,22,23,69,80,123,135,137,161,179,443,445,3389,5040,5900,7547,8080,8443,62078,65535"
probes="layer2,syn,netbios,ntp,snmp,tftp"

while [[ -n $1 ]]; do
    case $1 in
      -i | --input_list)  shift
                          input_list=$( echo $1 )
                          ;;
      -c | --communities) shift
                          comms+=",$1"
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

# test that input target list exists and that is a regular file, exit if either condition in not true
if [[ ! -e $input_list ]] || [[ ! -f $input_list ]]; then
    echo " Provided input list of targets does not exist or is not a regular file."
    usage
    exit 1
fi

echo "Preparing OT Limited scan..."

# define parameters to reflect OT limited scan at https://help.runzero.com/docs/playbooks/scanning-ot-networks/#step-3a-create-an-ot-limited-scan-template 
runzero -i $input_list --host-ping -r 300 --max-host-rate 20 --max-ttl 64 --max-group-size 2048 \
  --tcp-ports $ports \
  --probes $probes \
  --snmp-comms $comms \
  /

echo "Scan complete!"