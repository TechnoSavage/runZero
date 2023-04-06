#!/usr/bin/python

""" EXAMPLE PYTHON SCRIPT! NOT INTENDED FOR PRODUCTION USE! 
    createScan.py, version 1.0 by Derek Burke
    Sample python script to set up and perform a scan task through the runZero API."""

import json
import re
import requests
import sys
from getpass import getpass
from requests.exceptions import ConnectionError

def usage():
    """ Display usage and switches. """
    print(""" Usage:
                    createScan.py [arguments]

                    You will be prompted to provide your runZero Organization API key unless
                    it is included in a specified config file. If no config is provided you will
                    prompted to provide scan task parameters.
                    
                    Optional arguments:

                    -u <uri>              URI of console (default is https://console.runzero.com)
                    -t <target file/path> Specify a file containing scan targets (e.g.
                                          IP addresses/CIDR blocks, one per line)
                    -c <config file/path> Filename of config file including absolute path
                    -g                    Generate config file template
                    -h                    Show this help dialogue
                    
                Examples:
                    createScan.py -t targets.txt -c example.config
                    python3 -m createScan -u https://custom.runzero.com -t targets.txt""")

def genConfig():
    """Create a template for script configuration file."""

    template = """orgToken= #Organization API Key\nuri=https://console.runzero.com #Console URL\nsiteID= #Site ID whare scan results are saved\n
    scanExplor= #UID of explorer to use\nscanName= #name of scan task\nscanDesc= #Description for scan task\nscanRate= #scan rate in packets per second"""
    writeFile("config_template", template)
    exit()

def readConfig(configFile):
    """ Read values from configuration file

        :param config: a file, file containing values for script
        :returns: a tuple, console url at index, API token at index 1, and task number at index 2.
        :raises: IOError: if file cannot be read.
        :raises: FileNotFoundError: if file doesn't exist."""
    try:
        with open(configFile, 'r') as c:
            config = c.read()
            url = re.search("uri=(http[s]?://[a-z0-9.-]+)", config).group(1)
            token = re.search("orgToken=([0-9A-Z]+)", config).group(1)
            siteID = re.search("siteID=([0-9a-z-]+)", config).group(1)
            scanExplor = re.search("scanExplor=([0-9a-z-]+)", config).group(1)
            scanName = re.search("scanName=([0-9a-zA-Z-_ ]+)", config).group(1)
            scanDesc = re.search("scanDesc=([0-9a-zA-Z-_ ]+)", config).group(1)
            scanRate = re.search("scanRate=([0-9]+)", config).group(1)
            return(url, token, siteID, scanExplor, scanName, scanDesc, scanRate)
    except IOError as error:
        raise error
    except FileNotFoundError as error:
        raise error
    
def readTargets(targetFile):
    """ Read IP addresses, CIDR blocks, domains etc. from provided file

        :param targetFile: a file, file containing targets one per line.
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
        raise error
    except FileNotFoundError as error:
        raise error

#This function only addresses basic settings for the scan in the config file. Adapt or modify as needed.
def createScan(uri, token, siteID, explorer, name, description, rate, targetList): 
    """ Create new scan task.
           
           :param uri: A string
           :param token: A string, Organization API Key.
           :returns: A JSON object, scan creation results.
           :raises: ConnectionError: if unable to successfully make PUT request to console."""
    
    uri = uri + "/api/v1.0/org/sites/%s/scan" % siteID
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
               'Authorization': 'Bearer %s' % token}
    try:
        response = requests.put(uri, headers=headers, data=payload)
        content = response.content
        data = json.loads(content)
        return data
    except ConnectionError as error:
        content = "No Response"
        raise error

def writeFile(fileName, contents):
    """ Write contents to output file. 
    
        :param filename: a string, name for file including (optionally) file extension.
        :param contents: anything, file contents.
        :raises: IOError: if unable to write to file. """
    try:
        with open( fileName, 'w') as o:
                    o.write(contents)
    except IOError as error:
        raise error

if __name__ == "__main__":
    if "-h" in sys.argv:
        usage()
        exit()
    if "-g" in sys.argv:
        genConfig()
    consoleURL = "https://console.runzero.com"
    token = ""
    siteID = ""
    explorer = ""
    name = ""
    description = ""
    rate = ""
    config = False
    configFile = ""
    targetFile = ""
    targetList = []
    if "-c" in sys.argv:
        try:
            config = True
            configFile = sys.argv[sys.argv.index("-c") + 1]
            confParams = readConfig(configFile)
            consoleURL = confParams[0]
            token = confParams[1]
            siteID = confParams[2]
            explorer = confParams[3]
            name = confParams[4]
            description = confParams[5]
            rate = confParams[6]
        except IndexError as error:
            print("Config file switch used but no file provided!\n")
            usage()
            exit()
    if "-u" in sys.argv and not config:
        try:
            uri = sys.argv[sys.argv.index("-u") + 1]
        except IndexError as error:
            print("URI switch used but URI not provided!\n")
            usage()
            exit()
    if "-t" in sys.argv:
        try:
            targetFile = sys.argv[sys.argv.index("-t") + 1]
            targetList = readTargets(targetFile)
        except ValueError as error:
            raise error
        except IndexError as error:
            print("List of targets not provided!\n")
            usage()
            exit()
    if token == "":
        print("Enter your Organization API Key: ")
        token = getpass()
    response = createScan(consoleURL, token, siteID, explorer, name, description, rate, targetList)
    print(response)
