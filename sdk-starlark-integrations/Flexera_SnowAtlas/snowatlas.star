load('runzero.types', 'ImportAsset', 'NetworkInterface', 'Software')
load('json', json_encode='encode', json_decode='decode')
load('net', 'ip_address')
load('http', http_get='get', 'url_encode')
load('uuid', 'new_uuid')

#Change the URL to match your Snow Atlas server
ATLAS_BASE_URL = 'https://<region>.snowsoftware.io'
RUNZERO_REDIRECT = 'https://console.runzero.com/'

def build_assets(assets_json, token):
    assets_import = []
    for asset in assets_json:
        id = asset.get('id', new_uuid)
        hostname = asset.get('hostName', '')
        manufacturer = asset.get('manufacturer', '')
        os = asset.get('operatingSystem', '')
        hardware = asset.get('model', '')
        custom_attributes = {}
        
        # Map custom fields from Snow Atlas
        portable = asset.get('isPortable', '')
        virtual = asset.get('isVirtual', '')
        server = asset.get('isServer', '')
        vdi = asset.get('isVDI', '')
        hostComputerId  = asset.get('hostComputerId', '')
        mostFrequentUser = asset.get('mostFrequentUser', '')
        mostRecentUser = asset.get('mostRecentUser', '')
        domain = asset.get('domain', '')
        lastScanDate = asset.get('lastScanDate', '')
        status = asset.get('status', '')
        organizationId = asset.get('organizationId', '')
        processorCount = asset.get('processorCount', '')
        processorCoreCount = asset.get('coreCount', '')

        # Retrieve computer details and map to asset
        comp_details = get_comp_details(id, token)
        for key, value in comp_details.items():
                custom_attributes[key] = value

        # Retrive computer hardware and map to asset
        asset_hw = get_comp_hw(id, token)
        for key, value in asset_hw.items():
                custom_attributes[key] = value

        # Retrieve network interfaces and map to asset
        interfaces = get_comp_interfaces(id, token)

        # parse IP addresses
        networks = []
        base_ip = (asset.get('ipAddress', None))
        base_network = build_network_interface(ips=[base_ip], mac=None)
        for interface in interfaces:
            ip = interface.get('ipAddress', None)
            mac = interface.get('macAddress', None)
            network = build_network_interface(ips=[ip], mac=mac)
            networks.append(network)

        # Retrieve software and map to asset
        apps = get_comp_apps(id, base_ip, token)
        software = build_software(apps, token)

        assets_import.append(
            ImportAsset(
                id=str(id),
                model=hardware,
                manufacturer=manufacturer,
                networkInterfaces=networks,
                customAttributes=custom_attributes,
                software=software[:99]
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

def build_software(applications):
    software = []
    for app in applications:
        # API call to get software family
        # APi call to get software versions
        # API call to get user names from IDs
        software.append(
            Software(
                id='',
                vendor='',
                product='',
                version='',
                serviceAddress=''
            )
        )

def get_assets(token):
    page = 1
    item_count = 100
    assets_all = []

    # while items returned is == to items returned per page perform successive page fetches
    while True:
        url = '{}/{}={}={}'.format(ATLAS_BASE_URL, 'api/sam/estate/v1/computers?page_size', item_count, '&page_number', page)
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token}
        response = http_get(url, headers=headers, timeout=300)

        if response.status_code != 200:
            print('failed to retrieve assets for page: ', page, 'status code: ', response.status_code)
        else:
            assets = json_decode(response.body)['items']
            assets_all.extend(assets)
            if len(assets) < item_count:
                break
            page += 1

    return assets_all

def get_comp_details(id, token):
    url = '{}/{}/{}'.format(ATLAS_BASE_URL, 'api/sam/estate/v1/computers', id)
    response = http_get(url, headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token}, timeout=300)
    if response.status_code != 200:
            print('failed to retrieve computer details for computer: ', id, 'status code: ', response.status_code)
            return None
    return json_decode(response)

def get_comp_hw(id, token):
    url = '{}/{}/{}/{}'.format(ATLAS_BASE_URL, 'api/sam/estate/v1/computers', id, 'hardware')
    response = http_get(url, headers={'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token}, timeout=300)
    if response.status_code != 200:
            print('failed to retrieve computer hardware for computer: ', id, 'status code: ', response.status_code)
            return None
    return response

def get_comp_interfaces(id, token):
    page = 1
    item_count = 25
    interfaces_all = []

    # while items returned is == to items returned per page perform successive page fetches
    while True:
        url = '{}/{}/{}/{}'.format(ATLAS_BASE_URL, 'api/sam/estate/v1/computers', id, 'hardware/networkadapters?page_size', item_count, '&page_number', page)
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token}
        response = http_get(url, headers=headers, timeout=300)

        if response.status_code != 200:
            print('failed to retrieve computer interfaces for computer: ', id, 'status code: ', response.status_code)
        else:
            interfaces = json_decode(response.body)['items']
            interfaces_all.extend(interfaces)
            if len(interfaces) < item_count:
                break
            page += 1

    return interfaces_all

def get_comp_apps(id, address, token):
    page = 1
    item_count = 100
    applications_all = []

    while True:
        url = '{}/{}/{}/{}'.format(ATLAS_BASE_URL, 'api/sam/estate/v1/computers', id, 'applications?page_size', item_count, '&page_number', page)
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token}
        response = http_get(url, headers=headers, timeout=300)
        
        if response.status_code != 200:
            print('failed to retrieve applications for computer: ', id, 'status code: ', response.status_code)
        else:
            applications = json_decode(response.body)['items']
            applications_all.extend(applications)
            if len(applications) < item_count:
                break
            page += 1

    return applications_all

def main(**kwargs):
    # assign API key from kwargs
    token = kwargs['access_secret']

    # retrieve initial computer assets
    computers = get_assets(token)

    # build asset import
    assets_import = build_assets(computers, token)
    if not assets_import:
        print('no assets')
        return None

    return assets_import