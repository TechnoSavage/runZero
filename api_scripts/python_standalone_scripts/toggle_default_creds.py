""" EXAMPLE PYTHON SCRIPT! NOT INTENDED FOR PRODUCTION USE! 
    toggle_default_creds.py, version 1.0
    Quickly enable/disable default credential checks for all recurring scan tasks."""

import argparse
import json
import os
import requests
from getpass import getpass
from requests.exceptions import ConnectionError
    
def parse_args():
    parser = argparse.ArgumentParser(description="Quickly enable/disable default credential checks for all recurring scan tasks.")
    parser.add_argument('-u', '--url', dest='consoleURL', help='URL of console. This argument will override the .env file', 
                        required=False, default=os.environ["RUNZERO_BASE_URL"])
    parser.add_argument('-k', '--key', dest='token', help='Prompt for Organization API key (do not enter at command line). This argument will override the .env file', 
                        nargs='?', const=None, required=False, default=os.environ["RUNZERO_ORG_TOKEN"])
    parser.add_argument('-e', '--enable', action='store_true', required=False)
    parser.add_argument('-d', '--disable', dest='enable', action='store_false', required=False)
    parser.set_defaults(enable=False)
    parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    return parser.parse_args()

def get_tasks(url, token): 
    '''
        Retrieve Tasks from Organization corresponding to supplied token.

        :param url: A string, URL of the runZero console.
        :param token: A string, Organization API Key.
        :returns: A JSON object, runZero task data.
        :raises: ConnectionError: if unable to successfully make GET request to console.
    '''
    
    url = f"{url}/api/v1.0/org/tasks"
    params = {'search': f'recur:t and type:scan'}
    headers = {'Accept': 'application/json',
               'Authorization': f'Bearer {token}'}
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            print('Unable to retrieve tasks' + str(response))
            exit()
        content = response.content
        data = json.loads(content)
        return data
    except ConnectionError as error:
        raise error
    
def parse_IDs(data, taskNo=1000):
    '''
        Extract task IDs from supplied recent task data. 
    
        :param data: JSON object, runZero task data.
        :param taskNo: an Integer, number of tasks to process.
        :returns: A List, list of task IDs.
        :raises: TypeError: if data variable passed is not JSON format.
    '''
    
    try:
        taskIDs = [item.get('id') for counter, item in enumerate(data) if counter <= taskNo - 1]
        return taskIDs
    except TypeError as error:
        raise error
    
def update_tasks(url, token, task_ids, enable):
    '''
        Loop through task IDs and patch default credential checks to true or false. 
    
        :param url: A string, URL of the runZero console.
        :param token: A string, Organization API Key.
        :param task_ids: A list, list of runZero task IDs.
        :param enable: A bool, True or False.
        :returns: None, returns none.
        :raises: ConnectionError: if unable to successfully make PATCH request to console.
    '''

    if enable:
        state = "true"
    else:
        state = "false"
    for id in task_ids:
            url = f"{url}/api/v1.0/org/tasks/{id}"
            headers = {'Accept': 'application/json',
                       'Content-Type': 'application/json',
                       'Authorization': f'Bearer {token}'}
            payload = json.dumps({"params": {"vscan-scope-default-login-http": state}})
            try:
                response = requests.patch(url, headers=headers,data=payload)
                if response.status_code != 200:
                    print(f"Unable to modify task {id}")
                else:
                    print(f"Task {id} default login credential check set to {state}")
            except ConnectionError as error:
                raise error

def main():
    args = parse_args()
    token = args.token
    if token == None:
        token = getpass(prompt="Enter the Organization API Key: ")
    task_data = get_tasks(args.consoleURL, token)
    task_list = parse_IDs(task_data) 
    updated_tasks = update_tasks(args.consoleURL, token, task_list, args.enable)
    
if __name__ == "__main__":
    main()