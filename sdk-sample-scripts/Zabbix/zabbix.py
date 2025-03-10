# runZero Custom Integration with Zabbix
# Docs: https://www.runzero.com/docs/integrations-inbound/
# Docs: https://pypi.org/project/runzero-sdk/
# Docs: https://www.zabbix.com/documentation/6.4/en/manual/api
# Docs: https://www.zabbix.com/documentation/6.4/en/manual
# Prerequisite: pip install runzero-sdk

import json
import os
import requests
import runzero
import uuid
from ipaddress import ip_address
from flatten_json import flatten
from typing import Any, Dict, List
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
ZABBIX_CUSTOM_SOURCE_ID = os.environ['ZABBIX_CUSTOM_SOURCE_ID']
ZABBIX_IMPORT_TASK_NAME = os.environ['ZABBIX_IMPORT_TASK_NAME']

# Configure Zabbix variables
ZABBIX_API_URL = f"{os.environ['ZABBIX_BASE_URL']}/zabbix/api_jsonrpc.php"
ZABBIX_API_KEY = os.environ['ZABBIX_API_KEY']

def build_assets_from_json(json_input: List[Dict[str, Any]]) -> List[ImportAsset]:
    '''
    Map asset attributes from API reponse and populate custom attributes and network interfaces.

    :param json_input: a dict, API JSON response of asset data.
    :returns: a list, asset data formatted for runZero import.  
    '''
    
    assets: List[ImportAsset] = []
    for item in json_input:
        # assign known API attributes from the json dict that are always present
        #If custom fields created in Zabbix align to asset fields in r0 SDK docs
        #additional attributes can be added here following the pattern
        item = flatten(item)
    
        asset_id = item.get('hostid', str(uuid.uuid4()))
        ip = item.get('interfaces_0_ip')
        mac = item.get('inventory_macaddress_a')
        os_name = item.get('inventory_os_short', '')
        model = item.get('inventory_model')
        name = item.get('host', '').upper()
        deviceType = item.get('inventory_hardware_full')
        man = item.get('inventory_vendor')

        #Correct empty mac address fields
        if mac == '':
            mac = None

        # create the network interface
        network = build_network_interface(ips=[ip], mac=mac)

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
                os=os_name,
                networkInterfaces=[network],
                hostnames=[name],
                model=model,
                deviceType=deviceType,
                manufacturer=man,
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
    import_task = import_mgr.upload_assets(org_id=RUNZERO_ORG_ID, site_id=RUNZERO_SITE_ID, custom_integration_id=ZABBIX_CUSTOM_SOURCE_ID, assets=assets, task_info=ImportTask(name=ZABBIX_IMPORT_TASK_NAME))

    if import_task:
        print(f'task created! view status here: {RUNZERO_BASE_URL}/api/v1.0/tasks?task={import_task.id}')


def get_assets(url=ZABBIX_API_URL, token=ZABBIX_API_KEY):
    '''
    Retrieve assets from Zabbix API endpoint.
    
    :param url: A string, URL of Zabbix API endpoint.
    :param token: A string, authentication token for API endpoint.
    :returns: A dict, Zabbix asset data.
    :raises: ConnectionError: if unable to successfully make GET request to Zabbix webserver.
    '''

    headers = {'Content-Type' : 'application/json-rpc',
                  'Authorization': f'Bearer {token}'}
    # Modify to return more or fewer data points as needed
    payload = json.dumps({"jsonrpc": "2.0", "method": "host.get",
                          "params": {"output": ["hostid", "host"],
                          "selectInterfaces": ["interfaceid", "ip"],
                          "selectInventory": ["os", "os_full","os_short", "type", "macaddress_a", "hardware", 
                                              "hardware_full", "hw_arch", "serialno_a", "location", "notes", 
                                              "contact", "deployment_status", "site_address_a", "site_city", 
                                              "site_country", "site_notes"]},
                          "id": 1})
    try:
        response = requests.get(url, headers=headers, data=payload)
        if response.status_code != 200:
            print(f"Unable to retrieve assets from Zabbix. Received {response.status_code}")
            exit()
        return response.json()
    except ConnectionError as error:
        print("No Response from Manage Engine server.", error)
        exit()

def main():

    hosts_json_raw = get_assets()
    hosts_json = hosts_json_raw["result"]
    # Format asset list for import into runZero
    import_assets = build_assets_from_json(hosts_json)
    # Import assets into runZero
    import_data_to_runzero(assets=import_assets)

if __name__ == '__main__':
    main()