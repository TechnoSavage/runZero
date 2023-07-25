""" EXAMPLE PYTHON SCRIPT! NOT INTENDED FOR PRODUCTION USE! 
    scanSync.py, version 1.0 by Derek Burke
    This script is designed to sync task data from one console to another by downloading the last 'n' successful tasks
    from one console and uploading them to another. Example use case, download external scan tasks from a SaaS console
    and import them into a self-hosted instance. The script will attempt to automatically delete local files it creates."""

import json
import os
import re
import requests
import sys
import subprocess
from getpass import getpass
from requests.exceptions import ConnectionError

def usage():
    """ Display usage and switches. """
    print(""" Usage:
                    scanSync.py [arguments]

                    You will be prompted to provide a runZero Organization API key for each console unless
                    it is included in a specified config file.
                    
                    Optional arguments:

                    -s <url>              URL of the source (download) console, this argument will take priority over the .env file
                    -d <url>              URL of the destination (upload) console, this argument will take priority over the .env file
                    -k                    Prompt for source Organization API key, this argument will take priority over the .env file
                    -q                    Prompt for destination Organization API key, this argument will take priority over the .env file
                    -l <site ID>          UUID of the site to upload scan data to, this argument will take priority over the .env file
                    -p <path>             Specify the path to the task data save location, this argument will take priority over the .env file
                    -t <1-1000>           Number of tasks to fetch from console, this argument will take priority over the .env file
                    -h                    Show this help dialogue
                    
                Examples:
                    scanSync.py -t 5
                    python3 -m scanSync -s https://custom.runzero.com -d https://custom.runzero.com -t 2""")
    
def getTasks(uri, token): 
    """ Retrieve Tasks from Organization corresponding to supplied token.

           :param uri: A string, URL of the runZero console.
           :param token: A string, Account API Key.
           :returns: A JSON object, runZero task data.
           :raises: ConnectionError: if unable to successfully make GET request to console."""
    
    uri = uri + "/api/v1.0/org/tasks"
    payload = {'search':'scan',
               'status':'processed'} #change {'search':'scan'} to {'search':'sample'} to retrieve traffic sampling tasks 
    headers = {'Accept': 'application/json',
               'Authorization': 'Bearer %s' % token}
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
           :param taskID: A string, UUID of scan task to download.
           :param path: A string, path to write files to.
           :returns: None, this function returns no data but writes files to disk.
           :raises: ConnectionError: if unable to successfully make GET request to console.
           :raises: IOError: if unable to write file."""
    
    uri = uri + "/api/v1.0/org/tasks/%s/data" % taskID
    payload = ""
    headers = {'Accept': 'application/json',
               'Authorization': 'Bearer %s' % token}
    try:
        response = requests.get(uri, headers=headers, data=payload, stream=True)
        with open( path + 'scan_' + id + '.json.gz', 'wb') as f:
            for chunk in response.iter_content(chunk_size=128):
                f.write(chunk)
    except ConnectionError as error:
        raise error
    except IOError as error:
        raise error
        
def uploadData(uri, token, site_id, path, taskData):
    """ Upload task Data to console.

        :param uri: A string, URL of the runZero console.
        :param token: a string, Organization API key.
        :param site_id: A string, UUID of site to upload scan to.
        :param path: A string, directory path to scan data file.
        :param taskData: A string, filename of the scan data (json.gz) file.
        :raises: TypeError: if data variable passed is not JSON format.
        :raises: ConnectionError: if unable to successfully make GET request to console."""
    
    uri = uri + "/api/v1.0/org/sites/%s/import" % site_id
    file = [('application/octet-stream',(taskData,open(path + taskData,'rb'),'application/octet-stream'))]
    headers = {'Accept': 'application/json',
               'Content-Type': 'application/octet-stream',
               'Authorization': 'Bearer %s' % token}
    try:
        response = requests.put(uri, headers=headers, data=file, stream=True)
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

    handle = 'scan_' + taskID + '.json.gz'
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
        
if __name__ == "__main__":
    if "-h" in sys.argv:
        usage()
        exit()
    srcURL = os.environ['CONSOLE_SOURCE_URL']
    dstURL = os.environ['CONSOLE_BASE_URL']
    srcTok = os.environ['SOURCE_ORG_TOKEN']
    dstTok = os.environ['RUNZERO_ORG_TOKEN']
    siteID = os.environ['SITE_ID']
    tasks = int(os.environ['TASK_NO'])
    path = os.environ['SAVE_PATH']
    if "-s" in sys.argv:
        try:
            srcURL = sys.argv[sys.argv.index("-s") + 1]
        except IndexError as error:
            print("source URL switch used but URL not provided!\n")
            usage()
            exit()
    if "-d" in sys.argv:
        try:
            dstURL = sys.argv[sys.argv.index("-d") + 1]
        except IndexError as error:
            print("destination URL switch used but URL not provided!\n")
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
    if "-k" in sys.argv:
        token = getpass(prompt="Enter the Organization API Key for the source console: ")
        if token == '':
            print("No API token provided!\n")
            usage()
            exit()
    if "-q" in sys.argv:
        token = getpass(prompt="Enter the Organization API Key for the destination console: ")
        if token == '':
            print("No API token provided!\n")
            usage()
            exit()
    if "-l" in sys.argv:
        try:
            siteID = sys.argv[sys.argv.index("-l") + 1]
        except IndexError as error:
            print("Site ID switch used but site ID not provided!\n")
            usage()
            exit()
    if "-p" in sys.argv:
        try:
            path = sys.argv[sys.argv.index("-p") + 1]
        except IndexError as error:
            print("Path switch used but directory not provided!\n")
            usage()
            exit()
    taskInfo = getTasks(srcURL, srcTok)
    idList = parseIDs(taskInfo, tasks)
    for id in idList:
        taskData = getData(srcURL, srcTok, id, path)
        try:
            response = uploadData(dstURL, dstTok, siteID, path, 'scan_' + id + '.json.gz')
            cleanUp(id, path)
        except OSError as error:
            print(error)
    
