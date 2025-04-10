""" EXAMPLE PYTHON SCRIPT! NOT INTENDED FOR PRODUCTION USE! 
    findDupes.py, version 3.5
    Query runZero API for all assets found within an Organization (tied to Export API key provided) and sort out assets with
    same MAC, Hostname, and IP but different asset ID. Optionally, an output file format can be specified to write to.
    
    !!!NOTE!!! runZero now supports queries for address_overlap, mac_overlap, and name_overlap. These keywords allow for 
    identification of potential duplicate assets directly in the console making the functionality of this script redundant."""

import argparse
import json
import os
import pandas as pd
import requests
from datetime import datetime, timezone
from getpass import getpass
from requests.exceptions import ConnectionError
    
def parseArgs():
    parser = argparse.ArgumentParser(description="Report potential duplicate assets sharing MAC, IP, and/or hostname.")
    parser.add_argument('-r', '--range', dest='timeRange', help='Time span to search for duplicate assets e.g. 1day, 2weeks, 1month. This argument will override the .env file', 
                        required=False, default=os.environ["TIME"])
    parser.add_argument('-u', '--url', dest='consoleURL', help='URL of console. This argument will override the .env file', 
                        required=False, default=os.environ["RUNZERO_BASE_URL"])
    parser.add_argument('-k', '--key', dest='token', help='Prompt for Export API key (do not enter at command line). This argument will override the .env file', 
                        nargs='?', const=None, required=False, default=os.environ["RUNZERO_EXPORT_TOKEN"])
    parser.add_argument('-p', '--path', help='Path to write file. This argument will override the .env file', 
                        required=False, default=os.environ["SAVE_PATH"])
    parser.add_argument('-o', '--output', dest='output', help='output file format', choices=['txt', 'json', 'csv', 'excel', 'html'], required=False)
    parser.add_argument('--version', action='version', version='%(prog)s 3.5')
    return parser.parse_args()
    
def getAssets(url, token, filter='', fields=''):
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
            print('Unable to retrieve assets' + str(response))
            exit()
        content = response.content
        data = json.loads(content)
        return data
    except ConnectionError as error:
        content = "No Response"
        raise error
    
def findDupes(data):
    '''
        Parse runZero asset data (JSON) to find potential duplicates. 
    
        :param data: a dict, JSON formatted runZero asset data.
        :raises: KeyError: if key:value pair not present in asset data.
    '''

    #Create list of assets(dicts) with unique IDs
    uniqIDs = []
    try:
        for item in data:
            count = 0
            for asset in uniqIDs:
                if item['id'] == asset['id']:
                    count += 1
            if count == 0: 
                uniqIDs.append(item)
    except KeyError as error:
        raise error
    #Loop through unique IDs and identify assets with identical MACs, Hostnames, and/or IPs
    #Add these assets with duplicate fields to list
    possblDups = []
    for asset in uniqIDs:
        uid = asset.get('id')
        macs = asset.get('macs')
        addresses = asset.get('addresses')
        hostnames = asset.get('names')
        for others in uniqIDs:
            #So asset doesn't match itself as a duplicate
            if uid == others['id']:
                pass
            else:
                macMatch = False
                addrMatch = False
                nameMatch = False
                matchedMACs = []
                matchedAddresses = []
                matchedHostnames = []  
                for mac in others['macs']:
                    if mac in macs:
                        macMatch = True
                        matchedMACs.append(mac)
                for addr in others['addresses']:
                    if addr in addresses:
                        addrMatch = True
                        matchedAddresses.append(addr)
                for name in others['names']:
                    if name in hostnames:
                        nameMatch = True
                        matchedHostnames.append(name)
                if macMatch or addrMatch or nameMatch:
                    asset['possible_dupe'] = {'id': others['id'], 'os': others['os'], 'hw': others['hw']}
                    asset['shared_fields'] = {'MAC': macMatch,
                                                'matched_MACs': matchedMACs,  
                                                'IP address': addrMatch, 
                                                'matched_Addresses': matchedAddresses, 
                                                'Hostname': nameMatch, 
                                                'matched_Hostnames': matchedHostnames, 
                                                'site': others['site_id']}
                    possblDups.append(asset)
    if len(possblDups) > 0:
        return possblDups
    else:
        return([{"Msg": "No potential duplicate assets found."}])
    
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
        Write contents to output file in plaintext. 
    
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
    fileName = f'{args.path}Duplicate_Asset_Report_{timestamp}'
    token = args.token
    if token == None:
        token = getpass(prompt="Enter your Export API Key: ")
    #fields to return in API call; modify for more or less
    fields = "id, os, hw, addresses, macs, names, alive, site_id"
    assets = getAssets(args.consoleURL, token, f"first_seen:<{args.timeRange}", fields)
    dupes = findDupes(assets)
    outputFormat(args.output, fileName, dupes)
    
if __name__ == "__main__":
    main()