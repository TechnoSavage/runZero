""" EXAMPLE PYTHON SCRIPT! NOT INTENDED FOR PRODUCTION USE!
    ndaa889_traceroute.py, version 1.0
    Query runZero API for assets mathing NDAA section 889 query found within an Organization (tied to Export API key provided)
    and generate selected report type including asset name, addresses, type, and traceroute info."""

import argparse
import json
import os
import pandas as pd
import requests
from datetime import datetime, timezone
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
    parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    return parser.parse_args()

def get_ndaa_assets(url, token):
    '''
        Retrieve assets using supplied query filter from Console and restrict to fields supplied.
        
        :param url: A string, URL of runZero console.
        :param token: A string, Export API Key.
        :returns: a dict, JSON object of assets.
        :raises: ConnectionError: if unable to successfully make GET request to console.
    '''

    url = f"{url}/api/v1.0/export/org/assets.json"
    params = {'search': '((mac_vendor:zte OR mac_vendor:huawei OR mac_vendor:CRRC OR mac_vendor:dahua OR mac_vendor:hikvision OR mac_vendor:hisilicon OR mac_vendor:panda OR mac_vendor:dawning OR mac_vendor:hangzhou OR mac_vendor:hytera OR mac_vendor:inspur OR mac_vendor:"Aero Engine Corporation of China" OR mac_vendor:"Aviation Industry Corporation of China" OR mac_vendor:"China Aerospace" OR mac_vendor:"China Electronics" OR mac_vendor:"China General Nuclear Power" OR mac_vendor:"China Mobile" OR mac_vendor:"China National Nuclear Power" OR mac_vendor:"China North Industries Group" OR mac_vendor:"China Railway" OR mac_vendor:"China Shipbuilding" OR mac_vendor:"China South Industries Group" OR mac_vendor:"China State Shipbuilding" OR mac_vendor:"China Telecommunications" OR mac_vendor:ztec OR mac_vendor:ztek OR mac_vendor:"z-tec" OR mac_vendor:5shanghai OR mac_vendor:"Hella Sonnen" OR mac_vendor:anhui OR mac_vendor:"technology sdn bhd" OR mac_vendor:azteq) OR (hw:zte OR hw:huawei OR hw:CRRC OR hw:dahua OR hw:hikvision OR hw:hisilicon OR hw:panda OR hw:dawning OR hw:hangzhou OR hw:hytera OR hw:inspur OR hw:"Aero Engine Corporation of China" OR hw:"Aviation Industry Corporation of China" OR hw:"China Aerospace" OR hw:"China Electronics" OR hw:"China General Nuclear Power" OR hw:"China Mobile" OR hw:"China National Nuclear Power" OR hw:"China North Industries Group" OR hw:"China Railway" OR hw:"China Shipbuilding" OR hw:"China South Industries Group" OR hw:"China State Shipbuilding" OR hw:"China Telecommunications" OR hw:ztec OR hw:ztek OR hw:"z-tec" OR hw:5shanghai OR hw:"Hella Sonnen" OR hw:anhui OR hw:"technology sdn bhd" OR hw:azteq))',
              'fields': 'id,addresses,extra_addresses,os,hostname,type,hw,hw_vendor,mac_vendors,attributes'}
    headers = {'Accept': 'application/json',
               'Authorization': f'Bearer {token}'}
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            print('Unable to retrieve assets' + str(response))
            exit()
        content = response.content
        data = json.loads(content)
        return data
    except ConnectionError as error:
        content = "No Response"
        raise error
    
def parse_assets(data):
    '''
        Search assets "attributes" and assign key value pairs 
        that are not nested dicts and retrieve traceroute information
        from nested attribute dict, discard the remaining attributes.
     
       :param data: a dict: runZero JSON asset data.
       :returns: a dict: parsed runZero asset data.
       :raises: TypeError: if dataset is not iterable.
    '''
    
    try:
        asset_list = []
        for item in data:
            asset = {}
            for k, v in item.items():
                if not isinstance(v, dict):
                    asset[k] = item.get(k)
                asset['ipv4 traceroute'] = item.get('attributes', {}).get('ipv4.traceroute')
                asset['ipv6 traceroute'] = item.get('attributes', {}).get('ipv6.traceroute')
            asset_list.append(asset)
        return(asset_list)
    except TypeError as error:
        raise error
    
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
        if format == "excel":
            df.to_excel(f'{filename}.xlsx', freeze_panes=(1,0), na_rep='NA')
        elif format == 'csv':
            df.to_csv(f'{filename}.csv', na_rep='NA')
        else:
            df.to_html(f'{filename}.html', render_links=True, na_rep='NA')
    except IOError as error:
        raise error
    
def write_file(filename, contents):
    '''
        Write contents to output file. 
    
        :param filename: a string, name for file including (optionally) file extension.
        :param contents: anything, file contents.
        :raises: IOError: if unable to write to file.
    '''

    try:
        with open( filename, 'w') as o:
                    o.write(contents)
    except IOError as error:
        raise error
    
def main():
    args = parseArgs()
    #Output report name; default uses UTC time
    timestamp = str(datetime.now(timezone.utc).strftime('%y-%m-%d%Z_%H-%M-%S'))
    filename = f'{args.path}NDAA_traceroute_report_{timestamp}'
    token = args.token
    if token == None:
        token = getpass(prompt="Enter your Export API Key: ")
    results = get_ndaa_assets(args.consoleURL, token)
    parsed = parse_assets(results)
    output_format(args.output, filename, parsed)

if __name__ == "__main__":
    main()