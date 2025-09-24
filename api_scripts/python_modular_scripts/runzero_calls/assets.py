import json
import pandas as pd
import requests

def get_assets(url, token, filter=" ", fields=" "):
    '''
        Retrieve assets using supplied query filter from Console and restrict to fields supplied.
        
        :param url: A string, URL of runZero console.
        :param token: A string, Export API Key.
        :param filter: A string, query to filter returned assets(" " returns all).
        :param fields: A string, comma separated string of fields to return(" " returns all).
        :returns: a dict, JSON object of assets.
        :raises: ConnectionError: if unable to successfully make GET request to console.
    '''

    url = f"{url}/api/v1.0/export/org/assets.json"
    params = {'search': filter,
              'fields': fields}
    payload = ''
    headers = {'Accept': 'application/json',
               'Authorization': f'Bearer {token}'}
    try:
        response = requests.get(url, headers=headers, params=params, data=payload)
        if response.status_code != 200:
            return ('Unable to retrieve assets' + str(response))
        content = response.content
        data = json.loads(content)
        return data
    except ConnectionError as error:
        content = "No Response"
        raise error