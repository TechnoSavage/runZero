""" EXAMPLE PYTHON SCRIPT! NOT INTENDED FOR PRODUCTION USE! 
    dlTasks.py, version 3.0
    This script will download the scan data from the last 'n' processed tasks in an organization, 
    as specified by the user."""

import argparse
import json
import logging
import os
import requests
from getpass import getpass
from requests.exceptions import ConnectionError

logger = logging.getLogger(__name__)
    
def parseArgs():
    parser = argparse.ArgumentParser(description="Download task data from the last 'N' processed tasks.")
    parser.add_argument('-t', '--tasks', dest='taskNo', help='Number of tasks, from most recent to oldest to download. This argument will override the .env file', 
                        type=int, required=False, default=os.environ["TASK_NO"])
    parser.add_argument('-s', '--search', dest='type', help='Type of task to download ( scan | sample | import )', required=True, choices=['scan', 'sample', 'import'])
    parser.add_argument('-u', '--url', dest='consoleURL', help='URL of console. This argument will override the .env file', 
                        required=False, default=os.environ["RUNZERO_BASE_URL"])
    parser.add_argument('-k', '--key', dest='token', help='Prompt for Organization API key (do not enter at command line). This argument will override the .env file', 
                        nargs='?', const=None, required=False, default=os.environ["RUNZERO_ORG_TOKEN"])
    parser.add_argument('-p', '--path', help='Path to save scan data to. This argument will override the .env file', 
                        required=False, default=os.environ["SAVE_PATH"])
    parser.add_argument('-l', '--log', help='Path to write log file. This argument will take priority over the .env file', 
                        required=False, default=os.environ["LOG_PATH"])
    parser.add_argument('--version', action='version', version='%(prog)s 3.0')
    return parser.parse_args()
    
def get_tasks(url, type, token): 
    '''
        Retrieve Tasks from Organization corresponding to supplied token.

        :param url: A string, URL of the runZero console.
        :param type: A string, the type of scan task(s) to download.
        :param token: A string, Account API Key.
        :returns: A JSON object, runZero task data.
        :raises: ConnectionError: if unable to successfully make GET request to console.
    '''
    
    url = f"{url}/api/v1.0/org/tasks"
    params = {'search': f'type:{type}',
               'status':'processed'}
    headers = {'Accept': 'application/json',
               'Authorization': f'Bearer {token}'}
    try:
        response = requests.get(url, headers=headers, params=params)
        logger.info(f"Making GET request to {url}")
        if not response.ok:
            logger.critical('Unable to retrieve tasks' + str(response), 'exiting...')
            exit()
        logger.info('Received response.')
        content = response.json()
        return content
    except ConnectionError:
        logger.exception('Could not establish connection to console URL, exiting...')
        exit()

def parse_ids(data, task_number=1000):
    '''
        Extract task IDs from supplied recent task data. 
    
        :param data: JSON object, runZero task data.
        :param taskNo: an Integer, number of tasks to process.
        :returns: A List, list of task IDs.
        :raises: TypeError: if data variable passed is not JSON format.
    '''
    
    try:
        logger.info('Parsing Task IDs')
        task_ids = [item.get('id') for counter, item in enumerate(data) if counter <= task_number - 1]
        logger.info('Parsed Task IDs successfully')
        return task_ids
    except TypeError:
        logger.exception('Exiting...')
        exit()

def get_data(url, token, task_id, path):
    '''
        Download and write scan data (.json.gz) for each task ID provided.

        :param url: A string, URL of the runZero console.
        :param token: A string, Organization API key.
        :param taskID: A string, ID of scan task to download.
        :param path: A string, path to write files to.
        :returns: None, this function returns no data but writes files to disk.
        :raises: ConnectionError: if unable to successfully make GET request to console.
        :raises: IOError: if unable to write file.
    '''
    
    url = f"{url}/api/v1.0/org/tasks/{task_id}/data"
    payload = ""
    headers = {'Accept': 'application/json',
               'Authorization': f'Bearer {token}'}
    try:
        response = requests.get(url, headers=headers, data=payload, stream=True)
        logger.info(f"Making GET request to {url}")
        if not response.ok:
            logger.critical('Unable to retrieve task data' + str(response), 'exiting...')
            exit()
        logger.info('Received response. Writing Task Data to disk.')
        with open( f"{path}scan_{task_id}.json.gz", 'wb') as f:
            for chunk in response.iter_content(chunk_size=128):
                f.write(chunk)
        logger.info(f"{path}scan_{task_id}.json.gz successfully written to disk.")
    except ConnectionError:
        logger.exception('Could not establish connection to console URL, exiting...')
        exit()
    except IOError:
        logger.exception('Could not write task data file, exiting...')
        exit()

def main():
    args = parseArgs()
    logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%a, %d %b %Y %H:%M:%S', filename=f'{args.log}/dlTasks.log', level=logging.INFO)
    logger.info('Started')
    token = args.token
    if token == None:
        token = getpass(prompt="Enter your Organization API Key: ")
    task_info = get_tasks(args.consoleURL, args.type, token)
    id_list = parse_ids(task_info, args.taskNo)
    for id in id_list:
        get_data(args.consoleURL, token, id, args.path)
    logger.info('Finished')


if __name__ == "__main__":
    main()