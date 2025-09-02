# runZero Custom Integration with Arista CloudVision platform
# Docs: https://www.runzero.com/docs/integrations-inbound/
# Docs: https://pypi.org/project/runzero-sdk/ 
# Docs: https://aristanetworks.github.io/cloudvision-apis/
# Docs: https://arista.my.site.com/AristaCommunity/s/article/cloudvision-portal-restful-api-client
# Prerequisite: pip install runzero-sdk
# Prerequisite: pip install cvprac

import os
import uuid
from cvprac.cvp_client import CvpClient
from cvprac.cvp_client_errors import CvpApiError
from ipaddress import ip_address
from typing import Any, Dict, List
import runzero
from runzero.client import AuthError
from runzero.api import CustomAssets, Sites
from runzero.types import (ImportAsset,IPv4Address,IPv6Address,NetworkInterface,ImportTask)

# Configure runZero variables
# Script uses pipenv, but os.environ[] can be swapped out for a hardcoded value to make testing easier
RUNZERO_BASE_URL = os.environ['RUNZERO_BASE_URL']
RUNZERO_CLIENT_ID = os.environ['RUNZERO_CLIENT_ID']
RUNZERO_CLIENT_SECRET = os.environ['RUNZERO_CLIENT_SECRET']
RUNZERO_ORG_ID = os.environ['RUNZERO_ORG_ID']
RUNZERO_SITE_NAME = os.environ['RUNZERO_SITE_NAME']
RUNZERO_SITE_ID = os.environ['RUNZERO_SITE_ID']
CV_CUSTOM_SOURCE_ID = os.environ['CV_CUSTOM_SOURCE_ID']
CV_IMPORT_TASK_NAME = os.environ['CV_IMPORT_TASK_NAME']


# Configure CloudVision Portal API variables
# Script uses pipenv, but os.environ[] can be swapped out for a hardcoded value to make testing easier

# Variables for CV On-Prem connection
CV_NODE_LIST = os.environ['CV_CONSOLE_URL']
CV_USERNAME = os.environ['CV_USERNAME']
CV_PASSWORD = os.environ['CV_PASSWORD']

# Variables for CVaaS connction
CV_CONSOLE_URL = os.environ['CV_CONSOLE_URL']
CV_API_KEY = os.environ['CV_API_KEY']

def build_assets_from_json(json_input: List[Dict[str, Any]]) -> List[ImportAsset]:
    '''
    Map asset attributes from API reponse and populate custom attributes and network interfaces.

    :param json_input: a dict, API JSON response of asset data.
    :returns: a list, asset data formatted for runZero import.  
    '''

    assets: List[ImportAsset] = []
    for item in json_input:
        #Assign API attributes from the json dict that correspond to SDK
        asset_id = item.get('id', str(uuid.uuid4()))
        address = item.get('ipAddress', None)
        mac = item.get('systemMacAddress', None)
        model = item.get('modelName', '')
        device_type = item.get('type', '')

        # create the network interface
        network = build_network_interface(ips=[address], mac=mac)

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
    import_task = import_mgr.upload_assets(org_id=RUNZERO_ORG_ID, site_id=RUNZERO_SITE_ID, custom_integration_id=CV_CUSTOM_SOURCE_ID, assets=assets, task_info=ImportTask(name=CV_IMPORT_TASK_NAME))

    if import_task:
        print(f'task created! view status here: {RUNZERO_BASE_URL}/api/v1.0/tasks?task={import_task.id}')

def main():
    # Create CVP client
    #client = CvpClient(syslog=True, filename='/path_to_file/cvprac_log')
    client = CvpClient()

    # Connect CVP client to On-Prem Nodes
    #client.connect(nodes=CV_NODE_LIST, username=CV_USERNAME, password=CV_PASSWORD)
    
    # Connect CVP client to CVaaS console
    client.connect(nodes=[CV_CONSOLE_URL], username='', password='', is_cvaas=True, api_token=CV_API_KEY)

    #Retrieve Inventory
    try:
        assets = client.api.get_inventory()
    except CvpApiError as err:
        raise err

    # Format asset list for import into runZero
    import_assets = build_assets_from_json(assets)

    # Import assets into runZero
    import_data_to_runzero(assets=import_assets)

if __name__ == '__main__':
    main()