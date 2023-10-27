""" EXAMPLE PYTHON SCRIPT! NOT INTENDED FOR PRODUCTION USE! 
    softwareAsset_dedupe.py, version 2.1
    This script is created with the intention of deduplicating assets by UUID after running a query
    in the software portion of the runZero asset inventory. Specifically, this script is intended 
    assist when a user wants to find all assets that do NOT have a specific application installed.
    This typically assumes the user has an integration that provides comprehensive software 
    inventory (such as Crowdstrike or SentinelOne) and when running a query such as 'source:sentinelone and not 
    product:"1password"' wishes to see only the assets missing the software. The query results will 
    show all assets without 1password but will also include multiple entries for each asset corresponding 
    to every other installed software product. This script will accept the JSON export from the resulting
    query and deduplicate assets by UUID to provide a list solely of the assets in question. """

import argparse
import json
import re
    
def parseArgs():
    parser = argparse.ArgumentParser(description="Deduplicate assets from runZero software inventory JSONl export.")
    parser.add_argument('-f', '--file', metavar='<path>filename', dest='fileName', help='jsonl file exported from console, including absolute path', required=True)
    parser.add_argument('--version', action='version', version='%(prog)s 2.1')
    return parser.parse_args()

def parseFile(inputFile):
    """ Read input file, parse contents and return list of JSON formatted
        assets. 
    
        :param inputFile: JSONl formatted file.    
        :raises: FileNotFoundError: if provided filename not found is not JSON formatted.
        :raises: JSONDecodeError: if content is not JSON formatted."""
    try:
        assetList = []
        with open (inputFile, 'r') as input:
            content = input.readlines()
            for line in content:
                line = json.loads(line)
                asset = {}
                for key, value in line.items():
                    if 'software' not in key:
                        asset[key] = line.get(key)
                count = 0
                for item in assetList:
                    if asset["id"] == item["id"]:
                        count += 1
                if count == 0: 
                    assetList.append(asset)        
        return assetList
    except FileNotFoundError as error:
        raise error
    except json.JSONDecodeError as error:
        raise error

def writeFile(fileName, contents):
    """ Write contents to output file. 
    
        :param filename: a string, name for file including (optionally) file extension.
        :param contents: anything, file contents.
        :raises: IOError: if unable to write to file. """
    try:
        with open( fileName, 'w') as fileName:
                    fileName.write(contents)
    except IOError as error:
        raise error
    
def main():
    args = parseArgs()
    delFileExt = re.match("[^.]*", args.fileName)
    outputName = f"{delFileExt[0]}_deduped.json"
    parsed = parseFile(args.fileName)
    writeFile(outputName, json.dumps(parsed))

if __name__ == "__main__":
    main()