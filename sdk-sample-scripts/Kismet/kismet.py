# runZero Custom Integration with Kismet
# Docs: https://www.runzero.com/docs/integrations-inbound/
# Docs: https://pypi.org/project/runzero-sdk/ 
# Docs: https://www.kismetwireless.net/docs/readme/intro/kismet/
# Docs: https://www.kismetwireless.net/docs/api/rest_like/
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
from runzero.types import (ImportAsset,IPv4Address,IPv6Address,NetworkInterface,ImportTask)

# Configure runZero variables
RUNZERO_BASE_URL = os.environ['RUNZERO_BASE_URL']
RUNZERO_BASE_URL = f'{RUNZERO_BASE_URL}/api/v1.0'
RUNZERO_CLIENT_ID = os.environ['RUNZERO_CLIENT_ID']
RUNZERO_CLIENT_SECRET = os.environ['RUNZERO_CLIENT_SECRET']
RUNZERO_ORG_ID = os.environ['RUNZERO_ORG_ID']
RUNZERO_CUSTOM_SOURCE_ID = os.environ['RUNZERO_CUSTOM_SOURCE_ID']
RUNZERO_SITE_NAME = os.environ['RUNZERO_SITE_NAME']
RUNZERO_SITE_ID = os.environ['RUNZERO_SITE_ID']
RUNZERO_IMPORT_TASK_NAME = os.environ['RUNZERO_IMPORT_TASK_NAME']

# Configure Integration API variables
KISMET_URL = os.environ['KISMET_URL']
KISMET_PORT = os.environ['KISMET_PORT']
KISMET_PHY = os.environ['KISMET_PHY']
KISMET_KEY = os.environ['KISMET_KEY']

def build_assets_from_json(json_input: List[Dict[str, Any]]) -> List[ImportAsset]:

    assets: List[ImportAsset] = []
    for item in json_input:
        #Assign API attributes from the json dict that correspond to SDK
        item = flatten(item)
        asset_id = item.get('id', str(uuid.uuid4()))
        mac = item.get('kismet.device.base.macaddr', None)
        device_type = item.get('kismet.device.base.type')
        manuf = item.get('kismet.device.base.manuf')
        name = item.get('kismet.device.base.commonname')
        first_seen = item.get('kismet.device.base.first.time')

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
                deviceType=device_type,
                manufacturer=manuf,
                hostnames=[name],
                firstSeenTS=first_seen,
                customAttributes=custom_attrs,
            )
        )
    return assets

def build_network_interface(ips: List[str], mac: str = None) -> NetworkInterface:
    ''' 
    This function converts a mac and a list of strings in either ipv4 or ipv6 format and creates a NetworkInterface that
    is accepted in the ImportAsset
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
    The code below gives an example of how to create a custom source and upload valid assets to a site using
    the new custom source.
    '''

    # create the runzero client
    c = runzero.Client()

    # try to log in using OAuth credentials
    try:
        c.oauth_login(RUNZERO_CLIENT_ID, RUNZERO_CLIENT_SECRET)
    except AuthError as e:
        print(f'login failed: {e}')
        return

    # create the site manager to get our site information; set site ID for any new hosts
    site_mgr = Sites(c)
    site = site_mgr.get(RUNZERO_ORG_ID, RUNZERO_SITE_NAME)
    if not site:
        print(f'unable to find requested site')
        return

    # create the import manager to upload custom assets
    import_mgr = CustomAssets(c)
    import_task = import_mgr.upload_assets(org_id=RUNZERO_ORG_ID, site_id=RUNZERO_SITE_ID, custom_integration_id=RUNZERO_CUSTOM_SOURCE_ID, assets=assets, task_info=ImportTask(name=RUNZERO_IMPORT_TASK_NAME))

    if import_task:
        print(f'task created! view status here: {RUNZERO_BASE_URL}/tasks?task={import_task.id}')

def get_kismet_assets(cookie=KISMET_KEY, uri=KISMET_URL, port=KISMET_PORT, phy=KISMET_PHY):
    '''
        Retrieve assets using supplied query filter from Console and restrict to fields supplied.
            
            :param cookie: A string, Kismet session cookie.
            :param KISMET_URL: A string, URL of Kismet webserver.
            :param KISMET_PORT: A string, Port of the Kismet webserver.
            :param KISMET_PHY: A string, UUID of the Kismet data source.
            :returns: A dict, Kismet asset data from given source.
            :raises: ConnectionError: if unable to successfully make GET request to Kismet webserver.
    '''
    
    url = f"{uri}:{port}/devices/views/seenby-{phy}/devices.json"
    headers = {'Cookie': f"KISMET={cookie}",
               'Content-Type': 'application/json',
               'Accept': 'application/json'}
    try:
        response = requests.get(url, headers=headers)
        return json.loads(response.content)
    except ConnectionError as error:
        print("No Response from Kismet server.", error)
        exit()

def main():
    asset_json = get_kismet_assets()

    # Format asset list for import into runZero
    import_assets = build_assets_from_json(asset_json)

    # Import assets into runZero
    import_data_to_runzero(assets=import_assets)

if __name__ == '__main__':
    main()