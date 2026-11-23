CONFIG = {
    "id": "forward networks",
    "name": "Forward Networks",
    "type": "inbound",
    "description": "Imports devices from Forward Networks",
    "version": "1",
    "minVersion": "0",
    "params": [
        {"key": "url", "label": "Forward Networks URL", "type": "url", "required": True},
        {"key": "username", "label": "username|access_key", "type": "secret", "required": True},
        {"key": "password", "label": "password|access_secret", "type": "secret", "required": True},
        {"key": "networkId", "label": "network ID", "type": "int", "required": True}
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
load('time', 'parse_time')

def build_devices(assets, networkId):
    import_devices = []
    for asset in assets:
        asset_id = str(networkId + asset.get('name', new_uuid))
        addresses = asset.get('managementIps', [])
        hostname = asset.get('name', '')
        model = asset.get('model', '')
        os = asset.get('platform', '')
        os_version = asset.get('osVersion', '')
        device_type = asset.get('type', '')

        # create the network interfaces
        interface = build_network_interface(ips=addresses, mac=None)

        # Retrieve and map custom attributes

        # custom_attributes = {}

        # Build assets for import
        import_devices.append(
            ImportAsset(
                id=asset_id,
                hostnames=[hostname],
                model=model,
                device_type=device_type,
                os=os,
                os_version=os_version,
                networkInterfaces=[interface]
            )
        )
    return import_devices

def build_endpoints(assets, networkId):
    import_endpoints = []
    for asset in assets:
        asset_id = str(networkId + asset.get('name', new_uuid))
        addresses = asset.get('host', '')
        hostname = asset.get('name', '')

        # create the network interfaces
        interface = build_network_interface(ips=addresses, mac=None)

        # Retrieve and map custom attributes

        createdAt = asset.get('createdAt', '')
        if createdAt and createdAt != '':
            createdAt = parse_time(createdAt).unix
        updatedAt = asset.get('updatedAt', '')
        if updatedAt and updatedAt != '':
            updatedAt = parse_time(updatedAt).unix


        custom_attributes = {
            'port': str(asset.get('port', '')),
            'protocol': asset.get('protocol', ''),
            'profileId': asset.get('profileId', ''),
            'credentialId': asset.get('credentialId', ''),
            'jumpserverId': asset.get('jumpserverId', ''),
            'fullCollectionLog': asset.get('fullCollectionLog', ''),
            'largeRtt': asset.get('largeRtt', ''),
            'collect': asset.get('collect', ''),
            'note': asset.get('note', ''),
            'createById': asset.get('createById', ''),
            'createdAt': createdAt,
            'createdBy': asset.get('createdBy', ''),
            'updatedById': asset.get('updatedById', ''),
            'updatedAt': updatedAt,
            'updatedBy': asset.get('updatedBy', ''),

        }

        # Build assets for import
        import_endpoints.append(
            ImportAsset(
                id=asset_id,
                hostnames=[hostname],
                model=model,
                device_type=device_type,
                os=os,
                os_version=os_version,
                networkInterfaces=[interface]
            )
        )
    return import_endpoints

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

def get_devices(base_url, networkId, creds):
    url = base_url + '/api/networks/' + networkId + '/devices'
    headers = {'Accept': 'application/json',
               'Authorization': 'Basic ' + creds}
    params = {}
    response = http_get(url, headers=headers, params=params)
    if response.status_code != 200:
        print('failed to retrieve devices',  'status code: ' + str(response.status_code))
    devices = json_decode(response.body)            
    return devices

def get_endpoints(base_url, networkId, creds):
    url = base_url + '/api/networks/' + networkId + '/endpoints'
    headers = {'Accept': 'application/json',
               'Authorization': 'Basic ' + creds}
    params = {}
    response = http_get(url, headers=headers, params=params)
    if response.status_code != 200:
        print('failed to retrieve endpoints',  'status code: ' + str(response.status_code))
    endpoints = json_decode(response.body)            
    return endpoints

def main(*args, **kwargs):
    base_url = get_url_base(kwargs)
    b64_creds = base64_encode(kwargs['username'] + ":" + kwargs['password'])
    networkId = kwargs['networkId']
    devices = get_devices(base_url, networkId, b64_creds)
    endpoints = get_endpoints(base_url, networkId, b64_creds)
    
    # Format asset list for import into runZero
    import_devices = build_devices(devices, networkId)
    import_endpoints = build_endpoints(endpoints, networkId)
    import_devices.extend(import_endpoints)
    if not import_devices:
        print('no assets')
        return None

    return import_devices