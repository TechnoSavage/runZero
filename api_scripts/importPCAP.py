""" EXAMPLE PYTHON SCRIPT! NOT INTENDED FOR PRODUCTION USE! 
    importPCAP.py, version 1.4
    Bulk import all packet capture files in a specified folder via the runZero API."""

import argparse
import json
import os
import pandas as pd
import re
import requests
import subprocess
from datetime import datetime, timezone
from getpass import getpass
from requests.exceptions import ConnectionError

def parseArgs():
    parser = argparse.ArgumentParser(description="Bulk import all packet capture files in a specified folder.")
    parser.add_argument('-u', '--url', dest='consoleURL', help='URL of console. This argument will take priority over the .env file', 
                        required=False, default=os.environ["RUNZERO_BASE_URL"])
    parser.add_argument('-k', '--key', dest='token', help='Prompt for Organization API key (do not enter at command line). This argument will take priority over the .env file', 
                        nargs='?', const=None, required=False, default=os.environ["RUNZERO_ORG_TOKEN"])
    parser.add_argument('-s', '--site', help='UUID of site to upload captures to. This argument will take priority over the .env file', 
                        required=False, default=os.environ["RUNZERO_SITE_ID"])
    parser.add_argument('-d', '--dir', help='Path to fetch capture files from. This argument will take priority over the .env file', 
                        required=False, default=os.environ["PACKET_DIR"])
    parser.add_argument('-p', '--path', help='Path to write log files. This argument will take priority over the .env file', 
                        required=False, default=os.environ["SAVE_PATH"])
    parser.add_argument('-c', '--clean', help='Enable file clean up. Automatically delete capture files that are successfully uploaded', action='store_true', required=False)
    parser.add_argument('-l', '--log', dest='log', help='Write results to log file in selected format', choices=['txt', 'json', 'csv', 'excel', 'html'], required=False)
    parser.add_argument('--version', action='version', version='%(prog)s 1.4')
    return parser.parse_args()

def importPCAP(url, token, siteID, capture, name, description=""):
    '''
        Upload a capture file . 
    
        :param url: A string, URL of the runZero console.
        :param token: A string, Organization API key
        :param siteID: A string, the site ID of the Site to upload to.
        :param capture: A capture file, packet capture file to upload (including path).
        :param name: A string, a name for the import task.
        :param description: A string, a description for the import task.
        :returns: Dict Object, JSON formatted.
        :raises: ConnectionError: if unable to successfully make PUT request to console.
    '''
    
    url = f"{url}/api/v1.0/org/sites/{siteID}/import/packet"
    # params are currently ignored and PCAP API import does not support name and descripiton
    # retaining expecting that scan import params will be carried over to PCAP import as it doesn't hurt anything
    params = {'name': name,
              'description': description}
    headers = {'Accept': 'application/octet-stream',
               'Authorization': f'Bearer {token}'}
    try:
        with open(capture, 'rb') as file:
            response = requests.put(url, headers=headers, params=params, data=file, stream=True)
        code = response.status_code
        content = response.content
        data = json.loads(content)
        return(code, data)
    except ConnectionError as error:
        raise error
    
def fileUpload(url, token, siteID, dir):
    '''
        Identify packet capture in a directory and pass them
        to importPCAP function. 
    
        :param url: A string, URL of the runZero console.
        :param token: A string, Organization API key
        :param siteID: A string, the site ID of the Site to upload to.
        :param dir: A string, the directory path containing the packet capture.
        :returns: Dict Object, JSON formatted.
        :raises: OSError: if unable to run subprocess commands.
    '''

    uploadLog = []
    try:     
        contents = subprocess.check_output(['ls', dir]).splitlines()
        for item in contents:
            fileName = re.match("b'((.*)\.[p]?cap[n]?[g]?)", str(item))
            if fileName is not None:
                fileType = subprocess.check_output([f'file', dir + fileName.group(1)])
                fileDescription = re.search("(: (.*))", str(fileType))
                if 'pcap' in str(fileDescription) or 'pcapng' in str(fileDescription):
                    response = importPCAP(url, token, siteID, f'{dir}{fileName.group(1)}', fileName.group(2))
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
    
def cleanUp(dir, log):
    '''
        Remove packet capture files that are uploaded successfully.

        :param dir: A String, the directory path to packet capture location(s).
        :param log: A Dict, dictionary of packet capture filenames and upload status.
        :returns None: this function returns nothing but removes files from disk.
        :raises: IOerror, if unable to delete file.
    '''
    
    for entry in log:
        if entry['Status'] == 'success':
            try:
                os.remove(dir + entry['File Name'])
            except IOError as error:
                print(error)
        else:
            pass

def outputFormat(format, fileName, data):
    '''
        Determine output format and call function to write appropriate file.
        
        :param format: A String, the desired output format.
        :param fileName: A String, the filename, minus extension.
        :para data: json data, file contents
        :returns None: Calls another function to write the file or prints the output.
    '''
    
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
    '''
        Write contents to output file. 
    
        :param format: a string, excel, csv, or html
        :param fileName: a string, the filename, excluding extension.
        :param contents: json data, file contents.
        :raises: IOError: if unable to write to file.
    '''
    
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
    '''
        Write contents to output file in plaintext. 
    
        :param fileName: a string, name for file including (optionally) file extension.
        :param contents: anything, file contents.
        :raises: IOError: if unable to write to file.
    '''
    
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
        timestamp = str(datetime.now(timezone.utc).strftime('%y-%m-%d%Z_%H-%M-%S'))
        fileName = f'{args.path}importPacket_log_{timestamp}'
        outputFormat(args.log, fileName, uploadLog)
    else:
        print(json.dumps(uploadLog, indent=4))
    if args.clean:
        cleanUp(args.dir, uploadLog)

if __name__ == "__main__":
    main()