"""
EXAMPLE PYTHON SCRIPT! NOT INTENDED FOR PRODUCTION USE!
known_subnets_to_rfc1918_exclusions.py version 1.0
Fetch all site scopes and registered subnets across all orgs in an Account and apply them to a specific site exclusion list e.g. RFC1918 scan
"""
import ipaddress
import json
import os
import requests
from requests.exceptions import ConnectionError

#--------------------------------------------------------------------------------------------#
# Uncomment the following lines to read secrets from a .env file using pipenv and os.environ #
#--------------------------------------------------------------------------------------------#
# RUNZERO_BASE_URL = os.environ['RUNZERO_BASE_URL']
# ACCOUNT_API_TOKEN = os.environ['ACCOUNT_API_TOKEN']
# EXCLUSION_ORG_UUID = os.environ['EXCLUSION_ORG_UUID']
# EXCLUSION_SITE_UUID = os.environ['EXCLUSION_SITE_UUID']

# If using pipenv and os.environ, comment or delete the following 4 variables. Otherwise assign the necessary values
RUNZERO_BASE_URL = 'https://console.runzero.com'
ACCOUNT_API_TOKEN = ''
EXCLUSION_ORG_UUID = ''
EXCLUSION_SITE_UUID = ''

def get_sites(token):
    """ 
    Retrive all sites across all orgs in an account.
    
    :param token: A string, Accont API Key.
    :returns: A dict, JSON output.
    :raises: ConnectionError: if unable to successfully make GET request to console.
    """
    url = f"{RUNZERO_BASE_URL}/api/v1.0/account/sites"
    headers = {'Accept': 'application/json',
               'Authorization': f'Bearer {token}'}
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print('Unable to retrieve sites' + str(response))
            exit()
        content = response.content
        data = json.loads(content)
        return data
    except ConnectionError as error:
        content = "No Response"
        raise error
    
def extract_site_scopes(sites):
    """
    Extract site scope and subnets.

    :param sites: A list, list of site config dicts from the API.
    :returns: A list, list of scan targets from site configs
    """
    exclusion_list = []
    for site in sites:
        if site['id'] != EXCLUSION_SITE_UUID:
            #site scope includes individual IPs, domains, and ASNs that are defined as scan targets in the site
            if site['scope']:
                scope = site['scope'].split('\n')
                exclusion_list.extend(scope)
            #site subnets includes registered subnets for the site
            if site['subnets']:
                #subnets = [k for k, v in site['subnets'].items()]
                subnets = list(site['subnets'].keys())
                exclusion_list.extend(subnets)
    return exclusion_list

def parse_scopes(scopes):
    """
    Remove any non RFC1918 address ranges from site scope and subnet configurations
    
    :param scopes: A List, list of site scan targets.
    :returns: A List, list of domains and RFC1918 addresses and address ranges.
    """
    exclusions = ''
    for target in scopes:
        try:
            # Remove any CIDR notation or Subnet mask
            host = target.split('/')[0]
            # Check if the result is an IP address
            ip_check = ipaddress.ip_address(host)
            # Discard if not an IPv4 address
            if ip_check.version != 4:
                pass
            # Discard if not an RFC1918 v4 address
            if ip_check.is_private:
                exclusions = exclusions + target + ' '
        except ValueError:
            # If the target is not an IP address is would have to be a hostname, domain, or ASN so append to exclusions list
            exclusions = exclusions + target + ' '
    return exclusions

def patch_exclusions(token, exclusions):
    """ 
    Append to site exclusions.
    
    :param token: A string, Organization API Key.
    :param exclusions: A string, a string of space separated target exclusions.
    :returns: A dict, JSON output.
    :raises: ConnectionError: if unable to successfully make PATCH request to console.
    """

    url = f"{RUNZERO_BASE_URL}/api/v1.0/org/sites/{EXCLUSION_SITE_UUID}"
    params = {'_oid': EXCLUSION_ORG_UUID}
    payload = json.dumps({"excludes": exclusions})
    headers = {'Accept': 'application/json',
               'Authorization': f'Bearer {token}'}
    try:
        response = requests.patch(url, headers=headers, params=params, data=payload)
        content = response.content
        data = json.loads(content)
        return data
    except ConnectionError as error:
        content = "No Response"
        raise error

def main():
    sites = get_sites(ACCOUNT_API_TOKEN)
    scopes = extract_site_scopes(sites)
    exclusions = parse_scopes(scopes)
    patch_exclusions(ACCOUNT_API_TOKEN, exclusions)

if __name__ == "__main__":
    main()