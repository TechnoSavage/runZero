CONFIG = {
    "id": "catalyst_center",
    "name": "Cisco Catalyst Center",
    "type": "inbound",
    "description": "Imports devices from Cisco Catalyst Center",
    "version": "1",
    "minVersion": "0",
    "params": [
        {"key": "url", "label": "Catalyst Center URL", "type": "url", "required": True},
        {"key": "username", "label": "username", "type": "secret", "required": True},
        {"key": "password", "label": "password", "type": "secret", "required": True}
    ],
    "includes": {
        "tls_": OPTIONS_TLS,
        "http_": OPTIONS_HTTP,
    },
}

load('runzero.types', 'ImportAsset', 'NetworkInterface')
load('kwargs', 'get_url_base', 'get_http_options')
load('base64', base64_encode='encode', base64_decode='decode')
load('http', http_get='get', http_post='post', 'url_encode')
load('json', json_encode='encode', json_decode='decode')
load('net', 'ip_address')
load('time', 'parse_time')
load('uuid', 'new_uuid')

def build_assets(assets):
    assets_import = []
    for device in assets:
        asset_id = str(device.get('id', new_uuid))
        mgmt_address = device.get('managementIpAddress', '')
        mac = device.get('macAddress', None)
        hostname = device.get('hostname', '')
        model = device.get('series', '')
        os = device.get('softwareType', '')
        os_version = device.get('softwareVersion', '')
        device_type = device.get('type', '')
        apManagerInterfaceIp = device.get('apManagerInterfaceIp', '')
        associatedWlcIp = device.get('associatedWlcIp', '')
        dnsResolvedManagementAddress = device.get('dnsResolvedManagementAddress', '')
        addresses = [mgmt_address, apManagerInterfaceIp, associatedWlcIp, dnsResolvedManagementAddress]

        # create the network interfaces
        interface = build_network_interface(ips=addresses, mac=mac)

        # Retrieve and map custom attributes

        custom_attributes = {
            'apEthernetMacAddress': device.get('apEthernetMacAddress', ''),
            'apManagerInterfaceIp': apManagerInterfaceIp,
            'associatedWlcIp': associatedWlcIp,
            'bootDateTime': device.get('bootDateTime', ''),
            'collectionInterval': device.get('collectionInterval', ''),
            'collectionStatus': device.get('collectionStatus', ''),
            'description': device.get('description', ''),
            'deviceSupportLevel': device.get('deviceSupportLevel', ''),
            'dnsResolvedManagementAddress': dnsResolvedManagementAddress,
            'errorCode': device.get('errorCode', ''),
            'errorDescription': device.get('errorDescription', ''),
            'family': device.get('family', ''),
            'instanceTenantId': device.get('instanceTenantId', ''),
            'instanceUuid': device.get('instanceUuid', ''),
            'interfaceCount': device.get('interfaceCount', ''),
            'inventoryStatusDetail': device.get('inventoryStatusDetail', ''),
            'lastDeviceResyncStartTime': device.get('lastDeviceResyncStartTime', ''),
            'lastManagedResyncReasons': device.get('lastManagedResyncReasons', ''),
            'lastUpdated': device.get('lastUpdated', ''),
            'lastUpdateTime': device.get('lastUpdateTime', ''), #epoch timestamp
            'lineCardCount': device.get('lineCardCount', ''),
            'lineCardId': device.get('lineCardId', ''),
            'managedAtleastOnce': str(device.get('managedAtleastOnce', '')),
            'managementIpAddress': mgmt_address,
            'managementState': device.get('managementState', ''),
            'memorySize': device.get('memorySize', ''),
            'pendingSyncRequestsCount': device.get('pendingSyncRequestsCount', ''),
            'platformId': device.get('platformId', ''),
            'reachabilityFailureReason': device.get('reachabilityFailureReason', ''),
            'reachabilityStatus': device.get('reachabilityStatus', ''),
            'reasonsForDeviceResync': device.get('reasonsForDeviceResync', ''),
            'reasonsForPendingSyncRequests': device.get('reasonsForPendingSyncRequests', ''),
            'role': device.get('role', ''),
            'roleSource': device.get('roleSource', ''),
            'serialNumber': device.get('serialNumber', ''),
            'snmpContact': device.get('snmpContact', ''),
            'snmpLocation': device.get('snmpLocation', ''),
            'syncRequestedByApp': device.get('syncRequestedByApp', ''),
            'tagCount': device.get('tagCount', ''),
            'tunnelUdpPort': device.get('tunnelUdpPort', ''),
            'upTime': device.get('upTime', ''),
            'uptimeSeconds': str(device.get('uptimeSeconds', '')),
            'waasDeviceMode': device.get('waasDeviceMode', '')
        }

        # Build assets for import
        assets_import.append(
            ImportAsset(
                id=asset_id,
                hostnames=[hostname],
                model=model,
                device_type=device_type,
                os=os,
                os_version=os_version,
                networkInterfaces=[interface],
                customAttributes=custom_attributes
            )
        )
    return assets_import

def build_network_interface(ips, mac):
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
    if not mac:
        return NetworkInterface(ipv4Addresses=ip4s, ipv6Addresses=ip6s)
    else:
        return NetworkInterface(macAddress=mac, ipv4Addresses=ip4s, ipv6Addresses=ip6s)

def get_devices(base_url, token):
    url = base_url + '/dna/intent/api/v1/network-device'
    headers = {'Accept': 'application/json',
               'Authorization': 'Bearer ' + token}
    params = {}
    response = http_get(url, headers=headers, params=params)
    if response.status_code != 200:
        print('failed to retrieve devices',  'status code: ' + str(response.status_code))
    data = json_decode(response.body)
    devices = data['response']            
    return devices

def get_token(base_url, creds):
    url = base_url + '/dna/system/api/v1/auth/token'
    headers = {'Accept': 'application/json',
               'Authorization': 'Basic ' + creds}
    params = {}
    response = http_post(url, headers=headers, params=params)
    if response.status_code != 200:
        print('failed to retrieve authroization token',  'status code: ' + str(response.status_code))
        return None

    data = json_decode(response.body)
    if not data:
        print('invalid authentication data')
        return None

    return data['Token']

def main(*args, **kwargs):
    base_url = get_url_base(kwargs)
    b64_creds = base64_encode(kwargs['username'] + ":" + kwargs['password'])
    token = get_token(b64_creds)
    assets = get_devices(base_url, token)
    
    # Format asset list for import into runZero
    import_assets = build_assets(assets)
    if not import_assets:
        print('no assets')
        return None

    return import_assets