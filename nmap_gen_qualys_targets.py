#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# TODO
# - [ ] Add help functions to parser, etc
# - [ ] Modify to pull all up hosts from nmapP and all hosts with open Ports on rest

import argparse
import ipcalc
import os
import time
import xml.etree.ElementTree as ET
from libnmap.parser import NmapParser
from libnmap.objects import NmapReport
 # print "Nmap scan summary: {0}".format(nmap_report.commandline)
from xml.etree.ElementTree import ParseError

_files_to_parse = []
_broadcast = []
_subnetid = []
_up_hosts = []


def parse_options():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-i', '--input', default='./')
    argparser.add_argument('-o', '--output', default='../qualys_targets')
    argparser.add_argument( '-s', '--subnets-file', default='../targets')
    args = argparser.parse_args()
    # I can set these as globals, or just break all this out of a function.
    # Unsure which sounds better to me right now.
    global _input
    global _output
    global _subnets_file
    _input = args.input
    _output = args.output
    _subnets_file = args.subnets_file

def do_not_scan():
    for line in open(_subnets_file, 'r'):
        _subnet = ipcalc.Network(line.rstrip())
        _subnetid.append(str(_subnet.network()))
        _broadcast.append(str(_subnet.broadcast()))

def validate_xml():
    for file in os.listdir(_input):
        try:
            _tree = ET.parse(file)
            _files_to_parse.append(file)
        except ParseError:
            # File is not a xml or is malformed xml
            pass
        except IOError:
            # File is a directory
            pass

def parse_live_hosts():
    for xml in _files_to_parse:
        print(xml)
        if 'nmap-P-' in xml:
            xml = NmapParser.parse_fromfile(xml)
            for _host in xml.hosts:
                if _host.is_up():
                    _up_hosts.append(_host.address)
        else:
            xml = NmapParser.parse_fromfile(xml)
            for _host in xml.hosts:
                if _host.services:
                    _up_hosts.append(_host.address)

def file_exists_check():
    if os.path.isfile(_output):
        _output_bak = str(int(time.time()))
        os.rename(_output, _output + '-' + _output_bak)

def write_live_hosts():
    global _up_hosts
    _test_up_hosts = list(set(_up_hosts))
    _scan_targets = list(set(_up_hosts) - set(_broadcast) - set(_subnetid))
    _newline = ''
    for _scan_target in sorted(_scan_targets):
        with open(_output, 'a') as results:
            results.write(_newline + _scan_target)
            _newline = ',\n'


parse_options()
file_exists_check()
do_not_scan()
validate_xml()
parse_live_hosts()
write_live_hosts()
