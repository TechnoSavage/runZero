""" EXAMPLE PYTHON SCRIPT! NOT INTENDED FOR PRODUCTION USE! 
    taskSearch.py, version 0.2
    This script, when provided one or more IPs as an argument or in a file, will return the first and last tasks that discovered an asset,
    with relevant attributes, as well as any other task with a scope that could potentially discover the asset."""

import argparse
import datetime
import json
import os
import re
import pandas as pd
import requests
from getpass import getpass
from requests.exceptions import ConnectionError

    
def parseArgs():
    parser = argparse.ArgumentParser(description="Retrieve all hardware specific attributes.")
    parser.add_argument('-t', '--targets', dest='targets', help='Comma separated list (no spaces) of IPs to locate.', 
                        required=False)
    parser.add_argument('-iL', '--input-list', dest='targetFile', help='Text file with scan targets.', 
                        required=False, default=os.environ["TARGETS"])
    parser.add_argument('-u', '--url', dest='consoleURL', help='URL of console. This argument will take priority over the .env file', 
                        required=False, default=os.environ["RUNZERO_BASE_URL"])
    parser.add_argument('-k', '--key', dest='token', help='Prompt for Organization API key (do not enter at command line). This argument will take priority over the .env file', 
                        nargs='?', const=None, required=False, default=os.environ["RUNZERO_ORG_TOKEN"])
    parser.add_argument('-p', '--path', help='Path to write file. This argument will take priority over the .env file', 
                        required=False, default=os.environ["SAVE_PATH"])
    parser.add_argument('-o', '--output', dest='output', help='output file format', choices=['txt', 'json', 'csv', 'excel'], required=False)
    parser.add_argument('--version', action='version', version='%(prog)s 0.2')
    return parser.parse_args()

def assignTaskQuery(address):
    """ Return a task search query to filter tasks for any task that contains a scope
        containing the provided IP address.
            
            :param address: A string, IP address of asset.
            :returns: A string | None, task search query or None if provided address
                                       is not a valid RFC1918 address."""
    #find pattern to exclude leading 0 without removing only 0
    if re.match('\A(192\.168\.)(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$', address):
        query = 'params:192.168.%.%'
    elif re.match('\A(172\.)(?:3[0-1]|2[0-9]|1[6-9])\.(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.)(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$', address):
        query = 'params:172.16.%.% or params:172.17.%.% or params:172.18.%.% or params:172.19.%.% or params:172.2%.%.% or params:172.30.%.% or params:172.31.%.%'
    elif re.match('\A(10\.)(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){2}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$', address):
        query = 'params:10.%.%.%'
    else:
        print('IP address does not appear to match any address in the RFC1918 address space')
        return
    return query

def targetList(args):
    """ Return list of asset targets from arguments.

           :param args: A namespace object , argparse.Namespace.
           :returns: A list, IP addresses of asset targets."""
     
    if args.targets:
        targets = args.targets.split(',')
    elif args.targetFile:
        with open(args.targetFile, 'r') as f:
            targets = [line.strip() for line in f.readlines()]
    else:
        print("No IP addresses were provided.")
        exit()
    return targets

def getAssets(url, token, address):
    """ Retrieve assets using supplied query filter from Console and restrict to fields supplied.
        
        :param url: A string, URL of runZero console.
        :param token: A string, Organization API Key.
        :returns: a dict, JSON object of assets.
        :raises: ConnectionError: if unable to successfully make GET request to console."""

    url = f"{url}/api/v1.0/export/org/assets.jsonl"
    params = {'search': f'source:runzero and address:{address}',
              'fields': 'id, addresses, names, os, hw, first_task_id, last_task_id, first_agent_id, last_agent_id'}
    payload = ''
    headers = {'Accept': 'application/json',
               'Authorization': f'Bearer {token}'}
    try:
        response = requests.get(url, headers=headers, params=params, data=payload)
        content = response.content
        if len(content) == 0:
            content = json.dumps({"addresses":f"{address}", "id": "not found", "first_task_id":"NA", "last_task_id": "NA", "first_agent_id":"NA", "last_agent_id":"NA"})
        data = json.loads(content)
        return data
    except ConnectionError as error:
        content = "No Response"
        raise error
    
def getTask(url, token, taskID):
    """ Retrieve Task from Organization corresponding to supplied task_id.

           :param url: A string, URL of the runZero console.
           :param token: A string, Account API Key.
           :param taskID: A string, UUID of runZero task.
           :returns: A JSON object, runZero task data.
           :raises: ConnectionError: if unable to successfully make GET request to console."""
    
    url = f"{url}/api/v1.0/org/tasks/{taskID}" 
    headers = {'Accept': 'application/json',
               'Authorization': f'Bearer {token}'}
    try:
        response = requests.get(url, headers=headers)
        content = response.content
        data = json.loads(content)
        return data
    except ConnectionError as error:
        raise error

