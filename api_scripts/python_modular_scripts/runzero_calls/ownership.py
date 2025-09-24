import json
import requests

def assign_owner(url, token, id, owner, owner_type):
    '''
        Assign supplied owner name to asset ID under given owner_type.
        
        :param url: A string, URL of runZero console.
        :param token: A string, Organization API Key.
        :param id: A string, UUID of asset.
        :param owner: A string, name of asset owner.
        :param owner_type: A string, UUID of ownership type.
        :returns: a dict, JSON object of assets.
        :raises: ConnectionError: if unable to successfully make PATCH request to console.
    '''
    
    url = f"{url}/api/v1.0/org/assets/{id}/owners"
    payload = json.dumps({"ownerships": [{"ownership_type_id": owner_type, "owner": owner}]})
    headers = {'Content-Type': 'application/json',
               'Authorization': f'Bearer {token}'}
    try:
        response = requests.patch(url, headers=headers, data=payload)
        if response.status_code != 200:
            print('Unable to add owner' + str(response))
            exit()
        content = response.content
        data = json.loads(content)
        return data
    except ConnectionError as error:
        content = "No Response"
        raise error