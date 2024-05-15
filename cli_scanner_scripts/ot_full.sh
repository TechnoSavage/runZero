#!/bin/bash

#Check for root privileges, exit if not run as root user
if [[ $(id -u) != 0 ]]; then
    cat << EOM

This script must be run as root!
Please rerun with sudo e.g.
sudo ./ot_full.sh

EOM
exit 1
fi

usage () {
  echo "$PROGNAME: Usage $PROGNAME -i  <target input list>
  e.g. $PROGNAME -i /path/to/my_scan_targets
  -i | --input_list   Text file with list of targets to scan
  -c | --communities  Additional SNMP community strings (comma separated, no spaces)
  -m | --modbus  <basic | regular (default) | extended>
  -s | --s7comm  <true | false (default)>
  -d | --dnp3    <require | prefer | ignore (default)>"
  return
}

input_list=
comms="public,private"
modbus="regular"
s7comm="false"
dnp3="ignore"
probes="layer2,syn,bacnet,dahua-dhip,dns,dtls,ike,ipmi,kerberos,knxnet,l2t,l2tp,lantronix,ldap,mssql,netbios,ntp,openvpn,pca,sip,ssdp,snmp,ssh,tftp,ubnt,vmware,webmin,modbus,ethernetip,s7comm,fins,dnp3"

while [[ -n $1 ]]; do
    case $1 in
      -i | --input_list)  shift
                          input_list=$( echo $1 )
                          ;;
      -c | --communities) shift
                          comms=$( echo $1 )
                          ;;
      -m | --modbus)      shift
                          modbus=$( echo $1 )
                          ;;
      -s | --s7comm)      shift
                          s7comm=$( echo $1 )
                          ;;
      -d | --dnp3)        shift
                          dnp3=$( echo $1 )
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
if [[ ! -e $input_list ]]; then
    echo "input list of targets does not exist; ensure target list exists and rerun script."
    usage()
    exit 1
fi
if [[ ! -f $input_list ]]; then
    echo "Specified input list is not a regular file."
    usage()
    exit 1
fi

echo "Preparing OT Full scan..."

# define parameters to reflect OT limited scan at https://help.runzero.com/docs/playbooks/scanning-ot-networks/#step-3b-create-an-ot-full-scan-template 

runzero -i $input_list --host-ping -r 500 --max-host-rate 20 --max-ttl 64 --max-group-size 2048 \
  --modbus-identification-level $modbus \
  --s7comm-request-extended-information $s7comm \
  --dnp3-banner-address-discovery $dnp3 \
  --probes $probes \
  --snmp-comms $comms \
  /

  echo "Scan complete!"