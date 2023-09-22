""" EXAMPLE PYTHON SCRIPT! NOT INTENDED FOR PRODUCTION USE! 
    hwProfile.py, version 3.0
    Query runZero API for physical assets found within an Organization (tied to Export API key provided) and generate JSON
    output of all attributes describing the physical hardware of the asset."""

import argparse
import csv
import json
import os
import requests
import sys
from datetime import datetime
from flatten_json import flatten
from getpass import getpass
from requests.exceptions import ConnectionError
    
def parseArgs():
    parser = argparse.ArgumentParser(description="Retrieve all hardware specific attributes.")
    parser.add_argument('-u', '--url', dest='consoleURL', help='URL of console. This argument will take priority over the .env file', 
                        required=False, default=os.environ["RUNZERO_BASE_URL"])
    parser.add_argument('-k', '--key', dest='token', help='Prompt for Export API key (do not enter at command line). This argument will take priority over the .env file', 
                        nargs='?', const=None, required=False, default=os.environ["RUNZERO_EXPORT_TOKEN"])
    parser.add_argument('-p', '--path', help='Path to write file. This argument will take priority over the .env file', 
                        required=False, default=os.environ["SAVE_PATH"])
    parser.add_argument('-o', '--output', dest='output', help='output file format', choices=['txt', 'json', 'csv'], required=False)
    parser.add_argument('--version', action='version', version='%(prog)s 3.0')
    return parser.parse_args()

def getAssets(url, token, filter=" ", fields=" "):
    """ Retrieve assets using supplied query filter from Console and restrict to fields supplied.
        
        :param uri: A string, URI of runZero console.
        :param token: A string, Export API Key.
        :param filter: A string, query to filter returned assets(" " returns all).
        :param fields: A string, comma separated string of fields to return(" " returns all).
        :returns: a dict, JSON object of assets.
        :raises: ConnectionError: if unable to successfully make GET request to console."""

    url = f"{url}/api/v1.0/export/org/assets.json"
    params = {'search': filter,
              'fields': fields}
    payload = ''
    headers = {'Accept': 'application/json',
               'Authorization': f'Bearer {token}'}
    try:
        response = requests.get(url, headers=headers, params=params, data=payload)
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
       :raises: TypeError: if dataset is not iterable."""
    
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
                asset['hw.product'] = flattened_items.get('attributes_hw.product', '')
                asset['hw.device'] = flattened_items.get('attributes_hw.device', '')
                asset['hw.vendor'] = flattened_items.get('attributes_hw.vendor', '')
                asset['snmp.sysDesc'] = flattened_items.get('attributes_snmp.sysDesc', '')
                asset['hw.serialNumber'] = flattened_items.get('attributes_hw.serialNumber', '')
                asset['snmp.serialNumbers'] = flattened_items.get('attributes_snmp.serialNumbers', '') 
                asset['ilo.serialNumber'] = flattened_items.get('attributes_ilo.serialNumber', '')
                asset['cpuID'] = flattened_items.get('foreign_attributes_@sentinelone.dev_0_cpuID', '')
                asset['modelName'] = flattened_items.get('foreign_attributes_@sentinelone.dev-0-modelName', '')
                asset['device.model'] = flattened_items.get('foreign_attributes_@miradore.dev_0_device.model', '')
                asset['device.serialnumber'] = flattened_items.get('foreign_attributes_@miradore.dev_0_device.serialNumber', '')
                asset['systemProductName'] = flattened_items.get('foreign_attributes_@crowdstrike.dev_0_systemProductName', '')
            assetList.append(asset)
        return(assetList)
    except TypeError as error:
        raise error
    
def writeCSV(fileName, contents):
    """ Write contents to output file. 
    
        :param filename: a string, name for file including.
        :param contents: json data, file contents.
        :raises: IOError: if unable to write to file. """
    try:
        cf = open( fileName, 'w')
        csv_writer = csv.writer(cf)
        count = 0
        for item in contents:
            if count == 0:
                header = item.keys()
                csv_writer.writerow(header)
                count += 1
            csv_writer.writerow(item.values())
        cf.close()
    except IOError as error:
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
    args = parseArgs()
    #Output report name; default uses UTC time
    fileName = f"{args.path}Physical_Hardware_Types_{str(datetime.utcnow())}"
    token = args.token
    if token == None:
        token = getpass(prompt="Enter your Export API Key: ")
    #Query to grab all physical assets
    query = "not attribute:virtual and not (source:vmware or source:aws or source:gcp or source:azure)"
    #fields to return in API call; modify for more or less
    fields = "os, os_vendor, hw, addresses, attributes, foreign_attributes"
    results = getAssets(args.consoleURL, token, query, fields)
    parsed = parseHW(results)
    if args.output == 'json':
        fileName = f'{fileName}.json'
        writeFile(fileName, json.dumps(parsed))
    elif args.output == 'txt':
        fileName = f'{fileName}.txt'
        stringList = []
        for line in parsed:
            stringList.append(str(line).replace('{', '').replace('}', '').replace(': ', '='))
        textFile = '\n'.join(stringList)
        writeFile(fileName, textFile)
    elif args.output == 'csv':
        fileName = f'{fileName}.csv'
        writeCSV(fileName, parsed)  
    else:
        for line in parsed:
            print(json.dumps(line, indent=4))

if __name__ == "__main__":
    main()