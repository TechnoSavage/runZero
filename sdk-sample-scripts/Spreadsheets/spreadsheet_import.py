# runZero Custom Integration for spreadsheet imports
# Docs: https://www.runzero.com/docs/integrations-inbound/
# Docs: https://pypi.org/project/runzero-sdk/ 
# Prerequisite: pip install runzero-sdk

import argparse
import json
import os
import pandas as pd
import runzero
import uuid
from ipaddress import ip_address
from runzero.client import AuthError
from runzero.api import CustomAssets, Sites
from runzero.types import (ImportAsset,IPv4Address,IPv6Address,NetworkInterface,ImportTask)
from typing import Any, Dict, List


# Configure runZero variables
RUNZERO_BASE_URL = os.environ["RUNZERO_BASE_URL"]
RUNZERO_CLIENT_ID = os.environ['RUNZERO_CLIENT_ID']
RUNZERO_CLIENT_SECRET = os.environ['RUNZERO_CLIENT_SECRET']
SHEET_CUSTOM_SOURCE_ID = os.environ['SHEET_CUSTOM_SOURCE_ID']
SHEET_IMPORT_TASK_NAME = os.environ['SHEET_IMPORT_TASK_NAME']

def parseArgs():
    parser = argparse.ArgumentParser(description="Import a spreadsheet dataset as an integration to runZero.")
    parser.add_argument('-o', '--org', dest='RUNZERO_ORG_ID', help='UUID of the site to import spreadsheet into. This argument will take priority over the .env file', 
                        required=False, default=os.environ["RUNZERO_ORG_ID"])
    parser.add_argument('-s', '--site', dest='RUNZERO_SITE_ID', help='UUID of the site to import spreadsheet into. This argument will take priority over the .env file', 
                        required=False, default=os.environ["RUNZERO_SITE_ID"])
    parser.add_argument('-n', '--site-name', dest='RUNZERO_SITE_NAME', help='Name of the site to import spreadsheet into. This argument will take priority over the .env file', 
                        required=False, default=os.environ["RUNZERO_SITE_NAME"])
    parser.add_argument('-f', '--file', dest='filename', help='Filename of spreadsheet, including path.', required=True)
    parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    return parser.parse_args()

def build_assets_from_json(json_input: List[Dict[str, Any]]) -> List[ImportAsset]:
    '''
    This is an example function to highlight how to handle converting data from an API into the ImportAsset format that
    is required for uploading to the runZero platform. This function assumes that the json has been converted into a list 
    of dictionaries using `json.loads()` (or any similar functions).
    '''

    assets: List[ImportAsset] = []
    for item in json_input:
        # assign API attributes from the json dict (spreadsheet column headers) that merge to runZero attributes
        # example values, adjust as needed
        asset_id = str(uuid.uuid4())
        ip = item.get('IP address')
        mac = item.get('MAC address')
        name = item.get('hostname', '')

        # create the network interfaces
        if ip:
            network = build_network_interface(ips=[ip], mac=mac)

        # handle any additional values (column headers) and add as custom attributes
        custom_attrs: Dict[str] = {}
        for key, value in item.items():
            if isinstance(value, dict):
                for k, v in value.items():
                    custom_attrs[k] = str(v)[:1023]
            else:
               custom_attrs[key] = str(value)

        # Build assets for import
        if ip:
            network = build_network_interface(ips=[ip], mac=None)       
            assets.append(
                ImportAsset(
                    id=asset_id,
                    hostnames=[name],
                    networkInterfaces=[network],
                    customAttributes=custom_attrs
                )
            )
        else:
            assets.append(
                ImportAsset(
                    id=asset_id,
                    hostnames=[name],
                    customAttributes=custom_attrs
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


def import_data_to_runzero(args, assets: List[ImportAsset]):
    '''
    The code below gives an example of how to create a custom source and upload valid assets to a site using
    the new custom source.
    '''
    # create the runzero client
    client = runzero.Client()

    # try to log in using OAuth credentials
    try:
        client.oauth_login(args.RUNZERO_CLIENT_ID, args.RUNZERO_CLIENT_SECRET)
    except AuthError as error:
        print(f'login failed: {error}')
        return

    # create the site manager to get our site information; set site ID for any new hosts
    site_mgr = Sites(client)
    site = site_mgr.get(args.RUNZERO_ORG_ID, args.RUNZERO_SITE_NAME)
    if not site:
        print(f'unable to find requested site')
        return

    # create the import manager to upload custom assets
    import_mgr = CustomAssets(client)
    import_task = import_mgr.upload_assets(org_id=args.RUNZERO_ORG_ID, site_id=args.RUNZERO_SITE_ID, custom_integration_id=SHEET_CUSTOM_SOURCE_ID, assets=assets, task_info=ImportTask(name=SHEET_IMPORT_TASK_NAME))

    if import_task:
        print(f'task created! view status here: {RUNZERO_BASE_URL}/api/v1.0/tasks?task={import_task.id}')

def main():
    args = parseArgs()
    spreadsheet = pd.ExcelFile(args.filename)
    for sheet in spreadsheet.sheet_names:
            if sheet != 'Rawdata':
                df = pd.read_excel(spreadsheet, sheet)
                asset_json = df.to_json(orient='records')

            # Format asset list for import into runZero
            import_assets = build_assets_from_json(json.loads(asset_json))

            # Import assets into runZero
            import_data_to_runzero(args, assets=import_assets)

if __name__ == '__main__':
    main()