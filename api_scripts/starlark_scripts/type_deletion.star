load('runzero.types', 'ImportAsset', 'NetworkInterface', 'Software')
load('json', json_encode='encode', json_decode='decode')
load('base64', base64_encode='encode', base64_decode='decode')
load('net', 'ip_address')
load('http', http_get='get', http_post='post', http_delete='delete', 'url_encode')
load('uuid', 'new_uuid')

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

def get_assets(export_token, oid, query='type:laptop or type:printer', fields='id'):
    url = RUNZERO_BASE_URL + '/api/v1.0/export/org/assets.json'
    headers = {'Accept': 'application/json',
               'Authorization': 'Bearer ' + export_token}
    params = {'search': query,
              'fields': fields,
              '_oid': oid}
    response = http_get(url, headers=headers, params=params)
    if response.status_code != 200:
        print('Unable to retrieve asset information ' + str(response))
        return None
    content = json_decode(response.body)
    asset_ids = [asset.get('id') for asset in content]
    return asset_ids

def delete_assets(account_token, asset_id, oid):
    url = RUNZERO_BASE_URL + '/api/v1.0/org/assets/' + asset_id
    headers = {'Accept': 'application/json',
               'Authorization': 'Bearer ' + account_token}
    params = {'asset_id': asset_id,
              '_oid': oid}
    response = http_delete(url, headers=headers, params=params)
    if response.status_code != 200:
        print('Unable to delete asset information ' + str(response))
        return None
    content = json_decode(response.body)
    print('removed asset ' + asset_id + ' response: ' + str(content))

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
    client_id = kwargs['access_key']
    client_secret = kwargs['access_secret']
    token = get_token(client_id, client_secret)
    org_ids = get_orgs(token)
    for oid in org_ids:
        asset_ids = get_assets(token, oid)
        for asset_id in asset_ids:
            delete_assets(token, asset_id, oid)
