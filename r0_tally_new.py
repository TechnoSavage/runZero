#!/usr/bin/python

""" EXAMPLE PYTHON SCRIPT! NOT INTENDED FOR PRODUCTION USE! 
    tally_new.py, version 1.2 by Derek Burke
    Script to retrieve last 'n' completed tasks and tally new asset counts. """

import json
import requests
import sys
from getpass import getpass
from requests.exceptions import ConnectionError

def usage():
    """ Display usage and switches. """
    print(""" Usage:
                    r0_tally_new.py [arguments]

                    You will be prompted to provide your runZero Organization API key
                    Default bahavior is to write output to stdout.
                    
                    Optional arguments:

                    -t <1-1000>   Number of tasks, from most recent to oldest to analyze (default is 1000)
                    -u <uri>      URI of console (default is https://console.runzero.com)
                    -j            Write output in JSON format
                    -f <filename> Write output to specified file (plain text default)
                                  combine with -j for JSON
                    -h            Show this help dialogue
                    
                Examples:
                    r0_tally_new.py -t 20
                    r0_tally_new.py -j -f output.json
                    r0_tally_new.py -u https://custom.runzero.com -t 15 -f output.txt """)

def getTasks(uri, token): 
    """ Retrieve Tasks from Organization corresponding to supplied token.

           :param token: A string, Account API Key.
           :returns: A JSON object, runZero task data.
           :raises: ConnectionError: if unable to successfully make GET request to console."""

    payload = ""
    headers = {'Accept': 'application/json',
               'Authorization': 'Bearer %s' % token}
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

if __name__ == "__main__":
    if "-h" in sys.argv:
        usage()
        exit()
    print("Enter your Organization API Key: ")
    token = getpass()
    uri = "https://console.runzero.com/api/v1.0/org/tasks"
    taskNo = 1000
    formatJSON = False
    saveFile = False
    fileName = ""
    
    if "-u" in sys.argv:
        uri = sys.argv[sys.argv.index("-u") + 1] + "/api/v1.0/org/tasks"
    if "-t" in sys.argv:
        try:
            taskNo = sys.argv[sys.argv.index("-t") + 1]
            int(taskNo)
        except ValueError as error:
            raise error
    if "-j" in sys.argv:
        formatJSON = True
    if "-f" in sys.argv:
        saveFile = True
        fileName = sys.argv[sys.argv.index("-f") + 1] 

    data = getTasks(uri, token)
    results = parseTasks(data, taskNo)
    if formatJSON:
        if saveFile:
            JSON = json.dumps(results, indent=4)
            writeFile(fileName, JSON)
        else:
            print(json.dumps(results, indent=4))
    else:
        if saveFile:
            stringList = []
            for line in results:
                stringList.append(str(line))
            textFile = '\n'.join(stringList)
            writeFile(fileName, textFile)
        else:
            for line in results:
                print(line)
