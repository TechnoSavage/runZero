# runZero Custom Integration with Manage Engine
# Docs: https://www.runzero.com/docs/integrations-inbound/
# Docs: https://pypi.org/project/runzero-sdk/ 
# Docs: https://www.manageengine.com/products/desktop-central/api/api-inventory-scancomputers.html
# Prerequisite: pip install runzero-sdk

import json
import requests
import os
import uuid
from ipaddress import ip_address
from typing import Any, Dict, List
import runzero
from runzero.client import AuthError
from runzero.api import CustomAssets, Sites
from runzero.types import (ImportAsset,IPv4Address,IPv6Address,NetworkInterface,ImportTask)

# Configure runZero variables
RUNZERO_BASE_URL = os.environ['RUNZERO_BASE_URL']
RUNZERO_CLIENT_ID = os.environ['RUNZERO_CLIENT_ID']
RUNZERO_CLIENT_SECRET = os.environ['RUNZERO_CLIENT_SECRET']
RUNZERO_ORG_ID = os.environ['RUNZERO_ORG_ID']
RUNZERO_SITE_NAME = os.environ['RUNZERO_SITE_NAME']
RUNZERO_SITE_ID = os.environ['RUNZERO_SITE_ID']
MEEC_CUSTOM_SOURCE_ID = os.environ['MEEC_CUSTOM_SOURCE_ID']
MEEC_IMPORT_TASK_NAME = os.environ['MEEC_IMPORT_TASK_NAME']


# Configure Manage Engine API variables
MEEC_URL = f"{os.environ['MEEC_BASE_URL']}api/1.4/inventory/scancomputers"
MEEC_KEY = os.environ['MEEC_KEY']

def build_assets_from_json(json_input: List[Dict[str, Any]]) -> List[ImportAsset]:
    '''
    Map asset attributes from API reponse and populate custom attributes and network interfaces.

    :param json_input: a dict, API JSON response of asset data.
    :returns: a list, asset data formatted for runZero import.  
    '''

    assets: List[ImportAsset] = []
    for item in json_input:
        #Assign API attributes from the json dict that correspond to SDK
        id = item.get('resource_id', str(uuid.uuid4()))
        asset_id = item.get('resource_id', str(uuid.uuid4()))
        macs = item.get('mac_address', '').replace('--', '').split(',')
        if macs == '' or len(macs) == 0:
            macs = None
        os = item.get('service_pack', '').replace('(x64)', '').replace('(x86)', '')
        if os == '':
            os = item.get('os_name', '')
        addresses = item.get('ip_address', '').split(',')
        name = item.get('resource_name', '')

        # create the network interfaces
        interfaces = []
        for address in addresses:
            index = addresses.index(address)
            try:
                interface = build_network_interface(ips=[address], mac=macs[index])
            except:
                interface = build_network_interface(ips=[address], mac=None)
            interfaces.append(interface)

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
                id=id,
                asset_id=asset_id,
                networkInterfaces=interfaces,
                os=os,
                name=name,
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
    import_task = import_mgr.upload_assets(org_id=RUNZERO_ORG_ID, site_id=RUNZERO_SITE_ID, custom_integration_id=MEEC_CUSTOM_SOURCE_ID, assets=assets, task_info=ImportTask(name=MEEC_IMPORT_TASK_NAME))

    if import_task:
        print(f'task created! view status here: {RUNZERO_BASE_URL}/api/v1.0/tasks?task={import_task.id}')

def get_assets():
    '''
    Retrieve assets from Manage Engine "Scan Computers" API endpoint.
            
    :returns: A dict, Manage Engine asset data.
    :raises: ConnectionError: if unable to successfully make GET request to Manage Engine webserver.
    '''
    
    url = MEEC_URL
    headers = {'Accept': 'application/json',
                 'Content-Type': 'application/json',
                 'Authorization': f'Bearer {MEEC_KEY}'}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Unable to retrieve assets from Manage Engine. Received {response.status_code}")
            exit()
        return json.loads(response.content)
    except ConnectionError as error:
        print("No Response from Manage Engine server.", error)
        exit()

def filter_assets(json_raw):
    '''
    Filter API response to only assets that have the Manage Engine agent installed.

    :param json_raw: a dict, Manage Engine API response.
    :returns: a dict, filtered API response.
    '''
    parsed = []
    for item in json_raw["message_response"]["scancomputers"]:
        status = item.get('installation_status', '')
        if status == 22:
            parsed.append(item)
    return parsed

def main():

    asset_json_raw = get_assets()
    
    # Filter initial API response to include only assets with agents
    asset_json = filter_assets(asset_json_raw)

    # Format asset list for import into runZero
    import_assets = build_assets_from_json(asset_json)
   
    # Import assets into runZero
    import_data_to_runzero(assets=import_assets)

if __name__ == '__main__':
    main()