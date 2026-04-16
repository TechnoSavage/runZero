load('http', http_get='get', http_post='post', 'url_encode')
load('json', json_encode='encode', json_decode='decode')
load('net', 'ip_address')
load('runzero.types', 'ImportAsset', 'NetworkInterface', 'Vulnerability')
load('time', 'parse_time')
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
                custom_attributes['product' + str(list.index(product)) + k] = v

        # Retrive and map vulnerabilities
        vulns = []
        findings = get_findings(asset_id, company_id, token)
        for finding in findings:
            vuln = build_vuln(finding)
            vulns.append(vuln)
            

        # Build assets for import
        assets_import.append(
            ImportAsset(
                id=asset_id,
                tags=tags,
                networkInterfaces=interfaces,
                customAttributes=custom_attributes,
                vulnerabilities=vulns
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

def build_vuln(vuln):
    ref = vuln.get()
    identifier = vuln.get('identifier', '')
    # cve_id = vuln.get('identifier', '')
    # name = vuln.get()
    # if identifier == '' or identifier == None:
        # identifier = name
    # description = vuln.get()
    # if description:
        # description = description[:1023]
    service_address = vuln.get()
    if service_address:
        service_address = ip_address(service_address)
    service_port = int(vuln.get('details', {}).get('src_port', 0))
    # service_transport = vuln.get()
    first_detected_timestamp = vuln.get('first_seen', '')
    if first_detected_timestamp:
        first_detected_timestamp = parse_time(first_detected_timestamp).unix
    #exploitability = detail.get('')
    #if not exploitability:
        #exploitability = detail.get('')
    #exploitable = True if float(exploitability) >= 5.0 else False
    cvss2_base_score = vuln.get('check_cvss', '')
    if cvss2_base_score:
        cvss2_base_score = float(cvss2_base_score)
    #cvss3_base_score = detail.get('')
    #if cvss3_base_score:
        #cvss3_base_score = float(cvss3_base_score)
    # risk_score = detail.get()
    # risk_rank = detail.get()
    severity_score = vuln.get('severity', '')
    if severity_score:
        severity_score = float(severity_score)
        if severity_score >= 0.1 and severity_score <=3.9:
            risk_rank = 1
        elif severity_score >= 4.0 and severity_score <=6.9:
            risk_rank = 2
        elif severity_score >= 7.0 and severity_score <= 8.9:
            risk_rank = 3
        elif severity_score >= 9.0 and severity_score <= 10.0:
            risk_rank = 4
        else:
            risk_rank = 0
    remediation = vuln.get('remediation', [])
    solutions = []
    for solution in remediation:
        title = solution.get('message', '')
        text = solution.get('help_text', '')
        solutions.append(title + ': ' + text)
    solution = solutions.join()
    solution = solution[:1023]

    # Map custom attributes
    affects_rating = str(vuln.get('affects_rating', ''))
    evidence_key = vuln.get('evidence_key', '')
    pcap_id = vuln.get('pcap_id', '')
    remaining_decay = vuln.get('remaining_decay', '')
    remediated = vuln.get('remediated', '')

    custom_attrs = {
                    'affectsRating': affects_rating,
                    'evidenceKey': evidence_key,
                    'pcapId': pcap_id,
                    'remainingDecay': remaining_decay,
                    'remediated': remediated 
                    }

    attributed_companies = vuln.get('attributed_companies', [])
    for company in attributed_companies:
        for k, v in company.items():
            custom_attributes['attributedCompanies' + str(list.index(company)) + k] = v
    
    # if cve_id:
    #     return Vulnerability(id=identifier,
    #                         cve=cve_id,
    #                         name=name,
    #                         description=description,
    #                         firstDetectedTS=first_detected_timestamp,
    #                         serviceAddress=service_address,
    #                         servicePort=service_port,
    #                         serviceTransport=service_transport,
    #                         #exploitable=exploitable,
    #                         cvss2BaseScore=cvss2_base_score,
    #                         #cvss3BaseScore=cvss3_base_score,
    #                         riskRank=risk_rank,
    #                         severityScore=severity_score,
    #                         # severityRank=severity_rank,
    #                         solution=solution,
    #                         customAttributes=custom_attributes
    #                         )
    # else:
    return Vulnerability(id=identifier,
                        #name=name,
                        #description=description,
                        firstDetectedTS=first_detected_timestamp,
                        serviceAddress=service_address,
                        servicePort=service_port,
                        #serviceTransport=service_transport,
                        #exploitable=exploitable,
                        cvss2BaseScore=cvss2_base_score,
                        #cvss3BaseScore=cvss3_base_score,
                        riskRank=risk_rank,
                        # severityScore=severity_score,
                        # severityRank=severity_rank,
                        solution=solution,
                        customAttributes=custom_attributes
                        )

def get_assets(company_id, token):
    assets_all = []
    total_count = 10000
    url = BITSIGHT_BASE_URL + '/ratings/v1/companies/' + company_id + '/assets?'
    headers = {'Accept': 'application/json',
                    'Authorization': 'Bearer ' + token}
    params = {}
    
    while len(assets_all) < total_count - 1:
        response = http_get(url, headers=headers, params=params)
        if response.status_code != 200:
            print('failed to retrieve assets', 'status code: ' + str(response.status_code))
            break
        else:
            data = json_decode(response.body)
            url = data.get('links', {}).get('next', '')
            total_count = data.get('count', 1)
            assets = data.get('results', [])
            assets_all.extend(assets)    

    return assets_all

def get_findings(asset_id, company_id, token):
    vulns_all = []
    vulns_count = 10000
    url = BITSIGHT_BASE_URL + '/ratings/v1/companies/' + company_id + '/findings?'
    headers = {'Accept': 'application/json',
                    'Authorization': 'Bearer ' + token}
    params = {'asset': asset_id}

    while len(vulns_all) < total_count - 1:
        response = http_get(url, headers=headers, params=params)
        if response.status_code != 200:
            print('failed to retrieve findings', 'status code: ' + str(response.status_code))
            break
        else:
            data = json_decode(response.body)
            url = data.get('links', {}).get('next', '')
            total_count = data.get('count', 1)
            findings = data.get('results', [])
            vulns_all.extend(findings)    

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