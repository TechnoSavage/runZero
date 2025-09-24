import json
import requests

def get_oids(url, token):
    '''
        Retrieve Organizational IDs from Console.

           :param url: A string, URL of runZero console.
           :param token: A string, Account API Key.
           :returns: A JSON object, runZero Org data.
           :raises: ConnectionError: if unable to successfully make GET request to console.
    '''

    url = f"{url}/api/v1.0/account/orgs"
    payload = ""
    headers = {'Accept': 'application/json',
               'Authorization': f'Bearer {token}'}
    try:
        response = requests.get(url, headers=headers, data=payload)
        if response.status_code != 200:
            print('Unable to retrieve Organization IDs' + str(response))
            exit()
        content = response.content
        data = json.loads(content)
        return data
    except ConnectionError as error:
        content = "No Response"
        raise error

def create_org(url, token):
    """ Create an Organization or Project.

           :param token: A string, Account API Key.
           :returns: A JSON object, Successful creation or error.
           :raises: ConnectionError: if unable to successfully make PUT request to console. """

    url = f"{url}/api/v1.0/account/orgs"
    payload = json.dumps({"name": "Test Project",
                          "description": "Testing API Created Project",
                          "export_token": "",
                          "project": "true",
                          "parent_id": "73bf6aab-5ef0-4d68-8d84-206dd1657642",
                          "expiration_assets_stale": "365",
                          "expiration_assets_offline": "365",
                          "expiration_scans": "365"})
    headers = {'Accept': 'application/json',
               'Content-Type': 'application/json',
               'Authorization': f'Bearer {token}'}

    try:
        response = requests.put(url, headers=headers, data=payload)
        content = response.content
        data = json.loads(content)
        return data
    except ConnectionError as error:
        content = "No Response"
        raise error