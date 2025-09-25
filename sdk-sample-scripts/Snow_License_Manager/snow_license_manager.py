# runZero Custom Integration with Snow Software License Manager
# Docs: https://www.runzero.com/docs/integrations-inbound/
# Docs: https://pypi.org/project/runzero-sdk/
# Docs:
# Docs:
# Prerequisite: pip install runzero-sdk

import json
import os
import requests
import runzero
import uuid
from ipaddress import ip_address
from typing import Any, Dict, List
from runzero.client import AuthError
from runzero.api import CustomAssets, Sites
from runzero.types import (ImportAsset,IPv4Address,IPv6Address,NetworkInterface,ImportTask,Software)

# Configure runZero variables
RUNZERO_BASE_URL = os.environ['RUNZERO_BASE_URL']
RUNZERO_CLIENT_ID = os.environ['RUNZERO_CLIENT_ID']
RUNZERO_CLIENT_SECRET = os.environ['RUNZERO_CLIENT_SECRET']
RUNZERO_ORG_ID = os.environ['RUNZERO_ORG_ID']
RUNZERO_SITE_NAME = os.environ['RUNZERO_SITE_NAME']
RUNZERO_SITE_ID = os.environ['RUNZERO_SITE_ID']
SNOW_CUSTOM_SOURCE_ID = os.environ['SNOW_CUSTOM_SOURCE_ID']
SNOW_IMPORT_TASK_NAME = os.environ['SNOW_IMPORT_TASK_NAME']

# Configure Snow Software License Manager variables
SNOW_BASE_URL = os.environ['SNOW_BASE_URL']
SNOW_USERNAME = os.environ['SNOW_USERNAME']
SNOW_PASSWORD = os.environ['SNOW_PASSWORD']
SNOW_CUSTOMER_ID = os.environ['SNOW_CUSTOMER_ID']

