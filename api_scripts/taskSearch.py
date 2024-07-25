""" EXAMPLE PYTHON SCRIPT! NOT INTENDED FOR PRODUCTION USE! 
    taskSearch.py, version 0.7
    This script, when provided one or more IPs as an argument or in a file, will return the first and last tasks that discovered an asset,
    with relevant attributes, as well as any other task with a scope that could potentially discover the asset. Optionally the script can
    search task data of possible discovery tasks to determine if a task ever discoverd the IP and IPs can be automatically applied as exclusions
    to recurring tasks."""

import argparse
import datetime
import gzip
import json
import os
import re
import requests
import subprocess
import pandas as pd
from getpass import getpass
from requests.exceptions import ConnectionError

    
def parseArgs():
    parser = argparse.ArgumentParser(description="Identify tasks that have or could discover provided IP(s).")
    parser.add_argument('-t', '--targets', dest='targets', help='Comma separated list (no spaces) of IPs to locate.', 
                        required=False)
    parser.add_argument('-iL', '--input-list', dest='targetFile', help='Text file with scan targets. This argument will take priority over the .env file', 
                        required=False, default=os.environ["TARGETS"])
    parser.add_argument('-d', '--deep-search', dest='deep', help='With this option enabled the task data for possible matches is temporarily downloaded and searched for the IP address.', 
                        action='store_true', required=False)
    parser.add_argument('-e', '--exclude', dest='exclude', help='add IP(s) as an exclusion to recurring tasks; limited excludes from first and last seen tasks, extended adds possible tasks.', 
                        choices=['limited','extended'], required=False, default='')
    parser.add_argument('-u', '--url', dest='consoleURL', help='URL of console. This argument will take priority over the .env file', 
                        required=False, default=os.environ["RUNZERO_BASE_URL"])
    parser.add_argument('-k', '--key', dest='token', help='Prompt for Organization API key (do not enter at command line). This argument will take priority over the .env file', 
                        nargs='?', const=None, required=False, default=os.environ["RUNZERO_ORG_TOKEN"])
    parser.add_argument('-p', '--path', help='Path to write temporary scan file downloads. This argument will take priority over the .env file', 
                        required=False, default=os.environ["SAVE_PATH"])
    parser.add_argument('-o', '--output', dest='output', help='output file format', choices=['txt', 'json', 'csv', 'excel', 'html'], required=False)
    parser.add_argument('--version', action='version', version='%(prog)s 0.7')
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
              'fields': 'id, addresses, names, os, hw, first_task_id, last_task_id, first_agent_id, last_agent_id, agent_name, site_id, site_name'}
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
           :param token: A string, Organization API Key.
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
    
def writeTaskData(url, token, taskID, path):
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
        return
    except ConnectionError as error:
        raise error
    except IOError as error:
        raise error
    
def searchTaskData(address, taskID, path):
    """ Search task data for any matches to address. 
    
        :param address: A string, IP address to search for.
        :param taskID: A String, UUID of task to identify scan file to search.
        :param path: A String, path to scan archive location. """

    with gzip.open( f'{path}scan_{taskID}.json.gz', 'rt') as f:
        content = f.read()
        pattern = f'"{address}"'
        instances = re.findall( pattern, content)
        if len(instances) > 0:
            return True
        else:
            return

def deleteTaskData(taskID, path):
    """Remove task data files created by writeTaskData funtion.

        :param taskID: A String, UUID of task to identify scan file to delete.
        :param path: A String, path used in getData to create scan files.
        :returns None: this function returns nothing but removes files from disk.
        :raises: IOerror, if unable to delete file."""

    handle = f"scan_{taskID}.json.gz"
    try:
        dir_contents = subprocess.check_output(['ls', path]).splitlines()
        for item in dir_contents:
            archiveName = re.match("b'((scan_.*)\.(json\.gz))", str(item))
            if archiveName is not None and archiveName.group(1) == handle:
                    os.remove(path + handle)
            else:
                pass
        return
    except IOError as error:
        raise error
    
def autoExclude(url, token, address, taskID):
    """ Apply address as exclusion to task corresponding to supplied task_id.

           :param url: A string, URL of the runZero console.
           :param token: A string, Organization API Key.
           :param taskID: A string, UUID of runZero task.
           :returns: NoneType.
           :raises: ConnectionError: if unable to successfully make PATCH request to console."""
    
    url = f"{url}/api/v1.0/org/tasks/{taskID}" 
    headers = {'Accept': 'application/json',
               'Authorization': f'Bearer {token}'}
    payload = {'params': {'excludes': address}}
    try:
        response = requests.patch(url, headers=headers, payload=payload)
        if response.status_code == 200:
            return 'success'
        else:
            return 'fail' 
    except ConnectionError as error:
        raise error

