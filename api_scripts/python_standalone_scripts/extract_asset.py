""" EXAMPLE PYTHON SCRIPT! NOT INTENDED FOR PRODUCTION USE! 
    extract_asset.py, version 0.1
    Extract an asset from runZero scan data provided one or more IP addresses."""

import argparse
import gzip

def parseArgs():
    parser = argparse.ArgumentParser(description="Extract asset from runZero scan data.")
    parser.add_argument('-f', '--file', help='filename of runZero scan data (gzip), including path, to extract asset from.', 
                        required=True)
    parser.add_argument('-a', '--addresses', help='Comma separated list of IP address(es) (no spaces) of lines to extract.', required=True)
    parser.add_argument('-o', '--output', help='filename, including path, of output file.', required=True)
    parser.add_argument('--version', action='version', version='%(prog)s 0.1')
    return parser.parse_args()

def open_file(filename):
    with gzip.open( filename, 'rt') as input:
        data = input.readlines()
        return data

def extract_asset(ip_list, data):
    addresses = ip_list.split(',')
    print(addresses)
    asset = []
    for ip in addresses:
        for line in data:
            if ip in line:
                asset.append(line)
    return asset

def write_file(filename, contents):
    '''
        Write contents to output file. 
    
        :param fileName: a string, name for file including (optionally) file extension.
        :param contents: anything, file contents.
        :raises: IOError: if unable to write to file.
    '''

    try:
        with open( filename, 'w') as o:
                    o.writelines(contents)
    except IOError as error:
        raise error
    
def main():
    args = parseArgs()
    data = open_file(args.file)
    results = extract_asset(args.addresses, data)
    write_file(args.output, results)

if __name__ == "__main__":
    main()