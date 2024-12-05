load('runzero.types', 'ImportAsset', 'NetworkInterface')
load('json', json_encode='encode', json_decode='decode')
load('net', 'ip_address')
load('http', http_post='post', http_get='get', 'url_encode')
load('uuid', 'new_uuid')

SNIPE_BASE_URL = http://192.168.68.64 #'https://<domain or IP>:<port>'
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
        age = asset.get('age', '')
        asset_tag = asset.get('asset_tag', '')
        book_value = asset.get(str('book_value'), '')
        byod = asset.get(str('byod'), '')
        checkin_count = asset.get(str('checkin_counter'), '')
        checkout_count = asset.get(str('checkout_counter'), '')
        company_info = asset.get('company', {})
        if company_info:
            company_name = company_info.get('')
        created_info = asset.get('created_at', {})
        if created_info:
            created = created_info.get('datetime', '')
        else:
            created = ''
        eol = asset.get(str('eol'), '')
        eol_date = asset.get(str('asset_eol_date'), 'NA')
        expected_checkin = asset.get(str('expected_checkin'), '')
        last_audit = asset.get('last_audit_date', '')
        last_checkout = asset.get(str('last_checkout'), '')
        location_info = asset.get('location', {})
        if location_info:
            location = location_info.get('name', '')
        else:
            location = ''
        model_number = asset.get('model_number', '')
        name = asset.get('name', '')
        next_audit = asset.get('next_audit_date', '')
        notes = asset.get('notes', '')
        order_number = asset.get(str('order_number'), '')
        purchase_cost = asset.get('purchase_cost', '')
        purchase_date = asset.get('purchase_date', '')
        requests_count = asset.get(str('requests_counter'), '')
        serial = asset.get('serial', '')
        status_info = asset.get('status_label', {})
        if status_info:
            status_name = status_info.get('name', '')
            status_type = status_info.get('status_type', '')
        else:
            status_name = ''
            status_type = ''
        supplier_info = asset.get('supplier', {})
        if supplier_info:
            supplier = supplier_info('name', '')
        else:
            supplier = ''
        updated_info = asset.get('updated_at', {})
        if updated_info:
            updated = updated_info('datetime', '')
        else:
            updated = ''
        user_checkout = asset.get(str('user_can_checkout'), '')
        warranty_months = asset.get('warranty_months', '')
        warranty_exp = asset.get(str('warranty_expires'), '')




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
                    "age": age,
                    "asset.tag": asset_tag,
                    "book.value": book_value,
                    "byod": byod,
                    "checkin.count": checkin_count,
                    "checkout.count": checkout_count,
                    "eol": eol,
                    "eol.date": eol_date,
                    "expected.checkin": expected_checkin,
                    "first.seen": created,
                    "last.audit": last_audit,
                    "last.checkout": last_checkout,
                    "last.seen": updated,
                    "location": location,
                    "model.number": model_number,
                    "name": name,
                    "next.audit": next_audit,
                    "notes": notes,
                    "order.number": order_number,
                    "purchase.cost": purchase_cost,
                    "purchase.date": purchase_date,
                    "requests.count": requests_count,
                    "serial.number": serial,
                    "status.name": status_name,
                    "status.type": status_type,
                    "supplier.name": supplier,
                    "user.checkout": user_checkout,
                    "warranty.months": warranty_months,
                    "warranty.expiration": warranty_exp
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