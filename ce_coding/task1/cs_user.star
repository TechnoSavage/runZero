load('json', json_encode='encode', json_decode='decode')
load('http', http_get='get', http_patch='patch', http_post='post', 'url_encode')

RUNZERO_BASE_URL = 'https://console.runzero.com'
RUNZERO_REDIRECT = 'https://console.runzero.com/'

def get_orgs(account_token):
    url = RUNZERO_BASE_URL + '/api/v1.0/account/orgs'
    headers = {'Accept': 'application/json',
               'Authorization': 'Bearer ' + account_token}
    response = http_get(url, headers=headers)
    if response.status_code != 200:
        print('Unable to retrieve organizations ' + str(response))
        return None
    content = json_decode(response.body)
    org_ids = [org.get('id') for org in content if not org.get('project')]
    return org_ids  

def get_assets(token, oid, query='source:crowdstrike', fields='id, foreign_attributes'):
    url = RUNZERO_BASE_URL + '/api/v1.0/export/org/assets.json'
    headers = {'Accept': 'application/json',
               'Authorization': 'Bearer ' + token}
    params = {'search': query,
              'fields': fields,
              '_oid': oid}
    response = http_get(url, headers=headers, params=params)
    if response.status_code != 200:
        print('Unable to retrieve assets ' + str(response))
        return None
    content = json_decode(response.body)
    return content
    
def get_recent_user(data):
    assetList = []
    for item in data:
        asset = {}
        asset['id'] = item.get('id')
        asset['owner'] = item.get('foreign_attributes', {}).get('@crowdstrike.dev', {}).get('lastLoginUser', '')
        assetList.append(asset)
    return(assetList)
    
def parse_owners(token, asset_list, group_id):
    no_assign = [None, 'sshd', 'ssm-user', 'nt authority\anonymous logon', 'default group', 'developer']
    for asset in asset_list:
        reported_owner = asset.get('owner', None)
        if reported_owner in no_assign:
            pass
        else:
            assignment = assign_owner(token, asset['id'], reported_owner, group_id)

def assign_owner(token, asset_id, owner, group_id):
    url = RUNZERO_BASE_URL + '/api/v1.0/org/assets/' + asset_id + '/owners'
    headers = {'Content-Type': 'application/json',
               'Authorization': 'Bearer ' + token}
    payload = json_encode({"ownerships": [{"ownership_type_id": group_id, "owner": owner}]})
    response = http_patch(url, headers=headers, body=bytes(url_encode(payload)))
    if response.status_code != 200:
        print('Unable to add owner ' + str(response))
        return None
    content = json_decode(response.body)
    print('assigned ' + owner + ' in ownership group ' + group_id + ' to asset ' + asset_id)
        
def get_owner_groups(token):
    url = RUNZERO_BASE_URL + '/api/v1.0/account/assets/ownership-types'
    headers = {'Content-Type': 'application/json',
               'Authorization': 'Bearer ' + token}
    response = http_get(url, headers=headers)
    if response.status_code != 200:
        print('Unable to retrieve ownership types ' + str(response))
        return None
    content = json_decode(response.body)
    return content

def create_owner_group(token, group_name):
    url = RUNZERO_BASE_URL + '/api/v1.0/account/assets/ownership-types'
    headers = {'Content-Type': 'application/json',
               'Authorization': 'Bearer ' + token}
    payload =  {"name": group_name,
                "reference": 1,
                "order": 1,
                "hidden": 'false'}
    response = http_post(url, headers=headers, body=bytes(url_encode(payload)))
    if response.status_code != 200:
        print('Unable to create ownership type ' + str(response))
        return None
    content = json_decode(response.body)
    return content['id']

def get_token(client_id, client_secret):
    url = RUNZERO_BASE_URL + '/api/v1.0/account/api/token'
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'application/json'}
    payload = {'grant_type': 'client_credential',
            'client_id': client_id,
            'client_secret': client_secret}
    response = http_post(url, headers=headers, body=bytes(url_encode(payload)))
    if response.status_code != 200:
        print('Unable to retrieve Oauth2.0 token ' + str(response))
        return None
    content = json_decode(response.body)
    return content['access_token']

def main(*args, **kwargs):
    # Retrieve Oauth token
    client_id = kwargs['access_key']
    client_secret = kwargs['access_secret']
    token = get_token(client_id, client_secret)
    # Check for existence of Crowdstrike User ownership group; create if not found
    owner_groups = get_owner_groups(token)
    group_id = None
    for group in owner_groups:
        if group['name'] == 'Crowdstrike User':
            group_id = group['id']
    if not group_id:             
        group_id = create_owner_group(token, 'Crowdstrike User')
    org_ids = get_orgs(token)
    for oid in org_ids:
        assets = get_assets(token, oid)
        owners = get_recent_user(assets)
        assignment = parse_owners(token, owners, group_id)