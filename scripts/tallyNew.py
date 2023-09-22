""" EXAMPLE PYTHON SCRIPT! NOT INTENDED FOR PRODUCTION USE! 
    tallyNew.py, version 3.2
    Script to retrieve last 'N' completed tasks and tally new asset counts. """

import argparse
import csv
import json
import os
import requests
from datetime import datetime
from flatten_json import flatten
from getpass import getpass
from requests.exceptions import ConnectionError
    
def parseArgs():
    parser = argparse.ArgumentParser(description="Analyze last N number of tasks to report total new assets found.")
    parser.add_argument('-t', '--tasks', dest='taskNo', help='Number of tasks, from most recent to oldest to analyze. This argument will take priority over the .env file', 
                        type=int, required=False, default=os.environ["TASK_NO"])
    parser.add_argument('-u', '--url', dest='consoleURL', help='URL of console. This argument will take priority over the .env file', 
                        required=False, default=os.environ["RUNZERO_BASE_URL"])
    parser.add_argument('-k', '--key', dest='token', help='Prompt for Org API key (do not enter at command line). This argument will take priority over the .env file', 
                        nargs='?', const=None, required=False, default=os.environ["RUNZERO_ORG_TOKEN"])
    parser.add_argument('-p', '--path', help='Path to write file. This argument will take priority over the .env file', 
                        required=False, default=os.environ["SAVE_PATH"])
    parser.add_argument('-o', '--output', dest='output', help='Output file format', choices=['txt', 'json', 'csv'], required=False)
    parser.add_argument('--version', action='version', version='%(prog)s 3.2')
    return parser.parse_args()

def getTasks(url, token): 
    """ Retrieve Tasks from Organization corresponding to supplied token.

           :param token: A string, Account API Key.
           :returns: A JSON object, runZero task data.
           :raises: ConnectionError: if unable to successfully make GET request to console."""
    url = f"{url}/api/v1.0/org/tasks"
    payload = ""
    headers = {'Accept': 'application/json',
               'Authorization': f'Bearer {token}'}
    try:
        response = requests.get(url, headers=headers, data=payload)
        content = response.content
        data = json.loads(content)
        return data
    except ConnectionError as error:
        content = "No Response"
        raise error

def parseTasks(data, taskNo=1000):
    """ Extract relevant fields from task data and tally new assets. 
    
        :param data: JSON object, runZero task data.
        :param taskNo: an Integer, how many recent tasks to loop through.
        :returns: Dict Object, JSON formatted dictionary of relevant values.
        :raises: TypeError: if data variable passed is not JSON format."""
    try:
        count = 0
        parsed = []
        for item in data:
            item = flatten(item)
            count += 1
            if count == int(taskNo) + 1:
                break
            task = {} 
            task["taskID"] = item.get("id", '')
            task["siteID"] = item.get("site_id", '')
            task["taskName"] = item.get("name", '')
            task["taskDescription"] = item.get("description", '')
            task["newAssets"] = item.get("stats_change.newAssets", 0)
            parsed.append(task)
        totalTasks = len(parsed) 
        totalNew = 0
        for item in parsed:        
            totalNew = totalNew + int(item["newAssets"])
        parsed.append({"tasksAnalyzed": totalTasks, "totalNew": totalNew})
        return parsed
    except TypeError as error:
        raise error
    
def writeCSV(fileName, contents):
    """ Write contents to output file. 
    
        :param filename: a string, name for file including.
        :param contents: json data, file contents.
        :raises: IOError: if unable to write to file. """
    try:
        cf = open(f'{fileName}.csv', 'w')
        csv_writer = csv.writer(cf)
        count = 0
        for item in contents:
            if count == 0:
                header = item.keys()
                csv_writer.writerow(header)
                count += 1
            csv_writer.writerow(item.values())
        cf.close()
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
    fileName = f"{args.path}Asset_Tally_Report_{str(datetime.utcnow())}"
    token = args.token
    if token == None:
        token = getpass(prompt="Enter your Organization API Key: ")
    data = getTasks(args.consoleURL, token)
    results = parseTasks(data, args.taskNo)
    if args.output == 'json':
        fileName = f'{fileName}.json'
        writeFile(fileName, json.dumps(results))
    elif args.output == 'txt':
        fileName = f'{fileName}.txt'
        stringList = []
        for line in results:
            stringList.append(str(line).replace('{', '').replace('}', '').replace(': ', '='))
        textFile = '\n'.join(stringList)
        writeFile(fileName, textFile)
    elif args.output == 'csv':
        fileName = f'{fileName}.csv'
        writeCSV(fileName, results)  
    else:
        for line in results:
            print(json.dumps(line, indent=4))

if __name__ == "__main__":
    main()