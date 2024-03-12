""" EXAMPLE PYTHON SCRIPT! NOT INTENDED FOR PRODUCTION USE! 
    scanSync.py, version 2.1
    This script is designed to sync task data from one console to another by downloading the last 'n' successful tasks
    from one console and uploading them to another. Example use case, download external scan tasks from a SaaS console
    and import them into a self-hosted instance. The script will attempt to automatically delete local files it creates."""

import argparse
import json
import os
import re
import requests
import subprocess
from getpass import getpass
from requests.exceptions import ConnectionError
    
def parseArgs():
    parser = argparse.ArgumentParser(description="Download last 'N' scans from one console and upload them to another console.")
    parser.add_argument('-t', '--tasks', dest='taskNo', help='Number of tasks, from most recent to oldest to sync. This argument will override the .env file', 
                        type=int, required=False, default=os.environ["TASK_NO"])
    parser.add_argument('-su', '--src', dest='srcURL', help='URL of source console. This argument will override the .env file', 
                        required=False, default=os.environ["CONSOLE_SOURCE_URL"])
    parser.add_argument('-du', '--dst', dest='dstURL', help='URL of destination console. This argument will override the .env file', 
                        required=False, default=os.environ["RUNZERO_BASE_URL"])
    parser.add_argument('-sk', '--srckey', dest='srcTok', help='Prompt for source Organization API key (do not enter at command line). This argument will override the .env file', 
                        nargs='?', const=None, required=False, default=os.environ["SOURCE_ORG_TOKEN"])
    parser.add_argument('-dk', '--dstkey', dest='dstTok', help='Prompt for destination Organization API key (do not enter at command line). This argument will override the .env file', 
                        nargs='?', const=None, required=False, default=os.environ["RUNZERO_ORG_TOKEN"])
    parser.add_argument('-s', '--site', help='UUID of site to upload scan data to. This argument will override the .env file', 
                        required=False, default=os.environ["RUNZERO_SITE_ID"])
    parser.add_argument('-p', '--path', help='Path to save scan data to. This argument will override the .env file', 
                        required=False, default=os.environ["SAVE_PATH"])
    parser.add_argument('--version', action='version', version='%(prog)s 2.1')
    return parser.parse_args()
    
def getTasks(url, token): 
    """ Retrieve Tasks from Organization corresponding to supplied token.

           :param url: A string, URL of the runZero console.
           :param token: A string, Account API Key.
           :returns: A JSON object, runZero task data.
           :raises: ConnectionError: if unable to successfully make GET request to console."""
    
    url = f"{url}/api/v1.0/org/tasks"
    #change {'search':'type": "scan'} to {'search':'type": "sample'} to retrieve traffic sampling tasks 
    payload = {'search':'type": "scan',
               'status':'processed'}
    headers = {'Accept': 'application/json',
               'Authorization': f'Bearer {token}'}
    try:
        response = requests.get(url, headers=headers, params=payload)
        content = response.content
        data = json.loads(content)
        return data
    except ConnectionError as error:
        raise error

def parseIDs(data, taskNo=1000):
    """ Extract task IDs from supplied task data. 
    
            :param data: JSON object, runZero task data.
            :param taskNo: an Integer, number of tasks to process.
            :returns: A List, list of task IDs.
            :raises: TypeError: if data variable passed is not JSON format."""
    
    try:
        taskIDs = [item.get('id') for counter, item in enumerate(data) if counter <= taskNo - 1]
        return taskIDs
    except TypeError as error:
        raise error

def getData(url, token, taskID, path):
    """ Download and write scan data (.json.gz) for each task ID provided.

           :param url: A string, URL of the runZero console.
           :param token: A string, Organization API key.
           :param taskID: A string, UUID of scan task to download.
           :param path: A string, path to write files to.
           :returns: None, this function returns no data but writes files to disk.
           :raises: ConnectionError: if unable to successfully make GET request to console.
           :raises: IOError: if unable to write file."""
    
    url = f"{url}/api/v1.0/org/tasks/{taskID}/data"
    payload = ""
    headers = {'Accept': 'application/json',
               'Authorization': f'Bearer {token}'}
    try:
        response = requests.get(url, headers=headers, data=payload, stream=True)
        with open( f'{path}scan_{taskID}.json.gz', 'wb') as f:
            for chunk in response.iter_content(chunk_size=128):
                f.write(chunk)
    except ConnectionError as error:
        raise error
    except IOError as error:
        raise error
        
def uploadData(url, token, site_id, path, taskData):
    """ Upload task Data to console.

        :param url: A string, URL of the runZero console.
        :param token: a string, Organization API key.
        :param site_id: A string, UUID of site to upload scan to.
        :param path: A string, directory path to scan data file.
        :param taskData: A string, filename of the scan data (json.gz) file.
        :raises: ConnectionError: if unable to successfully make PUT request to console."""
    
    url = f"{url}/api/v1.0/org/sites/{site_id}/import"
    headers = {'Content-Type': 'application/octet-stream',
               'Content-Encoding': 'gzip',
               'Authorization': f'Bearer {token}'}
    try:
        with open(path + taskData, 'rb') as file:
            response = requests.put(url, headers=headers, data=file, stream=True)
            content = response.content
            data = json.loads(content)
        return data
    except ConnectionError as error:
        content = "No Response"
        raise error
        
def cleanUp(taskID, path):
    """Remove task data files created by getData funtion.

        :param taskID: A String, UUID of task to identify scan file to delete.
        :param path: A String, path used in getData to create scan files.
        :returns None: this function returns nothing but removes files from disk.
        :raises: IOerror, if unable to delete file."""

    handle = f"scan_{taskID}.json.gz"
    try:
        dir_contents = subprocess.check_output(['ls', path]).splitlines()
        for item in dir_contents:
            fileName = re.match("b'((scan_.*)\.(json\.gz))", str(item))
            if fileName is not None and fileName.group(1) == handle:
                    os.remove(path + handle)
            else:
                pass
    except IOError as error:
        raise error
    
def main():
    args = parseArgs()
    srcTok = args.srcTok    
    if srcTok == None:
        srcTok = getpass(prompt="Enter the Organization API Key for the source console: ")
    dstTok = args.dstTok
    if dstTok == None:
        dstTok = getpass(prompt="Enter the Organization API Key for the destination console: ")
    taskInfo = getTasks(args.srcURL, srcTok)
    idList = parseIDs(taskInfo, args.taskNo)
    for id in idList:
        getData(args.srcURL, srcTok, id, args.path)
        try:
            uploadData(args.dstURL, dstTok, args.site, args.path, f"scan_{id}.json.gz")
            cleanUp(id, args.path)
        except OSError as error:
            print(error)
        
if __name__ == "__main__":
    main()