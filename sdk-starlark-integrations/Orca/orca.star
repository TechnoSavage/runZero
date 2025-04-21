load('runzero.types', 'ImportAsset', 'NetworkInterface')
load('json', json_encode='encode', json_decode='decode')
load('net', 'ip_address')
load('http', http_get='get', http_post='port', 'url_encode')
load('uuid', 'new_uuid')

#Change the URL to match your Orca instance
ORCA_API_URL = "https://app.au.orcasecurity.io/api/assets"
RUNZERO_REDIRECT = 'https://console.runzero.com/'

def build_assets(asset_data):
    assets = []

    for asset in asset_data:
        custom_attrs = {
            "cloud_provider": asset.get("cloud_provider", ""),
            "account_id": asset.get("account_id", ""),
            "region": asset.get("region", ""),
            "service": asset.get("service", ""),
            "resource_type": asset.get("resource_type", ""),
            "status": asset.get("status", ""),
            "risk_level": asset.get("risk_level", ""),
            "last_seen": asset.get("last_seen", ""),
        }

        mac_address = asset.get("mac_address", "")

        # Collect IPs
        ips = asset.get("private_ips", [])

        assets.append(
            ImportAsset(
                id=str(asset.get("asset_unique_id", "")),
                networkInterfaces=[build_network_interface(ips, mac_address)],
                hostnames=[asset.get("name", "")],
                os_version=asset.get("os_version", ""),
                os=asset.get("os", ""),
                customAttributes=custom_attrs
            )
        )
    return assets

# build runZero network interfaces; shouldn't need to touch this
def build_network_interface(ips, mac=None):
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

def get_assets(token, url=ORCA_API_URL):
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + api_token
    }

    query = {
        "limit": "100",  # Adjust limit as needed
        "page": "1"
    }

    assets = []
    while True:
        response = http_get(url, headers=headers, params=query)

        if response.status_code != 200:
            print("Failed to fetch assets from Orca Security. Status:", response.status_code)
            return assets

        batch = json_decode(response.body).get("assets", [])

        if not batch:
            break  # No more assets

        assets.extend(batch)
        query["page"] = str(int(query["page"]) + 1)

    print("Loaded", len(assets), "assets")
    return assets

def main(**kwargs):
    # assign API key from kwargs
    token = kwargs['access_secret']

    # retrive Orca assets
    all_assets = get_assets(token)

    # map assets to runZero
    assets = build_assets(all_assets)
    
    if not assets:
        print("No assets retrieved from Orca Security")
        return None

    return assets