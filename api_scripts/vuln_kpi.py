""" EXAMPLE PYTHON SCRIPT! NOT INTENDED FOR PRODUCTION USE! 
    vuln_kpi.py, version 3.1
    Proof of concept to illustrate use of runZero API to generate KPI reports. This script focuses on generating a report for 
    a provided time period that reports all assets discovered within the specified time as well as assets with vulnerabilies 
    discovered within the same time period. Report states what percentage of vulnerable assets are compared to the total asset 
    count for the time period and then calculates a compliance metric based on weighted scoring of vulnerability criticality."""

import argparse
import csv
import json
import os
import requests
from datetime import datetime, timezone
from getpass import getpass
from requests.exceptions import ConnectionError
    
def parseArgs():
    parser = argparse.ArgumentParser(description="Report percentage of vulnerable assets compared to total asset count for a given time period; calculated a weighted compliance metric.")
    parser.add_argument('-r', '--range', dest='timeRange', help='Time span to search for new assets e.g. 1day, 2weeks, 1month. This argument will override the .env file', 
                        required=False, default=os.environ["TIME"])
    parser.add_argument('-u', '--url', dest='consoleURL', help='URL of console. This argument will override the .env file', 
                        required=False, default=os.environ["RUNZERO_BASE_URL"])
    parser.add_argument('-k', '--key', dest='token', help='Prompt for Organization API key (do not enter at command line). This argument will override the .env file', 
                        nargs='?', const=None, required=False, default=os.environ["RUNZERO_ORG_TOKEN"])
    parser.add_argument('-p', '--path', help='Path to write file. This argument will override the .env file', 
                        required=False, default=os.environ["SAVE_PATH"])
    parser.add_argument('-o', '--output', dest='output', help='output file format', choices=['txt', 'json', 'csv'], required=False)
    parser.add_argument('--version', action='version', version='%(prog)s 3.1')
    return parser.parse_args()

def getAssets(url, token, filter):
    '''
        Retrieve assets using supplied query filter from Console and tally the number of assets found.
        
        :param url: A string, URI of runZero console.
        :param token: A string, Organization API Key.
        :param filter: A string, query to filter returned assets.
        :returns: an integer, number of assets found.
        :raises: ConnectionError: if unable to successfully make GET request to console.
    '''

    url = f"{url}/api/v1.0/org/assets"
    params = {'search': filter}
    payload = ''
    headers = {'Accept': 'application/json',
               'Authorization': f'Bearer {token}'}
    try:
        response = requests.get(url, headers=headers, params=params, data=payload)
        if response.status_code != 200:
            print('Unable to retrieve assets' + response)
            exit()
        content = response.content
        data = json.loads(content)
        #Returning length of asset list is equivalent to the number of assets matching the query
        return len(data)
    except ConnectionError as error:
        content = "No Response"
        raise error

def getVulns(url, token, filter):
    '''
        Retrieve vulnerabilities using supplied query filter from Console, deduplicate asset
        entries, and tally unique asset count.
        
           :param url: A string, URI of runZero console.
           :param token: A string, Organization API Key.
           :param filter: A string, query to filter returned vulnerabilities.
           :returns: A JSON object, runZero vulnerability data.
           :raises: ConnectionError: if unable to successfully make GET request to console.
           :raises: TypeError: if dataset is not iterable.
           :raises: KeyError: if dictionary key does not exist.
    '''

    url = f"{url}/api/v1.0/export/org/vulnerabilities.json"
    params = {'search': filter}
    payload = ""
    headers = {'Accept': 'application/json',
               'Authorization': f'Bearer {token}'}
    try:
        response = requests.get(url, headers=headers, params=params, data=payload)
        if response.status_code != 200:
            print('Unable to retrieve vulnerabilities' + response)
            exit()
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
    '''
        Calculate criticality weighting and KPIs for asset report.
        
        :param report: a dict object, report generated by this script.
        :raises: KeyError: if dictionary key does not exist.
        :raises: ZeroDivisionError: if initial discovery query returns zero assets.
    '''

    report = []
    try:
        totalAssets = 0
        weightedComply = 0
        normalAverage = 0
        for metric, count in assetCounts.items():
            if 'Discovered' in metric:
                totalAssets = count
                report.append({metric: str(count)})
            elif 'Critical' in metric:
                percentOfTotal = count / totalAssets * 100
                weightedPriority = count * 3 / totalAssets * 100
                compliance = 100 - percentOfTotal
                normalAverage += count
                weightedComply += count * 3
                report.append({metric: count,
                              'percent_of_total': round(percentOfTotal, 2),
                              'percent_in_compliance': round(compliance, 2),
                              'weight': '3',
                              'weighted_total': round(weightedPriority, 2)})
            elif 'High' in metric:
                percentOfTotal = count / totalAssets * 100
                weightedPriority = count * 2 / totalAssets * 100
                compliance = 100 - percentOfTotal
                normalAverage += count
                weightedComply += count * 2
                report.append({metric: count,
                              'percent_of_total': round(percentOfTotal, 2),
                              'percent_in_compliance': round(compliance, 2),
                              'weight': '2',
                              'weighted_total': round(weightedPriority, 2)})
            elif 'Medium' in metric:
                percentOfTotal = count / totalAssets * 100
                weightedPriority = percentOfTotal
                compliance = 100 - percentOfTotal
                normalAverage += count
                weightedComply += count
                report.append({metric: count,
                              'percent_of_total': round(percentOfTotal, 2),
                              'percent_in_compliance': round(compliance, 2),
                              'weight': '1',
                              'weighted_total': round(weightedPriority, 2)})
            else:
                pass
        report.append({'Total Compliance KPI': str(round(100 - (weightedComply / totalAssets * 100), 2))})
        report.append({'vs normal average of all figures': str(round(100 - (normalAverage / totalAssets * 100), 2))})
        return report
    except KeyError as error:
        raise error
    except ZeroDivisionError as error:
        report.append({'Info':'Zero assets were discovered that match the initial query; nothing to process'})
        return report
    
