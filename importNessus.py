""" EXAMPLE PYTHON SCRIPT! NOT INTENDED FOR PRODUCTION USE! 
    importNessus.py, version 3.3 by Derek Burke
    Bulk import all .nessus files in a specified folder via the runZero API."""

import json
import os
import re
import requests
import subprocess
import sys
from datetime import datetime
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
                    -c                    Enable file clean up. Automatically delete .nessus files that are successfully uploaded.
                    -l                    Create log. Generate a timestamped text file listing filename and upload status. 
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

    uri = f"{uri}/api/v1.0/org/sites/{siteID}/import/nessus"
    payload = ""
    file = [('application/octet-stream',(scan,open(scan,'rb'),'application/octet-stream'))]
    headers = {'Accept': 'application/octet-stream',
               'Authorization': f'Bearer {token}'}
    try:
        response = requests.put(uri, headers=headers, data=payload, files=file)
        code = response.status_code
        content = response.content
        data = json.loads(content)
        return(code, data)
    except ConnectionError as error:
        raise error
    
def cleanUp(path, log):
    """Remove nessus files that are uploaded successfully.

        :param path: A String, path to nessus file location(s).
        :param log: A Dict, dictionary of nessus filenames and upload status.
        :returns None: this function returns nothing but removes files from disk.
        :raises: IOerror, if unable to delete file."""
    
    for file, status in log.items():
        if status == "success":
            try:
                os.remove(path + file)
            except IOError as error:
                print(error)
        else:
            pass
    
def logging(log):
    """ Write log to output file. 
    
        :param log: A Dict, dictionary of nessus filenames and upload status.
        :raises: IOError: if unable to write to file. """
    try:
        with open( f"importNessus_log_{str(datetime.now())}", 'w') as o:
                    o.write(json.dumps(log, indent=4))
    except IOError as error:
        raise error
    
def main():
    if "-h" in sys.argv:
        usage()
        exit()
    consoleURL = os.environ["CONSOLE_BASE_URL"]
    token = os.environ["RUNZERO_ORG_TOKEN"]
    siteID = os.environ["SITE_ID"]
    path = os.environ["NESSUS_DIR"]
    tidy = False
    writeLog = False
    log = {}
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
    if "-c" in sys.argv:
        tidy = True
    if "-l" in sys.argv:
        writeLog = True
    try:     
        contents = subprocess.check_output(['ls', path]).splitlines()
        for item in contents:
            fileName = re.match("b'((.*)\.(nessus))", str(item))
            if fileName is not None:
                fileType = subprocess.check_output(['file', path + fileName.group(1)])
                if fileName.group(3) == "nessus" and 'XML' in str(fileType):
                    response = importScan(consoleURL, token, siteID, path + fileName.group(1))
                    if response[0] == 200 and response[1]['error'] == '':
                        log[fileName.group(1)] = 'success'
                    else:
                        log[fileName.group(1)] = 'fail'
                else:
                    pass
        print(json.dumps(log, indent=4))
    except OSError as error:
        print(error)
    if writeLog:
        logging(log)
    if tidy:
        cleanUp(path, log)

if __name__ == "__main__":
    main()

