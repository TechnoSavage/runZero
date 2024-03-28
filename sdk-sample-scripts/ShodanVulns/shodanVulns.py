# runZero Custom Integration with NVD to provide Shodan reported vulnerabilities
# Docs: https://www.runzero.com/docs/integrations-inbound/
# Docs: https://pypi.org/project/runzero-sdk/ 
# Docs: https://nvd.nist.gov/developers/vulnerabilities
# Prerequisite: pip install runzero-sdk

from flatten_json import flatten
import json
import os
import requests
import runzero
from runzero.client import AuthError
from runzero.api import CustomAssets, Sites
from runzero.types import (ImportAsset, ImportTask, Vulnerability)
from typing import Any, Dict, List

# Configure runZero variables
# Script uses pipenv, but os.environ[] can be swapped out for a hardcoded value to make testing easier
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
# Script uses pipenv, but os.environ[] can be swapped out for a hardcoded value to make testing easier
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
        # grab known API attributes from the json dict that are always present
        #If custom fields created in FileWave align to asset fields in r0 SDK docs
        #additional attributes can be added here following the pattern
        asset_id = item.get('id')

        # *** Should not need to touch this ***
        # handle any additional values and insert into custom_attrs
        vulnerability: Dict[str, Vulnerability] = {}
        for vuln in item['vuln']:
            vuln = flatten(vuln)
            vulnerability['cve'] = item.get(vuln['vulnerabilities_0_cve_id'])
            vulnerability['name'] = item.get(vuln['vulnerabilities_0_cve_cisaVulnerabilityName'])
            vulnerability['description'] = item.get(vuln['vulnerabilities_0_cve_descriptions_0_value'])
            vulnerability['service_address'] = item.get(vuln['address'])
            vulnerability['service_port'] = ', '.join(item.get(vuln['ports']))
            # vulnerability['service_transport'] = item.get()
            vulnerability['cvss2_base_score'] = item.get(vuln['vulnerabilities_0_cve_metrics_cvssMetricV2_baseScore'])
            vulnerability['cvss3_base_score'] = item.get(vuln['vulnerabilities_0_cve_metrics_cvssMetricV31_baseScore'])
            # vulnerability['risk_score'] = item.get()
            # vulnerability['risk_rank'] = item.get()
            # vulnerability['severity_score'] = item.get()
            vulnerability['severity_rank'] = item.get(vuln['vulnerabilities_0_cve_metrics_baseSeverity'])
            # vulnerability['solution'] = item.get()

        # Build assets for import
        assets.append(ImportAsset(id=asset_id,
                                  vulnerabilities=vulnerability))

    return assets


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
    params = {'search': 'source:shodan and not @shodan.dev.host.hostnames:=""',
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
    Extract asset IDs and Shodan CVEs from supplied asset data. 
    
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
            asset['address'] = item.get('foreign_attributes_@shodan.dev_host.ipStr')
            asset['ports'] = item.get('foreign_attributes_@shodan.dev_host.ports').split('/t')
            asset['cves'] = item.get('foreign_attributes_@shodan.dev_host.vulns').split('/t')
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
            record['vuln'] = []
            for cve in asset['cves']:
                params = {'cveId': cve}
                headers = {'Accept': 'application/json'}
                response = requests.get(url, headers=headers, params=params)
                cve_details = json.loads(response.content)
                record['vuln'].append(cve_details)
            vulns.append(record)
    except ConnectionError as error:
        content = "No Response"
        raise error

def main():
    assets = get_assets(RUNZERO_BASE_URL, RUNZERO_EXPORT_TOKEN)
    parsed = parse_assets(assets)
    vulnData = match_nvd(NVD_API_URL, parsed)
    
    # Format asset list for import into runZero
    import_assets = build_assets_from_json(vulnData)

    # Import assets into runZero
    import_data_to_runzero(assets=import_assets)

# *** Should not need to touch this ***
if __name__ == '__main__':
    main()