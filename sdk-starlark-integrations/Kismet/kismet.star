load('runzero.types', 'ImportAsset', 'NetworkInterface')
load('json', json_encode='encode', json_decode='decode')
load('net', 'ip_address')
load('http', http_post='post', http_get='get', 'url_encode')
load('uuid', 'new_uuid')

#Change the URL to match your Kismet server
KISMET_BASE_URL = 'http://192.168.68.57:2501' # 'http://<domain or IP>:<port>'
KISMET_PHY = '<PHY device>'
RUNZERO_REDIRECT = 'https://console.runzero.com/'

def build_assets(assets_json):
    assets_import = []
    for asset in assets_json:
        id = asset.get(str('id'), new_uuid)
        name = asset.get('kismet.device.base.commonname', '')
        manufacturer = asset.get('kismet.device.base.manuf', '')
        device_type = asset.get('kismet.device.base.type', '')
        first_seen = asset.get('kismet.device.base.first_time', '')
        mac = asset.get('kismet.device.base.macaddr', None)

        # Map additional Kismet fields as custom attributes

        # Map Kismet dot11.device attributes
        dot11_device = asset.get('dot11.device', {})
        beacon_fingerprint = dot11_device.get('dot11.device.beacon_fingerprint', '')
        bss_timestamp = dot11_device.get('dot11.device.bss_timestamp', '')
        client_disconnects = dot11_device.get('dot11.device.client_disconnects', '')
        client_disconnects_last = dot11_device.get('dot11.device.client_disconnects_last', '')
        datasize = dot11_device.get('dot11.device.datasize', '')
        datasize_retry = dot11_device.get('dot11.device.datasize_retry', '')
        last_beacon_timestamp = dot11_device.get('dot11.device.last_beacon_timestamp', '')
        last_bssid = dot11_device.get('dot11.device.last_bssid', '')
        last_sequence = dot11_device.get('dot11.device.last_sequence', '')
        link_measurement_capable = dot11_device.get('dot11.device.link_measurement_capable', '')
        max_tx_power = dot11_device.get('dot11.device.max_tx_power', '')
        min_tx_power = dot11_device.get('dot11.device.min_tx_power', '')
        neighbor_report_capable = dot11_device.get('dot11.device.neighbor_report_capable', '')
        num_advertised_ssids = dot11_device.get('dot11.device.num_advertised_ssids', '')
        num_associated_clients = dot11_device.get('dot11.device.num_associated_clients', '')
        num_client_aps= dot11_device.get('dot11.device.num_client_aps', '')
        num_fragments = dot11_device.get('dot11.device.num_fragments', '')
        num_probed_ssids = dot11_device.get('dot11.device.num_probed_ssids', '')
        num_retries = dot11_device.get('dot11.device.num_retries', '')
        num_responded_ssids = dot11_device.get('dot11.device.num_responded_ssids', '')
        probe_fingerprint = dot11_device.get('dot11.device.probe_fingerprint', '')
        response_fingerprint = dot11_device.get('dot11.device.response_fingerprint', '')
        typeset = dot11_device.get('dot11.device.typeset', '')
        wps_m3_count = dot11_device.get('dot11.device.wps_m3_count', '')
        wps_m3_last = dot11_device.get('dot11.device.wps_m3_last', '')
        
        # Map Kismet last beaconed SSID record
        last_beaconed_ssid_record = dot11_device.get('dot11.device.last_beaconed_ssid_record', {})
        beaconed_advertisedssid_beacon = last_beaconed_ssid_record.get('dot11.advertisedssid.beacon', '')
        beaconed_advertisedssid_beaconrate = last_beaconed_ssid_record.get('dot11.advertisedssid.beaconrate', '')
        beaconed_advertisedssid_beacons_sec = last_beaconed_ssid_record.get('dot11.advertisedssid.beacons_sec', '')
        beaconed_advertisedssid_channel = last_beaconed_ssid_record.get('dot11.advertisedssid.channel', '')
        beaconed_advertisedssid_ccx_txpower= last_beaconed_ssid_record.get('dot11.advertisedssid.ccx_txpower', '')
        beaconed_advertisedssid_cisco_client_mfp = last_beaconed_ssid_record.get('dot11.advertisedssid.cisco_client_mfp', '')
        beaconed_advertisedssid_cloaked= last_beaconed_ssid_record.get('dot11.advertisedssid.cloaked', '')
        beaconed_advertisedssid_crypt_set = last_beaconed_ssid_record.get('dot11.advertisedssid.crypt_set', '')
        beaconed_advertisedssid_dot11d_country = last_beaconed_ssid_record.get('dot11.advertisedssid.dot11d_country', '')
        beaconed_advertisedssid_dot11e_channel_utilization_perc = last_beaconed_ssid_record.get('dot11.advertisedssid.dot11e_channel_utilization_perc', '')
        beaconed_advertisedssid_dot11e_qbss = last_beaconed_ssid_record.get('dot11.advertisedssid.dot11e_qbss', '')
        beaconed_advertisedssid_dot11e_qbss_stations = last_beaconed_ssid_record.get('dot11.advertisedssid.dot11e_qbss_stations', '')
        beaconed_advertisedssid_dot11r_mobility_domain_id = last_beaconed_ssid_record.get('dot11.advertisedssid.dot11r_mobility_domain_id', '')
        beaconed_advertisedssid_dot11r_mobility = last_beaconed_ssid_record.get('dot11.advertisedssid.dot11r_mobility', '')
        beaconed_advertisedssid_first_time = last_beaconed_ssid_record.get('dot11.advertisedssid.first_time', '')
        beaconed_advertisedssid_ht_center_1 = last_beaconed_ssid_record.get('dot11.advertisedssid.ht_center_1', '')
        beaconed_advertisedssid_ht_center_2 = last_beaconed_ssid_record.get('dot11.advertisedssid.ht_center_2', '')
        beaconed_advertisedssid_ht_mode = last_beaconed_ssid_record.get('dot11.advertisedssid.ht_mode', '')
        beaconed_advertisedssid_ietag_checksum = last_beaconed_ssid_record.get('dot11.advertisedssid.ietag_checksum', '')
        beaconed_advertisedssid_last_time = last_beaconed_ssid_record.get('dot11.advertisedssid.last_time', '')
        beaconed_advertisedssid_maxrate = last_beaconed_ssid_record.get('dot11.advertisedssid.maxrate', '')
        beaconed_advertisedssid_probe_response = last_beaconed_ssid_record.get('dot11.advertisedssid.probe_response', '')
        beaconed_advertisedssid_ssid = last_beaconed_ssid_record.get('dot11.advertisedssid.ssid', '')
        beaconed_advertisedssid_ssid_hash = last_beaconed_ssid_record.get('dot11.advertisedssid.ssid_hash', '')
        beaconed_advertisedssid_ssidlen = last_beaconed_ssid_record.get('dot11.advertisedssid.ssidlen', '')
        beaconed_advertisedssid_wpa_mfp_required = last_beaconed_ssid_record.get('dot11.advertisedssid.wpa_mfp_required', '')
        beaconed_advertisedssid_wpa_mfp_supported = last_beaconed_ssid_record.get('dot11.advertisedssid.wpa_mfp_supported', '')
        beaconed_advertisedssid_wps_config_methods = last_beaconed_ssid_record.get('dot11.advertisedssid.wps_config_methods', '')
        beaconed_advertisedssid_wps_state = last_beaconed_ssid_record.get('dot11.advertisedssid.wps_state', '')
        beaconed_advertisedssid_wps_version = last_beaconed_ssid_record.get('dot11.advertisedssid.wps_version', '')

        # Build custom attributes dictionary
        custom_attributes = {
                "first.seen": first_seen,
                "name": name,
                "dot11.device.beacon_fingerprint": beacon_fingerprint,
                "dot11.device.bss_timestamp": bss_timestamp,
                "dot11.device.client_disconnects": client_disconnects,
                "dot11.device.client_disconnects_last": client_disconnects_last,
                "dot11.device.datasize": datasize,
                "dot11.device.datasize_retry": datasize_retry,
                "dot11.device.last_beacon_timestamp": last_beacon_timestamp,
                "dot11.device.last_bssid": last_bssid,
                "dot11.device.last_sequence": last_sequence,
                "dot11.device.link_measurement_capable": link_measurement_capable,
                "dot11.device.max_tx_power": max_tx_power,
                "dot11.device.min_tx_power": min_tx_power,
                "dot11.device.neighbor_report_capable": neighbor_report_capable,
                "dot11.device.num_advertised_ssids": num_advertised_ssids,
                "dot11.device.num_associated_clients": num_associated_clients,
                "dot11.device.num_client_aps": num_client_aps,
                "dot11.device.num_fragments": num_fragments,
                "dot11.device.num_probed_ssids": num_probed_ssids,
                "dot11.device.num_retries": num_retries,
                "dot11.device.num_responded_ssids": num_responded_ssids,
                "dot11.device.probe_fingerprint": probe_fingerprint,
                "dot11.device.response_fingerprint": response_fingerprint,
                "dot11.device.typeset": typeset,
                "dot11.device.wps_m3_count": wps_m3_count,
                "dot11.device.wps_m3_last": wps_m3_last
        }

        # Map Kismet associated client map
        associated_client_map = dot11_device.get('dot11.device.associated_client_map', {})
        
        # Map Kismet responded SSID map
        responded_ssid_map = dot11_device.get('dot11.device.responded_ssid_map', [])
        for item in responded_ssid_map:
            for key, value in item.items():
                print(key, value)
                custom_attributes["{}.{}.{}".format("responded_ssid_map", str(responded_ssid_map.index(item)), key)] = value # item.get(key, '')
            # custom_attributes["{}.{}.{}".format("responded_ssid_map", str(responded_ssid_map.index(item)),"dot11.advertisedssid.ssidlen")] = item.get('dot11.advertisedssid.ssidlen', '')
            # custom_attributes["{}.{}.{}".format("responded_ssid_map", str(responded_ssid_map.index(item)),"dot11.advertisedssid.cloaked")] = item.get('dot11.advertisedssid.cloaked', '')
            # custom_attributes["{}.{}.{}".format("responded_ssid_map", str(responded_ssid_map.index(item)), "dot11.advertisedssid.ccx_txpower")] = item.get('dot11.advertisedssid.ccx_txpower', '')
            # custom_attributes["{}.{}.{}".format("responded_ssid_map", str(responded_ssid_map.index(item)), "dot11.advertisedssid.cisco_client_mfp")] = item.get('dot11.advertisedssid.cisco_client_mfp', '')
            # custom_attributes["{}.{}.{}".format("responded_ssid_map", str(responded_ssid_map.index(item)), "dot11.advertisedssid.dot11e_qbss")] = item.get('dot11.advertisedssid.dot11e_qbss', '')
            # custom_attributes["{}.{}.{}".format("responded_ssid_map", str(responded_ssid_map.index(item)), "dot11.advertisedssid.probe_response")] = item.get('dot11.advertisedssid.probe_response', '')
            # custom_attributes["{}.{}.{}".format("responded_ssid_map", str(responded_ssid_map.index(item)), "dot11.advertisedssid.wps_uuid_e")] = item.get('dot11.advertisedssid.wps_uuid_e', '')
            # custom_attributes["{}.{}.{}".format("responded_ssid_map", str(responded_ssid_map.index(item)), "dot11.advertisedssid.ht_center_1")] = item.get('dot11.advertisedssid.ht_center_1', '')
            # custom_attributes["{}.{}.{}".format("responded_ssid_map", str(responded_ssid_map.index(item)), "dot11.advertisedssid.maxrate")] = item.get('dot11.advertisedssid.maxrate', '')
            # custom_attributes["{}.{}.{}".format("responded_ssid_map", str(responded_ssid_map.index(item)), "dot11.advertisedssid.beacon")] = item.get('dot11.advertisedssid.beacon', '')
            # custom_attributes["{}.{}.{}".format("responded_ssid_map", str(responded_ssid_map.index(item)), "dot11.advertisedssid.ietag_checksum")] = item.get('dot11.advertisedssid.ietag_checksum', '')
            # custom_attributes["{}.{}.{}".format("responded_ssid_map", str(responded_ssid_map.index(item)), "dot11.advertisedssid.ht_center_2")] = item.get('dot11.advertisedssid.ht_center_2', '')
            # custom_attributes["{}.{}.{}".format("responded_ssid_map", str(responded_ssid_map.index(item)), "dot11.advertisedssid.wps_model_name")] = item.get('dot11.advertisedssid.wps_model_name', '')
            # custom_attributes["{}.{}.{}".format("responded_ssid_map", str(responded_ssid_map.index(item)), "dot11.advertisedssid.ssid_hash")] = item.get('dot11.advertisedssid.ssid_hash', '')
            # custom_attributes["{}.{}.{}".format("responded_ssid_map", str(responded_ssid_map.index(item)), "dot11.advertisedssid.ht_mode")] = item.get('dot11.advertisedssid.ht_mode', '')
            # custom_attributes["{}.{}.{}".format("responded_ssid_map", str(responded_ssid_map.index(item)), "dot11.advertisedssid.wps_manuf")] = item.get('dot11.advertisedssid.wps_manuf', '')
            # custom_attributes["{}.{}.{}".format("responded_ssid_map", str(responded_ssid_map.index(item)),)] = item.get('dot11.advertisedssid.first_time', '')
            # custom_attributes["{}.{}.{}".format("responded_ssid_map", str(responded_ssid_map.index(item)),)] = item.get('dot11.advertisedssid.beaconrate', '')
            # custom_attributes["{}.{}.{}".format("responded_ssid_map", str(responded_ssid_map.index(item)),)] = item.get('dot11.advertisedssid.dot11e_channel_utilization_perc', '')
            # custom_attributes["{}.{}.{}".format("responded_ssid_map", str(responded_ssid_map.index(item)),)] = item.get('dot11.advertisedssid.crypt_set', '')
            # custom_attributes["{}.{}.{}".format("responded_ssid_map", str(responded_ssid_map.index(item)),)] = item.get('dot11.advertisedssid.wpa_mfp_supported', '')
            # custom_attributes["{}.{}.{}".format("responded_ssid_map", str(responded_ssid_map.index(item)),)] = item.get('dot11.advertisedssid.last_time', '')
            # custom_attributes["{}.{}.{}".format("responded_ssid_map", str(responded_ssid_map.index(item)),)] = item.get('dot11.advertisedssid.dot11e_qbss_stations', '')
            # custom_attributes["{}.{}.{}".format("responded_ssid_map", str(responded_ssid_map.index(item)),)] = item.get('dot11.advertisedssid.wps_version', '')
            # custom_attributes["{}.{}.{}".format("responded_ssid_map", str(responded_ssid_map.index(item)),)] = item.get('dot11.advertisedssid.dot11r_mobility_domain_id', '')
            # custom_attributes["{}.{}.{}".format("responded_ssid_map", str(responded_ssid_map.index(item)),)] = item.get('dot11.advertisedssid.ssid', '')
            # custom_attributes["{}.{}.{}".format("responded_ssid_map", str(responded_ssid_map.index(item)),)] = item.get('dot11.advertisedssid.wps_config_methods', '')
            # custom_attributes["{}.{}.{}".format("responded_ssid_map", str(responded_ssid_map.index(item)),)] = item.get('dot11.advertisedssid.beacons_sec', '')
            # custom_attributes["{}.{}.{}".format("responded_ssid_map", str(responded_ssid_map.index(item)),)] = item.get('dot11.advertisedssid.wps_state', '')
            # custom_attributes["{}.{}.{}".format("responded_ssid_map", str(responded_ssid_map.index(item)),)] = item.get('dot11.advertisedssid.wpa_mfp_required', '')
            # custom_attributes["{}.{}.{}".format("responded_ssid_map", str(responded_ssid_map.index(item)),)] = item.get('dot11.advertisedssid.channel', '')
            # custom_attributes["{}.{}.{}".format("responded_ssid_map", str(responded_ssid_map.index(item)),)] = item.get('dot11.advertisedssid.wps_serial_number', '')
            # custom_attributes["{}.{}.{}".format("responded_ssid_map", str(responded_ssid_map.index(item)),)] = item.get('dot11.advertisedssid.wps_device_name', '')
            # custom_attributes["{}.{}.{}".format("responded_ssid_map", str(responded_ssid_map.index(item)),)] = item.get('dot11.advertisedssid.dot11r_mobility', '')
            # custom_attributes["{}.{}.{}".format("responded_ssid_map", str(responded_ssid_map.index(item)),)] = item.get('dot11.advertisedssid.wps_model_number', '')

        # Map Kismet associated SSID map
        # advertised_ssid_map = dot11_device.get('dot11.device.advertised_ssid_map', [])
        # for item in advertised_ssid_map:


        

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
                deviceType=device_type,
                manufacturer=manufacturer,
                networkInterfaces=[network],
                customAttributes=custom_attributes
            )
        )
    print(custom_attributes)
    # return assets_import

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
    # assign Kismet cookie from kwargs
    cookie = kwargs['access_secret']

    # get assets
    assets = []
    #url = '{}/{}-{}/{}'.format(KISMET_BASE_URL, 'devices/views/seenby', KISMET_PHY, 'devices.json')
    url = '{}/{}'.format(KISMET_BASE_URL, 'devices/last-time/-60/devices.json')
    cookie = '{}={}'.format('KISMET', cookie)
    assets = http_get(url, headers={'Cookie': cookie, 'Content-Type': 'application/json', 'Accept': 'application/json'})
    if assets.status_code != 200:
        print('failed to retrieve assets' + str(assets))
        return None

    assets_json = json_decode(assets.body)

    # build asset import
    assets_import = build_assets(assets_json)
    if not assets_import:
         print('no assets')
    
    return assets_import