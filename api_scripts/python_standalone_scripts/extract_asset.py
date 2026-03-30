""" EXAMPLE PYTHON SCRIPT! NOT INTENDED FOR PRODUCTION USE! 
    extract_asset.py, version 0.2
    Extract an asset from runZero scan data provided one or more IP addresses."""

import argparse
import gzip
import logging
import os

logger = logging.getLogger(__name__)

def parseArgs():
    parser = argparse.ArgumentParser(description="Extract asset from runZero scan data.")
    parser.add_argument('-f', '--file', help='filename of runZero scan data (gzip), including path, to extract asset from.', 
                        required=True)
    parser.add_argument('-a', '--addresses', help='Comma separated list of IP address(es) (no spaces) of lines to extract.', required=True)
    parser.add_argument('-o', '--output', help='filename, including path, of output file.', required=True)
    parser.add_argument('-l', '--log', help='Path to write log file. This argument will take priority over the .env file', 
                        required=False, default=os.environ["LOG_PATH"])
    parser.add_argument('--version', action='version', version='%(prog)s 0.2')
    return parser.parse_args()

def open_file(filename):
    logger.info(f"Opening {filename}.")
    try:
        with gzip.open( filename, 'rt') as input:
            data = input.readlines()
            return data
    except IOError:
        logger.exception(f"Could not read input file: {filename}, exiting...")
        exit()
    

def extract_asset(ip_list, data):
    addresses = ip_list.split(',')
    print(addresses)
    asset = []
    for ip in addresses:
        logger.info(f"Extracting {ip} from data.")
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
        logger.info(f"Writing {filename} to disk.")
        with open( filename, 'w') as o:
                    o.writelines(contents)
        logger.info(f"{filename} successfully written to disk.")
    except IOError:
        logger.exception("Could not write output file, exiting...")
        exit()
    
if __name__ == "__main__":
    args = parseArgs()
    logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%a, %d %b %Y %H:%M:%S', filename=f'{args.log}/extract_asset.log', level=logging.INFO)
    logger.info('Started')
    data = open_file(args.file)
    results = extract_asset(args.addresses, data)
    write_file(args.output, results)
    logger.info('Finished.')
