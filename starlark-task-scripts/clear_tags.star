load('json', json_encode='encode', json_decode='decode')
load('http', http_get='get', http_patch='patch', http_post='post', 'url_encode')

RUNZERO_BASE_URL = 'https://console.runzero.com'
RUNZERO_REDIRECT = 'https://console.runzero.com/'
QUERY = 'something' # Replace with query to filter assets for tag removal

def clear_tags(token, query=QUERY):
    url = RUNZERO_BASE_URL + '/api/v1.0/org/assets/bulk/clearTags'
    headers = {'Content-Type': 'application/json',
               'Authorization': 'Bearer ' + token}
    payload = json_encode({"search": query})
    response = http_post(url, headers=headers, body=bytes(url_encode(payload)))
    if response.status_code != 200:
        print('Unable to clear tags from ' + query + str(response))
        return None
    content = json_decode(response.body)
    print('cleared tags from assets matching ' + query)

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
        clear_tags(token)
        