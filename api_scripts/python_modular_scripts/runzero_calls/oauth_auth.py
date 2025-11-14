import json
import requests
from requests.exceptions import ConnectionError


def oauth_auth(url, client_id, client_secret):
    url = f'{url}/api/v1.0/account/api/token'
    headers = {'Accept': '*/*', 
               'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {'grant_type': 'client_credentials', 
               'client_id': client_id, 
               'client_secret': client_secret}
    try:
        response = requests.post(url, headers=headers, data=payload)
        if response.status_code != 200:
            print('Unable to authenticate' + str(response))
            exit()
        data = json.loads(response.content)
        token = data.get('access_token')
        if token:
            return token
        else:
            print('200 response but no access_token provided')
            return None
    except ConnectionError as error:
        content = "No Response"
        raise error
    