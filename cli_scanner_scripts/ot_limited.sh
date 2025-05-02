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
  ${PROGNAME} -i  </path/to/scan_targets_file> [ -c <snmp,community,strings> ] [ -o <path/to/output/directory> ]
  -i | --input_targets   Text file with list of targets to scan
  -c | --communities  Additional SNMP community strings (comma separated, no spaces)
  -o | --output       Path to output directory for scan results"
  return
}

input_targets=
comms="public,private"
ports="21,22,23,69,80,123,135,137,161,179,443,445,3389,5040,5900,7547,8080,8443,62078,65535"
probes="layer2,syn,netbios,ntp,snmp,tftp"
output=${PWD}

while [[ $# -ge 1 ]] && [[ -n ${1} ]]; do
    case ${1} in
      -i | --input_targets)  shift
                          input_targets="$1"
                          ;;
      -c | --communities) shift
                          comms+=",$1"
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

echo "Preparing OT Limited scan..."

# define parameters to reflect OT limited scan at https://help.runzero.com/docs/playbooks/scanning-ot-networks/#step-3a-create-an-ot-limited-scan-template 
runzero scan --input-targets ${input_targets} --host-ping --rate 300 --max-host-rate 20 --max-ttl 64 --max-group-size 2048 \
  --tcp-ports ${ports} \
  --probes ${probes} \
  --snmp-comms ${comms} \
  --output ${output}

echo "Scan complete!"