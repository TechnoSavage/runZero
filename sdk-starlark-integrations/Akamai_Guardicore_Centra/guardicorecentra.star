load('runzero.types', 'ImportAsset', 'NetworkInterface')
load('json', json_encode='encode', json_decode='decode')
load('net', 'ip_address')
load('http', http_get='get', http_post='post', 'url_encode')
load('uuid', 'new_uuid')

#Change the URL to match your Guardicore Centra server
CENTRA_BASE_URL = 'https://<Guardicore Centra URL>'
RUNZERO_REDIRECT = 'https://console.runzero.com/'

def build_assets(assets, creds):
    assets_import = []
    for asset in assets:
        asset_id = str(asset.get('id', new_uuid))
        hostname = asset.get('name', '')
        os_info = asset.get('os_info', {})
        os = os_info.get('type', '')
        first_seen = asset.get('first_seen', '')

        # create the network interfaces
        interfaces = []
        nics = asset.get('nics', [])
        for nic in nics:
            addresses = nic.get('ip_addresses', [])
            interface = build_network_interface(ips=addresses, mac=nic.get('mac_address', None))
            interfaces.append(interface)

        # Retrieve and map custom attributes
        asset_type = asset.get('asset_type', '')
        os_kernel = os_info.get('full_kernel_version', '')
        bios_uuid = asset.get('bios_uuid', '')
        scoping_details = asset.get('scoping_details', {}).get('worksite', {})
        worksite_mod = scoping_details.get('modified', '')
        worksite_name = scoping_details.get('name', '')
        last_seen = asset.get('last_seen', '')
        mssp_tenant = asset.get('mssp_tenant_name', '')
        status = asset.get('status', '')
        instance_id = asset.get('instance_is', '')
        agent_info = asset.get('agent', {})
        agent_last_seen = agent_info.get('agent_last_seen', '')
        agent_version = agent_info.get('agent_version', '')
        comments = asset.get('comments', '')
        orchestration_metadata = asset.get('orchestration_metadata', {})
        orc_asset_type = orchestration_metadata('asset_type', '')
        orc_dev_name = orchestration_metadata('f5_device_hostname', '')
        orc_partition = orchestration_metadata('partition', '')
        orc_vs_name = orchestration_metadata('vs_name', '')

        custom_attributes = {
            'assetType': asset_type,
            'osInfo.fullKernelVersion': os_kernel,
            'biosUuid': bios_uuid,
            'scopingDetails.worksite.modified': worksite_mod,
            'scopingDetails.worksite.name': worksite_name,
            'lastSeenTS': last_seen,
            'msspTenantName': mssp_tenant,
            'status': status,
            'instanceId': instance_id,
            'agentLastSeenTS': agent_last_seen,
            'agentVersion': agent_version,
            'orchestrationMetadata.assetType': orc_asset_type,
            'orchestrationMetadata.f5DeviceHostname': orc_dev_name,
            'orchestrationMetadata.partition': orc_partition,
            'orchestrationMetadata.vsName': orc_vs_name
        }

        ## Additional custom attributes to implement:
        # label_groups = asset.get('label_groups', [])
        # orchestration_details = asset.get('orchestration_details', [])
        # labels = asset.get('labels', [])


        # Build assets for import
        assets_import.append(
            ImportAsset(
                id=asset_id,
                hostnames=[hostname],
                os=os,
                first_seen_ts=first_seen,
                networkInterfaces=interfaces,
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

def get_assets(token):
    results_per_page = 1000
    assets_all = []

    url = CENTRA_BASE_URL + '/api/v4.0/assets?'
    headers = {'Accept': 'application/json',
                'Authorization': 'Bearer ' + token}
    params = {'max_results': results_per_page}
    response = http_get(url, headers=headers, params=params)
    if response.status_code != 200:
        print('failed to retrieve assets',  'status code: ' + str(response.status_code))
    else:
        data = json_decode(response.body)
        assets = data['objects']
        assets_all.extend(assets)           

    return assets_all

def get_token(username, password):
    # Need to determine Centra Ouath endpoint
    url = CENTRA_BASE_URL + '</api/v4.0/authenticate'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {'username': username,
              'password': password}
    
    response = http_post(url, headers=headers, body=bytes(url_encode(payload)))
    if response.status_code != 200:
        print('authentication failed: ', response.status_code)
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
    import_assets = build_assets(assets)
    if not import_assets:
        print('no assets')
        return None

    return import_assets