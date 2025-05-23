#!/bin/bash

set -euo pipefail

PROGNAME=$(basename $0)

#Check for root privileges, exit if not run as root user
if [[ $(id -u) != 0 ]]; then
    cat << EOM

This script must be run as root!
Please rerun with sudo e.g.
sudo ./${PROGNAME}

EOM
exit 1
fi

usage () {
  echo "${PROGNAME} usage: 
  ${PROGNAME} -i  </path/to/scan_targets_file> [ -c <snmp,community,strings> ] [ -m <basic | regular | extended> ] [ -s <true | false> ] [ -d <require | prefer | ignore> ] [ -o <path/to/output/directory> ]
  -i | --input_targets                                     Text file with list of targets to scan
  -c | --communities                                    Additional SNMP community strings (comma separated, no spaces)
  -m | --modbus  <basic | regular (default) | extended> Specify Modbus identification level
  -s | --s7comm  <true | false (default)>               Request s7comm extended information
  -d | --dnp3    <require | prefer | ignore (default)>  Specify dnp3 banner address discovery
  -o | --output                                         Path to output directory for scan results"
  return
}

input_targets=
comms="public,private"
modbus="regular"
s7comm="false"
dnp3="ignore"
probes="layer2,syn,bacnet,dahua-dhip,dns,dtls,ike,ipmi,kerberos,knxnet,l2t,l2tp,lantronix,ldap,mssql,netbios,ntp,openvpn,pca,sip,ssdp,snmp,ssh,tftp,ubnt,vmware,webmin,modbus,ethernetip,s7comm,fins,dnp3"
modbus_valid=( "basic" "regular" "default" )
s7comm_valid=( "true" "false" )
dnp3_valid=( "require" "prefer" "ignore" )
output=${PWD}


while [[ $# -ge 1 ]] && [[ -n ${1} ]]; do
    case ${1} in
      -i | --input_targets)  shift
                          input_targets="$1"
                          ;;
      -c | --communities) shift
                          comms+=",$1"
                          ;;
      -m | --modbus)      shift
                          modbus=$( echo ${1} | tr '[:upper:]' '[:lower:]' )
                          ;;
      -s | --s7comm)      shift
                          s7comm=$( echo ${1} | tr '[:upper:]' '[:lower:]' )
                          ;;
      -d | --dnp3)        shift
                          dnp3=$( echo ${1} | tr '[:upper:]' '[:lower:]' )
                          ;;
      -o | --output)      shift
                          output="$1"
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
if [[ ! -e ${input_targets} ]] || [[ ! -f ${input_targets} ]]; then
    echo " Provided input list of targets does not exist or is not a regular file."
    usage
    exit 1
fi

# test that output directory exists and that is a directory, exit if either condition in not true
if [[ ! -e ${output} ]] || [[ ! -d ${output} ]]; then
    echo " Provided output directory does not exist or is not a directory."
    usage
    exit 1
fi

#test if values provided for OT protocol options are valid, exit if invalid
if [[ ! " ${modbus_valid[*]} " =~ [[:space:]]${modbus}[[:space:]] ]]; then
    echo "Provided modbus identification level is not a valid option ( basic, regular, or extended )."
    usage
    exit 1
fi
if [[ ! " ${s7comm_valid[*]} " =~ [[:space:]]${s7comm}[[:space:]] ]]; then
    echo "Provided option for requesting s7comm extended information is invalid ( true or false )."
    usage
    exit 1
fi
if [[ ! " ${dnp3_valid[*]} " =~ [[:space:]]${dnp3}[[:space:]] ]]; then
    echo "Provided dnp3 banner address discovery option is invalid ( require, prefer, or ignore )."
    usage
    exit 1
fi

echo "Preparing OT Full scan..."

# define parameters to reflect OT full scan at https://help.runzero.com/docs/playbooks/scanning-ot-networks/#step-3b-create-an-ot-full-scan-template 

runzero scan --input-targets ${input_targets} --host-ping --rate 500 --max-host-rate 20 --max-ttl 64 --max-group-size 2048 \
  --modbus-identification-level ${modbus} \
  --s7comm-request-extended-information ${s7comm} \
  --dnp3-banner-address-discovery ${dnp3} \
  --probes ${probes} \
  --snmp-comms ${comms} \
  --output ${output}

  echo "Scan complete!"