def writeCSV(fileName, contents, timeRange):
    '''
        Write contents to output file. 
    
        :param filename: a string, name for file including.
        :param contents: json data, file contents.
        :raises: IOError: if unable to write to file.
    '''

    try:
        with open(f'{fileName}', 'w') as o:
            fieldNames = [f'Systems Discovered within the Last {timeRange}', 
                          f'Systems within the Last {timeRange} with Critical Vulnerabilities',
                          f'Systems within the Last {timeRange} with High Vulnerabilities', 
                          f'Systems within the Last {timeRange} with Medium Vulnerabilities', 
                          'percent_of_total', 'percent_in_compliance', 'weight', 'weighted_total', 
                          'Total Compliance KPI', 'vs normal average of all figures', 'Info']
            csv_writer = csv.DictWriter(o, fieldNames)
            csv_writer.writeheader()
            for entry in contents:
                try:
                    csv_writer.writerow(entry)
                except ValueError as error:
                    pass
    except IOError as error:
        raise error
    
def writeFile(fileName, contents):
    '''
        Write contents to output file. 
    
        :param filename: a string, name for file including (optionally) file extension.
        :param contents: anything, file contents.
        :raises: IOError: if unable to write to file.
    '''
    
    try:
        with open( fileName, 'w') as o:
                    o.write(contents)
    except IOError as error:
        raise error 

def main():
    args = parseArgs()
    token = args.token
    if token == None:
        token = getpass(prompt="Enter your Organization API Key: ")
    #Output report name; default uses UTC time
    timestamp = str(datetime.now(timezone.utc).strftime('%y-%m-%d%Z_%H-%M-%S'))
    fileName = f'{args.path}KPI_report_{timestamp}'
    #KPIs variable is a list of dictionaries for each metric that will be iterated over and used to return total 
    # number of matching assets. Format is 'title' (Reported KPI metric), 'query' (the query needed to filter the assets 
    # according to KPI), and 'type' which is either 'asset' or 'vuln' according to the API endpoint that must be queried to obtain
    #the desired information.
    KPIs = [{'title': f'Systems Discovered within the Last {args.timeRange}', 'query': f'first_seen:<"{args.timeRange}"', 'type': 'asset'},
            {'title': f'Systems within the Last {args.timeRange} with Critical Vulnerabilities', 'query': f'severity:critical AND first_detected_at:<"{args.timeRange}"', 'type': 'vuln'},
            {'title': f'Systems within the Last {args.timeRange} with High Vulnerabilities', 'query': f'severity:high AND first_detected_at:<"{args.timeRange}"', 'type': 'vuln'},
            {'title': f'Systems within the Last {args.timeRange} with Medium Vulnerabilities', 'query': f'severity:medium AND first_detected_at:<"{args.timeRange}"', 'type': 'vuln'}]
    assetCounts = {}
    for item in KPIs:
        if item['type'] == 'vuln':
            results = getVulns(args.consoleURL, token, item['query'])
        else:
            results = getAssets(args.consoleURL, token, item['query'])
        assetCounts[item['title']] = results
    #Generate report from asset counts
    report = metrics(assetCounts)
    #Write resulting report to file
    if args.output == 'json':
        fileName = f'{fileName}.json'
        writeFile(fileName, json.dumps(report))
    elif args.output == 'txt':
        fileName = f'{fileName}.txt'
        stringList = []
        for line in report:
            stringList.append(str(line).replace('{', '').replace('}', '').replace(': ', '='))
        textFile = '\n'.join(stringList)
        writeFile(fileName, textFile)
    elif args.output == 'csv':
        fileName = f'{fileName}.csv'
        writeCSV(fileName, report, args.timeRange)  
    else:
        for line in report:
            print(json.dumps(line, indent=4))

if __name__ == "__main__":
    main()