def getPossibleTasks(url, token, query): 
    """ Retrieve Tasks from Organization corresponding to supplied token.

           :param url: A string, URL of the runZero console.
           :param token: A string, Account API Key.
           :returns: A JSON object, runZero task data.
           :raises: ConnectionError: if unable to successfully make GET request to console."""
    
    url = f"{url}/api/v1.0/org/tasks" 
    payload = {'search': query,
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

#Modify to retrieve pertinent tasks
def parseTaskData(url, token, taskID, path):
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
    
def buildReportEntry(url, token, address):
    """ Build a report of the assets and related tasks data based on IP address.
     
        :param url: A string, URL of the runZero console.
        :param token: A string, Organization API key.
        :param address: A string, IP address of asset.
        :returns: A dict, asset and task attributes."""
    
    entry = {}
    discovered = getAssets(url, token, address)
    entry['address'] = discovered
    #First task discovery information
    if discovered['first_task_id'] != "NA":
        firstDiscovered = {}
        firstTaskParams = getTask(url, token, discovered['first_task_id'])
        firstDiscovered['task_id'] = firstTaskParams['id']
        firstDiscovered['task_url'] = f'{url}/tasks/search/completed?task={firstTaskParams["id"]}'
        firstDiscovered['task_organization_id'] = firstTaskParams['organization_id']
        firstDiscovered['task_targets'] = firstTaskParams['params']['targets']
        firstDiscovered['task_agent_id'] = firstTaskParams['agent_id']
        firstDiscovered['task_agent_name'] = firstTaskParams['agent_name']
        firstDiscovered['task_site_id'] = firstTaskParams['site_id']
        firstDiscovered['task_site_name'] = firstTaskParams['site_name']
        firstDiscovered['task_type'] = firstTaskParams['type']
        entry['first_discovery'] = firstDiscovered
    #Last task discovery information
    if discovered['last_task_id'] != "NA":
        lastDiscovered = {}
        lastTaskParams = getTask(url, token, discovered['last_task_id'])
        lastDiscovered['task_id'] = lastTaskParams['id']
        lastDiscovered['task_url'] = f'{url}/tasks/search/completed?task={lastTaskParams["id"]}'
        lastDiscovered['task_organization_id'] = lastTaskParams['organization_id']
        lastDiscovered['task_targets'] = lastTaskParams['params']['targets']
        lastDiscovered['task_agent_id'] = lastTaskParams['agent_id']
        lastDiscovered['task_agent_name'] = lastTaskParams['agent_name']
        lastDiscovered['task_site_id'] = lastTaskParams['site_id']
        lastDiscovered['task_site_name'] = lastTaskParams['site_name']
        lastDiscovered['task_type'] = lastTaskParams['type']
        entry['last_discovery'] = lastDiscovered
    query = assignTaskQuery(address)
    #Return all tasks whose scope could enumerate the target
    possibleDiscoveryTasks = getPossibleTasks(url, token, query)
    possibleList = []
    for task in possibleDiscoveryTasks:
        if task['id'] != entry.get('first_discovery', {}).get('task_id', '') or task['id'] != entry.get('last_discovery', {}).get('task_id', ''):
            possible = {}
            possible['task_id'] = task['id']
            possible['task_url'] = f'{url}/tasks/search/completed?task={task["id"]}'
            possible['task_organization_id'] = task['organization_id']
            possible['task_targets'] = task['params']['targets']
            possible['task_agent_id'] = task['agent_id']
            possible['task_agent_name'] = task['agent_name']
            possible['task_site_id'] = task['site_id']
            possible['task_site_name'] = task['site_name']
            possible['task_type'] = task['type']
            possibleList.append(possible)
    entry['tasks_with_discovery_potential'] = possibleList
    return entry

def outputFormat(format, fileName, data):
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
    elif format in ('csv', 'excel'):
        writeDF(format, fileName, data)  
    else:
        for line in data:
            print(json.dumps(line, indent=4))

    
def writeDF(format, fileName, data):
    """ Write contents to output file. 
    
        :param filename: a string, name for file including.
        :param format: a string, excel or csv
        :param contents: json data, file contents.
        :raises: IOError: if unable to write to file.  """
    
    df = pd.DataFrame(data)
    try:
        if format == "excel":
            df.to_excel(f'{fileName}.xlsx')
        else:
            df.to_csv(f'{fileName}.csv', encoding='utf-8')
    except IOError as error:
        raise error
    
def writeFile(fileName, contents):
    """ Write contents to output file. 
    
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
    #Output report name; default uses UTC time
    fileName = f"{args.path}Task_Discovery_Report_{str(datetime.datetime.now(datetime.timezone.utc))}"
    token = args.token
    if token == None:
        token = getpass(prompt="Enter your Organization API Key: ")
    targets = targetList(args)
    #Asset query to report last task discovery
    report = []
    for address in targets:
        entry = buildReportEntry(args.consoleURL, token, address)
        report.append(entry)
    outputFormat(args.output, fileName, report)

if __name__ == "__main__":
    main()