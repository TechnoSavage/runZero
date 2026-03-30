""" EXAMPLE PYTHON SCRIPT! NOT INTENDED FOR PRODUCTION USE! 
    findDupes.py, version 4.0
    Query runZero API for all assets found within an Organization (tied to Export API key provided) and sort out assets with
    same MAC, Hostname, and IP but different asset ID. Optionally, an output file format can be specified to write to.
    
    !!!NOTE!!! runZero now supports queries for address_overlap, mac_overlap, and name_overlap. These keywords allow for 
    identification of potential duplicate assets directly in the console making the functionality of this script redundant."""

import argparse
import json
import logging
import os
import pandas as pd
import requests
from datetime import datetime, timezone
from getpass import getpass
from requests.exceptions import ConnectionError

logger = logging.getLogger(__name__)
    
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
    parser.add_argument('-l', '--log', help='Path to write log file. This argument will take priority over the .env file', 
                        required=False, default=os.environ["LOG_PATH"])
    parser.add_argument('-o', '--output', dest='output', help='output file format', choices=['txt', 'json', 'csv', 'excel', 'html'], required=False)
    parser.add_argument('--version', action='version', version='%(prog)s 4.0')
    return parser.parse_args()
    
def get_assets(url, token, filter='', fields=''):
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
        logger.info(f"Making GET request to {url}")
        response = requests.get(url, headers=headers, params=params, data=payload)
        if not response.ok:
            logger.critical('Unable to retrieve assets' + str(response), 'exiting...')
            exit()
        logger.info("Received response.")
        content = response.json()
        return content
    except ConnectionError:
        logger.exception('Could not establish connection to console URL, exiting...')
        exit()
    
def find_dupes(data):
    '''
        Parse runZero asset data (JSON) to find potential duplicates. 
    
        :param data: a dict, JSON formatted runZero asset data.
        :raises: KeyError: if key:value pair not present in asset data.
    '''

    #Create list of assets(dicts) with unique IDs
    uniqIDs = []
    try:
        logger.info('Parsing asset data for duplicates.')
        for item in data:
            count = 0
            for asset in uniqIDs:
                if item['id'] == asset['id']:
                    count += 1
            if count == 0: 
                uniqIDs.append(item)
    except KeyError:
        logger.exception('Key "id" does not exist in data. Exiting...')
        exit()
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
    logger.info('Data assessed for duplicate asset records.')
    if len(possblDups) > 0:
        return possblDups
    else:
        return([{"Msg": "No potential duplicate assets found."}])
    
def output_format(format, filename, data):
    '''
        Determine output format and call function to write appropriate file.
        
        :param format: A String, the desired output format.
        :param fileName: A String, the filename, minus extension.
        :param data: json data, file contents
        :returns None: Calls another function to write the file or prints the output.
    '''
    
    if format == 'json':
        filename = f'{filename}.json'
        write_file(filename, json.dumps(data))
    elif format == 'txt':
        filename = f'{filename}.txt'
        string_list = []
        for line in data:
            string_list.append(str(line).replace('{', '').replace('}', '').replace(': ', '='))
        text_file = '\n'.join(string_list)
        write_file(filename, text_file)
    elif format in ('csv', 'excel', 'html'):
        write_df(format, filename, data)  
    else:
        for line in data:
            print(json.dumps(line, indent=4))
    
def write_df(format, filename, data):
    '''
        Write contents to output file. 
    
        :param format: a string, excel, csv, or html
        :param filename: a string, the filename, excluding extension.
        :param contents: json data, file contents.
        :raises: IOError: if unable to write to file.
    '''
    
    df = pd.DataFrame(data)
    try:
        logger.info(f"Writing {filename} in {format} to disk.")
        if format == "excel":
            df.to_excel(f'{filename}.xlsx', freeze_panes=(1,0), na_rep='NA')
        elif format == 'csv':
            df.to_csv(f'{filename}.csv', na_rep='NA')
        else:
            df.to_html(f'{filename}.html', render_links=True, na_rep='NA')
    except IOError:
        logger.exception(f"Could not write output file: {filename}, exiting...")
        exit()
    
def write_file(filename, contents):
    '''
        Write contents to output file in plaintext. 
    
        :param filename: a string, name for file including (optionally) file extension.
        :param contents: anything, file contents.
        :raises: IOError: if unable to write to file.
    '''
    
    try:
        logger.info(f"Writing {filename} to disk.")
        with open( filename, 'w') as o:
                    o.write(contents)
    except IOError:
        logger.exception(f"Could not write output file: {filename}, exiting...")
        exit()

def main():
    args = parseArgs()
    logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%a, %d %b %Y %H:%M:%S', filename=f'{args.log}/findDupes.log', level=logging.INFO)
    logger.info('Started')
    #Output report name; default uses UTC time
    timestamp = str(datetime.now(timezone.utc).strftime('%y-%m-%d%Z_%H-%M-%S'))
    fileName = f'{args.path}Duplicate_Asset_Report_{timestamp}'
    token = args.token
    if token == None:
        token = getpass(prompt="Enter your Export API Key: ")
    #fields to return in API call; modify for more or less
    fields = "id, os, hw, addresses, macs, names, alive, site_id"
    assets = get_assets(args.consoleURL, token, f"first_seen:<{args.timeRange}", fields)
    dupes = find_dupes(assets)
    output_format(args.output, fileName, dupes)
    logger.info('Finished.')

if __name__ == "__main__":
    main()