# runZero Custom Integration with FileWave
# Docs: https://www.runzero.com/docs/integrations-inbound/
# Docs: https://pypi.org/project/runzero-sdk/ 
# Docs: https://kb.filewave.com/books/application-programming-interface-api
# Prerequisite: pip install runzero-sdk

from datetime import datetime
from ipaddress import ip_address
import json
import os
import requests
import runzero
from runzero.client import AuthError
from runzero.api import CustomAssets, Sites
from runzero.types import (CustomAttribute,ImportAsset,IPv4Address,IPv6Address,NetworkInterface,ImportTask)
from typing import Any, Dict, List
import uuid

# Configure runZero variables
RUNZERO_BASE_URL = os.environ['RUNZERO_BASE_URL']
RUNZERO_CLIENT_ID = os.environ['RUNZERO_CLIENT_ID']
RUNZERO_CLIENT_SECRET = os.environ['RUNZERO_CLIENT_SECRET']
RUNZERO_ORG_ID = os.environ['RUNZERO_ORG_ID']
RUNZERO_SITE_NAME = os.environ['RUNZERO_SITE_NAME']
RUNZERO_SITE_ID = os.environ['RUNZERO_SITE_ID']
FW_CUSTOM_SOURCE_ID = os.environ['FW_CUSTOM_SOURCE_ID']
FW_IMPORT_TASK_NAME = os.environ['FW_IMPORT_TASK_NAME']

# Configure FileWave variables
FW_API_URL = f"{os.environ['FW_BASE_URL']}/api/inv/api/v1/" # curl -s  -H "Authorization: $auth" https://$server_dns:/api/inv/api/v1/query_result/191
FW_API_KEY = os.environ['FW_API_KEY']
FW_REPORT = os.environ['FW_REPORT']

def build_assets_from_json(json_input: List[Dict[str, Any]]) -> List[ImportAsset]:
    '''
    Map asset attributes from API reponse and populate custom attributes and network interfaces.

    :param json_input: a dict, API JSON response of asset data.
    :returns: a list, asset data formatted for runZero import.  
    '''

    assets: List[ImportAsset] = []
    for item in json_input:
        # assign known API attributes from the json dict that are always present
        # if custom fields created in FileWave align to asset fields in r0 SDK docs
        # additional attributes can be added here following the pattern
        asset_id = item.get('Client_device_id', str(uuid.uuid4()))
        ip = item.get('Client_current_ip_address', '')
        macs = item.get('NetworkInterface_mac_address', [])
        os_name = item.get('OperatingSystem_name', '')
        name = item.get('Client_device_name', '')
        model = item.get('Client_device_product_name', '')
        vendor = item.get('DesktopClient_device_manufacturer', '')

        # create the network interfaces
        networks = []
        for mac in macs:
            network = build_network_interface(ips=[ip], mac=mac)
            networks.append(network)

        # handle any additional values and insert into custom_attrs
        custom_attrs: Dict[str] = {}
        for key, value in item.items():
            if isinstance(value, dict):
                for k, v in value.items():
                    custom_attrs[k] = str(v)[:1023]
            else:
               custom_attrs[key] = str(value)

        # Build assets for import
        assets.append(
            ImportAsset(
                id=asset_id,
                hostnames=[name],
                os=os_name,
                networkInterfaces=networks,
                model=model,
                manufacturer=vendor,
                customAttributes=custom_attrs,
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
    import_task = import_mgr.upload_assets(org_id=RUNZERO_ORG_ID, site_id=RUNZERO_SITE_ID, custom_integration_id=FW_CUSTOM_SOURCE_ID, assets=assets, task_info=ImportTask(name=FW_IMPORT_TASK_NAME))

    if import_task:
        print(f'task created! view status here: {RUNZERO_BASE_URL}/api/v1.0/tasks?task={import_task.id}')

def get_assets(url=FW_API_URL, token=FW_API_KEY, report=FW_REPORT):
    '''
    Retrieve asset data from specified Filewave report.
        
    :param url: A string, URL of Filewave instance.
    :param token: A string, Filewave API Key.
    :returns: a dict, JSON object of assets.
    :raises: ConnectionError: if unable to successfully make GET request to console.
    '''

    url = f"{url}/api/inv/api/v1/query_result/{report}"
    params = ''
    payload = ''
    headers = {'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {token}'}
    try:
        response = requests.get(url, headers=headers, params=params, data=payload)
        if response.status_code != 200:
            print(f"Unable to retrieve assets from FileWave. Received {response.status_code}")
            exit()
        content = response.content
        data = json.loads(content)
        return data
    except ConnectionError as error:
        content = "No Response"
        raise error

def reformat_response(raw_json):
    '''
    Function to reformat the API response by mapping the fields
    to the corresponding values for each asset in values.
         
    :param raw_json: a dict, FileWave API response
    :returns: a list of dictionaries. 
    '''
    
    # assign reported fields as keys to all reported value sets
    mapped_keys = []
    keys = raw_json['fields']
    for values in raw_json['values']:
        asset = {}
        for key in keys:
            position = keys.index(key)
            asset[key] = values[position]
        mapped_keys.append(asset)
    # create a list of unique asset IDs
    uniqIDs = set([asset['Client_device_id'] for asset in mapped_keys])
    # formatted json will capture most recent asset info according to most recent check-in date
    # and contain a list of all reported MAC addresses instead of a single value
    formatted_json = []
    # Use the unique IDs to find all assets with the same ID and create a list of check-in dates
    # and create a list of reported MACS
    for assetID in uniqIDs:
        checkinDates = list(set([asset['Client_last_check_in'] for asset in mapped_keys if assetID == asset['Client_device_id']]))
        checkinDates.sort(key=lambda date: datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ'), reverse=True)
        mostRecent = checkinDates[0]
        macAddresses = list(set([asset['NetworkInterface_mac_address'] for asset in mapped_keys if assetID == asset['Client_device_id']]))
        # sort reported timestamps to retrieve most recently reported asset information
        for asset in mapped_keys:
            if asset['Client_device_id'] == assetID and asset['Client_last_check_in'] == mostRecent:
                # replace single value of reported MAC address with list of reported MAC address
                asset['NetworkInterface_mac_address'] = macAddresses
                if asset not in formatted_json:
                    formatted_json.append(asset)
    # Reformat OS field for MacOS to fit runZero expected format
    for asset in formatted_json:
        if "macOS" in asset['OperatingSystem_name']:
            asset['OperatingSystem_name'] = 'macOS ' + asset['OperatingSystem_version']
    return formatted_json

def main():
    with open('filewave_raw.json', 'r') as input:
        asset_json_raw = json.load(input)

    # asset_json_raw = getAssets()

    asset_json_formatted = reformat_response(asset_json_raw)
    
    # Format asset list for import into runZero
    import_assets = build_assets_from_json(asset_json_formatted)

    # Import assets into runZero
    import_data_to_runzero(assets=import_assets)

# *** Should not need to touch this ***
if __name__ == '__main__':
    main()