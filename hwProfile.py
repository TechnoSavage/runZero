""" EXAMPLE PYTHON SCRIPT! NOT INTENDED FOR PRODUCTION USE! 
    hwProfile.py, version 2.0 by Derek Burke
    Query runZero API for physical assets found within an Organization (tied to Export API key provided) and generate JSON
    output of all attributes describing the physical hardware of the asset."""

import json
import os
import requests
import sys
from datetime import datetime
from flatten_json import flatten
from getpass import getpass
from requests.exceptions import ConnectionError

def usage():
    """ Display usage and switches. """
    print(""" Usage:
                    hwProfile.py [arguments]

                    You will be prompted to provide your runZero Export API key unless it is
                    specified in the .env file.

                    Optional arguments:
                    -u <uri>                    URI of console (default is https://console.runzero.com)
                    -h                          Show this help dialogue
                    
                Examples:
                    hwProfile.py
                    python -m hwProfile -u https://custom.runzero.com""")

def getAssets(uri, token, filter=" ", fields=" "):
    """ Retrieve assets using supplied query filter from Console and restrict to fields supplied.
        
        :param uri: A string, URI of runZero console.
        :param token: A string, Export API Key.
        :param filter: A string, query to filter returned assets(" " returns all).
        :param fields: A string, comma separated string of fields to return(" " returns all).
        :returns: a dict, JSON object of assets.
        :raises: ConnectionError: if unable to successfully make GET request to console."""

    uri = f"{uri}/api/v1.0/export/org/assets.json?"
    params = {'search': filter,
              'fields': fields}
    payload = ''
    headers = {'Accept': 'application/json',
               'Authorization': f'Bearer {token}'}
    try:
        response = requests.get(uri, headers=headers, params=params, data=payload)
        content = response.content
        data = json.loads(content)
        return data
    except ConnectionError as error:
        content = "No Response"
        raise error
    
def parseHW(data):
    """Search assets "attributes" and "foreign_attributes"
        for hardware information, discard the rest.
     
       :param data: a dict: runZero JSON asset data.
       :returns: a dict: parsed runZero asset data.
       :raises: TypeError: if dataset is not iterable.
       :raises: KeyError: if dictionary key does not exist."""
    
    try:
        assetList = []
        for item in data:
            asset = {}
            for key, value in item.items():
                if not isinstance(value, dict):
                    asset[key] = item.get(key)

            root_keys_to_ignore = []
            for key, value in item.items():
                if not isinstance(value, dict):
                    root_keys_to_ignore.append(key)
                flattened_items = flatten(nested_dict=item, root_keys_to_ignore=root_keys_to_ignore)
                asset['hw.product'] = flattened_items.get('attributes_hw.product')
                asset['hw.device'] = flattened_items.get('attributes_hw.device')
                asset['hw.vendor'] = flattened_items.get('attributes_hw.vendor')
                asset['snmp.sysDesc'] = flattened_items.get('attributes_snmp.sysDesc')
                asset['hw.serialNumber'] = flattened_items.get('attributes_hw.serialNumber')
                asset['snmp.serialNumbers'] = flattened_items.get('attributes_snmp.serialNumbers') 
                asset['ilo.serialNumber'] = flattened_items.get('attributes_ilo.serialNumber')
                asset['cpuID'] = flattened_items.get('foreign_attributes_@sentinelone.dev_0_cpuID')
                asset['modelName'] = flattened_items.get('foreign_attributes_@sentinelone.dev-0-modelName')
                asset['device.model'] = flattened_items.get('foreign_attributes_@miradore.dev_0_device.model')
                asset['device.serialnumber'] = flattened_items.get('foreign_attributes_@miradore.dev_0_device.serialNumber')
                asset['systemProductName'] = flattened_items.get('foreign_attributes_@crowdstrike.dev_0_systemProductName')
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
    
def main():
    if "-h" in sys.argv:
        usage()
        exit()
    consoleURL = os.environ["RUNZERO_BASE_URL"]
    token = os.environ["RUNZERO_EXPORT_TOKEN"]
    #Output report name; default uses UTC time
    fileName = f"Physical_Hardware_Types_{str(datetime.utcnow())}.json"
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

    query = "not attribute:virtual" #Query to grab all physical assets
    fields = "os, os_vendor, hw, addresses, attributes, foreign_attributes" #fields to return in API call; modify for more or less
    results = getAssets(consoleURL, token, query, fields)
    parsed = parseHW(results)
    writeFile(fileName, json.dumps(parsed))

if __name__ == "__main__":
    main()