def getPossibleTasks(url, token, query): 
    """ Retrieve Tasks from Organization corresponding to supplied token.

           :param url: A string, URL of the runZero console.
           :param token: A string, Organization API Key.
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
    
def buildReportEntry(url, token, address, deepDiscovery, path, exclusion):
    """ Build a report of the assets and related tasks data based on IP address.
     
        :param url: A string, URL of the runZero console.
        :param token: A string, Organization API key.
        :param address: A string, IP address of asset.
        :returns: A dict, asset and task attributes."""
    
    entry = {}
    discovered = getAssets(url, token, address)
    for key, value in discovered.items():
        entry[key] = value
    #First task discovery information
    if discovered['first_task_id'] != "NA":
        firstTaskParams = getTask(url, token, discovered['first_task_id'])
        entry['first_discovered_task_id'] = firstTaskParams['id']
        entry['first_discovered_task_url'] = f'{url}/tasks/search/completed?task={firstTaskParams["id"]}'
        entry['first_discovered_task_organization_id'] = firstTaskParams['organization_id']
        entry['first_discovered_task_targets'] = firstTaskParams['params']['targets']
        entry['first_discovered_task_exclusions'] = firstTaskParams['params']['excludes']
        entry['first_discovered_task_agent_id'] = firstTaskParams['agent_id']
        entry['first_discovered_task_agent_name'] = firstTaskParams['agent_name']
        entry['first_discovered_task_site_id'] = firstTaskParams['site_id']
        entry['first_discovered_task_site_name'] = firstTaskParams['site_name']
        entry['first_discovered_task_type'] = firstTaskParams['type']
        entry['first_discovered_recurring'] = firstTaskParams['recur']
        if exclusion in ('limited', 'extended') and firstTaskParams['recur'] == 'true':
            entry['excluded'] = autoExclude(url, token, address, firstTaskParams['id'])
        else:
            entry['first_discovery_excluded'] = 'not attempted'
    #Last task discovery information
    if discovered['last_task_id'] != "NA":
        lastTaskParams = getTask(url, token, discovered['last_task_id'])
        entry['last_discovered_task_id'] = lastTaskParams['id']
        entry['last_discovered_task_url'] = f'{url}/tasks/search/completed?task={lastTaskParams["id"]}'
        entry['last_discovered_task_organization_id'] = lastTaskParams['organization_id']
        entry['last_discovered_task_targets'] = lastTaskParams['params']['targets']
        entry['last_discovered_task_exclusions'] = lastTaskParams['params']['excludes']
        entry['last_discovered_task_agent_id'] = lastTaskParams['agent_id']
        entry['last_discovered_task_agent_name'] = lastTaskParams['agent_name']
        entry['last_discovered_task_site_id'] = lastTaskParams['site_id']
        entry['last_discovered_task_site_name'] = lastTaskParams['site_name']
        entry['last_discovered_task_type'] = lastTaskParams['type']
        entry['last_discovered_recurring'] = lastTaskParams['recur']
        if exclusion in ('limited', 'extended') and lastTaskParams['recur'] == 'true':
            entry['last_discovery_excluded'] = autoExclude(url, token, address, lastTaskParams['id'])
        else:
            entry['last_discovery_excluded'] = 'not attempted'
    query = assignTaskQuery(address)
    #Return all tasks whose scope could enumerate the target
    possibleDiscoveryTasks = getPossibleTasks(url, token, query)
    possibleList = []
    for task in possibleDiscoveryTasks:
        #Condition to exclude first and last discovery task details from appearing in possible matches
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
            possible['recurring'] = task['recur']
            if deepDiscovery:
                writeTaskData(url, token, task['id'], path)
                instances = searchTaskData(address, task['id'], path)
                deleteTaskData(task['id'], path)
                if instances:
                    possible['task_has_seen_ip'] = 'True'
                else:
                    possible['task_has_seen_ip'] = 'False'
            if exclusion == 'extended' and task['recur'] == 'true':
                possible['excluded'] = autoExclude(url, token, address, task['id'])
            possibleList.append(possible)
    entry['tasks_with_discovery_potential'] = possibleList
    return entry

#Output formats require some finessing
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
    elif format in ('csv', 'excel', 'html'):
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
            df.to_excel(f'{fileName}.xlsx', freeze_panes=(1,0), na_rep="NA")
        elif format == 'csv':
            df.to_csv(f'{fileName}.csv', na_rep="NA")
        else:
            df.to_html(f'{fileName}.html', render_links=True, na_rep='NA')
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
        entry = buildReportEntry(args.consoleURL, token, address, args.deep, args.path, args.exclude)
        report.append(entry)
    outputFormat(args.output, fileName, report)

if __name__ == "__main__":
    main()