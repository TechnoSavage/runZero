# runZero Custom Integration with GVM community edition (OpenVAS)
# Docs: https://www.runzero.com/docs/integrations-inbound/
# Docs: https://pypi.org/project/runzero-sdk/
# Docs: https://python-gvm.readthedocs.io/en/latest/index.html 
# Docs: https://greenbone.github.io/docs/latest/api.html
# Prerequisite: pip install runzero-sdk
# Prerequisite: pip install python-gvm

import os
import runzero
import uuid
import xmltodict
from ipaddress import ip_address
from flatten_json import flatten
from gvm.connections import UnixSocketConnection
from gvm.protocols.gmp import Gmp
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
GVM_CUSTOM_SOURCE_ID = os.environ['GVM_CUSTOM_SOURCE_ID']
GVM_IMPORT_TASK_NAME = os.environ['GVM_IMPORT_TASK_NAME']

# Configure GVM variables
GVM_BASE_URL = os.environ['GVM_BASE_URL']
GVM_PORT = os.environ['GVM_PORT']
GVM_USERNAME = os.environ['GVM_USERNAME']
GVM_PASSWORD = os.environ['GVM_PASSWORD']
GVM_SOCKET_PATH = os.environ['GVM_SOCKET_PATH']
GVM_CONN_METHOD = os.environ['GVM_CONN_METHOD']

def build_assets_from_json(json_input: List[Dict[str, Any]]) -> List[ImportAsset]:
    '''
    Map asset attributes from API reponse and populate custom attributes and network interfaces.

    :param json_input: a dict, API JSON response of asset data.
    :returns: a list, asset data formatted for runZero import.  
    '''

    assets: List[ImportAsset] = []
    for item in json_input:
        # assign known API attributes from the json dict that are always present
        # if custom fields created in GVM align to asset fields in r0 SDK docs
        # additional attributes can be added here following the pattern
        baseAttr = flatten(item)
        key_list = list(baseAttr.keys())
        val_list = list(baseAttr.values())

        asset_id = item.get('@id', uuid.uuid4)  
        ip = hostname = os_name = ''
        mac = None
        if 'ip' in val_list:
            ipPos = val_list.index('ip')
            ipKey = key_list[ipPos]
            ip = baseAttr.get(ipKey.replace('_name', '_value'))
        if 'MAC' in val_list:
            macPos = val_list.index('MAC')
            macKey = key_list[macPos]
            mac = baseAttr.get(macKey.replace('_name', '_value'))
        if 'hostname' in val_list:
            hostPos = val_list.index('hostname')
            hostKey = key_list[hostPos]
            hostname = baseAttr.get(hostKey.replace('_name', '_value')).upper()
        if 'OS' in val_list:
            osPos = val_list.index('best_os_txt')
            osKey = key_list[osPos]
            os_name = baseAttr.get(osKey.replace('_name', '_value')).replace('/', ' ')

        # create the network interfaces
        network = build_network_interface(ips=[ip], mac=mac)

        # handle any additional values and insert into custom_attrs
        custom_attrs: Dict[str] = {}
        # remap json key, value pairs generated from XML to cleaner, more useful pairs
        remap = {}
        for key, value in item.items():
            if not isinstance(value, dict):
                remap[key] = value
        item = flatten(item)
        for key, value in item.items():
            if '_name' in key and 'source_name' not in key:
                remap[value] = item.get(key.replace('_name', '_value'))
            if 'severity' in key:
                remap['severity'] = value
        for key, value in remap.items():
               custom_attrs[key] = str(value)[:1023]

        # Build assets for import
        assets.append(
            ImportAsset(
                id=asset_id,
                hostnames=[hostname],
                os=os_name,
                networkInterfaces=[network],
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
    import_task = import_mgr.upload_assets(org_id=RUNZERO_ORG_ID, site_id=RUNZERO_SITE_ID, custom_integration_id=GVM_CUSTOM_SOURCE_ID, assets=assets, task_info=ImportTask(name=GVM_IMPORT_TASK_NAME))

    if import_task:
        print(f'task created! view status here: {RUNZERO_BASE_URL}/api/v1.0/tasks?task={import_task.id}')

def socketConnect():
    path = GVM_SOCKET_PATH
    connection = UnixSocketConnection(path=path)

    with Gmp(connection=connection) as conn:
        conn.authenticate(GVM_USERNAME, GVM_PASSWORD)
        # get the response message returned as a utf-8 encoded string
        hosts = conn.get_hosts()
        vulns = conn.get_vulnerabilities()
        return(hosts, vulns)
    
def sshConnect():
    pass

def tlsConnect():
    pass

def main():
    if GVM_CONN_METHOD.lower() == 'socket':
        assetXML = socketConnect()
    elif GVM_CONN_METHOD.lower() == 'ssh':
        assetXML = sshConnect()
    elif GVM_CONN_METHOD.lower() == 'tls':
        assetXML = tlsConnect()
    else:
        print("Invalid connection method to GVM")
        exit()
    assetJSON = xmltodict.parse(assetXML)
    # Format asset list for import into runZero
    import_assets = build_assets_from_json(assetJSON['get_assets_response']['asset'])

    # Import assets into runZero
    import_data_to_runzero(assets=import_assets)

if __name__ == '__main__':
    main()