""" EXAMPLE PYTHON SCRIPT! NOT INTENDED FOR PRODUCTION USE! 
    remedyBMC.py, version 0.1 ."""

import os
import requests
import pandas as pd
from io import BytesIO
from requests.exceptions import ConnectionError

# Configure runZero variables
RUNZERO_BASE_URL = os.environ['RUNZERO_BASE_URL']
RUNZERO_EXPORT_TOKEN = os.environ['RUNZERO_EXPORT_TOKEN']

# Configure Remedy
REMEDY_BASE_URL = os.environ['REMEDY_BASE_URL'],
REMEDY_USERNAME = os.environ['REMEDY_USERNAME'],
REMEDY_PASSWORD = os.environ['REMEDY_PASSWORD'],
CSV_FILE_PATH = os.environ['CSV_FILE_PATH'],

def get_assets(url=RUNZERO_BASE_URL, token=RUNZERO_EXPORT_TOKEN, filter=" "):
    '''
    Retrieve assets using supplied query filter from Console and restrict to fields supplied.
        
        :param url: A string, URL of runZero console.
        :param token: A string, Export API Key.
        :param filter: A string, query to filter returned assets(" " returns all).
        :returns: bytes object, CSV export of assets.
        :raises: ConnectionError: if unable to successfully make GET request to console.
    '''

    url = f"{url}/api/v1.0/export/org/assets.csv"
    params = {'search': filter}
    payload = ''
    headers = {'Accept': 'application/json',
               'Authorization': f'Bearer {token}'}
    try:
        response = requests.get(url, headers=headers, params=params, data=payload)
        response.raise_for_status()
        content = response.content
        return content
    except ConnectionError as error:
        content = "No Response"
        raise error
    
def map_assets(runzero_asset_csv):
    '''
    Map runZero CSV export fields to Remedy BMC import fields
        
        :param runzero_asset_csv: A bytes object, runZero CSV export response from API.
        :returns: None.
    '''
    #Read runZero export into pandas data frame
    runzero_df = pd.read_csv(BytesIO(runzero_asset_csv))
    remedy_df = pd.DataFrame(columns=['Name',
                                      'AssetTag',
                                      'SerialNumber',
                                      'Description',
                                      'AssetLifecycleStatus',
                                      'ProductCategorization1',
                                      'Manufacturer',
                                      'Model'])
    remedy_df['Name'] = runzero_df['hostname']
    remedy_df['AssetTag'] = runzero_df['tags']
    remedy_df['SerialNumber'] = runzero_df['serialNumbers']
    remedy_df['Description'] = runzero_df['comments']
    remedy_df['AssetLifecycleStatus'] = runzero_df['eol_os']
    remedy_df['ProductCategorization1'] = runzero_df['type']
    remedy_df['Manufacturer'] = runzero_df['newest_mac_vendor']
    remedy_df['Model'] = runzero_df['hw']
    remedy_df.to_csv(f"{CSV_FILE_PATH}/runZero_asset_update.csv", na_rep='')
    
def get_auth_token():
    '''
    Get authentication token from Remedy BMC.

    :returns: a sring, Remedy JWT token.
    :raises: ConnectionError: if unable to successfully make POST request to Remedy.
    '''
    try:
        response = requests.post(f"{REMEDY_BASE_URL}/jwt/login", json={
            "username": REMEDY_USERNAME,
            "password": REMEDY_PASSWORD
        })
        response.raise_for_status()
        return response.text
    except ConnectionError as error:
        content = "No Response"
        raise error
    
def upload_csv(token):
    '''
    Upload the CSV file to Remedy for batch processing.

    :param runzero_asset_csv: A bytes object, runZero CSV export response from API.
    :returns: None
    :raises: ConnectionError: if unable to successfully make POST request to Remedy.
    '''
    url = f"{REMEDY_BASE_URL}/import/csv"
    headers = {
        "Authorization": f"AR-JWT {token}"
    }
    files = {"file": open(f"{CSV_FILE_PATH}/runzero_asset_update.csv", "rb")}
    try:
        response = requests.post(url, headers=headers, files=files)
        response.raise_for_status()
        job_id = response.json().get("jobId")
        print(f"CSV uploaded successfully. Job ID: {job_id}")
    except ConnectionError as error:
        content = "No Response"
        raise error
    
def clean_up():
    '''
    Remove CSV file created by map_assets function.

        :returns None: this function returns nothing but removes files from disk.
        :raises: IOerror, if unable to delete file.
    '''

    try:
        os.remove(f"{CSV_FILE_PATH}/runzero_asset_update.csv")
    except IOError as error:
        raise error
    
def main():
    # Retrieve asset csv from runZero
    runzero_asset_csv = get_assets()
    # Perform mapping to Remedy import
    map_assets(runzero_asset_csv)
    # Retrieve Remedy JWT
    token = get_auth_token
    # Upload asset csv to Remedy
    upload_csv(token)
    # Cleanup written CSV
    clean_up()

if __name__ == "__main__":
    main()