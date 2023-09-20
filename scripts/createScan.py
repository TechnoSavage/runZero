""" EXAMPLE PYTHON SCRIPT! NOT INTENDED FOR PRODUCTION USE! 
    createScan.py, version 2.0 by Derek Burke
    Sample python script to set up and perform a scan task through the runZero API."""

import json
import os
import requests
import sys
from getpass import getpass
from requests.exceptions import ConnectionError

def usage():
    """ Display usage and switches. """
    print(""" Usage:
                    createScan.py [arguments]

                    You will be prompted to provide your runZero Organization API key unless
                    it is read from the .env file.
                    
                    Optional arguments:

                    -u <uri>              URI of console, this argument will take priority over the .env file
                    -k                    Prompt for Organization API key, this argument will take priority over the .env file
                    -x <explorer UUID>    UUID of Explorer to scan with, this argument will take priority over the .env file
                    -s <site ID>          UUID of the site to apply scan task to, this argument will take priority over the .env file
                    -t <target file/path> Specify a file containing scan targets (e.g.
                                          IP addresses/CIDR blocks, one per line)
                    -r <rate>             Specify rate (packets per second) for scan; defaults to 1000
                    -n                    Prompt for scan name; otherwise "API Scan" will be used
                    -d                    Prompt for scan description; otherwise blank
                    -h                    Show this help dialogue
                    
                Examples:
                    createScan.py -t targets.txt
                    python3 -m createScan -u https://custom.runzero.com -t targets.txt""")
    
def readTargets(targetFile):
    """ Read IP addresses, CIDR blocks, domains etc. from provided file

        :param targetFile: a text file, file containing targets one per line.
        :returns: a List, list of targets to pass to scan task.
        :raises: IOError: if file cannot be read.
        :raises: FileNotFoundError: if file doesn't exist."""
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
def createScan(uri, token, siteID, explorer, targetList, name="", description="", rate=1000): 
    """ Create new scan task.
           
           :param uri: A string, URL of the runZero console.
           :param token: A string, Organization API Key.
           :returns: A JSON object, scan creation results.
           :raises: ConnectionError: if unable to successfully make PUT request to console."""
    
    uri = f"{uri}/api/v1.0/org/sites/{siteID}/scan"
    payload = json.dumps({"targets": ', '.join(targetList),
               "excludes": "string",
               "scan-name": name,
               "scan-description": description,
               "scan-frequency": "once",
               "scan-start": "0",
               "scan-tags": "",
               "scan-grace-period": "4",
               "agent": explorer,
               "rate": str(rate),
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
        response = requests.put(uri, headers=headers, data=payload)
        content = response.content
        data = json.loads(content)
        return data
    except ConnectionError as error:
        content = "No Response"
        raise error
    
def main():
    if "-h" in sys.argv:
        usage()
        exit()
    consoleURL = os.environ["RUNZERO_BASE_URL"]
    token = os.environ["RUNZERO_ORG_TOKEN"]
    siteID = os.environ["RUNZERO_SITE_ID"]
    explorer = os.environ["EXPLORER"]
    targetFile = os.environ["TARGETS"]
    name = 'API scan'
    description = ''
    rate = 1000
    if "-u" in sys.argv:
        try:
            consoleURL = sys.argv[sys.argv.index("-u") + 1]
        except IndexError as error:
            print("URL switch used but URL not provided!\n")
            usage()
            exit()
    if "-k" in sys.argv:
        token = getpass(prompt="Enter the Organization API Key: ")
        if token == '':
            print("No API token provided!\n")
            usage()
            exit()
    if "-x" in sys.argv:
        try:
            explorer = sys.argv[sys.argv.index("-x") + 1]
        except IndexError as error:
            print("Explorer switch used but UUID not provided!\n")
            usage()
            exit()
    if "-s" in sys.argv:
        try:
            siteID = sys.argv[sys.argv.index("-s") + 1]
        except IndexError as error:
            print("Site switch used but site ID not provided!\n")
            usage()
            exit()
    if "-t" in sys.argv:
        try:
            targetFile = sys.argv[sys.argv.index("-t") + 1]
        except ValueError as error:
            raise error
        except IndexError as error:
            print("List of targets not provided!\n")
            usage()
            exit()
    if "-r" in sys.argv:
        try:
            rate = int(sys.argv[sys.argv.index("-r") + 1])
        except ValueError as error:
            raise error
        except IndexError as error:
            print("Scan rate switch used but value invalid or not provided!\n")
            usage()
            exit()
    if "-n" in sys.argv:
        name = input('Enter scan name: ')
        if name == '':
            name = "API scan"
    if "-d" in sys.argv:
        description = input('Enter scan description: ')
    targetList = readTargets(targetFile)
    if type(targetList) is not list:
        print("Target file is invalid or does not exist.")
        exit()
    response = createScan(consoleURL, token, siteID, explorer, targetList, name, description, rate)
    print(response)
    
if __name__ == "__main__":
    main()