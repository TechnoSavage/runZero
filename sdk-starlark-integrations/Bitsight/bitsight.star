load('runzero.types', 'ImportAsset', 'NetworkInterface')
load('json', json_encode='encode', json_decode='decode')
load('net', 'ip_address')
load('http', http_get='get', http_post='post', 'url_encode')
load('uuid', 'new_uuid')

#Change the URL to match your Guardicore BITSIGHT server
BITSIGHT_BASE_URL = 'https://api.bitsighttech.com'
RUNZERO_REDIRECT = 'https://console.runzero.com/'

def build_assets(assets, company_id, token):
    assets_import = []
    for asset in assets:
        asset_id = str(asset.get('temporary_id', new_uuid))
        ip_addresses = asset.get('ip_adddresses', [])

        # create the network interfaces
        interfaces = build_network_interface(ips=ip_addresses, mac=None)


        bitsight_tags = asset.get('tags', [])
        tags = []
        for tag in bitsight_tags:
            tag = tag.strip().replace(' ', '_')
            tags.append(tag)
        asset_name = asset.get('asset', '')
        asset_type = asset.get('asset_type', '')
        app_grade = str(asset.get('app_grade', ''))
        country_code = asset.get('country_code', '')
        country = asset.get('coutry', '')
        hosted_by_guid = asset.get('hosted_by', {}).get('guid', '')
        hosted_by_name = asset.get('hosted_by', {}).get('name', '')
        importance = str(asset.get('importance', ''))
        importance_category = asset.get('importance_category', '')
        long = str(asset.get('longitude', ''))
        lat = str(asset.get('latitude', ''))
        origins_sub_guid = asset.get('origin_subsidiary', {}).get('guid', '')
        origins_sub_name = asset.get('origin_subsidiary', {}).get('name', '')
        is_monitored = str(asset.get('is_monitored', ''))
        cloud_context = asset.get('cloud_context', {})
        slug = cloud_context.get('provider', {}).get('slug', '')
        cloud_name = cloud_context.get('provider', {}).get('name', '')
        region = cloud_context.get('provider', {}).get('region', '')
        service = cloud_context.get('provider', {}).get('service', '')

        custom_attributes = {
                             'asset': asset_name,
                             'assetType': asset_type,
                             'appGrade': app_grade,
                             'countryCode': country_code,
                             'country': country,
                             'hostedBy.guid': hosted_by_guid,
                             'hostedBy.name': hosted_by_name,
                             'importance': importance,
                             'importanceCategory': importance_category,
                             'longitude': long,
                             'latitude': lat,
                             'originSubsidiary.guid': origins_sub_guid,
                             'originSubsidiary.name': origins_sub_name,
                             'isMonitored': is_monitored,
                             'cloudContext.slug': slug,
                             'cloudContext.name': cloud_name,
                             'cloudContext.region': region,
                             'cloudContext.service': service
                             }
        
        products = asset.get('products', [])
        for product in products:
            for k, v in product.items():
                custom_attributes['product' + str(index(product)) + k] = v

        # Retrive and map vulnerabilities


        # Build assets for import
        assets_import.append(
            ImportAsset(
                id=asset_id,
                tags=tags,
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

def get_assets(company_id, token):
    assets_all = []
    total_count = 10000
    url = BITSIGHT_BASE_URL + '/ratings/v1/companies/' + company_id + '/assets?'
    headers = {'Accept': 'application/json',
                    'Authorization': 'Bearer ' + token}
    params = {}
    
    while len(assets_all) > total_count - 1:
        response = http_get(url, headers=headers, params=params)
        if response.status_code != 200:
            print('failed to retrieve assets from page ' + str(page), 'status code: ' + str(response.status_code))
            break
        else:
            data = json_decode(response.body)
            url = data.get('links', {}).get('next', '')
            total_count = data.get('count', 1)
            assets = data.get('results', [])
            assets_all.extend(assets)    

    return assets_all

def get_vulns(company_id, asset_id, token):
    vulns_all = []
    vulns_count = 10000
    url = BITSIGHT_BASE_URL + '/ratings/v1/companies/' + company_id + '/findings?'
    headers = {'Accept': 'application/json',
                    'Authorization': 'Bearer ' + token}
    params = {'asset': asset_id}

    while len(assets_all) > total_count - 1:
        response = http_get(url, headers=headers, params=params)
        if response.status_code != 200:
            print('failed to retrieve assets from page ' + str(page), 'status code: ' + str(response.status_code))
            break
        else:
            data = json_decode(response.body)
            url = data.get('links', {}).get('next', '')
            total_count = data.get('count', 1)
            assets = data.get('results', [])
            assets_all.extend(assets)    

    return vulns_all


def main(*args, **kwargs):
    company_id = kwargs['access_key']
    token = kwargs['access_secret']
    assets = get_assets(company_id, token)

    # Format asset list for import into runZero
    import_assets = build_assets(assets, company_id, token)
    if not import_assets:
        print('no assets')
        return None

    return import_assets