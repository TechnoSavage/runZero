# runZero Custom Integration with XYZ platform
# Docs: https://www.runzero.com/docs/integrations-inbound/
# Docs: https://pypi.org/project/runzero-sdk/ 
# Docs: 
# Docs: 
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
INTEGRATION_CUSTOM_SOURCE_ID = os.environ['INTEGRATION_CUSTOM_SOURCE_ID']
INTEGRATION_IMPORT_TASK_NAME = os.environ['INTEGRATION_IMPORT_TASK_NAME']


# Configure Integration API variables (examples provided)
# Script uses pipenv, but os.environ[] can be swapped out for a hardcoded value to make testing easier
API_URL = f"{os.environ['API_BASE_URL']}/api/v1/foobar"
API_KEY = os.environ['API_KEY']

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

        # create software entries
        warez = []
        for app in item['app_list']:
            application = build_app(app_details=app)
            warez.append(application)

        # create the vulnerabilities
        vulnerabilities = []
        for vuln in item['vuln_list']:
            vulnerability = build_vuln(vuln_details=vuln)
            vulnerabilities.append(vulnerability)

        # Build assets for import
        assets.append(
            ImportAsset(
                id=asset_id,
                networkInterfaces=[network],
                model=model,
                deviceType=device_type,
                manufacturer=manuf,
                customAttributes=custom_attrs,
                software=warez,
                vulnerabilities=vulnerabilities
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
    
def build_app(app_details):
    '''
    '''
    return Software()
    
def build_vuln(vuln_details):
    '''
    '''
    ranking = {'NONE': 0,
               'LOW': 1,
               'MEDIUM': 2,
               'HIGH': 3,
               'CRITICAL': 4}

    vuln_detail = flatten(vuln_detail)
    identifier = vuln_detail.get('id')
    cve_id = vuln_detail.get('cve_id')
    vuln_name = vuln_detail.get('vulnerability_name')
    if vuln_name and vuln_name != '':
        vuln_name = identifier
    vuln_description = vuln_detail.get('vulnerabilities_0_cve_descriptions_0_value')[:1023]
    service_address = IPv4Address(ip_address('address'))
    service_port = vuln_detail('ports')
    exploitability = vuln_detail.get('cvssMetricV31_exploitabilityScore')
    if not exploitability:
        exploitability = vuln_detail.get('cvssMetricV2_exploitabilityScore')
    exploitable = True if float(exploitability) >= 5.0 else False
    service_transport = vuln_detail.get()
    cvss2_base_score = vuln_detail.get('cvssV2_baseScore')
    if cvss2_base_score and cvss2_base_score != '':
        cvss2_base_score = float(cvss2_base_score)
    cvss3_base_score = vuln_detail.get('cvssV31_baseScore')
    if cvss3_base_score and cvss3_base_score != '':
        cvss3_base_score = float(cvss3_base_score)
    risk_score = vuln_detail.get()
    risk_rank = vuln_detail.get()
    severity_score = vuln_detail.get()
    severity_rank = vuln_detail.get('cvssV31_baseSeverity')
    if severity_rank and severity_rank == '':
        severity_rank = vuln_detail.get('cvssV2_baseSeverity')
    severity_rank = ranking[severity_rank]
    solution = vuln_detail.get('solution')[:1023]
    custom_attrs: Dict[str] = {}
    for key, value in vuln_detail.items():
        custom_attrs[key] = str(value)[:1023]
        
    return Vulnerability(id=identifier,
                         cve=cve_id,
                         name=vuln_name,
                         description=vuln_description,
                         serviceAddress=service_address,
                         servicePort=service_port,
                         serviceTransport=service_transport,
                         exploitable=exploitable,
                         cvss2BaseScore=cvss2_base_score,
                         cvss3BaseScore=cvss3_base_score,
                         riskScore=risk_score,
                         riskRank=risk_rank,
                         severityScore=severity_score,
                         severityRank=severity_rank,
                         solution=solution,
                         customAttributes=custom_attrs)

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
    import_task = import_mgr.upload_assets(org_id=RUNZERO_ORG_ID, site_id=RUNZERO_SITE_ID, custom_integration_id=INTEGRATION_CUSTOM_SOURCE_ID, assets=assets, task_info=ImportTask(name=INTEGRATION_IMPORT_TASK_NAME))

    if import_task:
        print(f'task created! view status here: {RUNZERO_BASE_URL}/api/v1.0/tasks?task={import_task.id}')

def get_assets(url=API_URL, token=API_KEY):
    '''
    Retrieve assets from API endpoint.
    
    :param url: A string, URL of API endpoint.
    :param token: A string, authentication token for API endpoint.
    :returns: A dict, asset data.
    :raises: ConnectionError: if unable to successfully make GET request to webserver.
    '''

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