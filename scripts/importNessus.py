""" EXAMPLE PYTHON SCRIPT! NOT INTENDED FOR PRODUCTION USE! 
    importNessus.py, version 4.0
    Bulk import all .nessus files in a specified folder via the runZero API."""

import argparse
import csv
import json
import os
import re
import requests
import subprocess
from datetime import datetime
from getpass import getpass
from requests.exceptions import ConnectionError

def parseArgs():
    parser = argparse.ArgumentParser(description="Bulk import all .nessus files in a specified folder.")
    parser.add_argument('-u', '--url', dest='consoleURL', help='URL of console. This argument will take priority over the .env file', 
                        required=False, default=os.environ["RUNZERO_BASE_URL"])
    parser.add_argument('-k', '--key', dest='token', help='Prompt for Organization API key (do not enter at command line). This argument will take priority over the .env file', 
                        nargs='?', const=None, required=False, default=os.environ["RUNZERO_ORG_TOKEN"])
    parser.add_argument('-s', '--site', help='UUID of site to upload nessus scan info to. This argument will take priority over the .env file', 
                        required=False, default=os.environ["RUNZERO_SITE_ID"])
    parser.add_argument('-d', '--dir', help='Path to fetch nessus scan files from. This argument will take priority over the .env file', 
                        required=False, default=os.environ["NESSUS_DIR"])
    parser.add_argument('-p', '--path', help='Path to write log files. This argument will take priority over the .env file', 
                        required=False, default=os.environ["SAVE_PATH"])
    parser.add_argument('-c', '--clean', help='Enable file clean up. Automatically delete .nessus files that are successfully uploaded', action='store_true', required=False)
    parser.add_argument('-l', '--log', dest='log', help='Write results to log file in selected format', choices=['txt', 'json', 'csv'], required=False)
    parser.add_argument('--version', action='version', version='%(prog)s 4.0')
    return parser.parse_args()

def importScan(url, token, siteID, scan):
    """ Upload a .nessus scan file . 
    
        :param uri: A string, URL of the runZero console.
        :param token: A string, Organization API key
        :param siteID: A string, the site ID of the Site to apply scan to.
        :param scan: A .nessus file, Nessus scan file to upload.
        :returns: Dict Object, JSON formatted.
        :raises: ConnectionError: if unable to successfully make PUT request to console."""

    url = f"{url}/api/v1.0/org/sites/{siteID}/import/nessus"
    payload = ""
    file = [('application/octet-stream',(scan,open(scan,'rb'),'application/octet-stream'))]
    headers = {'Accept': 'application/octet-stream',
               'Authorization': f'Bearer {token}'}
    try:
        response = requests.put(url, headers=headers, data=payload, files=file)
        code = response.status_code
        content = response.content
        data = json.loads(content)
        return(code, data)
    except ConnectionError as error:
        raise error
    
def fileUpload(url, token, site, dir):
    uploadLog = []
    try:     
        contents = subprocess.check_output(['ls', dir]).splitlines()
        for item in contents:
            fileName = re.match("b'((.*)\.(nessus))", str(item))
            if fileName is not None:
                fileType = subprocess.check_output(['file', dir + fileName.group(1)])
                if fileName.group(3) == "nessus" and 'XML' in str(fileType):
                    response = importScan(url, token, site, f'{dir}{fileName.group(1)}')
                    entry = {}
                    if response[0] == 200 and response[1]['error'] == '':
                        entry['File Name'] = fileName.group(1) 
                        entry['Status'] = 'success'
                    else:
                        entry['File Name'] = fileName.group(1)
                        entry['Status'] = 'fail'
                    uploadLog.append(entry)
                else:
                    pass
    except OSError as error:
        uploadLog.append({error : 'A connection to the runZero console could not be established'})
    return uploadLog
    
def cleanUp(path, log):
    """Remove nessus files that are uploaded successfully.

        :param path: A String, path to nessus file location(s).
        :param log: A Dict, dictionary of nessus filenames and upload status.
        :returns None: this function returns nothing but removes files from disk.
        :raises: IOerror, if unable to delete file."""
    
    for entry in log:
        if entry['Status'] == 'success':
            try:
                os.remove(path + entry['File Name'])
            except IOError as error:
                print(error)
        else:
            pass

def writeCSV(fileName, contents):
    """ Write contents to output file. 
    
        :param filename: a string, name for file including.
        :param contents: json data, file contents.
        :raises: IOError: if unable to write to file. """
    try:
        with open(f'{fileName}', 'w') as o:
            fieldNames = ['File Name', 'Status']
            csv_writer = csv.DictWriter(o, fieldNames)
            csv_writer.writeheader()
            for entry in contents:
                csv_writer.writerow(entry)
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
    token = args.token
    if token == None:
        token = getpass(prompt="Enter your Organization API Key: ")
    uploadLog = fileUpload(args.consoleURL, token, args.site, args.dir)
    if args.log is not None:
        fileName = f'{args.path}importNessus_log_{str(datetime.now())}'
        if args.log == 'json':
                fileName = f'{fileName}.json'
                writeFile(fileName, json.dumps(uploadLog))
        elif args.log == 'txt':
            fileName = f'{fileName}.txt'
            stringList = []
            for line in uploadLog:
                stringList.append(str(line).replace('{', '').replace('}', '').replace(': ', '='))
            textFile = '\n'.join(stringList)
            writeFile(fileName, textFile)
        elif args.log == 'csv':
            fileName = f'{fileName}.csv'
            writeCSV(fileName, uploadLog)
    else:
        print(json.dumps(uploadLog, indent=4))
    if args.clean:
        cleanUp(args.dir, uploadLog)

if __name__ == "__main__":
    main()

