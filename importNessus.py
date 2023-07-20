#!/usr/bin/python

""" EXAMPLE PYTHON SCRIPT! NOT INTENDED FOR PRODUCTION USE! 
    importNessus.py, version 3.1 by Derek Burke
    Bulk import all .nessus files in a specified folder via the runZero API."""

import json
import os
import re
import requests
import subprocess
import sys
from getpass import getpass
from requests.exceptions import ConnectionError

def usage():
    """ Display usage and switches. """
    print(""" Usage:
                    importNessus.py [arguments]

                    This script will upload all .nessus vulnerability scan files from a specified
                    folder to a specified site in the runZero console. This requires the Organization
                    API key for which the site belongs to. This script should work on *nix systems
                    and MacOS.
                    
                    Optional arguments:

                    -u <url>              URL of console, , this argument will take priority over the .env file
                    -k                    Prompt for Organization API key, this argument will take priority over the .env file
                    -s <site ID>          Site ID to apply scan data to, , this argument will take priority over the .env file
                    -d <path/directory>   Specify directory path to .nessus scan files, , this argument will take priority over the .env file
                    -h                    Show this help dialogue
                    
                Examples:
                    importNessus.py -k -s 92hu9740-1ed3-4365-b6a4-733638f2a63d
                    python3 -m importNessus -u https://custom.runzero.com -s 92hu9740-1ed3-4365-b6a4-733638f2a63d -d /documents/scans/""")

def importScan(uri, token, siteID, scan):
    """ Upload a .nessus scan file . 
    
        :param uri: A string, URL of the runZero console.
        :param token: A string, Organization API key
        :param siteID: A string, the site ID of the Site to apply scan to.
        :param scan: A .nessus file, Nessus scan file to upload.
        :returns: Dict Object, JSON formatted.
        :raises: ConnectionError: if unable to successfully make PUT request to console."""

    uri = uri + "/api/v1.0/org/sites/%s/import/nessus" % siteID
    payload = ""
    file = [('application/octet-stream',(scan,open(scan,'rb'),'application/octet-stream'))]
    headers = {'Accept': 'application/octet-stream',
               'Authorization': 'Bearer %s' % token}
    try:
        response = requests.put(uri, headers=headers, data=payload, files=file)
        content = response.content
        data = json.loads(content)
        return data
    except ConnectionError as error:
        raise error

if __name__ == "__main__":
    if "-h" in sys.argv:
        usage()
        exit()
    consoleURL = os.environ["CONSOLE_BASE_URL"]
    token = os.environ["RUNZERO_ORG_TOKEN"]
    siteID = os.environ["SITE_ID"]
    path = os.environ["NESSUS_DIR"]
    if "-u" in sys.argv:
        try:
            consoleURL = sys.argv[sys.argv.index("-u") + 1]
        except IndexError as error:
            print("URI switch used but URI not provided!\n")
            usage()
            exit()
    if "-k" in sys.argv:
        token = getpass(prompt="Enter your Organization API Key: ")
        if token == '':
            print("No API token provided!\n")
            usage()
            exit()
    if "-s" in sys.argv:
        try:
            siteID = sys.argv[sys.argv.index("-s") + 1]
        except IndexError as error:
            print("site ID switch used but site ID not provided!\n")
            usage()
            exit()
    if "-d" in sys.argv:
        try:
            path = sys.argv[sys.argv.index("-d") + 1]
        except IndexError as error:
            print("Directory switch used but directory not provided!\n")
            usage()
            exit()
    try:     
        contents = subprocess.check_output(['ls', path]).splitlines()
        for item in contents:
            fileName = re.match("b'((.*)\.(nessus))", str(item))
            if fileName is not None:
                fileType = subprocess.check_output(['file', path + fileName.group(1)])
                if fileName.group(3) == "nessus" and 'XML' in str(fileType):
                    print("Uploading scan: ", fileName.group(1))
                    response = importScan(consoleURL, token, siteID, path + fileName.group(1))
                    print(response)
                else:
                    pass
    except OSError as error:
        print(error)
