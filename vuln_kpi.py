#!/usr/bin/python

""" EXAMPLE PYTHON SCRIPT! NOT INTENDED FOR PRODUCTION USE! 
    vuln_kpi.py, version 1.0 by Derek Burke
    Updated version of kpi script with additional functionality. Proof of concept to illustrate use of runZero API to generate
    KPI reports. This script focuses on generating a report for a provided time period that reports all assets discovered within
    the specified time as well as assets with vulnerabilies discovered within the same time period. Report states what percentage
    of vulnerable assets are compared to the total asset count for the time period and then calculates a compliance metric based on
    weighted scoring of vulnerability criticality."""

import json
import re
import requests
import sys
from datetime import datetime
from getpass import getpass
from requests.exceptions import ConnectionError

def usage():
    """ Display usage and switches. """
    print(""" Usage:
                    kpi.py [arguments]

                    You will be prompted to provide your runZero Organization API key unless a
                    configuration file is specified as an argument.
                    
                    Optional arguments:

                    -u <uri>                    URI of console (default is https://console.runzero.com)
                    -t <time span>              Time span for KPI measurements e.g. 1day, 2weeks, 1month
                    -c <config file/path>       Filename of config file including absolute path
                    -o <text| json | all> Output file format for report. Plain text is default.
                    -g                          Generate config file template
                    -h                          Show this help dialogue
                    
                Examples:
                    kpi.py -c example.config
                    python3 -m kpi -u https://custom.runzero.com -t 5months""")

def genConfig():
    """Create a template for script configuration file."""

    template = "orgToken= #Organization API Key\nuri=https://console.runzero.com #Console URL\ntime=1month #Time span for query in runZero syntax\n"
    writeFile("config_template", template)
    exit()

def readConfig(configFile):
    """ Read values from configuration file

        :param config: a file, file containing values for script
        :returns: a tuple, console url at index, API token at index 1, and time query at index 2.
        :raises: IOError: if file cannot be read.
        :raises: FileNotFoundError: if file doesn't exist."""
    try:
        with open( configFile, 'r') as c:
            config = c.read()
            url = re.search("uri=(http[s]?://[a-z0-9.]+)", config).group(1)
            token = re.search("orgToken=([0-9A-Z]+)", config).group(1)
            time = re.search("time=([0-9]*[a-z]+)", config).group(1)
            return(url, token, time)
    except IOError as error:
        raise error
    except FileNotFoundError as error:
        raise error

def getAssets(uri, token, filter):
    """ Retrieve assets using supplied query filter from Console and tally the number of assets found.
        
           :param uri: A string, URI of runZero console.
           :param token: A string, Organization API Key.
           :param filter: A string, query to filter returned assets.
           :returns: an integer, number of assets found.
           :raises: ConnectionError: if unable to successfully make GET request to console."""

    uri = uri + "/api/v1.0/org/assets?"
    params = {'search': filter}
    payload = ''
    headers = {'Accept': 'application/json',
               'Authorization': 'Bearer %s' % token}
    try:
        response = requests.get(uri, headers=headers, params=params, data=payload)
        content = response.content
        data = json.loads(content)
        #Returning length of asset list is equivalent to the number of assets matching the query
        return len(data)
    except ConnectionError as error:
        content = "No Response"
        raise error

def getVulns(uri, token, filter):
    """ Retrieve vulnerabilities using supplied query filter from Console, deduplicate asset
        entries, and tally unique asset count.
        
           :param uri: A string, URI of runZero console.
           :param token: A string, Organization API Key.
           :param filter: A string, query to filter returned vulnerabilities.
           :returns: A JSON object, runZero vulnerability data.
           :raises: ConnectionError: if unable to successfully make GET request to console.
           :raises: TypeError: if dataset is not iterable.
           :raises: KeyError: if dictionary key does not exist."""

    uri = uri + "/api/v1.0/export/org/vulnerabilities.json"
    params = {'search': filter}
    payload = ""
    headers = {'Accept': 'application/json',
               'Authorization': 'Bearer %s' % token}
    try:
        response = requests.get(uri, headers=headers, params=params, data=payload)
        content = response.content
        data = json.loads(content)
    except ConnectionError as error:
        content = "No Response"
        raise error
    #Take JSON data returned and deduplicate by unique asset ID
    try:
        assetList = []
        for item in data:
            if item['id'] not in assetList:
                assetList.append(item["id"])
        #Length of deduplicated asset list is equivalent to unique assets that match the query
        return len(assetList)
    except TypeError as error:
        raise error
    except KeyError as error:
        raise error
    
