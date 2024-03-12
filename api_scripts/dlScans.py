""" EXAMPLE PYTHON SCRIPT! NOT INTENDED FOR PRODUCTION USE! 
    dlScans.py, version 2.1
    This script will download the scan data from the last 'n' processed tasks in an organization, 
    as specified by the user."""

import argparse
import json
import os
import requests
from getpass import getpass
from requests.exceptions import ConnectionError
    
def parseArgs():
    parser = argparse.ArgumentParser(description="Download scan data from the last 'N' processed tasks.")
    parser.add_argument('-t', '--tasks', dest='taskNo', help='Number of tasks, from most recent to oldest to download. This argument will override the .env file', 
                        type=int, required=False, default=os.environ["TASK_NO"])
    parser.add_argument('-u', '--url', dest='consoleURL', help='URL of console. This argument will override the .env file', 
                        required=False, default=os.environ["RUNZERO_BASE_URL"])
    parser.add_argument('-k', '--key', dest='token', help='Prompt for Organization API key (do not enter at command line). This argument will override the .env file', 
                        nargs='?', const=None, required=False, default=os.environ["RUNZERO_ORG_TOKEN"])
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
    payload = {'search': 'type": "scan',
               'status':'processed'}
    headers = {'Accept': 'application/json',
               'Authorization': f'Bearer {token}'}
    try:
        response = requests.get(url, headers=headers, params=payload)
        content = response.content
        data = json.loads(content)
        print(data)
        return data
    except ConnectionError as error:
        raise error

def parseIDs(data, taskNo=1000):
    """ Extract task IDs from supplied recent task data. 
    
            :param data: JSON object, runZero task data.
            :param taskNo: an Integer, number of tasks to process.
            :returns: A List, list of task IDs.
            :raises: TypeError: if data variable passed is not JSON format. """
    
    try:
        taskIDs = [item.get('id') for counter, item in enumerate(data) if counter <= taskNo - 1]
        return taskIDs
    except TypeError as error:
        raise error

def getData(url, token, taskID, path):
    """ Download and write scan data (.json.gz) for each task ID provided.

           :param url: A string, URL of the runZero console.
           :param token: A string, Organization API key.
           :param taskID: A string, ID of scan task to download.
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
        with open( f"{path}scan_{taskID}.json.gz", 'wb') as f:
            for chunk in response.iter_content(chunk_size=128):
                f.write(chunk)
    except ConnectionError as error:
        raise error
    except IOError as error:
        raise error
    
def main():
    args = parseArgs()
    token = args.token
    if token == None:
        token = getpass(prompt="Enter your Organization API Key: ")
    taskInfo = getTasks(args.consoleURL, token)
    idList = parseIDs(taskInfo, args.taskNo)
    for id in idList:
        getData(args.consoleURL, token, id, args.path)

if __name__ == "__main__":
    main()