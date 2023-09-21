""" EXAMPLE PYTHON SCRIPT! NOT INTENDED FOR PRODUCTION USE! 
    softwareAsset_dedupe.py, version 2.0
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
    parser.add_argument('--version', action='version', version='%(prog)s 2.0')
    return parser.parse_args()

def parseFile(inputFile):
    """ Read input file, parse contents and return list of JSON formatted
        assets. 
    
        :param inputFile: JSONl formatted file.    
        :raises: FileNotFoundError: if provided filename not found is not JSON formatted.
        :raises: JSONDecodeError: if content is not JSON formatted.
        :raises: KeyError: if key:value pair not present in file content. """
    try:
        assetList = []
        with open (inputFile, 'r') as input:
            content = input.readlines()
            for line in content:
                line = json.loads(line)
                asset = {}
                #add or remove asset attributes as needed
                asset["id"] = line["id"]
                asset["alive"] = line["alive"]
                asset["type"] = line["type"]
                asset["os_vendor"] = line["os_vendor"]
                asset["os_product"] = line["os_product"]
                asset["os_version"] = line["os_version"]
                asset["os"] = line["os"]
                asset["hw_vendor"] = line["hw_vendor"]
                asset["hw_product"] = line["hw_product"]
                asset["hw_version"] = line["hw_version"]
                asset["hw"] = line["hw"]
                asset["addresses"] = line["addresses"]
                asset["addresses_extra"] = line["addresses_extra"]
                asset["macs"] = line["macs"]
                asset["mac_vendors"] = line["mac_vendors"]
                asset["names"] = line["names"]
                asset["tags"] = line["tags"]
                asset["domains"] = line["domains"]
                asset["attributes"] = line["attributes"]
                asset["first_seen"] = line["first_seen"]
                asset["last_seen"] = line["last_seen"]
                asset["alive"] = line["alive"]
                asset["site_id"] = line["site_id"]
                asset["organization_id"] = line["organization_id"]
                asset["detected_by"] = line["detected_by"]
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
    except KeyError as error:
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