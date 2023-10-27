""" EXAMPLE PYTHON SCRIPT! NOT INTENDED FOR PRODUCTION USE! 
    orgIDs.py, version 4.0
    Script to retrieve all Organization IDs and 'friendly' names for a given account. """

import argparse
import csv
import json
import os
import requests
from datetime import datetime
from getpass import getpass
from requests.exceptions import ConnectionError
    
def parseArgs():
    parser = argparse.ArgumentParser(description="Retrieve all Organization IDs and 'friendly' names for a given account.")
    parser.add_argument('-u', '--url', dest='consoleURL', help='URL of console. This argument will take priority over the .env file', 
                        required=False, default=os.environ["RUNZERO_BASE_URL"])
    parser.add_argument('-k', '--key', dest='token', help='Prompt for Account API key (do not enter at command line). This argument will take priority over the .env file', 
                        nargs='?', const=None, required=False, default=os.environ["RUNZERO_ACCOUNT_TOKEN"])
    parser.add_argument('-p', '--path', help='Path to write file. This argument will take priority over the .env file', 
                        required=False, default=os.environ["SAVE_PATH"])
    parser.add_argument('-o', '--output', dest='output', help='output file format', choices=['txt', 'json', 'csv'], required=False)
    parser.add_argument('--version', action='version', version='%(prog)s 4.0')
    return parser.parse_args()

def getOIDs(url, token):
    """ Retrieve Organizational IDs from Console.

           :param token: A string, Account API Key.
           :returns: A JSON object, runZero Org data.
           :raises: ConnectionError: if unable to successfully make GET request to console."""

    url = f"{url}/api/v1.0/account/orgs"
    payload = ""
    headers = {'Accept': 'application/json',
               'Authorization': f'Bearer {token}'}
    try:
        response = requests.get(url, headers=headers, data=payload)
        content = response.content
        data = json.loads(content)
        return data
    except ConnectionError as error:
        content = "No Response"
        raise error

def parseOIDs(data):
    """ Parse API response to extract Organization names and IDs. 
    
        :param data: JSON object, runZero org data.
        :returns: Dict Object, JSON formatted dictionary of relevant values.
        :raises: TypeError: if data variable passed is not JSON format."""
    try:
        parsed = []
        for item in data:
            orgs = {}
            orgs["name"] = item.get('name', '')
            orgs["oid"] = item.get('id')
            orgs["is_project"] = item.get('project')
            orgs["is_inactive"] = item.get('inactive')
            orgs["is_demo"] = item.get('demo')
            parsed.append(orgs)
        return parsed
    except TypeError as error:
        raise error
    
def writeCSV(fileName, contents):
    """ Write contents to output file. 
    
        :param filename: a string, name for file including.
        :param contents: json data, file contents.
        :raises: IOError: if unable to write to file. """
    try:
        with open(fileName, 'w') as o:
            csv_writer = csv.writer(o)
            count = 0
            for item in contents:
                if count == 0:
                    header = item.keys()
                    csv_writer.writerow(header)
                    count += 1
                csv_writer.writerow(item.values())
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
    fileName = f"{args.path}Org_IDs_Report_{str(datetime.utcnow())}"
    token = args.token
    if token == None:
        token = getpass(prompt="Enter your Account API Key: ")
    orgData = getOIDs(args.consoleURL, token)
    orgOIDs = parseOIDs(orgData)
    if args.output == 'json':
        fileName = f'{fileName}.json'
        writeFile(fileName, json.dumps(orgOIDs))
    elif args.output == 'txt':
        fileName = f'{fileName}.txt'
        stringList = []
        for line in orgOIDs:
            stringList.append(str(line).replace('{', '').replace('}', '').replace(': ', '='))
        textFile = '\n'.join(stringList)
        writeFile(fileName, textFile)
    elif args.output == 'csv':
        fileName = f'{fileName}.csv'
        writeCSV(fileName, orgOIDs)  
    else:
        for line in orgOIDs:
            print(json.dumps(line, indent=4))

if __name__ == "__main__":
    main()