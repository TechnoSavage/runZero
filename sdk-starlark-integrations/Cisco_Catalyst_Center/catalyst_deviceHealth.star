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
load('base64', base64_encode='encode', base64_decode='decode')
load('http', http_get='get', http_post='post', 'url_encode')
load('json', json_encode='encode', json_decode='decode')
load('net', 'ip_address')
load('time', 'parse_time')
load('uuid', 'new_uuid')

#Change the URL to match your Snow Software License Manager server
CATCENTER_BASE_URL = 'https://<Catalyst Center URL>'
RUNZERO_REDIRECT = 'https://console.runzero.com/'

def build_assets(assets):
    assets_import = []
    for device in assets:
        asset_id = str(device.get('uuid', new_uuid))
        ip_address = device.get('ipAddress', '')
        mac = device.get('macAddress', None)
        hostname = device.get('name', '')
        model = device.get('model', '')
        os = device.get('osVersion', '')

        # create the network interfaces
        interface = build_network_interface(ips=[ip_address], mac=mac)

        # Retrieve and map custom attributes

        custom_attributes = {
            'deviceType': device.get('deviceType', ''),
            'cpuUtilization': str(device.get('cpuUtilization', '')),
            'overallHealth': str(device.get('overallHealth', '')),
            'cpuHealth': str(device.get('cpuHealth', '')),
            'deviceFamily': device.get('deviceFamily', ''),
            'issueCount': str(device.get('issueCount', '')),
            'interfaceLinkErrHealth': str(device.get('interfaceLinkErrHealth', '')),
            'memoryUtilization': str(device.get('memoryUtilization', '')),
            'interDeviceLinkAvailHealth': str(device.get('interDeviceLinkAvailHealth', '')),
            'location': device.get('location', ''),
            'reachabilityHealth': str(device.get('reachabilityHealth', '')),
            'memoryUtilizationHealth': str(device.get('memoryUtilizationHealth', '')),
            'avgTemperature': str(device.get('avgTemperature', '')),
            'maxTemperature': str(device.get('maxTemperature', '')),
            'interDeviceLinkAvailFabric': str(device.get('interDeviceLinkAvailFabric', '')),
            'apCount': str(device.get('apCount', '')),
            'freeTimerScore': str(device.get('freeTimerScore', '')),
            'freeTimer': device.get('freeTimer', ''),
            'packetPoolHealth': str(device.get('packetPoolHealth', '')),
            'packetPool': str(device.get('packetPool', '')),
            'freeMemoryBufferHealth': str(device.get('freeMemoryBufferHealth', '')),
            'freeMemoryBuffer': str(device.get('freeMemoryBuffer', '')),
            'wqePoolsHealth': str(device.get('wqePoolsHealth', '')),
            'wqePools': str(device.get('wqePools', '')),
            'wanLinkUtilization': str(device.get('wanLinkUtilization', '')),
            'cpuUlitilization': str(device.get('cpuUlitilization', '')),
        }
        
        util_health = device.get('utilizationHealth', {})
        if util_health and type(util_health) == 'dict':
            for k, v in util_health.items():
                custom_attributes['utilaztionHealth.' + k] = str(v)

        aq_health = device.get('airQualityHealth', {})
        if aq_health and type(aq_health) == 'dict':
            for k, v in aq_health.items():
                custom_attributes['airQualityHealth.' + k] = str(v)

        noise_health = device.get('noiseHealth', {})
        if noise_health and type(noise_health) == 'dict':
            for k, v in noise_health.items():
                custom_attributes['noiseHealth.' + k] = str(v)

        interf_health = device.get('interferenceHealth', {})
        if interf_health and type(interf_health) == 'dict':
            for k, v in interf_health.items():
                custom_attributes['interferenceHealth.' + k] = str(v)

        band = device.get('band', {})
        if band and type(band) == 'dict':
            for k, v in band.items():
                custom_attributes['band.' + k] = str(v)

        clients = device.get('clientCount', {})
        if clients and type(clients) == 'dict':
            for k, v in clients.items():
                custom_attributes['clientCount.' + k] = str(v)

        # Build assets for import
        assets_import.append(
            ImportAsset(
                id=asset_id,
                hostnames=[hostname],
                model=model,
                os=os,
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

def get_devices(creds):
    url = CATCENTER_BASE_URL + '/dna/intent/api/v1/device-health'
    headers = {'Accept': 'application/json',
               'Authorization': 'Basic ' + creds}
    params = {}
    response = http_get(url, headers=headers, params=params)
    if response.status_code != 200:
        print('failed to retrieve assets at $skip=' + str(items_returned),  'status code: ' + str(response.status_code))
    else:
        data = json_decode(response.body)
        devices = data['response']            
        return devices

def main(*args, **kwargs):
    username = kwargs['access_key']
    password = kwargs['access_secret']
    b64_creds = base64_encode(username + ":" + password)
    assets = get_devices(b64_creds)
    
    # Format asset list for import into runZero
    import_assets = build_assets(assets)
    if not import_assets:
        print('no assets')
        return None

    return import_assets