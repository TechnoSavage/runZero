#!/usr/bin/python

""" EXAMPLE PYTHON SCRIPT! NOT INTENDED FOR PRODUCTION USE! 
    orgIDs.py, version 3.0 by Derek Burke
    Script to retrieve all Organization IDs and 'friendly' names for a given account. """

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
                    orgIDs.py [arguments]

                    You will be prompted to provide your runZero Account API key if it
                    is not specified in the .env file. Default bahavior is to write output 
                    to stdout.

                    Optional arguments:

                    -u <uri>              URI of console (default is https://console.runzero.com)
                    -j                    Write output in JSON format
                    -f                    Write output to specified file (plain text default)
                                          combine with -j for JSON
                    -h --help             Show this help dialogue
                    
                    Examples:
                    orgIDs.py 
                    orgIDs.py -j -f output.json
                    python3 -m orgIDs -u https://custom.runzero.com -f output.txt """)

def getOIDs(uri, token):
    """ Retrieve Organizational IDs from Console.

           :param token: A string, Account API Key.
           :returns: A JSON object, runZero Org data.
           :raises: ConnectionError: if unable to successfully make GET request to console."""

    uri = uri + "/api/v1.0/account/orgs"
    payload = ""
    headers = {'Accept': 'application/json',
               'Authorization': 'Bearer %s' % token}
    try:
        response = requests.get(uri, headers=headers, data=payload)
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
        :raises: TypeError: if data variable passed is not JSON format.
        :raises: KeyError: if dict key is incorrect or doesn't exist. """
    try:
        parsed = []
        for item in data:
            orgs = {}
            orgs["name"] = item["name"]
            orgs["oid"] = item["id"]
            orgs["is_project"] = item["project"]
            orgs["is_inactive"] = item["inactive"]
            orgs["is_demo"] = item["demo"]
            parsed.append(orgs)
        return parsed
    except TypeError as error:
        raise error
    except KeyError as error:
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

if __name__ == "__main__":
    if "-h" in sys.argv:
        usage()
        exit()
    consoleURL = os.environ["CONSOLE_BASE_URL"]
    token = os.environ["RUNZERO_ACCOUNT_TOKEN"]
    formatJSON = False
    saveFile = False
    #Output report name; default uses UTC time
    fileName = "Org_IDs_Report_" + str(datetime.utcnow())
    if token == '':
        token = getpass(prompt="Enter your Account API Key: ")
    if "-u" in sys.argv:
        try:
            consoleURL = sys.argv[sys.argv.index("-u") + 1]
        except IndexError as error:
            print("URI switch used but URI not provided!\n")
            usage()
            exit()
    if "-j" in sys.argv:
        formatJSON = True
    if "-f" in sys.argv:
        saveFile = True
    if consoleURL == '':
         consoleURL = input('Enter the URL of the console (e.g. http://console.runzero.com): ')

    orgData = getOIDs(consoleURL, token)
    orgOIDs = parseOIDs(orgData)
    if formatJSON:
        if saveFile:
            fileName = fileName + '.json'
            JSON = json.dumps(orgOIDs, indent=4)
            writeFile(fileName, JSON)
        else:
            print(json.dumps(orgOIDs, indent=4))
    else:
        if saveFile:
            fileName = fileName + '.txt'
            stringList = []
            for line in orgOIDs:
                stringList.append(str(line))
            textFile = '\n'.join(stringList)
            writeFile(fileName, textFile)
        else:
            for line in orgOIDs:
                print(line)
