#!/usr/bin/python

""" EXAMPLE PYTHON SCRIPT! NOT INTENDED FOR PRODUCTION USE! 
    kpi.py, version 1.0 by Derek Burke
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
    #Provide Organization API key as hard-coded variable
    token = ''
    #Provide URL of console
    console = 'https://console.runzero.com'
    #Output report name; default uses UTC time
    fileName = "KPI_report" + str(datetime.utcnow())
    #KPIs variable is a list that will be iterated over and used to return total number of matching assets.
    #Format is 'title' (Reported KPI metric), 'query' (the query needed to filter the assets according to KPI),
    #and 'type' which is either 'asset' or 'vuln' according to the API endpoint that must be queried to obtain
    #the desired information
    #Add or remove relevant KPIs AND associated queries as needed.
    KPIs = [{'title': 'Systems Discovered within Last 30 Days', 'query': 'first_seen:<"1month"', 'type': 'asset'},
            {'title': 'Systems with Critical Vulnerabilities','query': 'source:crowdstrike AND severity:critical', 'type': 'vuln'},
            {'title': 'Systems with Critical Vulnerabilities Older than 30 Days', 'query': 'source:crowdstrike AND severity:critical AND first_detected_at:>"1month"', 'type': 'vuln'},
            {'title': 'Systems with Critical Vulnerabilities Older than 14 Days', 'query': 'source:crowdstrike AND severity:critical AND first_detected_at:>"14days"', 'type': 'vuln'},
            {'title': 'Systems with Critical Vulnerabilities Older than 3 Days', 'query': 'source:crowdstrike AND severity:critical AND first_detected_at:>"3days"', 'type': 'vuln'},
            {'title': 'Systems with High Vulnerabilities', 'query': 'source:crowdstrike AND severity:high', 'type': 'vuln'},
            {'title': 'Systems with High Vulnerabilities Older than 30 Days', 'query': 'source:crowdstrike AND severity:high AND first_detected_at:>"1month"', 'type': 'vuln'},
            {'title': 'Systems with Critical Vulnerabilities Older than 3 Days', 'query': 'source:crowdstrike AND severity:high AND first_detected_at:>"14days"', 'type': 'vuln'},
            {'title': 'Systems with Critical Vulnerabilities Older than 3 Days', 'query': 'source:crowdstrike AND severity:high AND first_detected_at:>"3days"', 'type': 'vuln'},
            {'title': 'Systems with Medium Vulnerabilities', 'query': 'source:crowdstrike AND severity:medium', 'type': 'vuln'},
            {'title': 'Systems with Medium Vulnerabilities Older than 30 Days', 'query': 'source:crowdstrike AND severity:medium AND first_detected_at:>"1month"', 'type': 'vuln'},
            {'title': 'Systems with Medium Vulnerabilities Older than 30 Days', 'query': 'source:crowdstrike AND severity:medium AND first_detected_at:>"14days"', 'type': 'vuln'},
            {'title': 'Systems with Medium Vulnerabilities Older than 30 Days', 'query': 'source:crowdstrike AND severity:medium AND first_detected_at:>"3days"', 'type': 'vuln'},
            ]
    report = {}
    for item in KPIs:
        if item['type'] == 'vuln':
            results = getVulns(console, token, item['query'])
        else:
            results = getAssets(console, token, item['query'])
        report[item['title']] = results
    #Write resulting report to file
    writeFile(fileName, json.dumps(report))

    