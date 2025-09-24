import json
import requests

def nessus(url, token, siteID, scan, name, description=""):
    '''
        Upload a .nessus scan file . 
    
        :param url: A string, URL of the runZero console.
        :param token: A string, Organization API key
        :param siteID: A string, the site ID of the Site to apply scan to.
        :param scan: A .nessus file, Nessus scan file to upload (including path).
        :param name: A string, a name for the import task.
        :param description: A string, a description for the import task.
        :returns: Dict Object, JSON formatted.
        :raises: ConnectionError: if unable to successfully make PUT request to console.
    '''

    url = f"{url}/api/v1.0/org/sites/{siteID}/import/nessus"
    params = {'name': name,
              'description': description}
    payload = ""
    file = [('application/octet-stream',(scan,open(scan,'rb'),'application/octet-stream'))]
    headers = {'Accept': 'application/octet-stream',
               'Authorization': f'Bearer {token}'}
    try:
        response = requests.put(url, headers=headers, params=params, data=payload, files=file)
        code = response.status_code
        content = response.content
        data = json.loads(content)
        return(code, data)
    except ConnectionError as error:
        raise error
    
def pcap(url, token, siteID, capture, name, description=""):
    '''
        Upload a capture file . 
    
        :param url: A string, URL of the runZero console.
        :param token: A string, Organization API key
        :param siteID: A string, the site ID of the Site to upload to.
        :param capture: A capture file, packet capture file to upload (including path).
        :param name: A string, a name for the import task.
        :param description: A string, a description for the import task.
        :returns: Dict Object, JSON formatted.
        :raises: ConnectionError: if unable to successfully make PUT request to console.
    '''
    
    url = f"{url}/api/v1.0/org/sites/{siteID}/import/packet"
    # params are currently ignored and PCAP API import does not support name and descripiton
    # retaining expecting that scan import params will be carried over to PCAP import as it doesn't hurt anything
    params = {'name': name,
              'description': description}
    headers = {'Accept': 'application/octet-stream',
               'Authorization': f'Bearer {token}'}
    try:
        with open(capture, 'rb') as file:
            response = requests.put(url, headers=headers, params=params, data=file, stream=True)
        code = response.status_code
        content = response.content
        data = json.loads(content)
        return(code, data)
    except ConnectionError as error:
        raise error
    
def scan(url, token, site_id, scan, name, description=""):
    '''
        Upload task Data to console.

        :param url: A string, URL of the runZero console.
        :param token: a string, Organization API key.
        :param site_id: A string, UUID of site to upload scan to.
        :param scan: A string, filename of the scan data (json.gz) file.
        :param name: A string, a name for the import task.
        :param description: A string, a description for the import task.
        :raises: ConnectionError: if unable to successfully make PUT request to console.
    '''
    
    url = f"{url}/api/v1.0/org/sites/{site_id}/import"
    params = {'name': name,
              'description': description}
    headers = {'Content-Type': 'application/octet-stream',
               'Content-Encoding': 'gzip',
               'Authorization': f'Bearer {token}'}
    try:
        with open(scan, 'rb') as file:
            response = requests.put(url, params=params, headers=headers, data=file, stream=True)
        code = response.status_code
        content = response.content
        data = json.loads(content)
        return(code, data)
    except ConnectionError as error:
        content = "No Response"
        raise error