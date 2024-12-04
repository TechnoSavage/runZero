load('runzero.types', 'ImportAsset', 'NetworkInterface')
load('json', json_encode='encode', json_decode='decode')
load('net', 'ip_address')
load('http', http_post='post', http_get='get', 'url_encode')
load('uuid', 'new_uuid')

SNIPE_BASE_URL = 'http://192.168.68.60' #'https://<domain or IP>:<port>'
RUNZERO_REDIRECT = 'https://console.runzero.com/'

def build_assets(assets_json):
    assets_import = []
    for item in assets_json:
        id = item.get(item['id'], new_uuid)
        model = item.get(item['model']['value'], '')
        device_type = item.get(item['category']['name'], '')
        man = item.get(item['manufacturer']['name'], '')
        # Map custom fields from Snipe-IT
        custom_fields = item.get('custom_fields', '')
        mac = item.get(custom_fields['MAC Address']['value'], None)

        # parse IP addresses
        ipv4s = []
        ipv6s = []
        ips = []
        networks = item.get('networks', {})
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

        # Map additional fields as custom attributes
                
        assets_import.append(
            ImportAsset(
                id=str(id),
                model=model,
                deviceType=device_type,
                manufacturer=man,
                networkInterfaces=[network],
                customAttributes={
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
    token = kwargs['api_key']

    # get assets
    assets = []
    url = '{}/{}'.format(SNIPE_BASE_URL, 'api/v1/hardware')
    assets = http_get(url, headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': 'Bearer' + token})
    if assets.status_code != 200:
        print('failed to retrieve assets' + assets)
        return None

    assets_json = json_decode(assets.body['rows'])
    print(assets_json)

    # build asset import
    # assets_import = build_assets(assets_json)
    # if not assets_import:
    #     print('no assets')
    
    #return assets_import