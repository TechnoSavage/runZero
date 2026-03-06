load('runzero.types', 'ImportAsset', 'NetworkInterface')
load('http', http_get='get', http_post='post', 'url_encode')
load('json', json_encode='encode', json_decode='decode')
load('net', 'ip_address')
load('time', 'parse_time')
load('uuid', 'new_uuid')

#Change the URL to match your Guardicore Cortex server
CORTEX_BASE_URL = 'https://<Guardicore Cortex URL>'
RUNZERO_REDIRECT = 'https://console.runzero.com/'

def build_assets(assets, token):
    assets_import = []
    label_mapping = {}
    for asset in assets:
        os_info = asset.get('os_info', {})
        asset_id = agent_info.get('id', str(new_uuid))
        hostname = asset.get('name', '')
        os = os_info.get('type', '')
        first_seen = asset.get('first_seen', '')
        #reformat first_seen timestamp for runZero parsing
        if first_seen != '':
            split_space = first_seen.split(' ')
            first_seen = parse_time(split_space[0] + 'T' + split_space[1] + 'Z')

        # create the network interfaces
        interfaces = []
        nics = asset.get('nics', [])
        for nic in nics:
            addresses = nic.get('ip_addresses', [])
            interface = build_network_interface(ips=addresses, mac=nic.get('mac_address', None))
            interfaces.append(interface)

        #reformat agent_last_seen timestamp for runZero parsing
        if agent_last_seen != '':
            split_space = agent_last_seen.split(' ')
            agent_last_seen = parse_time(split_space[0] + 'T' + split_space[1] + 'Z').unix
        last_seen = asset.get('last_seen', '')
        #reformat last_seen timestamp for runZero parsing
        if last_seen != '':
            split_space = last_seen.split(' ')
            last_seen = parse_time(split_space[0] + 'T' + split_space[1] + 'Z').unixß


        custom_attributes = {
        }

        # Build assets for import
        assets_import.append(
            ImportAsset(
                id=asset_id,
                hostnames=[hostname],
                os=os,
                first_seen_ts=first_seen,
                networkInterfaces=interfaces,
                customAttributes=custom_attributes,
                tags=tags
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

def get_assets(token):
    assets_all = []
    results_per_page = 1000
    start = 0
    last_return = 1000

    # Return all 'status:on' assets
    while True:
        url = CORTEX_BASE_URL + '/api/v4.0/assets?'
        headers = {'Accept': 'application/json',
                    'Authorization': 'Bearer ' + token}
        params = {'max_results': results_per_page,
                  'start_at': start,
                  'status': 'on',
                  'expand': 'agent'}
        response = http_get(url, headers=headers, params=params)
        if response.status_code != 200:
            print('failed to retrieve "on" assets ' + str(start) + ' to ' + str(start + results_per_page), 'status code: ' + str(response.status_code))
            break
        else:
            data = json_decode(response.body)
            assets = data['objects']
            assets_all.extend(assets)
            last_return = len(assets)
            start += last_return
            if last_return < results_per_page:
                start = 0
                last_return = 1000
                break      

    return assets_all

def get_token(username, password):
    url = CORTEX_BASE_URL + '/api/v1/authenticate'
    headers = {'Content-Type': 'application/json'}
    payload = {'username': username,
              'password': password}
    
    response = http_post(url, headers=headers, body=bytes(json_encode(payload)))
    if response.status_code != 200:
        print('authentication failed: ' + str(response.status_code))
        return None

    auth_data = json_decode(response.body)
    if not auth_data:
        print('invalid authentication data')
        return None

    return auth_data['access_token']  

def main(*args, **kwargs):
    username = kwargs['access_key']
    password = kwargs['access_secret']
    token = get_token(username, password)
    assets = get_assets(token)
    
    # Format asset list for import into runZero
    import_assets = build_assets(assets, token)
    if not import_assets:
        print('no assets')
        return None

    return import_assets