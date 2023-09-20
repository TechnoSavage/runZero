""" EXAMPLE PYTHON SCRIPT! NOT INTENDED FOR PRODUCTION USE! 
    dlScans.py, version 1.2 by Derek Burke
    This script will download the scan data from the last 'n' processed tasks in an organization, 
    as specified by the user."""

import json
import os
import requests
import sys
from getpass import getpass
from requests.exceptions import ConnectionError

def usage():
    """ Display usage and switches. """

    print(""" Usage:
                    scanSync.py [arguments]

                    You will be prompted to provide a runZero Organization API key for the console unless
                    it is included in a specified config file.
                    
                    Optional arguments:

                    -u <url>              URL of the runZero console, this argument will take priority over the .env file
                    -k                    Prompt for Organization API key, this argument will take priority over the .env file
                    -t <1-1000>           Number of tasks to fetch from the console, this argument will take priority over the .env file
                    -h                    Show this help dialogue
                    
                Examples:
                    dlScans.py -t 500
                    python3 -m dlScans -c https://custom.runzero.com -t 1""")
    
def getTasks(uri, token): 
    """ Retrieve Tasks from Organization corresponding to supplied token.

           :param uri: A string, URL of the runZero console.
           :param token: A string, Account API Key.
           :returns: A JSON object, runZero task data.
           :raises: ConnectionError: if unable to successfully make GET request to console."""
    
    uri = f"{uri}/api/v1.0/org/tasks"
    payload = {'search':'scan',
               'status':'processed'} #change {'search':'scan'} to {'search':'sample'} to retrieve traffic sampling tasks 
    headers = {'Accept': 'application/json',
               'Authorization': f'Bearer {token}'}
    try:
        response = requests.get(uri, headers=headers, params=payload)
        content = response.content
        data = json.loads(content)
        return data
    except ConnectionError as error:
        raise error

def parseIDs(data, taskNo=1000):
    """ Extract relevant fields from task data and tally new assets. 
    
            :param data: JSON object, runZero task data.
            :param taskNo: an Integer, number of tasks to process.
            :returns: A List, list of task IDs.
            :raises: TypeError: if data variable passed is not JSON format.
            :raises: KeyError: if dict key is incorrect or doesn't exist. """
    
    iters = 0
    taskIDs = []
    try:
        for item in data:
            if iters >= taskNo:
                break
            else:
                taskIDs.append(item['id'])
                iters += 1
        return taskIDs
    except TypeError as error:
        raise error
    except KeyError as error:
        raise error

def getData(uri, token, taskID, path):
    """ Download and write scan data (.json.gz) for each task ID provided.

           :param uri: A string, URL of the runZero console.
           :param token: A string, Organization API key.
           :param taskID: A string, ID of scan task to download.
           :param path: A string, path to write files to.
           :returns: None, this function returns no data but writes files to disk.
           :raises: ConnectionError: if unable to successfully make GET request to console.
           :raises: IOError: if unable to write file."""
    
    uri = f"{uri}/api/v1.0/org/tasks/{taskID}/data"
    payload = ""
    headers = {'Accept': 'application/json',
               'Authorization': f'Bearer {token}'}
    try:
        response = requests.get(uri, headers=headers, data=payload, stream=True)
        with open( f"{path}scan_{taskID}.json.gz", 'wb') as f:
            for chunk in response.iter_content(chunk_size=128):
                f.write(chunk)
    except ConnectionError as error:
        raise error
    except IOError as error:
        raise error
    
def main():
    if "-h" in sys.argv:
        usage()
        exit()
    consoleURL = os.environ['RUNZERO_BASE_URL']
    token = os.environ['RUNZERO_ORG_TOKEN']
    tasks = int(os.environ['TASK_NO'])
    path = os.environ['SAVE_PATH']
    if "-u" in sys.argv:
        try:
            consoleURL = sys.argv[sys.argv.index("-u") + 1]
        except IndexError as error:
            print("URL switch used but URL not provided!\n")
            usage()
            exit()
    if "-k" in sys.argv:
        token = getpass(prompt="Enter your Organization API Key: ")
        if token == '':
            print("No API token provided!\n")
            usage()
            exit()
    if "-t" in sys.argv:
        try:
            tasks = int(sys.argv[sys.argv.index("-t") + 1])
        except ValueError as error:
            raise error
        except IndexError as error:
            print("Task switch used but task number not provided!\n")
            usage()
            exit()
    taskInfo = getTasks(consoleURL, token)
    idList = parseIDs(taskInfo, tasks)
    for id in idList:
        getData(consoleURL, token, id, path)

if __name__ == "__main__":
    main()