""" EXAMPLE PYTHON SCRIPT! NOT INTENDED FOR PRODUCTION USE! 
    orgIDs.py, version 4.2
    Script to retrieve all Organization IDs and 'friendly' names for a given account. """

import argparse
import datetime
import json
import os
import pandas as pd
import requests
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
    parser.add_argument('-o', '--output', dest='output', help='output file format', choices=['txt', 'json', 'csv', 'excel'], required=False)
    parser.add_argument('--version', action='version', version='%(prog)s 4.2')
    return parser.parse_args()

def getOIDs(url, token):
    """ Retrieve Organizational IDs from Console.

           :param url: A string, URL of runZero console.
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
            orgs["id"] = item.get('id')
            orgs["is_project"] = item.get('project')
            orgs["is_inactive"] = item.get('inactive')
            orgs["is_demo"] = item.get('demo')
            parsed.append(orgs)
        return parsed
    except TypeError as error:
        raise error
    
#Output formats require some finessing
def outputFormat(format, fileName, data):
    """ Determine output format and call function to write appropriate file.
        
        :param format: A String, the desired output format.
        :param filename: A String, the filename, minus extension.
        :para data: json data, file contents
        :returns None: Calls another function to write the file or prints the output."""
    
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
    """ Write contents to output file. 
    
        :param format: a string, excel, csv, or html
        :param fileName: a string, the filename, excluding extension.
        :param contents: json data, file contents.
        :raises: IOError: if unable to write to file."""
    
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
    fileName = f"{args.path}Org_IDs_Report_{str(datetime.datetime.now(datetime.timezone.utc))}"
    token = args.token
    if token == None:
        token = getpass(prompt="Enter your Account API Key: ")
    orgData = getOIDs(args.consoleURL, token)
    if 'token is undefined or invalid: API key not found' in json.dumps(orgData):
        print("The provided Account API key appears to be invalid.")
        exit()
    orgOIDs = parseOIDs(orgData)
    outputFormat(args.output, fileName, orgOIDs)

if __name__ == "__main__":
    main()