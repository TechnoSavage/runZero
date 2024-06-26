""" EXAMPLE PYTHON SCRIPT! NOT INTENDED FOR PRODUCTION USE! 
    serialNumbers.py, version 3.2
    Retrieve assets from console using Export API endpoint, extract defined fields and serial numbers,
    and, optionally, write to file. This allows users to pull assets and SN information with a predefined
    set of attributes included."""

import argparse
import json
import os
import pandas as pd
import requests
from datetime import datetime
from flatten_json import flatten
from getpass import getpass
from requests.exceptions import ConnectionError
    
def parseArgs():
    parser = argparse.ArgumentParser(description="Retrive all available serial numbers from inventory assets.")
    parser.add_argument('-u', '--url', dest='consoleURL', help='URL of console. This argument will take priority over the .env file', 
                        required=False, default=os.environ["RUNZERO_BASE_URL"])
    parser.add_argument('-k', '--key', dest='token', help='Prompt for Export API key (do not enter at command line). This argument will take priority over the .env file', 
                        nargs='?', const=None, required=False, default=os.environ["RUNZERO_EXPORT_TOKEN"])
    parser.add_argument('-p', '--path', help='Path to write file. This argument will take priority over the .env file', 
                        required=False, default=os.environ["SAVE_PATH"])
    parser.add_argument('-o', '--output', dest='output', help='output file format', choices=['txt', 'json', 'csv', 'excel'], required=False)
    parser.add_argument('--version', action='version', version='%(prog)s 3.2')
    return parser.parse_args()
    
def getAssets(url, token, filter='', fields=''):
    """ Retrieve assets using supplied query filter from Console and restrict to fields supplied.
        
        :param url: A string, URL of runZero console.
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
    
def parseSNs(data):
    """Search assets "attributes" and extract SNs, discard the rest.
     
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
                asset['hw.serialNumber'] = flattened_items.get('attributes_hw.serialNumber', '')
                asset['snmp.serialNumbers'] = flattened_items.get('attributes_snmp.serialNumbers', '').split('\t')
                asset['ilo.serialNumber'] = flattened_items.get('attributes_ilo.serialNumber', '').split('\t')
            assetList.append(asset)
        return(assetList)
    except TypeError as error:
        raise error
    except AttributeError as error:
        print("Data is not JSON object; make sure provided API key is correct")
        exit()
    
def writeDF(fileName, format, data):
    """ Write contents to output file. 
    
        :param filename: a string, name for file including.
        :param format: a string, excel or csv
        :param contents: json data, file contents.
        :raises: IOError: if unable to write to file.  """
    
    df = pd.DataFrame(data)
    try:
        if format == "excel":
            df.to_excel(f'{fileName}.xlsx')
        else:
            df.to_csv(f'{fileName}.csv', encoding='utf-8')
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
    fileName = f"{args.path}Asset_Serial_Numbers_{str(datetime.utcnow())}"
    token = args.token
    if token == None:
        token = getpass(prompt="Enter your Export API Key: ")
    #Query to grab all assets with serial number fields
    query = "protocol:snmp or has:snmp.serialNumbers or hw.serialNumber:'%' or ilo.serialNumber:'%'"
    #fields to return in API call; modify for more or less
    fields = "id, hw, macs, attributes"
    assets = getAssets(args.consoleURL, token, query, fields)
    results = parseSNs(assets)
    if args.output == 'json':
        fileName = f'{fileName}.json'
        writeFile(fileName, json.dumps(results))
    elif args.output == 'txt':
        fileName = f'{fileName}.txt'
        stringList = []
        for line in results:
            stringList.append(str(line).replace('{', '').replace('}', '').replace(': ', '='))
        textFile = '\n'.join(stringList)
        writeFile(fileName, textFile)
    elif args.output in ('csv', 'excel'):
        writeDF(fileName, args.output, results)
    else:
        for line in results:
            print(json.dumps(line, indent=4))
    
if __name__ == "__main__":
    main()