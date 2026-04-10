# runZero Custom Integration with GVM community edition (OpenVAS)
# Docs: https://www.runzero.com/docs/integrations-inbound/
# Docs: https://pypi.org/project/runzero-sdk/
# Docs: https://python-gvm.readthedocs.io/en/latest/index.html 
# Docs: https://greenbone.github.io/docs/latest/api.html
# Prerequisite: pip install runzero-sdk
# Prerequisite: pip install python-g

import logging
import os
import runzero
import uuid
import xmltodict
from ipaddress import ip_address
from gvm.connections import (SSHConnection, TLSConnection, UnixSocketConnection)
from gvm.errors import GvmError
from gvm.protocols.gmp import Gmp
from runzero.client import AuthError
from runzero.api import CustomAssets, Sites
from runzero.types import (ImportAsset,IPv4Address,IPv6Address,NetworkInterface,ImportTask,Vulnerability)

logger = logging.getLogger(__name__)

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

host_os_mapping = {'Linux Kernel': 'Linux'}

def build_assets_from_json(hosts, vulns):
    '''
    Map asset attributes from API reponse and populate custom attributes and network interfaces.

    :param json_input: a dict, API JSON response of asset data.
    :returns: a list, asset data formatted for runZero import.  
    '''

    assets = []
    for host in hosts:
        # assign known API attributes from the json dict that are always present
        # if custom fields created in GVM align to asset fields in r0 SDK docs
        # additional attributes can be added here following the pattern
        
        identifiers = host.get('identifiers', {}).get('identifier', [])
        detail = host.get('host', {}).get('detail', [])
        host_id = str(host.get('@id', uuid.uuid4()))
        ip = host.get('name', '')
        mac = None
        os = ''
        hostnames = []
        cpe = ''
        best_os_txt = ''
        traceroute = ''
        severity = host.get('host', {}).get('severity', {}).get('value', '')
        ssh_keys = []
        # Parse all of the fun XML turned JSON
        if identifiers and type(identifiers) == list:
            for item in identifiers:
                if item['name'] == 'hostname':
                    hostnames.append(item['value'])
                if item['name'] == 'ssh-key':
                    ssh_keys.append(item['value'])
        if type(detail) == list:
            for item in detail:
                if item['name'] == 'best_os_cpe':
                    cpe = item['value']
                if item['name'] == 'best_os_txt':
                    best_os_txt = os = item['value']
                if item['name'] == 'traceroute':
                    traceroute = item['value'] 
        
        if ssh_keys:
            ssh_keys = ssh_keys[0]
        else:
            ssh_keys = ''

        # create the network interfaces
        network = build_network_interface(ips=[ip], mac=mac)

        # map custom attributes

        custom_attrs = {
                        'bestOsTxt': best_os_txt,
                        'os.cpe23': cpe,
                        'traceroute': traceroute,
                        'severity': severity,
                        'sshKey': ssh_keys
                        }

        vuln_list = []
        for vuln in vulns:
            if vuln['host']['asset']['@asset_id'] and vuln['host']['asset']['@asset_id'] == host_id:
                vuln_list.append(build_vuln(vuln))
            elif not vuln['host']['asset']['@asset_id'] and vuln['host']['#text'] and vuln['host']['#text'] == ip:
                vuln_list.append(build_vuln(vuln))
            else:
                pass

        # Build assets for import
        assets.append(
            ImportAsset(
                id=host_id,
                hostnames=hostnames,
                os=os,
                networkInterfaces=[network],
                customAttributes=custom_attrs,
                vulnerabilities=vuln_list
            )
        )
    return assets

def build_network_interface(ips, mac=None):
    ''' 
    This function converts a mac and a list of strings in either ipv4 or ipv6 format and creates a NetworkInterface that
    is accepted in the ImportAsset

    :param ips: A list, a list of IP addresses
    :param mac: A string, a MAC address formatted as follows 00:11:22:AA:BB:CC
    :returns: A list, a list of runZero network interface classes
    '''

    ip4s = []
    ip6s = []
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
    