def build_assets_from_json(json_input: List[Dict[str, Any]]) -> List[ImportAsset]:
    '''
    Map asset attributes from API reponse and populate custom attributes and network interfaces.

    :param json_input: a dict, API JSON response of asset data.
    :returns: a list, asset data formatted for runZero import.  
    '''

    assets: List[ImportAsset] = []
    for entry in json_input:
        item = entry.get('Body', {})
        asset_id = str(item.get('Id', uuid.uuid4))
        hostname = item.get('Name', '')
        vendor = item.get('Manufacturer', '')
        hw = item.get('Model', '')
        os = item.get('OperatingSystem', '')
        os_version = item.get('OperatingSystemServicePack', '')

        # create the network interfaces
        interfaces = []
        adapters = item.get('Hardware', {}).get('NetworkAdapters', [])
        for adapter in adapters:
            addresses = adapter.get('IpAddress', '').split(';')
            if type(addresses) != list:
                addresses = [addresses]
            interface = build_network_interface(ips=addresses, mac=adapter.get('MacAddress', None))
            interfaces.append(interface)

        # handle any additional values and insert into custom_attrs
        custom_attrs: Dict[str] = {}
        for key, value in item.items():
            if isinstance(value, dict):
                for k, v in value.items():
                    custom_attrs[k] = str(v)[:1023]
            else:
                custom_attrs[key] = str(value)[:1023]

        # Retrieve software information for asset
        # create software entries
        software = []
        applications = get_apps(asset_id)
        for app in applications:
            software_entry = build_app(app)
            software.append(software_entry)

        # Build assets for import
        assets.append(
            ImportAsset(
                id=asset_id,
                hostnames=[hostname],
                manufacturer=vendor,
                model=hw,
                os=os,
                os_version=os_version,
                networkInterfaces=interfaces,
                customAttributes=custom_attrs,
                software=software
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
    
def build_app(software_entry):
    '''

    '''
    app = software_entry.get('Body', {})
    app_id = app.get('Id', None)
    # if app_id:
    #     software_details = get_app_details(app_id)
    #installed = app.get('InstallDate', '')
    product = app.get('FamilyName', '')
    vendor = app.get('ManufacturerName', '')

    custom_attrs: Dict[str] = {}
    for key, value in software_entry.items():
        if isinstance(value, dict):
            for k, v in value.items():
                custom_attrs[k] = str(v)[:1023]
        else:
            custom_attrs[key] = str(value)[:1023]
    # if app_id:        
    #     for key, value in software_details.items():
    #         if isinstance(value, dict):
    #             for k, v in value.items():
    #                 custom_attrs[k] = str(v)[:1023]
    #         else:
    #             custom_attrs[key] = str(value)[:1023]

    return Software(
        id=app_id,
        product=product,
        vendor=vendor,
        customAttributes=custom_attrs
        )   


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
    import_task = import_mgr.upload_assets(org_id=RUNZERO_ORG_ID, site_id=RUNZERO_SITE_ID, custom_integration_id=SNOW_CUSTOM_SOURCE_ID, assets=assets, task_info=ImportTask(name=SNOW_IMPORT_TASK_NAME))

    if import_task:
        print(f'task created! view status here: {RUNZERO_BASE_URL}/api/v1.0/tasks?task={import_task.id}')

def get_computers(url=SNOW_BASE_URL, username=SNOW_USERNAME, password=SNOW_PASSWORD, id=SNOW_CUSTOMER_ID):
    '''
    Return a list of computers from the Snow Software License Manager API

    :param url: a string, the base URL of the Snow Software License Manager console.
    :param username: a string, username for Snow Software License Manager console basic auth.
    :param password: a string, password for Snow Software License Manager console basic auth.
    :param id: a string, numerical customer id to return computers from (found under https://<console ip>/api/customers ID column).
    :returns: a list, a list of dictionaries for each computer.
    :raises: ConnectionError: if unable to successfully make GET request to console.
    '''
    items_returned = 0
    total_items = 10000
    assets_all = []

    while True:
        try:
            url = f'{url}/api/customers/{id}/computers?'
            headers = {'Accept': 'application/json'}
            params = {'$inlinecount': 'allpages',
                      '$skip': str(items_returned)}
            response = requests.get(url, auth=requests.auth.HTTPBasicAuth(username, password), headers=headers, params=params)
            if response.status_code != 200:
                print(f'failed to retrieve assets at $skip={str(items_returned)}', f'status code: {response.status_code}')
                exit()
            else:
                data = json.loads(response.content)
                meta = data['Meta']
                has_page_size = False
                for item in meta:
                    if item['Name'] == 'Count':
                        total_items = item.get('Value')
                    if item['Name'] == 'PageSize':
                        has_page_size = True
                        items_returned += item.get('Value')
                computers = data['Body']
                assets_all.extend(computers)
                if not has_page_size: # The last page lacks the page size meta value
                    break
                print(f'{items_returned} computers of {total_items} returned from API')            
        except ConnectionError as error:
            print("No Response from server.", error)
            exit()

    return assets_all

def get_apps(asset_id, url=SNOW_BASE_URL, username=SNOW_USERNAME, password=SNOW_PASSWORD, id=SNOW_CUSTOMER_ID):
    '''
    Return a list of installed software for a given computer ID.

    :param asset_id: a string, the computer ID in Snow Software License Manager for which to retrieve applications.
    :param url: a string, the base URL of the Snow Software License Manager console.
    :param username: a string, username for Snow Software License Manager console basic auth.
    :param password: a string, password for Snow Software License Manager console basic auth.
    :param id: a string, numerical customer id to return computers from (found under https://<console ip>/api/customers ID column).
    :returns: a list, a list of dictionaries for each application for the specified computer ID.
    :raises: ConnectionError: if unable to successfully make GET request to console.
    '''
    items_returned = 0
    total_items = 10000
    applications_all = []

    while True:
        try:
            url = f'{url}/api/customers/{id}/computers/{asset_id}/applications?'
            headers = {'Accept': 'application/json'}
            params = {'$inlinecount': 'allpages',
                      '$skip': str(items_returned)}
            response = requests.get(url, auth=requests.auth.HTTPBasicAuth(username, password), headers=headers, params=params)
            if response.status_code != 200:
                print(f'failed to retrieve application for {asset_id} at $skip={str(items_returned)}', f'status code: {response.status_code}')
                exit()
            else:
                data = json.loads(response.content)
                meta = data['Meta']
                has_page_size = False
                for item in meta:
                    if item['Name'] == 'Count':
                        total_items = item.get('Value')
                    if item['Name'] == 'PageSize':
                        has_page_size = True
                        items_returned += item.get('Value')
                applications = data['Body']
                applications_all.extend(applications)
                if not has_page_size: # The last page lacks the page size meta value
                    break
                print(f'{items_returned} applications of {total_items} returned from API')            
        except ConnectionError as error:
            print("No Response from server.", error)
            exit()

    return applications_all

def get_app_details(app_id, url=SNOW_BASE_URL, username=SNOW_USERNAME, password=SNOW_PASSWORD, id=SNOW_CUSTOMER_ID):
    '''
    Return a application details for a given application ID.

    :param app_id: a string, the computer ID in Snow Software License Manager for which to retrieve applications.
    :param url: a string, the base URL of the Snow Software License Manager console.
    :param username: a string, username for Snow Software License Manager console basic auth.
    :param password: a string, password for Snow Software License Manager console basic auth.
    :param id: a string, numerical customer id to return computers from (found under https://<console ip>/api/customers ID column).
    :returns: a dict, application details.
    :raises: ConnectionError: if unable to successfully make GET request to console.
    '''

    try:
        url = f'{url}/api/customers/{id}/applications/{app_id}'
        headers = {'Accept': 'application/json'}
        response = requests.get(url, auth=requests.auth.HTTPBasicAuth(username, password), headers=headers)
        if response.status_code != 200:
            print(f'failed to retrieve application details for {app_id}', f'status code: {response.status_code}')
            exit()
        else:
            data = json.loads(response.content)
            details = data['Body']
    except ConnectionError as error:
        print("No Response from server.", error)
        exit()

    return details

def main():
    assets = get_computers()
    
    # Format asset list for import into runZero
    import_assets = build_assets_from_json(assets)

    # Import assets into runZero
    import_data_to_runzero(assets=import_assets)

if __name__ == '__main__':
    main()