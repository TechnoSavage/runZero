""" EXAMPLE PYTHON SCRIPT! NOT INTENDED FOR PRODUCTION USE! 
    updateSite.py, version 1.0
    This script can be used to programatically update or overwrite a site scope and/or registered
    subnets."""

import argparse
import json
import os
import pandas as pd
import re
import requests
from getpass import getpass
from requests.exceptions import ConnectionError
    
def parseArgs():
    parser = argparse.ArgumentParser(description="Update discovery scope for specified site. Default behavior is to append to scope; use -r to replace site.")
    parser.add_argument('-u', '--url', dest='consoleURL', help='URL of console. This argument will override the .env file', 
                        required=False, default=os.environ["RUNZERO_BASE_URL"])
    parser.add_argument('-k', '--key', dest='token', help='Prompt for Organization API key (do not enter at command line). This argument will override the .env file', 
                        nargs='?', const=None, required=False, default=os.environ["RUNZERO_ORG_TOKEN"])
    parser.add_argument('-s', '--site', help='UUID or name of site to modify. This argument will override the .env file', 
                        required=False, default=os.environ["RUNZERO_SITE_ID"])
    parser.add_argument('-c', '--create', help='Create the site if the name provided does not exist', action='store_true', required=False)
    parser.add_argument('-iL', '--input-list', dest='targetFile', help='Text file with site scope/registered subnets.', 
                        required=False)
    parser.add_argument('-eL', '--input-exclusion', dest='exclusionFile', help='Text file with site exclusions.', required=False)
    parser.add_argument('-r', '--replace', help='Replace current site scope with provided scope.', action='store_true', required=False)
    parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    return parser.parse_args()

def confirmSite(url, token, site):
    """ Confirm or retrieve UUID of Organization site. 
    
        :param url: A string, URL of the runZero console.
        :param token: A string, Organization API Key.
        :param site: A string, UUID or name of site.
        :returns: A string, runZero site UUID.
        :raises: ConnectionError: if unable to successfully make GET request to console."""
    
    url = f"{url}/api/v1.0/org/sites"
    payload = ""
    headers = {'Accept': 'application/json',
               'Authorization': f'Bearer {token}'}
    siteID = None
    try:
        response = requests.get(url, headers=headers, data=payload)
        content = response.content
        data = json.loads(content)
        for item in data:
            id = item.get('id', '')
            name = item.get('name', '')
            if site == id or site == name:
                siteID = id
        return siteID
    except ConnectionError as error:
        content = "No Response"
        raise error
    
def createSite(url, token, site):
    """ Confirm or retrieve UUID of Organization site.
    
        :param url: A string, URL of the runZero console.
        :param token: A string, Organization API Key.
        :param site: A string, name of site.
        :returns: A string, runZero site UUID.
        :raises: ConnectionError: if unable to successfully make PUT request to console."""
    
    url = f"{url}/api/v1.0/org/sites"
    payload = json.dumps({"name": site,
               "description": " ",
               "scope": " ",
               "excludes": " "})
    headers = {'Content-Type': 'application/json',
               'Authorization': f'Bearer {token}'}
    try:
        response = requests.put(url, headers=headers, data=payload)
        content = response.content
        data = json.loads(content)
        siteID = data['id']
        return siteID
    except ConnectionError as error:
        content = "No Response"
        raise error

def buildSiteFrame(targetFile, exclusionFile):
    pass

def subnetCheck(scope):
    """ Check for valid IPv4 address with CIDR mask or optional decimal subnet mask.
       
       :param test: A string, string to test for valid IP address and Subnet mask/CIDR format.
       :returns: A string, if input contains a valid match the match is returned in proper format.
       :returns: An int, if input contains no valid IP + subnet/CIDR format 0 is returned.
       :raises: TypeError: if regular expression match cannot be run on test variable."""
    subnets = []
    for item in scope:
        try:
            ipv4_address = re.findall('(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)', item)
            if "/" in item and len(ipv4_address) == 1:
                cidr = re.findall('/([1-9][0-9]*)', item)
                if int(cidr[0]) in range(1, 33):
                    ipv4_subnet = f"{ipv4_address[0]}/{cidr[0]}"
                    return ipv4_subnet
                else:
                    pass
            if len(ipv4_address) > 1:
                ipv4_subnet = f"{ipv4_address[0]}/{ipv4_address[1]}"
                subnets.append(ipv4_subnet)
        except TypeError as reason:
            return 0

def appendSubnets(url, token, siteUUID, scope, exclusions):
    """ Append to site scope.
    
        :param url: A string, URL of the runZero console.
        :param token: A string, Organization API Key.
        :param siteUUID: A string, UUID of site.
        :param scope: A list, targets for site scope.
        :returns: A dict, JSON output.
        :raises: ConnectionError: if unable to successfully make PATCH request to console."""

    url = f"{url}/api/v1.0/org/sites/{siteUUID}"
    payload = json.dumps({"scope": scope,
                          "excludes": exclusions})
    headers = {'Accept': 'application/json',
               'Authorization': f'Bearer {token}'}
    try:
        response = requests.patch(url, headers=headers, data=payload)
        content = response.content
        data = json.loads(content)
        return data
    except ConnectionError as error:
        content = "No Response"
        raise error

def replaceSubnets(url, token, siteUUID, scope, exclusions):
    """ Replace site scope.
    
        :param url: A string, URL of the runZero console.
        :param token: A string, Organization API Key.
        :param siteUUID: A string, UUID of site.
        :param scope: A list, targets for site scope.
        :returns: A dict, JSON output.
        :raises: ConnectionError: if unable to successfully make PATCH request to console."""

    url = f"{url}/api/v1.0/org/sites/{siteUUID}"
    subnets = {}
    for item in scope:
        subnets[item] = {"description": " "}
    payload = json.dumps({"scope" : scope,
                          "subnets": subnets, 
                          "excludes": exclusions})
    headers = {'Accept': 'application/json',
               'Authorization': f'Bearer {token}'}
    try:
        response = requests.patch(url, headers=headers, data=payload)
        content = response.content
        data = json.loads(content)
        return data
    except ConnectionError as error:
        content = "No Response"
        raise error
    
def main():
    args = parseArgs()
    token = args.token
    if token == None:
        token = getpass(prompt="Enter your Organization API Key: ")
    scope = buildSiteFrame(args.targetFile)
    exclusions = buildSiteFrame(args.exclusionFile)
    siteID = confirmSite(args.consoleURL, token, args.site)
    if siteID == None and args.create:
        siteID = createSite(args.consoleURL, token, args.site)
    if args.replace:
        replaceSubnets(args.consoleURL, token, siteID, scope, exclusions)
    else:
        appendSubnets(args.consoleURL, token, siteID, scope, exclusions)

if __name__ == "__main__":
    main()