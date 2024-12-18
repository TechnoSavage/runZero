""" EXAMPLE PYTHON SCRIPT! NOT INTENDED FOR PRODUCTION USE! 
    hwProfile.py, version 3.4
    Query runZero API for physical assets found within an Organization (tied to Export API key provided) and generate JSON
    output of all attributes describing the physical hardware of the asset."""

import argparse
import json
import os
import pandas as pd
import requests
from datetime import datetime, timezone
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
    parser.add_argument('-o', '--output', dest='output', help='output file format', choices=['txt', 'json', 'csv', 'excel', 'html'], required=False)
    parser.add_argument('--version', action='version', version='%(prog)s 3.4')
    return parser.parse_args()

def getAssets(url, token, filter=" ", fields=" "):
    '''
        Retrieve assets using supplied query filter from Console and restrict to fields supplied.
        
        :param url: A string, URL of runZero console.
        :param token: A string, Export API Key.
        :param filter: A string, query to filter returned assets(" " returns all).
        :param fields: A string, comma separated string of fields to return(" " returns all).
        :returns: a dict, JSON object of assets.
        :raises: ConnectionError: if unable to successfully make GET request to console.
    '''

    url = f"{url}/api/v1.0/export/org/assets.json"
    params = {'search': filter,
              'fields': fields}
    payload = ''
    headers = {'Accept': 'application/json',
               'Authorization': f'Bearer {token}'}
    try:
        response = requests.get(url, headers=headers, params=params, data=payload)
        if response.status_code != 200:
            print('Unable to retrieve assets' + response)
            exit()
        content = response.content
        data = json.loads(content)
        return data
    except ConnectionError as error:
        content = "No Response"
        raise error
    
def parseHW(data):
    '''
        Search assets "attributes" and "foreign_attributes"
        for hardware information, discard the rest.
     
       :param data: a dict: runZero JSON asset data.
       :returns: a dict: parsed runZero asset data.
       :raises: TypeError: if dataset is not iterable.
    '''
    
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
    
def outputFormat(format, fileName, data):
    '''
        Determine output format and call function to write appropriate file.
        
        :param format: A String, the desired output format.
        :param fileName: A String, the filename, minus extension.
        :para data: json data, file contents
        :returns None: Calls another function to write the file or prints the output.
    '''
    
    if format == 'json':
        fileName = f'{fileName}.json'
        writeFile(fileName, json.dumps(data))
    elif format == 'txt':
        fileName = f'{fileName}.txt'
        stringList = []
        for line in data:
            stringList.append(str(line).replace('{', '').replace('}', '').replace(': ', '='))
        textFile = '\n'.join(stringList)
        writeFile(fileName, textFile)
    elif format in ('csv', 'excel', 'html'):
        writeDF(format, fileName, data)  
    else:
        for line in data:
            print(json.dumps(line, indent=4))
    
def writeDF(format, fileName, data):
    '''
        Write contents to output file. 
    
        :param format: a string, excel, csv, or html
        :param fileName: a string, the filename, excluding extension.
        :param contents: json data, file contents.
        :raises: IOError: if unable to write to file.
    '''
    
    df = pd.DataFrame(data)
    try:
        if format == "excel":
            df.to_excel(f'{fileName}.xlsx', freeze_panes=(1,0), na_rep='NA')
        elif format == 'csv':
            df.to_csv(f'{fileName}.csv', na_rep='NA')
        else:
            df.to_html(f'{fileName}.html', render_links=True, na_rep='NA')
    except IOError as error:
        raise error
    
def writeFile(fileName, contents):
    '''
        Write contents to output file. 
    
        :param fileName: a string, name for file including (optionally) file extension.
        :param contents: anything, file contents.
        :raises: IOError: if unable to write to file.
    '''

    try:
        with open( fileName, 'w') as o:
                    o.write(contents)
    except IOError as error:
        raise error
    
def main():
    args = parseArgs()
    #Output report name; default uses UTC time
    timestamp = str(datetime.now(timezone.utc).strftime('%y-%m-%d%Z_%H-%M-%S'))
    fileName = f'{args.path}Physical_Hardware_Types_{timestamp}'
    token = args.token
    if token == None:
        token = getpass(prompt="Enter your Export API Key: ")
    #Query to grab all physical assets
    query = "not attribute:virtual and not (source:vmware or source:aws or source:gcp or source:azure)"
    #fields to return in API call; modify for more or less
    fields = "os, os_vendor, hw, addresses, attributes, foreign_attributes"
    results = getAssets(args.consoleURL, token, query, fields)
    parsed = parseHW(results)
    outputFormat(args.output, fileName, parsed)

if __name__ == "__main__":
    main()