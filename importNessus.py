""" EXAMPLE PYTHON SCRIPT! NOT INTENDED FOR PRODUCTION USE! 
    importNessus.py, version 1.0 by Derek Burke
    Bulk import all .nessus files in a specified folder via the runZero API."""

import json
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

                    You will be prompted to provide your runZero Organization API key
                    
                    Optional arguments:

                    -u  <uri>            URI of console (default is https://console.runzero.com)
                    -s  <site ID>        Site ID to apply scan data to
                    -d  <path/directory> Specify directory path to import .nessus scans from
                    -h                   Show this help dialogue
                    
                Examples:
                    importNessus.py -s 92hu9740-1ed3-4365-b6a4-733638f2a63d
                    importNessus.py -u https://custom.runzero.com -s 92hu9740-1ed3-4365-b6a4-733638f2a63d -d /documents/scans/
                    python -m importNessus""")

def importScan(uri, siteID, scan):
    """ Upload a .nessus scan file . 
    
        :param uri: A string, URL of the runZero console.
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
        content = "No Response"
        raise error

if __name__ == "__main__":
    if "-h" in sys.argv:
        usage()
        exit()
    print("Enter your Organization API Key: ")
    token = getpass()
    siteID = ""
    path = ""
    uri = "https://console.runzero.com"
    if "-s" not in sys.argv:
        siteID = input("Please provide the Site ID to apply the vulnerability scan data to: ")
    else:
        siteID = sys.argv[sys.argv.index("-s") + 1]
    if "-d" not in sys.argv:
        path = input("Please provide the path to the directory containing .nessus scan files: ")
    else:
        path = sys.argv[sys.argv.index("-d") + 1]
    if "-u" in sys.argv:
        try:
            uri = sys.argv[sys.argv.index("-u") + 1]
        except IndexError as error:
            print("URI switch used but URI not provided!\n")
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
                    response = importScan(uri, siteID, path + fileName.group(1))
                    print(response)
                else:
                    pass
    except OSError as error:
        print(error)
