""" EXAMPLE PYTHON SCRIPT! NOT INTENDED FOR PRODUCTION USE! 
    createScan.py, version 3.2
    Sample python script to set up and perform a scan task through the runZero API."""

import argparse
import json
import os
import requests
from getpass import getpass
from requests.exceptions import ConnectionError
    
def parseArgs():
    parser = argparse.ArgumentParser(description="Create scan task via API.")
    parser.add_argument('-u', '--url', dest='consoleURL', help='URL of console. This argument will override the .env file', 
                        required=False, default=os.environ["RUNZERO_BASE_URL"])
    parser.add_argument('-k', '--key', dest='token', help='Prompt for Organization API key (do not enter at command line). This argument will override the .env file', 
                        nargs='?', const=None, required=False, default=os.environ["RUNZERO_ORG_TOKEN"])
    parser.add_argument('-x', '--explorer', dest='explorer', help='UUID of the Explorer. This argument will override the .env file', 
                        required=False, default=os.environ["EXPLORER"])
    parser.add_argument('-s', '--site', help='UUID of site to add scan data to. This argument will override the .env file', 
                        required=False, default=os.environ["RUNZERO_SITE_ID"])
    parser.add_argument('-iL', '--input-list', dest='targetFile', help='Text file with scan targets. This argument will override the .env file', 
                        required=False, default=os.environ["TARGETS"])
    parser.add_argument('-n', '--name', help='Name for the scan task.', required=False, default='API Scan')
    parser.add_argument('-d', '--description', help='Description for scan task.', required=False)
    parser.add_argument('-r', '--rate', help='Scan rate for task.', required=False, default='1000')
    parser.add_argument('--version', action='version', version='%(prog)s 3.2')
    return parser.parse_args()
    
def readTargets(targetFile):
    '''
        Read IP addresses, CIDR blocks, domains etc. from provided file

        :param targetFile: a text file, file containing targets one per line.
        :returns: a List, list of targets to pass to scan task.
        :raises: IOError: if file cannot be read.
        :raises: FileNotFoundError: if file doesn't exist.
    '''

    targetList = []
    try:
        with open( targetFile, 'r') as t:
            targets = t.readlines()
            for target in targets:
                target.rstrip('\n')
                targetList.append(target)
        return(targetList)
    except IOError as error:
        return error
    except OSError.FileNotFoundError as error:
        return error 

#This function only addresses basic settings for the scan in arguments and .env file. Adapt or modify as needed.
def createScan(url, token, siteID, explorer, targetList, name, description, rate): 
    '''
        Create new scan task.
           
        :param url: A string, URL of the runZero console.
        :param token: A string, Organization API Key.
        :param siteID: A string, UID of site to scan.
        :param explorer: A string, UID of explorer.
        :param targetList: A list, list of scan targets.
        :param name: A string, name for scan task.
        :param description: A string, description for scan task.
        :param rate: A string, scan rate (packets per second).
        :returns: A JSON object, scan creation results.
        :raises: ConnectionError: if unable to successfully make PUT request to console.
    '''
    
    url = f"{url}/api/v1.0/org/sites/{siteID}/scan"
    payload = json.dumps({"targets": ', '.join(targetList),
               "excludes": "string",
               "scan-name": name,
               "scan-description": description,
               "scan-frequency": "once",
               "scan-start": "0",
               "scan-tags": "",
               "scan-grace-period": "4",
               "agent": explorer,
               "rate": rate,
               "max-host-rate": "40",
               "passes": "3",
               "max-attempts": "3",
               "max-sockets": "500",
               "max-group-size": "4096",
               "max-ttl": "255",
               "tcp-ports": "1-1000,5000-6000",
               "tcp-excludes": "9500",
               "screenshots": "true",
               "nameservers": "8.8.8.8",
               "subnet-ping": "true",
               "subnet-ping-net-size": "256",
               "subnet-ping-sample-rate": "3",
               "host-ping": "false",
               "probes": "arp,bacnet,connect,dns,echo,ike,ipmi,mdns,memcache,mssql,natpmp,netbios,pca,rdns,rpcbind,sip,snmp,ssdp,syn,ubnt,wlan-list,wsd"})
    headers = {'Accept': 'application/json',
               'Content-Type': 'application/json',
               'Authorization': f'Bearer {token}'}
    try:
        response = requests.put(url, headers=headers, data=payload)
        if response.status_code != 200:
            print('Unable to create task' + str(response))
            exit()
        content = response.content
        data = json.loads(content)
        return data
    except ConnectionError as error:
        content = "No Response"
        raise error
    
def main():
    args = parseArgs()
    token = args.token
    if token == None:
        token = getpass(prompt="Enter the Organization API Key: ")
    targetList = readTargets(args.targetFile)
    if type(targetList) is not list:
        print("Target file is invalid or does not exist.")
        exit()
    response = createScan(args.consoleURL, token, args.site, args.explorer, targetList, args.name, args.description, args.rate)
    print(response)
    
if __name__ == "__main__":
    main()