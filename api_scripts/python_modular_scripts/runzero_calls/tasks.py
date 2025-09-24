import json
import requests
    
def tasks(url, token, type=None, status=None): 
    '''
        Retrieve Tasks from Organization corresponding to supplied token.

        :param url: A string, URL of the runZero console.
        :param type: A string, the type of scan task(s) to download.
        :param token: A string, Account API Key.
        :returns: A JSON object, runZero task data.
        :raises: ConnectionError: if unable to successfully make GET request to console.
    '''
    
    url = f"{url}/api/v1.0/org/tasks"
    params = {}
    if type:
        params['search'] = type
    if status:
        params['status'] = status
    headers = {'Accept': 'application/json',
               'Authorization': f'Bearer {token}'}
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            print('Unable to retrieve tasks' + str(response))
            exit()
        content = response.content
        data = json.loads(content)
        return data
    except ConnectionError as error:
        raise error
    
def data(url, token, task_id, path):
    '''
        Download and write task data (.json.gz) for each task ID provided.

        :param url: A string, URL of the runZero console.
        :param token: A string, Organization API key.
        :param taskID: A string, UUID of scan task to download.
        :param path: A string, path to write files to.
        :returns: None, this function returns no data but writes files to disk.
        :raises: ConnectionError: if unable to successfully make GET request to console.
        :raises: IOError: if unable to write file.
    '''

    url = f"{url}/api/v1.0/org/tasks/{task_id}/data"
    payload = ""
    headers = {'Accept': 'application/json',
               'Authorization': f'Bearer {token}'}
    try:
        response = requests.get(url, headers=headers, data=payload, stream=True)
        if response.status_code != 200:
            print('Unable to retrieve task data' + str(response))
            exit()
        with open( f'{path}scan_{task_id}.json.gz', 'wb') as f:
            for chunk in response.iter_content(chunk_size=128):
                f.write(chunk)
    except ConnectionError as error:
        raise error
    except IOError as error:
        raise error

# replace so arg is a dict of scan configuraion
def new_scan(url, token, site_id, explorer, target_list, name, description, rate): 
    '''
        Create new scan task.
           
        :param url: A string, URL of the runZero console.
        :param token: A string, Organization API Key.
        :param siteID: A string, UID of site to scan.
        :param explorer: A string, UID of explorer.
        :param targetList: A list, list of scan targets.
        :param name: A string, name for scan task.
        :param description: A string, description for scan task.
        :param rate: A string, scan rate (packets per second).
        :returns: A JSON object, scan creation results.
        :raises: ConnectionError: if unable to successfully make PUT request to console.
    '''
    
    url = f"{url}/api/v1.0/org/sites/{site_id}/scan"
    payload = json.dumps({"targets": ', '.join(target_list),
               "excludes": "string",
               "scan-name": name,
               "scan-description": description,
               "scan-frequency": "once",
               "scan-start": "0",
               "scan-tags": "",
               "scan-grace-period": "4",
               "agent": explorer,
               "rate": rate,
               "max-host-rate": "40",
               "passes": "3",
               "max-attempts": "3",
               "max-sockets": "500",
               "max-group-size": "4096",
               "max-ttl": "255",
               "tcp-ports": "1-1000,5000-6000",
               "tcp-excludes": "9500",
               "screenshots": "true",
               "nameservers": "8.8.8.8",
               "subnet-ping": "true",
               "subnet-ping-net-size": "256",
               "subnet-ping-sample-rate": "3",
               "host-ping": "false",
               "probes": "arp,bacnet,connect,dns,echo,ike,ipmi,mdns,memcache,mssql,natpmp,netbios,pca,rdns,rpcbind,sip,snmp,ssdp,syn,ubnt,wlan-list,wsd"})
    headers = {'Accept': 'application/json',
               'Content-Type': 'application/json',
               'Authorization': f'Bearer {token}'}
    try:
        response = requests.put(url, headers=headers, data=payload)
        if response.status_code != 200:
            print('Unable to create task' + str(response))
            exit()
        content = response.content
        data = json.loads(content)
        return data
    except ConnectionError as error:
        content = "No Response"
        raise error