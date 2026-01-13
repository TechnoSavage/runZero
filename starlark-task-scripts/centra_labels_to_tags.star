# This script is a functional extension of the Guardicore Centra integration found here: https://github.com/TechnoSavage/runZero/tree/main/sdk-starlark-integrations/Akamai_Guardicore_Centra

load('json', json_encode='encode', json_decode='decode')
load('http', http_get='get', http_patch='patch', http_post='post', 'url_encode')

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

def get_assets(token, oid, query='custom_integration:centra', fields='id, foreign_attributes'):
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
    
def get_centra_labels(data):
    assetList = []
    for item in data:
        asset = {}
        asset['id'] = item.get('id')
        asset['tags'] = item.get('foreign_attributes', {}).get('@centra.custom', {}).get('labels', '')
        assetList.append(asset)
    return(assetList)
    
def parse_labels(token, asset_list):
    for asset in asset_list:
        tags = asset.get('tags', None)
        if tags:
            assignment = assign_owner(token, asset['id'], tags)

def apply_tags(token, asset_id, tags):
    url = RUNZERO_BASE_URL + '/api/v1.0/org/assets/' + asset_id + '/tags'
    headers = {'Content-Type': 'application/json',
               'Authorization': 'Bearer ' + token}
    tag_string = ''        
    for tag in tags:
        split_tag = tag.split(':').strip()
        reformat = split_tag[0] + '=' + split_tag[1]
        tag_string = tag_string + ' ' + reformat
    payload = json_encode({"tags": tag_string.lstrip()})
    response = http_patch(url, headers=headers, body=bytes(url_encode(payload)))
    if response.status_code != 200:
        print('Unable to apply tags to ' + asset_id + str(response))
        return None
    content = json_decode(response.body)
    print('assigned tags ' + tag_string + ' to asset ' + asset_id)

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
    if token:
        org_ids = get_orgs(token)
        for oid in org_ids:
            assets = get_assets(token, oid)
            labels = get_centra_labels(assets)
            assignment = apply_tags(token, labels, asset_id)