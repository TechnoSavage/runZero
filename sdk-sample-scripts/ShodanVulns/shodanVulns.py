# runZero Custom Integration with NVD to provide Shodan reported vulnerabilities
# Docs: https://www.runzero.com/docs/integrations-inbound/
# Docs: https://pypi.org/project/runzero-sdk/ 
# Docs: https://nvd.nist.gov/developers/vulnerabilities
# Prerequisite: pip install runzero-sdk


import json
import os
import requests
import runzero
import uuid
from flatten_json import flatten
from ipaddress import ip_address
from runzero.client import AuthError
from runzero.api import CustomAssets, Sites
from runzero.types import (ImportAsset,ImportTask,IPv4Address,IPv6Address,NetworkInterface,Vulnerability)
from typing import Any, Dict, List

# Configure runZero variables
RUNZERO_BASE_URL = os.environ['RUNZERO_BASE_URL']
RUNZERO_BASE_URL = f'{RUNZERO_BASE_URL}/api/v1.0'
RUNZERO_EXPORT_TOKEN = os.environ['RUNZERO_EXPORT_TOKEN']
RUNZERO_CLIENT_ID = os.environ['RUNZERO_CLIENT_ID']
RUNZERO_CLIENT_SECRET = os.environ['RUNZERO_CLIENT_SECRET']
RUNZERO_ORG_ID = os.environ['RUNZERO_ORG_ID']
RUNZERO_CUSTOM_SOURCE_ID = os.environ['RUNZERO_CUSTOM_SOURCE_ID']
RUNZERO_SITE_NAME = os.environ['RUNZERO_SITE_NAME']
RUNZERO_SITE_ID = os.environ['RUNZERO_SITE_ID']
RUNZERO_IMPORT_TASK_NAME = os.environ['RUNZERO_IMPORT_TASK_NAME']

# Configure NVD variables
NVD_API_URL = 'https://services.nvd.nist.gov/rest/json/cves/2.0?'
NVD_HEADERS = {'Accept': 'application/json',
               'Content-Type': 'application/json'}

def build_assets_from_json(json_input: List[Dict[str, Any]]) -> List[ImportAsset]:
    '''
    This is an example function to highlight how to handle converting data from an API into the ImportAsset format that
    is required for uploading to the runZero platform. This function assumes that the json has been converted into a list 
    of dictionaries using `json.loads()` (or any similar functions).
    '''

    assets: List[ImportAsset] = []
    for item in json_input:
        # Map vulnerabilities to asset using existing asset UID
        asset_id = item.get('id', uuid.uuid4().urn)
        mac = None
        ip = item.get('address')

        # create the network interface
        network = build_network_interface(ips=[ip], mac=mac)

        # create the vulnerabilities
        vulnerabilities = []
        for detail in item['cve_details']:
            vulnerability = build_vuln(address=item.get('address'), ports=item.get('ports'), detail=detail)
            vulnerabilities.append(vulnerability)

        # Build assets for import
        assets.append(ImportAsset(id=asset_id,
                                  networkInterfaces=[network],
                                  vulnerabilities=vulnerabilities))

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

