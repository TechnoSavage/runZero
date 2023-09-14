#!/usr/bin/python

""" EXAMPLE PYTHON SCRIPT! NOT INTENDED FOR PRODUCTION USE! 
    newAssetReport.py, version 2.3 by Derek Burke
    Query runZero API for all assets found within an Organization (tied to Export API key provided) first seen within the specified 
    time period and return select fields. Default behavior will be to print assets to stdout in JSON format. Optionally, an output 
    file format can be specified to write to."""

import json
import os
import requests
import sys
from datetime import datetime
from getpass import getpass
from requests.exceptions import ConnectionError

def usage():
    """ Display usage and switches. """
    print(""" Usage:
                    newAssetReport.py [arguments]

                    You will be prompted to provide your runZero Export API key unless it
                    is defined in the .env file.
                    
                    Optional arguments:

                    -u <uri>                URI of console (default is https://console.runzero.com)
                    -t <time span>          Time span to search for new assets e.g. 1day, 2weeks, 1month.
                    -o <text| json | all>   Output file format for report. Plain text is default.
                    -h                      Show this help dialogue
                    
                Examples:
                    newAssetReport.py -o json
                    python3 -m newAssetReport -u https://custom.runzero.com -t 1week""")
    
def getAssets(uri, token, filter=" ", fields=" "):
    """ Retrieve assets using supplied query filter from Console and restrict to fields supplied.
        
        :param uri: A string, URI of runZero console.
        :param token: A string, Export API Key.
        :param filter: A string, query to filter returned assets(" " returns all).
        :param fields: A string, comma separated string of fields to return(" " returns all).
        :returns: a dict, JSON object of assets.
        :raises: ConnectionError: if unable to successfully make GET request to console."""

    uri = uri + "/api/v1.0/export/org/assets.json?"
    params = {'search': filter,
              'fields': fields}
    payload = ''
    headers = {'Accept': 'application/json',
               'Authorization': f'Bearer {token}'}
    try:
        response = requests.get(uri, headers=headers, params=params, data=payload)
        content = response.content
        data = json.loads(content)
        return data
    except ConnectionError as error:
        content = "No Response"
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
    if "-h" in sys.argv:
        usage()
        exit()
    consoleURL = os.environ["CONSOLE_BASE_URL"]
    token = os.environ["RUNZERO_EXPORT_TOKEN"]
    timeRange = os.environ["TIME"]
    #Output report name; default uses UTC time
    fileName = "New_Asset_Report_" + str(datetime.utcnow())
    #Define config file to read from
    if token == '':
        token = getpass(prompt="Enter your Export API Key: ")
    if "-u" in sys.argv:
        try:
            consoleURL = sys.argv[sys.argv.index("-u") + 1]
        except IndexError as error:
            print("URI switch used but URI not provided!\n")
            usage()
            exit()
    if "-t" in sys.argv:
        try:
            timeRange = sys.argv[sys.argv.index("-t") + 1]
        except IndexError as error:
            print("Time Span switch used but time value not provided!\n")
            usage()
            exit()
    if consoleURL == '':
         consoleURL = input('Enter the URL of the console (e.g. http://console.runzero.com): ')
    if timeRange == '':
         timeRange = input('Enter the time range of new assets to report (e.g. 2weeks, 7days):')
    #Query to grab all assets first seen within the specified time value
    query = f"first_seen:<{timeRange}"
    #fields to return in API call; modify for more or less
    fields = "id, os, os_vendor, hw, addresses, macs, attributes"
    report = getAssets(consoleURL, token, query, fields)
    if "-o" in sys.argv and sys.argv[sys.argv.index("-o") + 1].lower() not in ('text', 'txt'):
        writeFile(fileName + '.json', json.dumps(report, indent=4))
    elif "-o" in sys.argv and sys.argv[sys.argv.index("-o") + 1].lower() in ('text', 'txt'):
        stringList = []
        for line in report:
                stringList.append(str(line))
        textFile = '\n'.join(stringList)
        writeFile(fileName + '.txt', textFile)
    else:
        print(json.dumps(report, indent=4))
    
if __name__ == "__main__":
    main()