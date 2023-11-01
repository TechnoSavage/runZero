""" EXAMPLE PYTHON SCRIPT! NOT INTENDED FOR PRODUCTION USE! 
    lastUser2Owner.py, version 1.0
    This script will search asset foreign attributes (EDR, MDM, etc.) for last logon user information
    and apply last logged on user as an asset owner type defined in the provided argument (e.g. Primary User)"""

import argparse
import json
import os
import requests
from flatten_json import flatten
from getpass import getpass
from requests.exceptions import ConnectionError
    
def parseArgs():
    parser = argparse.ArgumentParser(description="Search assets for last user field and assign last user as asset owner.")
    parser.add_argument('-u', '--url', dest='consoleURL', help='URL of console. This argument will override the .env file', 
                        required=False, default=os.environ["RUNZERO_BASE_URL"])
    parser.add_argument('-k', '--key', dest='token', help='Prompt for Organization API key (do not enter at command line). This argument will override the .env file', 
                        nargs='?', const=None, required=False, default=os.environ["RUNZERO_ORG_TOKEN"])
    parser.add_argument('-t', '--type', help='Ownership type UUID that reported last users should be assigned to', required=True)
    parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    return parser.parse_args()
    
def getAssets(url, token, filter=" ", fields=" "):
    """ Retrieve assets using supplied query filter from Console and restrict to fields supplied.
        
        :param url: A string, URL of runZero console.
        :param token: A string, Organization API Key.
        :param filter: A string, query to filter returned assets(" " returns all).
        :param fields: A string, comma separated string of fields to return(" " returns all).
        :returns: a dict, JSON object of assets.
        :raises: ConnectionError: if unable to successfully make GET request to console."""

    url = f"{url}/api/v1.0/export/org/assets.json"
    params = {'search': filter,
              'fields': fields}
    payload = ''
    headers = {'Accept': 'application/json',
               'Authorization': f'Bearer {token}'}
    try:
        response = requests.get(url, headers=headers, params=params, data=payload)
        content = response.content
        data = json.loads(content)
        return data
    except ConnectionError as error:
        content = "No Response"
        raise error
    
def getUsers(data):
    """Search asset "foreign_attributes" and extract last user where available, discard the rest.
     
       :param data: a dict: runZero JSON asset data.
       :returns: a dict: parsed runZero asset data.
       :raises: TypeError: if dataset is not iterable."""
    
    try:
        assetList = []
        for item in data:
            asset = {}
            for key, value in item.items():
                if not isinstance(value, dict) and key == 'id':
                    asset[key] = item.get(key)

            root_keys_to_ignore = []
            for key, value in item.items():
                if not isinstance(value, dict):
                    root_keys_to_ignore.append(key)
                flattened_items = flatten(nested_dict=item, root_keys_to_ignore=root_keys_to_ignore)
                asset['s1_user'] = flattened_items.get('foreign_attributes_@sentinelone.dev_0_lastLoggedInUserName', None)
                asset['mir_user'] = flattened_items.get('foreign_attributes_@miradore.dev_0_user.name', None)
                asset['goog_user'] = flattened_items.get('foreign_attributes_@googleworkspace.chromeos_0_recentUsers', None)
                asset['cs_user'] = flattened_items.get('foreign_attributes_@crowdstrike.dev_0_lastLoginUser', None)
            assetList.append(asset)
        return(assetList)
    except TypeError as error:
        raise error
    
def parseOwners(url, token, ownerList, owner_type):
    """ Parse supplied ownership sources for most detailed owner info.
        Pass owner to assign function to assign owner info. 

        :param url: A string, URL of runZero console.
        :param token: A string, Organization API Key.
        :param ownerList: A list, list of dictionaries containing asset ID and last user info.
        :param owner_type: A string, UUID of ownership type.
        :raises: ConnectionError: if unable to successfully make PATCH request to console. """
    
    #to do: improve method of filtering out system accounts
    #add system accounts to noAssign list to prevent them from being populated as owners
    noAssign = [None, 'sshd', 'ssm-user', 'nt authority\anonymous logon', 'default group', 'developer']
    for owner in ownerList:
        best_owner = ''
        for k,v in owner.items():
            if k == 'id' or not v or v and v.lower() in noAssign or len(v) <= len(best_owner):
                pass
            else:
                best_owner = v
        if best_owner != '':
            assignment = assignOwner(url, token, owner['id'], best_owner, owner_type)
            return assignment

def assignOwner(url, token, id, owner, owner_type):
    """ Assign supplied owner name to asset ID under given owner_type.
        
        :param url: A string, URL of runZero console.
        :param token: A string, Organization API Key.
        :param id: A string, UUID of asset.
        :param owner: A string, name of asset owner.
        :param owner_type: A string, UUID of ownership type.
        :returns: a dict, JSON object of assets.
        :raises: ConnectionError: if unable to successfully make PATCH request to console. """
    
    url = f"{url}/api/v1.0/org/assets/{id}/owners"
    payload = json.dumps({"ownerships": [{"ownership_type_id": owner_type, "owner": owner}]})
    headers = {'Content-Type': 'application/json',
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
    #Query to grab all assets with a last user source
    query = "source:sentinelone or source:crowdstrike or source:googleworkspace"
    #fields to return in API call
    fields = "id, foreign_attributes"
    assets = getAssets(args.consoleURL, token, query, fields)
    results = getUsers(assets)
    assignment = parseOwners(args.consoleURL, token, results, args.type)
    print(assignment)

if __name__ == "__main__":
    main()