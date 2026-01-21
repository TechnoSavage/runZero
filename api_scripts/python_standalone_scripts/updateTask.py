import argparse
import json
import os
import requests
from getpass import getpass
from requests.exceptions import ConnectionError
    
def parseArgs():
    parser = argparse.ArgumentParser(description="Create scan task via API.")
    parser.add_argument('-u', '--url', dest='consoleURL', help='URL of console. This argument will override the .env file', 
                        required=False, default=os.environ["RUNZERO_BASE_URL"])
    parser.add_argument('-k', '--key', dest='token', help='Prompt for Organization API key (do not enter at command line). This argument will override the .env file', 
                        nargs='?', const=None, required=False, default=os.environ["RUNZERO_ORG_TOKEN"])
    parser.add_argument('-x', '--explorer', dest='explorer', help='UUID of the Explorer. This argument will override the .env file', 
                        required=False, default=os.environ["EXPLORER"])
    parser.add_argument('-s', '--site', help='UUID of site to add scan data to. This argument will override the .env file', 
                        required=False, default=os.environ["RUNZERO_SITE_ID"])
    parser.add_argument('-iL', '--input-list', dest='targetFile', help='Text file with scan targets. This argument will override the .env file', 
                        required=False, default=os.environ["TARGETS"])
    parser.add_argument('-n', '--name', help='Name for the scan task.', required=False, default='API Scan')
    parser.add_argument('-d', '--description', help='Description for scan task.', required=False)
    parser.add_argument('-r', '--rate', help='Scan rate for task.', required=False, default='1000')
    parser.add_argument('--version', action='version', version='%(prog)s 3.2')
    return parser.parse_args()

def get_tasks(url, token):
    '''
        Retrieve Task from Organization corresponding to supplied task_id.

        :param url: A string, URL of the runZero console.
        :param token: A string, Organization API Key.
        :returns: A JSON object, runZero task data.
        :raises: ConnectionError: if unable to successfully make GET request to console.
    '''
    
    url = f"{url}/api/v1.0/org/tasks" 
    headers = {'Accept': 'application/json',
               'Authorization': f'Bearer {token}'}
    params = {'search': 'type:scan status:active recur:true'}
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            print('Unable to retrieve task' + str(response))
            exit()
        content = response.content
        data = json.loads(content)
        return data
    except ConnectionError as error:
        raise error
    
def parse_tasks(tasks):
    ids = []
    for task in tasks:
        id = task.get('id',)
        if id:
            ids.append(id)
    return ids

def patch_scan(url, token, ids):
    for id in ids:
        url = f"{url}/api/v1.0/org/tasks/{id}" 
        headers = {'Accept': 'application/json',
                   'Content-type': 'application/json',
                   'Authorization': f'Bearer {token}'}
        payload = json.dumps({"params": {"ssh-fingerprint": "false"}})
        try:
            response = requests.patch(url, headers=headers, data=payload)
            if response.status_code != 200:
                print(f'Unable to patch task:{id}' + str(response))
            content = response.content
            data = json.loads(content)
            return data
        except ConnectionError as error:
            raise error

def main():
    args = parseArgs()
    token = args.token
    if token == None:
        token = getpass(prompt="Enter the Organization API Key: ")
    tasks = get_tasks(args.consoleURL, token)
    print(tasks)
    ids = parse_tasks(tasks)
    response = patch_scan(args.consoleURL, token, ids)
    
if __name__ == "__main__":
    main()