def build_vuln(address, ports, detail):
    '''
    This function maps vulnerability information to runZero attribute fields and assigns all key, value pairs to
    vulnerability custom attributes
    '''
    ranking = {'NONE': 0,
               'LOW': 1,
               'MEDIUM': 2,
               'HIGH': 3,
               'CRITICAL': 4}

    detail = flatten(detail)
    identifier = detail.get('vulnerabilities_0_cve_id')
    cve_id = detail.get('vulnerabilities_0_cve_id')
    vuln_name = detail.get('vulnerabilities_0_cve_cisaVulnerabilityName')
    if vuln_name == '' or vuln_name == None:
        vuln_name = identifier
    vuln_description = detail.get('vulnerabilities_0_cve_descriptions_0_value')[:1023]
    service_address = IPv4Address(ip_address(address))
    #develop better logic for assigning port to CVE
    # likely a different function to parse CVE details and assign likely port from provided list
    service_port = ports[0]
    #exploit = detail.get()
    #service_transport = detail.get()[:255]
    cvss2_base_score = detail.get('vulnerabilities_0_cve_metrics_cvssMetricV2_0_cvssData_baseScore')
    if cvss2_base_score and cvss2_base_score != '':
        cvss2_base_score = float(cvss2_base_score)
    cvss3_base_score = detail.get('vulnerabilities_0_cve_metrics_cvssMetricV31_0_cvssData_baseScore')
    if cvss3_base_score and cvss3_base_score != '':
        cvss3_base_score = float(cvss3_base_score)
    # risk_score = detail.get()
    # risk_rank = detail.get()
    # severity_score = detail.get()
    severity_rank = detail.get('vulnerabilities_0_cve_metrics_cvssMetricV31_0_cvssData_baseSeverity')
    if severity_rank and severity_rank == '':
        severity_rank = detail.get('vulnerabilities_0_cve_metrics_cvssMetricV2_0_cvssData_baseSeverity')
    severity_rank = ranking[severity_rank]
    solution = detail.get('vulnerabilities_0_cve_cisaRequiredAction', '')[:1023]
    custom_attrs: Dict[str] = {}
    for key, value in detail.items():
        custom_attrs[key] = str(value)[:1023]

    return Vulnerability(id=identifier,
                         #cve=cve_id,   #runZero-sdk regex check is too restrictive for updated CVE ID formats (as few a 4 final digits to 7 or more)
                         name=vuln_name,
                         description=vuln_description,
                         serviceAddress=service_address,
                         servicePort=service_port,
                         #exploitable=exploit,
                         cvss2BaseScore=cvss2_base_score,
                         cvss3BaseScore=cvss3_base_score,
                         severityRank=severity_rank,
                         solution=solution,
                         customAttributes=custom_attrs
                         )

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

def get_assets(url, token):
    '''
    Retrieve assets containing Shodan reported CVEs from console.
        
        :param url: A string, URL of runZero console.
        :param token: A string, Export API Key.
        :returns: a dict, JSON object of assets.
        :raises: ConnectionError: if unable to successfully make GET request to console.
    '''

    url = f"{url}/api/v1.0/export/org/assets.json"
    params = {'search': 'source:shodan and not @shodan.dev.host.vulns:=""',
              'fields': 'id, foreign_attributes'}
    payload = ''
    headers = {'Accept': 'application/json',
               'Authorization': f'Bearer {token}'}
    try:
        response = requests.get(url, headers=headers, params=params, data=payload)
        content = response.content
        data = json.loads(content)
        return data
    except ConnectionError as error:
        content = "No Response"
        raise error
    
def parse_assets(data):
    '''
    Extract asset ID and Shodan reported IP, Ports, and CVEs from supplied asset data. 
    
            :param data: JSON object, runZero asset data.
            :returns: A Dict, asset IDs and CVE numbers.
            :raises: TypeError: if data variable passed is not JSON format.
    '''

    assets = []
    try:
        asset = {}
        for item in data:
            item = flatten(item)
            asset['id'] = item.get('id')
            asset['address'] = item.get('foreign_attributes_@shodan.dev_0_host.ipStr', '')
            asset['ports'] = item.get('foreign_attributes_@shodan.dev_0_host.ports', '').split('\t')
            asset['cves'] = item.get('foreign_attributes_@shodan.dev_0_host.vulns', '').split('\t')
            assets.append(asset)        
        return assets
    except TypeError as error:
        raise error
    
def match_nvd(url, data):
    '''
    Retrieve CVE details from NVD.
        
        :param url: A string, API URL of NVD.
        :param data: A Dict, containing the CVEs to retrieve details for
        :returns: a dict, JSON object of assets.
        :raises: ConnectionError: if unable to successfully make GET request to NVD API.
    '''
    vulns = []
    try:
        for asset in data:
            record = {}
            record['id'] = asset['id']
            record['address'] = asset['address']
            record['ports'] = asset['ports']
            record['cve_details'] = []
            for cve in asset['cves']:
                params = {'cveId': cve.upper()}
                headers = {'Accept': 'application/json'}
                response = requests.get(url, headers=headers, params=params)
                cve_details = json.loads(response.content)
                record['cve_details'].append(cve_details)
            vulns.append(record)
        return vulns
    except ConnectionError as error:
        content = "No Response"
        raise error

def main():
    assets = get_assets(RUNZERO_BASE_URL, RUNZERO_EXPORT_TOKEN)
    parsed = parse_assets(assets)
    vuln_data = match_nvd(NVD_API_URL, parsed)
    
    # Format asset list for import into runZero
    import_assets = build_assets_from_json(vuln_data)

    # Import assets into runZero
    import_data_to_runzero(assets=import_assets)

if __name__ == '__main__':
    main()