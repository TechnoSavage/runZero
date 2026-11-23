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

def build_assets(assets, networkId):
    assets_import = []
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
        assets_import.append(
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

def main(*args, **kwargs):
    base_url = get_url_base(kwargs)
    b64_creds = base64_encode(kwargs['username'] + ":" + kwargs['password'])
    networkId = kwargs['networkId']
    assets = get_devices(base_url, networkId, b64_creds)
    
    # Format asset list for import into runZero
    import_assets = build_assets(assets, networkId)
    if not import_assets:
        print('no assets')
        return None

    return import_assets