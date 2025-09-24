# Retrieve all export keys from an account token
def get_keys(account_token):
    url = RUNZERO_BASE_URL + '/api/v1.0/account/keys'
    headers = {'Accept': 'application/json',
               'Authorization': 'Bearer ' + account_token}
    response = http_get(url, headers=headers)
    if response.status_code != 200:
        print('Unable to retrieve keys ' + str(response))
        return None
    content = json_decode(response.body)
    export_keys = [item.get('token') for item in content if item.get('type') == 'export']
    return export_keys 