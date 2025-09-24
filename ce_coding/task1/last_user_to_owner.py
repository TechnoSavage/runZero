import argparse
import json
import os
import requests
from flatten_json import flatten
from getpass import getpass
from requests.exceptions import ConnectionError
    
def parseArgs():
    parser = argparse.ArgumentParser(description="Search assets for last user field from a specified source and assign that user as an asset owner to a given ownership type.")
    parser.add_argument('-u', '--url', dest='consoleURL', help='URL of console. This argument will override the .env file', 
                        required=False, default=os.environ["RUNZERO_BASE_URL"])
    parser.add_argument('-o', '--org', dest='organization', help='Organization UUID to execute against. This argument will override the .env file', 
                        required=False, default=os.environ["RUNZERO_ORG_ID"])
    parser.add_argument('-k', '--key', dest='token', help='Prompt for Account API key (do not enter at command line). This argument will override the .env file', 
                        nargs='?', const=None, required=False, default=os.environ["RUNZERO_ACCOUNT_TOKEN"])
    parser.add_argument('-s', '--source', help='Specify which recent user source to use for ownership assignment', choices=['crowdstrike', 'sentinelone', 'miradore', 'googleworkspace'], required=True)
    parser.add_argument('-t', '--type', help='Ownership type UUID that reported last users should be assigned to. If not specified, the found user will be added as "<user source> User"', required=False)
    parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    return parser.parse_args()
    
def get_assets(url, token, filter=" ", fields=" "):
    '''
        Retrieve assets using supplied query filter from Console and restrict to fields supplied.
        
        :param url: A string, URL of runZero console.
        :param token: A string, Organization API Key.
        :param filter: A string, query to filter returned assets(" " returns all).
        :param fields: A string, comma separated string of fields to return(" " returns all).
        :returns: a dict, JSON object of assets.
        :raises: ConnectionError: if unable to successfully make GET request to console.
    '''

    url = f"{url}/api/v1.0/export/org/assets.json"
    params = {'search': filter,
              'fields': fields}
    payload = ''
    headers = {'Accept': 'application/json',
               'Authorization': f'Bearer {token}'}
    try:
        response = requests.get(url, headers=headers, params=params, data=payload)
        if response.status_code != 200:
            print('Unable to retrieve assets' + str(response))
            exit()
        content = response.content
        data = json.loads(content)
        return data
    except ConnectionError as error:
        content = "No Response"
        raise error
    
def get_recent_user(data, source):
    '''
       Search asset "foreign_attributes" and extract last user for the specifed source.
     
       :param data: a dict: runZero JSON asset data.
       :param source: a string, the last user source to reference
       :returns: a dict: parsed runZero asset data.
       :raises: TypeError: if dataset is not iterable.
    '''
    
    try:
        assetList = []
        for item in data:
            asset = {}
            source_mapping = {'crowdstrike': 'foreign_attributes_@crowdstrike.dev_0_lastLoginUser',
                              'sentinelone': 'foreign_attributes_@sentinelone.dev_0_lastLoggedInUserName',
                              'googleworkspace': 'foreign_attributes_@googleworkspace.chromeos_0_recentUsers',
                              'miradore': 'foreign_attributes_@miradore.dev_0_user.name'}
            for key, value in item.items():
                if not isinstance(value, dict) and key == 'id':
                    asset[key] = item.get(key)

            root_keys_to_ignore = []
            for key, value in item.items():
                if not isinstance(value, dict):
                    root_keys_to_ignore.append(key)
                flattened_items = flatten(nested_dict=item, root_keys_to_ignore=root_keys_to_ignore)
                asset["owner"] = flattened_items.get(source_mapping[source.lower()], None)
            assetList.append(asset)
        return(assetList)
    except TypeError as error:
        raise error
    
def parse_owners(url, token, owner_list, owner_type):
    '''
        Parse supplied ownership sources for most detailed owner info.
        Pass owner to assign function to assign owner info. 

        :param url: A string, URL of runZero console.
        :param token: A string, Organization API Key.
        :param ownerList: A list, list of dictionaries containing asset ID and last user info.
        :param owner_type: A string, UUID of ownership type.
        :raises: ConnectionError: if unable to successfully make PATCH request to console.
    '''
    
    no_assign = [None, 'sshd', 'ssm-user', 'nt authority\anonymous logon', 'default group', 'developer']
    for owner in owner_list:
        reported_owner = None
        for k,v in owner.items():
            # In other words: do nothing if the Key is 'id' (used to identify asset), if the value is 'None', or if the last user is in the "No assign" list (case-insensitive)
            if k == 'id' or not v or v and v.lower() in no_assign:
                pass
            else:
                owner = v
        if reported_owner:
            assignment = assign_owner(url, token, owner['id'], reported_owner, owner_type)
            return assignment
        
def get_owner_groups(url, token):
    url = f"{url}/api/v1.0/account/assets/ownership-types"
    headers = {'Content-Type': 'application/json',
               'Authorization': f'Bearer {token}'}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print('Unable to retrieve ownership types' + str(response))
            exit()
        content = response.content
        data = json.loads(content)
        return data
    except ConnectionError as error:
        content = "No Response"
        raise error

def create_owner_group(url, token, group_name):
    url = f"{url}/api/v1.0/account/assets/ownership-types"
    headers = {'Content-Type': 'application/json',
               'Authorization': f'Bearer {token}'}
    payload =  {"name": group_name,
                "reference": 1,
                "order": 1,
                "hidden": 'false'}
    try:
        response = requests.post(url, headers=headers, data=payload)
        if response.status_code != 200:
            print('Unable to create ownership type' + str(response))
            exit()
        content = response.content
        data = json.loads(content)
        return data['id']
    except ConnectionError as error:
        content = "No Response"
        raise error

def assign_owner(url, token, id, owner, owner_type):
    '''
        Assign supplied owner name to asset ID under given owner_type.
        
        :param url: A string, URL of runZero console.
        :param token: A string, Organization API Key.
        :param id: A string, UUID of asset.
        :param owner: A string, name of asset owner.
        :param owner_type: A string, UUID of ownership type.
        :returns: a dict, JSON object of assets.
        :raises: ConnectionError: if unable to successfully make PATCH request to console.
    '''
    
    url = f"{url}/api/v1.0/org/assets/{id}/owners"
    payload = json.dumps({"ownerships": [{"ownership_type_id": owner_type, "owner": owner}]})
    headers = {'Content-Type': 'application/json',
               'Authorization': f'Bearer {token}'}
    try:
        response = requests.patch(url, headers=headers, data=payload)
        if response.status_code != 200:
            print('Unable to add owner' + str(response))
            exit()
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
    if not args.organization:
        print("No organization ID has been provided in the .env file. Please provide a valid Organization UUID using the '-o' argument")
    #Query to grab all assets with the specified last user source
    query = f"source:{args.source}"
    fields = "id, foreign_attributes" #fields to return in API call
    assets = get_assets(args.consoleURL, token, query, fields)
    results = get_recent_user(assets, args.source)
    group_id == args.type
    if not group_id:
        group_target = f'{args.source} user'.title()
        owner_groups = get_owner_groups(args.consoleURL, token)
        for group in owner_groups:
            if group['name'] == group_target:
                group_id = group['id']
    if not group_id:             
        group_id = create_owner_group(args.consoleURL, token, group_target)
    assignment = parse_owners(args.consoleURL, token, results, group_id)
    print(assignment)

if __name__ == "__main__":
    main()