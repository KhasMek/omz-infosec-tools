#!/usr/bin/python3
#
# Quick script to print list of targets/ports to verify.
# At this point it's inteded to be run from the Phase-1
# directory and will output it's results in the parent
# directory.

import argparse
import csv
import os
import xml.etree.ElementTree as ET

from collections import defaultdict
from libnmap.parser import NmapParser
from xml.etree.ElementTree import ParseError


def parse_args(print_help=False):
    argparser = argparse.ArgumentParser(prog='ip_calc')
    argparser.add_argument('-i', help='Path to the file or directory to parse \
                           (default: %(default)s)', default='./')
    argparser.add_argument('-o', help='Path to outfile (default: %(default)s)',
                           default='nmap_port_targets.csv')
    args = argparser.parse_args()
    if print_help:
        return argparser.print_help()
    else:
        return args


def check_in(input):
    infiles = []
    if os.path.isdir(input):
        print(" Input path is directory")
        for file in os.listdir(input):
            infiles.append(file)
    elif os.path.isfile(input):
        print(" Input path is a file")
        infiles.append(infiles)
    else:
        print(" Unknown input!")
    return infiles


def validate_xml(infiles):
    files_to_parse = []
    for file in infiles:
        try:
            ET.parse(file)
            files_to_parse.append(file)
        except ParseError:
            # File is not a xml or is malformed xml
            print(" {} is malformed or not a nmap xml".format(file))
            pass
        except IOError:
            # File is a directory
            pass
    return files_to_parse


def parse_live_hosts(files_to_parse):
    targets = defaultdict(list)
    for xml in files_to_parse:
        infile = NmapParser.parse_fromfile(xml)
        for _host in infile.hosts:
            if _host.services:
                _address = _host.address
                for s in _host.services:
                    targets[_host.address].append(s.port)
    return targets


def write_csv(targets, outfile):
    with open(outfile, 'w') as f:
        writer = csv.writer(f)
        for k,v in targets.items():
            writer.writerow([k] + v)
    print(" CSV file written to {}".format(outfile))


if __name__ == "__main__":
    args = parse_args()
    infiles = check_in(args.i)
    files_to_parse = validate_xml(infiles)
    port_targets = parse_live_hosts(files_to_parse)
    write_csv(port_targets, args.o)
