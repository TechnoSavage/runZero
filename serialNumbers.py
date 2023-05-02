#!/usr/bin/python

""" EXAMPLE PYTHON SCRIPT! NOT INTENDED FOR PRODUCTION USE! 
    serialNumbers.py, version 2.0 by Derek Burke
    Retrieve assets from console using Export API endpoint, extract defined fields and serial numbers,
    and write to file in JSON format. This allows users to pull assets and SN information with a predefined
    set of attributes included."""

import json
import os
import requests
import sys
from datetime import datetime
from getpass import getpass
from requests.exceptions import ConnectionError

def usage():
    """ Display usage and switches. """
    print(""" Usage:
                    serialNumbers.py [arguments]

                    You will be prompted to provide your runZero Export API key unless it is
                    specified in the .env file.

                    Optional arguments:
                    -u <uri>                    URI of console (default is https://console.runzero.com)
                    -h                          Show this help dialogue
                    
                Examples:
                    serialNumbers.py
                    python -m serialNumbers -u https://custom.runzero.com""")
    
def getAssets(uri, token, filter=" ", fields=" "):
    """ Retrieve assets using supplied query filter from Console and restrict to fields supplied.
        
        :param uri: A string, URI of runZero console.
        :param token: A string, Export API Key.
        :param filter: A string, query to filter returned assets(" " returns all).
        :param fields: A string, comma separated string of fields to return(" " returns all).
        :returns: a dict, JSON object of assets.
        :raises: ConnectionError: if unable to successfully make GET request to console."""

    uri = uri + "/api/v1.0/export/org/assets.json?"
    params = {'search': filter,
              'fields': fields}
    payload = ''
    headers = {'Accept': 'application/json',
               'Authorization': 'Bearer %s' % token}
    try:
        response = requests.get(uri, headers=headers, params=params, data=payload)
        content = response.content
        data = json.loads(content)
        return data
    except ConnectionError as error:
        content = "No Response"
        raise error
    
def parseSNs(data):
    """Search assets "attributes" and extract SNs, discard the rest.
     
       :param data: a dict: runZero JSON asset data.
       :returns: a dict: parsed runZero asset data.
       :raises: TypeError: if dataset is not iterable.
       :raises: KeyError: if dictionary key does not exist."""
    
    try:
        assetList = []
        for item in data:
            asset = {}
            for field in item:
                if field == 'attributes':
                    try:
                        asset['hw.serialNumber'] = item[field]['hw.serialNumber']
                    except KeyError as error:
                        pass
                    try: 
                        asset['snmp.serialNumbers'] = item[field]['snmp.serialNumbers']
                    except KeyError as error:
                        pass
                    try:
                        asset['ilo.serialNumber'] = item[field]['ilo.serialNumber']
                    except KeyError as error:
                        pass
                else:
                    asset[field] = item[field]
            assetList.append(asset)
        return(assetList)
    except TypeError as error:
        raise error
    except KeyError as error:
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
    consoleURL = os.environ["CONSOLE_BASE_URL"]
    token = os.environ["RUNZERO_EXPORT_TOKEN"]
    #Output report name; default uses UTC time
    fileName = "Asset_Serial_Numbers" + str(datetime.utcnow()) + ".json"
    if token == '':
        token = getpass(prompt="Enter your Export API Key: ")
    if "-u" in sys.argv:
        try:
            consoleURL = sys.argv[sys.argv.index("-u") + 1]
        except IndexError as error:
            print("URI switch used but URI not provided!\n")
            usage()
            exit()
    if consoleURL == '':
        consoleURL = input('Enter the URL of the console (e.g. http://console.runzero.com): ')

    query = "protocol:snmp has:snmp.serialNumbers or hw.serialNumber:t or ilo.serialNumber:t" #Query to grab all assets with serial number fields
    fields = "id, os, os_vendor, os_product, os_version, hw, addresses, macs, attributes" #fields to return in API call; modify for more or less
    results = getAssets(consoleURL, token, query, fields)
    parsed = parseSNs(results)
    writeFile(fileName, json.dumps(parsed))