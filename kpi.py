#!/usr/bin/python

""" EXAMPLE PYTHON SCRIPT! NOT INTENDED FOR PRODUCTION USE! 
    kpi.py, version 1.3 by Derek Burke
    Calculate defined KPI metrics. """

import json
import requests
from datetime import datetime
from requests.exceptions import ConnectionError

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
        weighted = 0
        normalAverage = 0
        categories = 3 #Critical, High, Medium
        critWeight = 3
        highWeight = 2
        medWeight = 1
        for metric, count in assetCounts.items():
            if 'Discovered' in metric:
                totalAssets = count
                report.append(metric + ': ' + str(count))
            elif 'Critical' in metric:
                percentOfTotal = count / totalAssets * 100
                compliance = 100 - percentOfTotal
                normalAverage += compliance
                weighted += compliance * critWeight
                report.append('%s: %s - %% of total: %s - %% in compliance: %s' % (metric, count, round(percentOfTotal, 2), round(compliance, 2)))
            elif 'High' in metric:
                percentOfTotal = count / totalAssets * 100
                compliance = 100 - percentOfTotal
                normalAverage += compliance
                weighted += compliance * highWeight
                report.append('%s: %s - %% of total: %s - %% in compliance: %s' % (metric, count, round(percentOfTotal, 2), round(compliance, 2)))
            elif 'Medium' in metric:
                percentOfTotal = count / totalAssets * 100
                compliance = 100 - percentOfTotal
                normalAverage += compliance
                weighted += compliance * medWeight
                report.append('%s: %s - %% of total: %s - %% in compliance: %s' % (metric, count, round(percentOfTotal, 2), round(compliance, 2)))
            else:
                pass
        report.append('Total Compliance KPI (weighted average based on priority, 3 = critical, 2 = medium, 1 = lowest): ' + str(round(weighted / (critWeight + highWeight + medWeight), 2)))
        report.append('vs normal average of all figures: ' + str(round(normalAverage / categories, 2)))
        return report
    except KeyError as error:
        raise error
    except ZeroDivisionError as error:
        print('Zero assets were discovered that match the intial query; nothing to process.')
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
    #Provide Organization API key to token variable
    token = ''
    #Provide URL of console
    console = 'https://console.runzero.com'
    #Output report name; default uses UTC time
    fileName = "KPI_report_" + str(datetime.utcnow())
    #KPIs variable is a list of dictionaries for each metric that will be iterated over and used to return total 
    # number of matching assets. Format is 'title' (Reported KPI metric), 'query' (the query needed to filter the assets 
    # according to KPI), and 'type' which is either 'asset' or 'vuln' according to the API endpoint that must be queried to obtain
    #the desired information. 
    timeRange = "1month" #Define time range for discovered assets in runZero syntax e.g. 1month, 2weeks, 3days, 12hours
    KPIs = [{'title': 'Systems Discovered within the Last %s' % timeRange, 'query': 'first_seen:<"%s"' % timeRange, 'type': 'asset'},
            {'title': 'Systems within the Last %s with Critical Vulnerabilities' % timeRange, 'query': 'source:crowdstrike AND severity:critical AND first_detected_at:<"%s"' % timeRange, 'type': 'vuln'},
            {'title': 'Systems within the Last %s with High Vulnerabilities' % timeRange, 'query': 'source:crowdstrike AND severity:high AND first_detected_at:<"%s"' % timeRange, 'type': 'vuln'},
            {'title': 'Systems within the Last %s with Medium Vulnerabilities' % timeRange, 'query': 'source:crowdstrike AND severity:medium AND first_detected_at:<"%s"' % timeRange, 'type': 'vuln'}]
    assetCounts = {}
    for item in KPIs:
        if item['type'] == 'vuln':
            results = getVulns(console, token, item['query'])
        else:
            results = getAssets(console, token, item['query'])
        assetCounts[item['title']] = results
    #Generate report from asset counts
    report = metrics(assetCounts)
    #Write resulting report to file
    writeFile(fileName, '\n'.join(report))