def build_vuln(vuln):
    '''
    This function maps vulnerability information to runZero attribute fields and assigns all key, value pairs to
    vulnerability custom attributes
    '''

    ref = vuln.get('nvt', {}).get('refs', {}).get('ref', [])
    identifier = cve_id = ''
    if ref and type(ref) == list:
        for item in ref:
            if item['@type'] == 'cve': 
                identifier = cve_id = item['@id']
    if ref and type(ref) == dict:
        if ref['@type'] == 'cve':
            identifier = cve_id = item['@id']
    name = vuln.get('name')
    if identifier == '' or identifier == None:
        identifier = name
    description = vuln.get('description')
    if description:
        description = description[:1023]
    service_address = vuln.get('host', {}).get('#text', '')
    if service_address:
        service_address = IPv4Address(ip_address(service_address))
    service = vuln.get('port').split('/')
    try:
        service_port = int(service[0])
    except:
        service_port = 0
    service_transport = service[1]
    first_detected_timestamp = vuln.get('creation_time', '')
    #exploitability = detail.get('')
    #if not exploitability:
        #exploitability = detail.get('')
    #exploitable = True if float(exploitability) >= 5.0 else False
    cvss2_base_score = vuln.get('nvt', {}).get('cvss_base', '')
    if cvss2_base_score:
        cvss2_base_score = float(cvss2_base_score)
    #cvss3_base_score = detail.get('')
    #if cvss3_base_score:
        #cvss3_base_score = float(cvss3_base_score)
    # risk_score = detail.get()
    # risk_rank = detail.get()
    severity_score = vuln.get('severity', '')
    if severity_score:
        severity_score = float(severity_score)
        if severity_score >= 0.1 and severity_score <=3.9:
            risk_rank = 1
        elif severity_score >= 4.0 and severity_score <=6.9:
            risk_rank = 2
        elif severity_score >= 7.0 and severity_score <= 8.9:
            risk_rank = 3
        elif severity_score >= 9.0 and severity_score <= 10.0:
            risk_rank = 4
        else:
            risk_rank = 0
        
    solution = vuln.get('solution', {}).get('@type', '') + ': ' + vuln.get('solution', {}).get('#text', '')
    solution = solution[:1023]

    custom_attrs = {}
    custom_attrs['vulnerabilityFamily'] = vuln.get('nvt', {}).get('family', '')
    custom_attrs['threat'] = vuln.get('threat', '')
    # custom_attrs refs URLs
    if cve_id:
        return Vulnerability(id=identifier,
                            cve=cve_id,
                            name=name,
                            description=description,
                            firstDetectedTS=first_detected_timestamp,
                            serviceAddress=service_address,
                            servicePort=service_port,
                            serviceTransport=service_transport,
                            #exploitable=exploitable,
                            cvss2BaseScore=cvss2_base_score,
                            #cvss3BaseScore=cvss3_base_score,
                            riskRank=risk_rank,
                            severityScore=severity_score,
                            # severityRank=severity_rank,
                            solution=solution,
                            customAttributes=custom_attrs
                            )
    else:
        return Vulnerability(id=identifier,
                            name=name,
                            description=description,
                            firstDetectedTS=first_detected_timestamp,
                            serviceAddress=service_address,
                            servicePort=service_port,
                            serviceTransport=service_transport,
                            #exploitable=exploitable,
                            cvss2BaseScore=cvss2_base_score,
                            #cvss3BaseScore=cvss3_base_score,
                            riskRank=risk_rank,
                            # severityScore=severity_score,
                            # severityRank=severity_rank,
                            solution=solution,
                            customAttributes=custom_attrs
                            )

def import_data_to_runzero(assets):
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
        hosts = xmltodict.parse(conn.get_hosts(details=True))
        hosts = hosts.get('get_assets_response', {}).get('asset', [])
        if not hosts:
            # add logging message here for zero hosts
            exit()
        vulns = []
        tasks = xmltodict.parse(conn.get_tasks(ignore_pagination=True))
        tasks = tasks.get('get_tasks_response', {}).get('task', {})
        if tasks and type(tasks) == dict:
            latest_reports = tasks.get('last_report', {}).get('report', {}).get('@id', '')
        if tasks and type(tasks) == list:    
            latest_reports = [task.get('last_report', {}).get('report', {}).get('@id', '') for task in tasks]
        if latest_reports:
            for id in latest_reports:
                report = xmltodict.parse(conn.get_report(report_id=id, ignore_pagination=True, details=True))
                vulnerabilities = report.get('get_reports_response', {}).get('report', {}).get('report', {}).get('results', {}).get('result', [])
                vulns.extend(vulnerabilities)
        return(hosts, vulns)
    
def sshConnect():
    pass

def tlsConnect():
    pass

def main():
    logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%a, %d %b %Y %H:%M:%S', filename=f'syncGVM.log', level=logging.INFO)
    if GVM_CONN_METHOD.lower() == 'socket':
        response = socketConnect()
    elif GVM_CONN_METHOD.lower() == 'ssh':
        assetXML = sshConnect()
    elif GVM_CONN_METHOD.lower() == 'tls':
        assetXML = tlsConnect()
    else:
        print("Invalid connection method to GVM")
        exit()

    asset_json = response[0]
    vuln_json = response[1]

    # Format asset list for import into runZero
    import_assets = build_assets_from_json(asset_json, vuln_json)

    # Import assets into runZero
    import_data_to_runzero(assets=import_assets)

if __name__ == '__main__':
    main()