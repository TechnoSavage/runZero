# runZero Custom Integration with XYZ platform
# Docs: https://www.runzero.com/docs/integrations-inbound/
# Docs: https://pypi.org/project/runzero-sdk/ 
# Docs: https://documentation.solarwinds.com/en/success_center/observability/content/api/api-swagger.htm
# Docs: https://documentation.solarwinds.com/en/success_center/observability/content/observability_administrator_guide.htm
# Docs: https://documentation.solarwinds.com/en/success_center/orionplatform/content/orion_platform_administrator_guide.htm
# Prerequisite: pip install runzero-sdk

import json
import requests
import os
import uuid
from flatten_json import flatten
from ipaddress import ip_address
from typing import Any, Dict, List
import runzero
from runzero.client import AuthError
from runzero.api import CustomAssets, Sites
from runzero.types import (ImportAsset,IPv4Address,IPv6Address,NetworkInterface,ImportTask,Software,Vulnerability)

# Configure runZero variables
# Script uses pipenv, but os.environ[] can be swapped out for a hardcoded value to make testing easier
RUNZERO_BASE_URL = os.environ['RUNZERO_BASE_URL']
RUNZERO_CLIENT_ID = os.environ['RUNZERO_CLIENT_ID']
RUNZERO_CLIENT_SECRET = os.environ['RUNZERO_CLIENT_SECRET']
RUNZERO_ORG_ID = os.environ['RUNZERO_ORG_ID']
RUNZERO_SITE_NAME = os.environ['RUNZERO_SITE_NAME']
RUNZERO_SITE_ID = os.environ['RUNZERO_SITE_ID']
ORION_CUSTOM_SOURCE_ID = os.environ['INTEGRATION_CUSTOM_SOURCE_ID']
ORION_IMPORT_TASK_NAME = os.environ['INTEGRATION_IMPORT_TASK_NAME']


# Configure Integration API variables (examples provided)
# Script uses pipenv, but os.environ[] can be swapped out for a hardcoded value to make testing easier
ORION_DATA_CENTER = os.environ['ORION_DATA_CENTER']
SWOKEN = os.environ['SWOKEN']

def build_assets_from_json(json_input: List[Dict[str, Any]]) -> List[ImportAsset]:
    '''
    This is an example function to highlight how to handle converting data from an API into the ImportAsset format that
    is required for uploading to the runZero platform. This function assumes that the json has been converted into a list 
    of dictionaries using `json.loads()` (or any similar functions).

    Map asset attributes from API reponse and populate custom attributes and network interfaces.

    :param json_input: a dict, API JSON response of asset data.
    :returns: a list, asset data formatted for runZero import.  
    '''

    assets: List[ImportAsset] = []
    for item in json_input:
        #Assign API attributes from the json dict that correspond to SDK
        item = flatten(item)
        asset_id = item.get('id', str(uuid.uuid4()))
        mac = item.get('custom_api_mac', None)
        model = item.get('custom_api_model_name', '')
        device_type = item.get('custom_api_device', '')
        manuf = item.get('custom_api_manufacturer', '')

        # create the network interface
        network = build_network_interface(ips=[], mac=mac)

        # handle any additional values and insert into custom_attrs
        custom_attrs: Dict[str] = {}
        for key, value in item.items():
            if isinstance(value, dict):
                for k, v in value.items():
                    custom_attrs[k] = str(v)[:1023]
            else:
               custom_attrs[key] = str(value)[:1023]

        # Build assets for import
        assets.append(
            ImportAsset(
                id=asset_id,
                networkInterfaces=[network],
                model=model,
                deviceType=device_type,
                manufacturer=manuf,
                customAttributes=custom_attrs
            )
        )
    return assets

def build_network_interface(ips: List[str], mac: str = None) -> NetworkInterface:
    ''' 
    This function converts a mac and a list of strings in either ipv4 or ipv6 format and creates a NetworkInterface that
    is accepted in the ImportAsset

    :param ips: A list, a list of IP addresses
    :param mac: A string, a MAC address formatted as follows 00:11:22:AA:BB:CC
    :returns: A list, a list of runZero network interface classes
    '''

    ip4s: List[IPv4Address] = []
    ip6s: List[IPv6Address] = []
    for ip in ips[:99]:
        ip_addr = ip_address(ip)
        if ip_addr.version == 4:
            ip4s.append(ip_addr)
        elif ip_addr.version == 6:
            ip6s.append(ip_addr)
        else:
            continue
    if mac is None:
        return NetworkInterface(ipv4Addresses=ip4s, ipv6Addresses=ip6s)
    else:
        return NetworkInterface(macAddress=mac, ipv4Addresses=ip4s, ipv6Addresses=ip6s)

def import_data_to_runzero(assets: List[ImportAsset]):
    '''
    Import assets to specified runZero Organization and Site using the specified Custom Source ID and Name.

    :param assets: A list, list of assets formatted by the ImportAsset class from the runZero SDK.
    :returns: None
    '''

    # create the runzero client
    client = runzero.Client()

    # try to log in using OAuth credentials
    try:
        client.oauth_login(RUNZERO_CLIENT_ID, RUNZERO_CLIENT_SECRET)
    except AuthError as error:
        print(f'login failed: {error}')
        return

    # create the site manager to get our site information; set site ID for any new hosts
    site_mgr = Sites(client)
    site = site_mgr.get(RUNZERO_ORG_ID, RUNZERO_SITE_NAME)
    if not site:
        print(f'unable to find requested site')
        return

    # create the import manager to upload custom assets
    import_mgr = CustomAssets(client)
    import_task = import_mgr.upload_assets(org_id=RUNZERO_ORG_ID, site_id=RUNZERO_SITE_ID, custom_integration_id=ORION_CUSTOM_SOURCE_ID, assets=assets, task_info=ImportTask(name=ORION_IMPORT_TASK_NAME))

    if import_task:
        print(f'task created! view status here: {RUNZERO_BASE_URL}/api/v1.0/tasks?task={import_task.id}')

def get_assets(dc=ORION_DATA_CENTER, token=SWOKEN):
    '''
    Retrieve assets from API endpoint.
    
    :param dc: A string, Solarwinds data ceneter.
    :param token: A string, authentication token for API endpoint.
    :returns: A dict, asset data.
    :raises: ConnectionError: if unable to successfully make GET request to webserver.
    '''
    url = f"https://api.{ORION_DATA_CENTER}.cloud.solarwinds.com/v1/metrics"
    headers = {'Accept': 'application/json',
               'Content-Type': 'application/json',
               'Authorization': f'Bearer {token}'}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Unable to retrieve assets from API. Received {response.status_code}")
            exit()
        return json.loads(response.content)
    except ConnectionError as error:
        print("No Response from server.", error)
        exit()

def parse_response(json_raw):
    '''
    Dummy function placeholder for any function that needs to parse or transform the Integration API response
    '''
    do_stuff = json_raw
    return do_stuff

def main():
    '''
    Your code to call the custom integration API here
    '''

    json_raw = get_assets()
    parsed_json = parse_response(json_raw)

    # Format asset list for import into runZero
    import_assets = build_assets_from_json(parsed_json)

    # Import assets into runZero
    import_data_to_runzero(assets=import_assets)

if __name__ == '__main__':
    main()