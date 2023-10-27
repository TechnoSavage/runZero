""" EXAMPLE PYTHON SCRIPT! NOT INTENDED FOR PRODUCTION USE! 
    importNessus.py, version 2.0 by Derek Burke
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

                    -u <uri>              URI of console (default is https://console.runzero.com)
                    -s <site ID>          Site ID to apply scan data to
                    -d <path/directory>   Specify directory path to import .nessus scans from
                    -c <config file/path> Filename of config file including absolute path.
                    -g                    Generate config file template.
                    -h                    Show this help dialogue
                    
                Examples:
                    importNessus.py -s 92hu9740-1ed3-4365-b6a4-733638f2a63d
                    importNessus.py -u https://custom.runzero.com -s 92hu9740-1ed3-4365-b6a4-733638f2a63d -d /documents/scans/
                    python -m importNessus -c example.config""")
    
def genConfig():
    """Create a template for script configuration file."""

    template = "orgToken= #Organization API Key\nuri=https://console.runzero.com #Console URL\nsiteID= #ID of site to upload nessus scan to\nnessusDir= #Directory path to nessus scan files\n"
    writeFile("config_template", template)
    exit()

def readConfig(configFile):
    """ Read values from configuration file

        :param config: a file, file containing values for script
        :returns: a tuple, console url at index 0, API token at index 1, site ID at index 2, and nessus file directory at index 3.
        :raises: IOError: if file cannot be read.
        :raises: FileNotFoundError: if file doesn't exist."""
    try:
        with open( configFile, 'r') as c:
            config = c.read()
            url = re.search("uri=(http[s]?://[a-z0-9.]+)", config).group(1)
            token = re.search("orgToken=([0-9A-Z]+)", config).group(1)
            siteID = re.search("siteID=([0-9a-z-]+)", config).group(1)
            #nessusDir regex may need to be modified depending on what characters are used in the path
            nessusDir = re.search("nessusDir=([0-9A-Za-z.-_/\"\']+)", config).group(1)
            return(url, token, siteID, nessusDir)
    except IOError as error:
        raise error
    except FileNotFoundError as error:
        raise error

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
        content = "No Response"
        raise error
    
def writeFile(fileName, contents):
    """ Write contents to output file in plaintext. 
    
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
    config = False
    configFile = ''
    consoleURL = 'https://console.runzero.com'
    token = ''
    siteID = ''
    path = ''
    if "-c" in sys.argv:
        try:
            config = True
            configFile =sys.argv[sys.argv.index("-c") + 1]
            confParams = readConfig(configFile)
            consoleURL = confParams[0]
            token = confParams[1]
            siteID = confParams[2]
            path = confParams[3]
        except IndexError as error:
            print("Config file switch used but no file provided!\n")
            usage()
            exit()
    else:
        token = getpass(prompt="Enter your Organization API Key: ")
    if "-s" in sys.argv and not config:
        try:
            siteID = sys.argv[sys.argv.index("-s") + 1]
        except IndexError as error:
            print("site ID switch used but site ID not provided!\n")
            usage()
            exit()
    if "-d" in sys.argv and not config:
        try:
            path = sys.argv[sys.argv.index("-d") + 1]
        except IndexError as error:
            print("Directory switch used but directory not provided!\n")
            usage()
            exit()
    if "-u" in sys.argv and not config:
        try:
            consoleURL = sys.argv[sys.argv.index("-u") + 1]
        except IndexError as error:
            print("URI switch used but URI not provided!\n")
            usage()
            exit()
    if siteID == '':
        siteID = input("Please provide the Site ID to apply the vulnerability scan data to: ")
    if path == '':
        path = input("Please provide the path to the directory containing .nessus scan files: ")
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
