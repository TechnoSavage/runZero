""" EXAMPLE PYTHON SCRIPT! NOT INTENDED FOR PRODUCTION USE! 
    importNessus.py, version 5.0
    Bulk import all .nessus files in a specified folder via the runZero API."""

import argparse
import logging
import os
import re
import requests
import subprocess
from getpass import getpass
from requests.exceptions import ConnectionError

logger = logging.getLogger(__name__)

def parseArgs():
    parser = argparse.ArgumentParser(description="Bulk import all .nessus files in a specified folder.")
    parser.add_argument('-u', '--url', dest='consoleURL', help='URL of console. This argument will take priority over the .env file', 
                        required=False, default=os.environ["RUNZERO_BASE_URL"])
    parser.add_argument('-k', '--key', dest='token', help='Prompt for Organization API key (do not enter at command line). This argument will take priority over the .env file', 
                        nargs='?', const=None, required=False, default=os.environ["RUNZERO_ORG_TOKEN"])
    parser.add_argument('-s', '--site', help='UUID of site to upload nessus scan info to. This argument will take priority over the .env file', 
                        required=False, default=os.environ["RUNZERO_SITE_ID"])
    parser.add_argument('-p', '--path', help='Path to fetch nessus scan files from. This argument will take priority over the .env file', 
                        required=False, default=os.environ["NESSUS_DIR"])
    parser.add_argument('-c', '--clean', help='Enable file clean up. Automatically delete .nessus files that are successfully uploaded', action='store_true', required=False)
    parser.add_argument('-l', '--log', help='Path to write log file. This argument will take priority over the .env file', 
                        required=False, default=os.environ["LOG_PATH"])
    parser.add_argument('--version', action='version', version='%(prog)s 5.0')
    return parser.parse_args()

def import_scan(url, token, site_id, scan):
    '''
        Upload a .nessus scan file . 
    
        :param url: A string, URL of the runZero console.
        :param token: A string, Organization API key
        :param site_id: A string, the site ID of the Site to apply scan to.
        :param scan: A .nessus file, Nessus scan file to upload (including path).
        :returns: Dict Object, JSON formatted.
        :raises: ConnectionError: if unable to successfully make PUT request to console.
    '''

    url = f"{url}/api/v1.0/org/sites/{site_id}/import/nessus"
    payload = ''
    file = [('application/octet-stream',(scan,open(scan,'rb'),'application/octet-stream'))]
    headers = {'Accept': 'application/octet-stream',
               'Authorization': f'Bearer {token}'}
    try:
        logger.info(f"Making PUT request to {url} to upload {scan}")
        response = requests.put(url, headers=headers, data=payload, files=file)
        code = response.status_code
        content = response.json()
        return(code, content)
    except ConnectionError:
        logger.exception('Could not establish connection to console URL, exiting...')
        exit()
    
def file_upload(url, token, site_id, path):
    '''
        Identify nessus files in a directory and pass them
        to importScan function. 
    
        :param url: A string, URL of the runZero console.
        :param token: A string, Organization API key
        :param site_id: A string, the site ID of the Site to upload to.
        :param path: A string, the directory/folder path containing the nessus scans.
        :returns: Dict Object, JSON formatted.
        :raises: OSError: if unable to run subprocess commands.
    '''

    upload_results = []
    try:     
        contents = subprocess.check_output(['ls', path]).splitlines()
        for item in contents:
            filename = re.match("b'((.*)\\.(nessus))", str(item))
            if filename is not None:
                file_type = subprocess.check_output(['file', path + filename.group(1)])
                if filename.group(3) == "nessus" and 'XML' in str(file_type):
                    logger.info(f"")
                    response = import_scan(url, token, site_id, f'{path}{filename.group(1)}')
                    entry = {}
                    if response[0] == 200 and response[1]['error'] == '':
                        entry['File Name'] = filename.group(1) 
                        entry['Status'] = 'success'
                    else:
                        entry['File Name'] = filename.group(1)
                        entry['Status'] = 'fail'
                    upload_results.append(entry)
                else:
                    pass
    except OSError:
        logger.exception(f"Could not locate valid Nessus file(s) in provided path {path}.")
        exit()
    return upload_results
    
def clean_up(path, results):
    '''
        Remove nessus files that are uploaded successfully.

        :param path: A String, directory path to nessus file location(s).
        :param results: A Dict, dictionary of nessus filenames and upload status.
        :returns None: this function returns nothing but removes files from disk.
        :raises: IOerror, if unable to delete file.
    '''
    
    for entry in results:
        if entry['Status'] == 'success':
            try:
                logger.info(f"Attempting to delete file {entry['File Name']}.")
                os.remove(path + entry['File Name'])
                logger.info(f"file {entry['File Name']} deleted successfully.")
            except IOError:
                logger.exception(f"The file {entry['File Name']} could not be deleted.")
        else:
            pass
    
def main():
    args = parseArgs()
    logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%a, %d %b %Y %H:%M:%S', filename=f'{args.log}/importNessus.log', level=logging.INFO)
    logger.info('Started.')
    token = args.token
    if token == None:
        token = getpass(prompt="Enter your Organization API Key: ")
    upload_results = file_upload(args.consoleURL, token, args.site, args.path)
    if args.clean:
        clean_up(args.path, upload_results)
    logger.info('Finished.')

if __name__ == "__main__":
    main()
