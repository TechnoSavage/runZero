""" EXAMPLE PYTHON SCRIPT! NOT INTENDED FOR PRODUCTION USE! 
    hwProfile.py, version 4.0
    Query runZero API for physical assets found within an Organization (tied to Export API key provided) and generate JSON
    output of all attributes describing the physical hardware of the asset."""

import argparse
import json
import logging
import os
import pandas as pd
import requests
from datetime import datetime, timezone
from flatten_json import flatten
from getpass import getpass
from requests.exceptions import ConnectionError

logger = logging.getLogger(__name__)
    
def parseArgs():
    parser = argparse.ArgumentParser(description="Retrieve all hardware specific attributes.")
    parser.add_argument('-u', '--url', dest='consoleURL', help='URL of console. This argument will take priority over the .env file', 
                        required=False, default=os.environ["RUNZERO_BASE_URL"])
    parser.add_argument('-k', '--key', dest='token', help='Prompt for Export API key (do not enter at command line). This argument will take priority over the .env file', 
                        nargs='?', const=None, required=False, default=os.environ["RUNZERO_EXPORT_TOKEN"])
    parser.add_argument('-p', '--path', help='Path to write file. This argument will take priority over the .env file', 
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
    except ConnectionError as error:
        logger.exception('Could not establish connection to console URL, exiting...')
        exit()
    
def parse_hw(data):
    '''
        Search assets "attributes" and "foreign_attributes"
        for hardware information, discard the rest.
     
       :param data: a dict: runZero JSON asset data.
       :returns: a dict: parsed runZero asset data.
       :raises: TypeError: if dataset is not iterable.
    '''
    
    try:
        logger.info('Parsing hardware from asset data.')
        asset_list = []
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
            asset_list.append(asset)
        logger.info('Hardware parsing complete.')
        return(asset_list)
    except TypeError:
        logger.exception('Data provided was not a dictionary. Exiting...')
        exit()
    
def output_format(format, filename, data):
    '''
        Determine output format and call function to write appropriate file.
        
        :param format: A String, the desired output format.
        :param filename: A String, the filename, minus extension.
        :para data: json data, file contents
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
        logger.info(f"output file written to {filename} in {format}")
    except IOError:
       logger.exception(f"Could not write output file: {filename}, exiting...")
       exit()
    
def write_file(filename, contents):
    '''
        Write contents to output file. 
    
        :param filename: a string, name for file including (optionally) file extension.
        :param contents: anything, file contents.
        :raises: IOError: if unable to write to file.
    '''

    try:
        logger.info(f"Writing {filename} to disk.")
        with open( filename, 'w') as o:
                    o.write(contents)
        logger.info(f"{filename} successfully written to disk.")
    except IOError:
       logger.exception(f"Could not write output file: {filename}, exiting...")
       exit()
    
def main():
    args = parseArgs()
    logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%a, %d %b %Y %H:%M:%S', filename=f'{args.log}/hwProfile.log', level=logging.INFO)
    logger.info('Started')
    #Output report name; default uses UTC time
    timestamp = str(datetime.now(timezone.utc).strftime('%y-%m-%d%Z_%H-%M-%S'))
    filename = f'{args.path}Physical_Hardware_Types_{timestamp}'
    token = args.token
    if token == None:
        token = getpass(prompt="Enter your Export API Key: ")
    #Query to grab all physical assets
    query = "not attribute:=virtual and not (source:=vmware or source:=aws or source:=gcp or source:=azure)"
    #fields to return in API call; modify for more or less
    fields = "os, os_vendor, hw, addresses, attributes, foreign_attributes"
    results = get_assets(args.consoleURL, token, query, fields)
    parsed = parse_hw(results)
    output_format(args.output, filename, parsed)
    logger.info('Finished.')

if __name__ == "__main__":
    main()