load('runzero.types', 'ImportAsset', 'NetworkInterface')
load('json', json_encode='encode', json_decode='decode')
load('net', 'ip_address')
load('http', http_post='post', http_get='get', 'url_encode')
load('uuid', 'new_uuid')

SNIPE_BASE_URL = 'https://<domain or IP>:<port>'
RUNZERO_REDIRECT = 'https://console.runzero.com/'

def build_assets(assets_json):
    assets_import = []
    for asset in assets_json:
        id = asset.get(str('id'), new_uuid)
        model_info = asset.get('model', {})
        if model_info:
            model = model_info.get('name', '')
        else:
            model = ''
        device_info = asset.get('category', {})
        if device_info:
            device_type = device_info.get('name', '')
        else:
            device_type = ''
        manuf_info = asset.get('manufacturer', {})
        if manuf_info:
            manufacturer = manuf_info.get('name', '')
        else:
            manufacturer = ''
        # Map custom fields from Snipe-IT
        custom_fields = asset.get('custom_fields', {})
        if custom_fields:
            mac_info =custom_fields.get('MAC Address', {})
            if mac_info:
                mac = mac_info.get('value', None)
        else:
            mac = None

        # Map additional Snipe-IT fields as custom attributes
        name = asset.get('name', '')
        serial = asset.get('serial', '')

        # parse IP addresses
        ipv4s = []
        ipv6s = []
        ips = []
        networks = asset.get('networks', {})
        if networks:
            ipv4s = networks.get('v4', [])
            ipv6s = networks.get('v6', [])
            
            if ipv4s:
                for v4 in ipv4s:
                    addr = v4.get('ip_address', '')
                    ips.append(addr)
        
            if ipv6s:
                for v6 in ipv6s:
                    addr = v6.get('ip_address', '')
                    ips.append(addr)        

        network = build_network_interface(ips=[], mac=mac)
        
        assets_import.append(
            ImportAsset(
                id=str(id),
                model=model,
                deviceType=device_type,
                manufacturer=manufacturer,
                networkInterfaces=[network],
                customAttributes={
                    "name": name,
                    "serial.number": serial
                }
            )
        )
    return assets_import

# build runZero network interfaces; shouldn't need to touch this
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
    
    return NetworkInterface(macAddress=mac, ipv4Addresses=ip4s, ipv6Addresses=ip6s)

def main(**kwargs):
    # assign API key from kwargs
    token = kwargs['access_secret']

    # get assets
    assets = []
    url = '{}/{}'.format(SNIPE_BASE_URL, 'api/v1/hardware')
    assets = http_get(url, headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token})
    if assets.status_code != 200:
        print('failed to retrieve assets' + str(assets))
        return None

    assets_json = json_decode(assets.body)['rows']

    # build asset import
    assets_import = build_assets(assets_json)
    if not assets_import:
         print('no assets')
    
    return assets_import