def metrics(assetCounts):
    """ Calculate criticality weighting and KPIs for asset report.
        
        :param report: a dict object, report generated by this script.
        :raises: KeyError: if dictionary key does not exist.
        :raises: ZeroDivisionError: if initial discovery query returns zero assets."""
    
    try:
        report = []
        totalAssets = 0
        weightedComply = 0
        normalAverage = 0
        for metric, count in assetCounts.items():
            if 'Discovered' in metric:
                totalAssets = count
                report.append(metric + ': ' + str(count))
            elif 'Critical' in metric:
                percentOfTotal = count / totalAssets * 100
                weightedPriority = count * 3 / totalAssets * 100
                compliance = 100 - percentOfTotal
                normalAverage += count
                weightedComply += count * 3
                report.append('%s: %s - %% of total: %s - %% in compliance: %s - weighted total: %s' % (metric, count, round(percentOfTotal, 2), round(compliance, 2), round(weightedPriority, 2)))
            elif 'High' in metric:
                percentOfTotal = count / totalAssets * 100
                weightedPriority = count * 2 / totalAssets * 100
                compliance = 100 - percentOfTotal
                normalAverage += count
                weightedComply += count * 2
                report.append('%s: %s - %% of total: %s - %% in compliance: %s - weighted total: %s' % (metric, count, round(percentOfTotal, 2), round(compliance, 2), round(weightedPriority, 2)))
            elif 'Medium' in metric:
                percentOfTotal = count / totalAssets * 100
                weightedPriority = percentOfTotal
                compliance = 100 - percentOfTotal
                normalAverage += count
                weightedComply += count
                report.append('%s: %s - %% of total: %s - %% in compliance: %s - weighted total: %s' % (metric, count, round(percentOfTotal, 2), round(compliance, 2), round(weightedPriority, 2)))
            else:
                pass
        report.append('Total Compliance KPI (weighted average based on priority, 3 = critical, 1 = lowest): ' + str(round(100 - (weightedComply / totalAssets * 100), 2)))
        report.append('vs normal average of all figures: ' + str(round(100 - (normalAverage / totalAssets * 100), 2)))
        return report
    except KeyError as error:
        raise error
    except ZeroDivisionError as error:
        print('Zero assets were discovered that match the intial query; nothing to process.')
        exit()

def writeJSON(fileName, contents):
    """ Write contents to output file in JSON format. 
    
        :param filename: a string, name for file including (optionally) file extension.
        :param contents: anything, file contents.
        :raises: IOError: if unable to write to file."""
    
    try:
        values = []
        for line in contents:
            metrics = re.findall("([a-zA-Z0-9%\s()=,]+): ([0-9.]+)", line)
            for metric in metrics:
                values.append(metric)
        JSON = {values[0][0]: {"count": values[0][1]},
                values[1][0]: {"count": values[1][1], values[2][0]: values[2][1], values[3][0]: values[3][1], values[4][0]: values[4][1]},
                values[5][0]: {"count": values[5][1], values[6][0]: values[6][1], values[7][0]: values[7][1], values[8][0]: values[8][1]},
                values[9][0]: {"count": values[9][1], values[10][0]: values[10][1], values[11][0]: values[11][1], values[12][0]: values[12][1]},
                values[13][0]: {"percent": values[13][1]},
                values[14][0]: {"percent": values[14][1]}}
        writeFile(fileName, json.dumps(JSON, indent=4))
    except IOError as error:
        raise error
    
def writeFile(fileName, contents):
    """ Write contents to output file in plaintext. 
    
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
    if "-g" in sys.argv:
        genConfig()
    config = False
    configFile = ''
    consoleURL = 'https://console.runzero.com'
    token = ''
    timeRange = ''
    #Output report name; default uses UTC time
    fileName = "KPI_report_" + str(datetime.utcnow())
    if "-c" in sys.argv:
        try:
            config = True
            configFile =sys.argv[sys.argv.index("-c") + 1]
            confParams = readConfig(configFile)
            consoleURL = confParams[0]
            token = confParams[1]
            timeRange = confParams[2]
        except IndexError as error:
            print("Config file switch used but no file provided!\n")
            usage()
            exit()
    else:
        print("Enter your Organization API Key: ")
        token = getpass()
    if "-u" in sys.argv and not config:
        try:
            consoleURL = sys.argv[sys.argv.index("-u") + 1]
        except IndexError as error:
            print("URI switch used but URI not provided!\n")
            usage()
            exit()
    if "-t" in sys.argv and not config:
        try:
            timeRange = sys.argv[sys.argv.index("-t") + 1]
        except IndexError as error:
            print("time range switch used but time range not provided!\n")
            usage()
            exit()
    #KPIs variable is a list of dictionaries for each metric that will be iterated over and used to return total 
    # number of matching assets. Format is 'title' (Reported KPI metric), 'query' (the query needed to filter the assets 
    # according to KPI), and 'type' which is either 'asset' or 'vuln' according to the API endpoint that must be queried to obtain
    #the desired information.
    if timeRange == '':
        timeRange = input('Please enter Time span for KPI measurements in runZero query syntax (e.g. 1day, 2weeks, 1month): ')
    KPIs = [{'title': 'Systems Discovered within the Last %s' % timeRange, 'query': 'first_seen:<"%s"' % timeRange, 'type': 'asset'},
            {'title': 'Systems within the Last %s with Critical Vulnerabilities' % timeRange, 'query': 'severity:critical AND first_detected_at:<"%s"' % timeRange, 'type': 'vuln'},
            {'title': 'Systems within the Last %s with High Vulnerabilities' % timeRange, 'query': 'severity:high AND first_detected_at:<"%s"' % timeRange, 'type': 'vuln'},
            {'title': 'Systems within the Last %s with Medium Vulnerabilities' % timeRange, 'query': 'severity:medium AND first_detected_at:<"%s"' % timeRange, 'type': 'vuln'}]
    assetCounts = {}
    for item in KPIs:
        if item['type'] == 'vuln':
            results = getVulns(consoleURL, token, item['query'])
        else:
            results = getAssets(consoleURL, token, item['query'])
        assetCounts[item['title']] = results
    #Generate report from asset counts
    report = metrics(assetCounts)
    #Write resulting report to file
    if "-o" in sys.argv and sys.argv[sys.argv.index("-o") + 1] not in ('csv', 'html', 'json'):
        fileName = fileName + '.txt'
        writeFile(fileName, '\n'.join(report))
    elif "-o" in sys.argv and sys.argv[sys.argv.index("-o") + 1] == 'json':
        fileName = fileName + '.json'
        writeJSON(fileName, report)
    else:
        fileName = fileName + '.txt'
        writeFile(fileName, '\n'.join(report))

    