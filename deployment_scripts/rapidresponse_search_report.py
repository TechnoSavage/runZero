""" EXAMPLE PYTHON SCRIPT! NOT INTENDED FOR PRODUCTION USE! 
    xxx.py, version 0.1
    This script is designed to extract Rapid Response queries from the runZero Blog RSS feed and run each query against a specified Organizations
    inventory. A report of queries and match counts will be generated, where match counts are greater than zero a dedicated report of asset matches
    will be generated for each query. """

import argparse
import datetime
import feedparser
import json
import os
import pandas as pd
import re
import requests
from getpass import getpass
from requests.exceptions import ConnectionError
    
def parseArgs():
    parser = argparse.ArgumentParser(description="Download scan data from the last 'N' processed tasks.")
    parser.add_argument('-r', '--range', help='Time range, from most recent to oldest, to check Rapid Response for queries. This argument will override the .env file', 
                        type=int, required=False, default=os.environ["TASK_NO"])
    parser.add_argument('-u', '--url', dest='consoleURL', help='URL of console. This argument will override the .env file', 
                        required=False, default=os.environ["RUNZERO_BASE_URL"])
    parser.add_argument('-k', '--key', dest='token', help='Prompt for Export API key (do not enter at command line). This argument will override the .env file', 
                        nargs='?', const=None, required=False, default=os.environ["RUNZERO_EXPORT_TOKEN"])
    parser.add_argument('-p', '--path', help='Path to save scan data to. This argument will override the .env file', 
                        required=False, default=os.environ["SAVE_PATH"])
    parser.add_argument('-o', '--output', dest='output', help='Output file format', choices=['txt', 'json', 'csv', 'html'], required=False)
    parser.add_argument('--version', action='version', version='%(prog)s 0.1')
    return parser.parse_args()

def rssFetch():
    '''
    Fetch RSS feed
    '''
    url = 'https://www.runzero.com/blog/index.xml'
    feed = feedparser.parse(url)
    return feed

def queryExtract(rssFeed):
    '''
    Extract queries from RR blogs
    '''
    # <a href=\"https://console.runzero.com/inventory\" target=\"_blank\">Asset Inventory</a>, use the following query to locate systems running potentially vulnerable software:</p>\n<pre><code>os:\"PAN-OS\"</code></pre>"
    dataSet = []
    for entry in rssFeed['entries']:
        blog = {}
        #rapidResponse = re.findall("<code>(.+)</code>", entry['content'][0]['value'])
        queries = re.findall("<code>(.+)</code>", entry['content'][0]['value'])
        if queries:
            blog['timestamp'] = entry['updated']
            blog['subject'] = entry['summary']
            # queries = re.findall("<a href=\"https://console.runzero.com/(inventory[/a-z|\"]+) target=.+</a>, .+</p>\n<pre><code>(.+)</code></pre>", entry['content'][0]['value']) # Doesn't work due to non-standard layout of RR queries
            inventory = re.findall("href=\"https://console.runzero.com/(inventory[/a-z|\"]+)", entry['content'][0]['value'])
            # build tuple sets for inventory and 
            blog['queries'] = queries
            dataSet.append(blog)
    return dataSet

def queryAssets(url, token, filter_list):
    '''
    compare queries to inventory.

        :param url: A string, URL of runZero console.
        :param token: A string, Export API Key.
        :param filter_list: A List, a list of filters to return assets.
        :returns: a dict, JSON object of assets.
    #     :raises: ConnectionError: if unable to successfully make GET request to console.
    '''
    for query in filter_list:
        url = f"{url}/api/v1.0/export/org/assets.json"
        params = {'search': filter,
                'fields': ''}
        payload = ''
        headers = {'Accept': 'application/json',
                'Authorization': f'Bearer {token}'}
        try:
            response = requests.get(url, headers=headers, params=params, data=payload)
            content = response.content
            data = json.loads(content)
            return data
        except ConnectionError as error:
            content = "No Response"
            raise error

def outputFormat(format, fileName, data):
    """ Determine output format and call function to write appropriate file.
        
        :param format: A String, the desired output format.
        :param fileName: A String, the filename, minus extension.
        :para data: json data, file contents
        :returns None: Calls another function to write the file or prints the output."""
    
    if format == 'json':
        fileName = f'{fileName}.json'
        writeFile(fileName, json.dumps(data))
    elif format == 'txt':
        fileName = f'{fileName}.txt'
        stringList = []
        for line in data:
            stringList.append(str(line).replace('{', '').replace('}', '').replace(': ', '='))
        textFile = '\n'.join(stringList)
        writeFile(fileName, textFile)
    elif format in ('csv', 'excel', 'html'):
        writeDF(format, fileName, data)  
    else:
        for line in data:
            print(json.dumps(line, indent=4))
    
def writeDF(format, fileName, data):
    """ Write contents to output file. 
    
        :param format: a string, excel, csv, or html
        :param fileName: a string, the filename, excluding extension.
        :param contents: json data, file contents.
        :raises: IOError: if unable to write to file."""
    
    df = pd.DataFrame(data)
    try:
        if format == "excel":
            df.to_excel(f'{fileName}.xlsx', freeze_panes=(1,0), na_rep='NA')
        elif format == 'csv':
            df.to_csv(f'{fileName}.csv', na_rep='NA')
        else:
            df.to_html(f'{fileName}.html', render_links=True, na_rep='NA')
    except IOError as error:
        raise error
    
def writeFile(fileName, contents):
    """ Write contents to output file in plaintext. 
    
        :param fileName: a string, name for file including (optionally) file extension.
        :param contents: anything, file contents.
        :raises: IOError: if unable to write to file. """
    try:
        with open( fileName, 'w') as o:
                    o.write(contents)
    except IOError as error:
        raise error

def main():
    args = parseArgs()
    token = args.token
    if token == None:
        token = getpass(prompt="Enter your Export API Key: ")
    fileName = f"{args.path}rapid_response_report_{str(datetime.datetime.now(datetime.timezone.utc))}"
    output = rssFetch()
    responseData = queryExtract(output)
    print(json.dumps(responseData, indent=4))
    # outputFormat(args.output, fileName, responseData)

if __name__ == "__main__":
    main()