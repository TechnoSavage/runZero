""" EXAMPLE PYTHON SCRIPT! NOT INTENDED FOR PRODUCTION USE! 
    tallyNew.py, version 2.2 by Derek Burke
    Script to retrieve last 'n' completed tasks and tally new asset counts. """

import json
import os
import requests
import sys
from datetime import datetime
from getpass import getpass
from requests.exceptions import ConnectionError

def usage():
    """ Display usage and switches. """
    print(""" Usage:
                    tallyNew.py [arguments]

                    You will be prompted to provide your runZero Organization API key
                    Default bahavior is to write output to stdout.
                    
                    Optional arguments:

                    -t <1-1000>           Number of tasks, from most recent to oldest to analyze (default is 1000)
                    -u <uri>              URI of console (default is https://console.runzero.com)
                    -j                    Write output in JSON format
                    -f                    Write output to file (plain text default)
                                          combine with -j for JSON
                    -h                    Show this help dialogue
                    
                Examples:
                    tallyNew.py -t 20
                    tallyNew.py -j -f output.json
                    tallyNew.py -u https://custom.runzero.com -t 15 -f output.txt
                    python3 -m tallyNew """)

def getTasks(uri, token): 
    """ Retrieve Tasks from Organization corresponding to supplied token.

           :param token: A string, Account API Key.
           :returns: A JSON object, runZero task data.
           :raises: ConnectionError: if unable to successfully make GET request to console."""
    uri = f"{uri}/api/v1.0/org/tasks"
    payload = ""
    headers = {'Accept': 'application/json',
               'Authorization': f'Bearer {token}'}
    try:
        response = requests.get(uri, headers=headers, data=payload)
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
        :raises: TypeError: if data variable passed is not JSON format.
        :raises: KeyError: if dict key is incorrect or doesn't exist. """
    try:
        count = 0
        parsed = []
        for item in data:
            count += 1
            if count == int(taskNo) + 1:
                break
            task = {} 
            task["taskID"] = item["id"]
            task["siteID"] = item["site_id"]
            task["taskName"] = item["name"]
            task["taskDescription"] = item["description"]
            try:
                task["newAssets"] = item["stats"]["change.new"]
            except KeyError as error:
                task["newAssets"] = 0
            parsed.append(task)
        totalTasks = len(parsed) 
        totalNew = 0
        for item in parsed:        
            totalNew = totalNew + int(item["newAssets"])
        parsed.append({"tasksAnalyzed": totalTasks, "totalNew": totalNew})
        return parsed
    except TypeError as error:
        raise error
    except KeyError as error:
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
    if "-h" in sys.argv:
        usage()
        exit()
    consoleURL = os.environ["RUNZERO_BASE_URL"]
    token = os.environ["RUNZERO_ORG_TOKEN"]
    taskNo = os.environ["TASK_NO"]
    formatJSON = False
    saveFile = False
    #Output report name; default uses UTC time
    fileName = f"Asset_Tally_Report_{str(datetime.utcnow())}"
    if token == '':
        token = getpass(prompt="Enter your Organization API Key: ")
    if "-u" in sys.argv:
        try:
            consoleURL = sys.argv[sys.argv.index("-u") + 1]
        except IndexError as error:
            print("URI switch used but URI not provided!\n")
            usage()
            exit()
    if "-t" in sys.argv:
        try:
            taskNo = sys.argv[sys.argv.index("-t") + 1]
            int(taskNo)
        except ValueError as error:
            raise error
        except IndexError as error:
            print("Task switch used but task number not provided!\n")
            usage()
            exit()
    if "-j" in sys.argv:
        formatJSON = True
    if "-f" in sys.argv:
        saveFile = True
    if consoleURL == '':
        consoleURL = input('Enter the URL of the console (e.g. http://console.runzero.com): ')
    if taskNo == '':
        taskNo = input('Enter the number of tasks to tally new assets for (e.g. 100):')

    data = getTasks(consoleURL, token)
    results = parseTasks(data, taskNo)
    if formatJSON:
        if saveFile:
            fileName = fileName + '.json'
            JSON = json.dumps(results, indent=4)
            writeFile(fileName, JSON)
        else:
            print(json.dumps(results, indent=4))
    else:
        if saveFile:
            fileName = fileName + '.txt'
            stringList = []
            for line in results:
                stringList.append(str(line))
            textFile = '\n'.join(stringList)
            writeFile(fileName, textFile)
        else:
            for line in results:
                print(line)


if __name__ == "__main__":
    main()