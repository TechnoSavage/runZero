""" EXAMPLE PYTHON SCRIPT! NOT INTENDED FOR PRODUCTION USE! 
    newAssetReport.py, version 3.0
    Query runZero API for all assets found within an Organization (tied to Export API key provided) first seen within the specified 
    time period and return select fields. Default behavior will be to print assets to stdout in JSON format. Optionally, an output 
    file and format can be specified."""

import argparse
import csv
import json
import os
import requests
from datetime import datetime
from getpass import getpass
from requests.exceptions import ConnectionError
    
def parseArgs():
    parser = argparse.ArgumentParser(description="Report all assets that were first found within a specified time range.")
    parser.add_argument('-r', '--range', dest='timeRange', help='Time span to search for new assets e.g. 1day, 2weeks, 1month. This argument will take priority over the .env file', 
                        required=False, default=os.environ["TIME"])
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
    
def writeCSV(fileName, contents):
    """ Write contents to output file. 
    
        :param filename: a string, name for file including.
        :param contents: json data, file contents.
        :raises: IOError: if unable to write to file. """
    try:
        cf = open(f'{fileName}', 'w')
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
    """ Write contents to output file in plaintext. 
    
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
    fileName = f"{args.path}New_Asset_Report_{str(datetime.utcnow())}"
    #Define config file to read from
    token = args.token
    if token == None:
        token = getpass(prompt="Enter your Export API Key: ")
    #Query to grab all assets first seen within the specified time value
    query = f"first_seen:<{args.timeRange}"
    #fields to return in API call; modify for more or less
    fields = "id, os, os_vendor, hw, addresses, macs, attributes"
    results = getAssets(args.consoleURL, token, query, fields)
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
    elif args.output == 'csv':
        fileName = f'{fileName}.csv'
        writeCSV(fileName, results)  
    else:
        for line in results:
            print(json.dumps(line, indent=4))
    
if __name__ == "__main__":
    main()