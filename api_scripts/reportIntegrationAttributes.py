""" EXAMPLE PYTHON SCRIPT! NOT INTENDED FOR PRODUCTION USE! 
    reportIntegrationAttributes.py, version 1.0
    Specify an integration source in order to generate a list of all discovered attributes reported by that source."""

import argparse
import datetime
import json
import os
import requests
from getpass import getpass
from requests.exceptions import ConnectionError
    
def parseArgs():
    parser = argparse.ArgumentParser(description="Report all attributes provided by a source.")
    parser.add_argument('-u', '--url', dest='consoleURL', help='URL of console. This argument will take priority over the .env file', 
                        required=False, default=os.environ["RUNZERO_BASE_URL"])
    parser.add_argument('-k', '--key', dest='token', help='Prompt for Export API key (do not enter at command line). This argument will take priority over the .env file', 
                        nargs='?', const=None, required=False, default=os.environ["RUNZERO_EXPORT_TOKEN"])
    parser.add_argument('-s', '--search', help='integration source to query, name must conform to runZero query syntax source value.', 
                        required=True)
    parser.add_argument('-p', '--path', help='Path to write file. This argument will take priority over the .env file', 
                        required=False, default=os.environ["SAVE_PATH"])
    parser.add_argument('-o', '--output', dest='output', help='output file format', choices=['txt', 'json', 'csv', 'excel', 'html'], required=False)
    parser.add_argument('--version', action='version', version='%(prog)s 1.0')
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
        if response.status_code != 200:
            print('failed to retrieve assets, bad status code!')
            exit()
        content = response.content
        data = json.loads(content)
        return data
    except ConnectionError as error:
        content = "No Response"
        raise error
    
def parseAttributes(data, source):
    """Search assets "foreign attributes" and extract all keys pertaining to the source.
     
       :param data: a dict, runZero JSON asset data.
       :param source: a string, the integration source to extract keys from.
       :returns: a dict: parsed runZero asset data.
       :raises: TypeError: if dataset is not iterable."""
    
    forAttrKey = f'@{source}.dev'
    try:
        #Gather all integration source information into one list
        sourceList = []
        for item in data:
            for source in item['foreign_attributes'][forAttrKey]:
                sourceList.append(source)
        #Gather all integration keys (attributes) in a list
        attributeList = []
        for item in sourceList:
            for key in item:
                attributeList.append(key)
        # Deduplicate keys
        attributeList = set(attributeList)
        return(attributeList)
    except TypeError as error:
        raise error
    except AttributeError as error:
        print("Data is not JSON object; make sure provided API key is correct")
        exit()
    
#Output formats require some finessing
def outputFormat(format, fileName, data):
    """ Determine output format and call function to write appropriate file.
        
        :param format: A String, the desired output format.
        :param filename: A String, the filename, minus extension.
        :param data: json data, file contents
        :returns None: Calls another function to write the file or prints the output."""
    
    if format == 'txt':
        fileName = f'{fileName}.txt'
        textFile = '\n'.join(data)
        writeFile(fileName, textFile)
    else:
        for item in data:
            print(item)
    
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
    fileName = f"{args.path}Asset_Serial_Numbers_{str(datetime.datetime.now(datetime.timezone.utc))}"
    token = args.token
    if token == None:
        token = getpass(prompt="Enter your Export API Key: ")
    #Query to grab all assets with the specified source
    search = f'source:{args.search}'
    #specify only return of foreign attributes
    fields = 'foreign_attributes'
    assets = getAssets(args.consoleURL, token, search, fields)
    results = parseAttributes(assets, args.search)
    outputFormat(args.output, fileName, sorted(results))
    
if __name__ == "__main__":
    main()