#!/usr/bin/python3

"""
TODO:
- support formats like 192.0.2.8[0-5]
"""

import argparse
import ipcalc
import sys

from colorama import init, Fore, Back, Style
from texttable import Texttable

# Initialize colorama
init(autoreset=True)

table = Texttable()
table2 = Texttable()


def parse_args(print_help=False):
    argparser = argparse.ArgumentParser(prog='ip_calc')
    argparser.add_argument('type', help='Type of query to perform. \
                           (default: %(default)s)', default='summary',
                           choices=['summary', 'range', 'isitin'])
    argparser.add_argument('target', help='Target ip address, range or subnet')
    argparser.add_argument('-n', '--netblock', help='Netblock to look up for ' +
                           'isitin function')
    args = argparser.parse_args()
    if print_help:
        return argparser.print_help()
    else:
        return args


def summary(subnet):
    for query in subnet:
        table.set_chars(['', '', '', ''])
        table.set_cols_width([15, 20])
        table.set_deco(Texttable.BORDER)
        table.add_row(["Query:", query])
        query = ipcalc.Network(query)
        table.add_row(["Subnet ID:", str(query.network())])
        table.add_row(["Broadcast:", str(query.broadcast())])
        table.add_row(["Netmask:", str(query.netmask())])
        # TODO: Fix when it's a single IP
        table.add_row(["Usable IP's:", str(query.size() - 2)])
        table.add_row(["IP Version:", str(query.version())])
        table.add_row(["Information:", str(query.info())])
        print(Style.BRIGHT + Fore.CYAN + table.draw())
        table.reset()


def range(subnet):
    print('woo')
    for query in subnet:
        summary([query])
        table2.set_cols_align(["c", "c"])
        table2.set_cols_valign(["m", "m"])
        table2.set_cols_width([15, 15])
        table2.header(['Subnet', 'Host Address'])
        ips = ""
        for ip in ipcalc.Network(query):
            ips += str(ip) + "\n"
        row = query, ips
        table2.add_row(row)
        print(Fore.CYAN + table2.draw())
        table2.reset()
        print("\n")


def isitin(net, key):
    result = ipcalc.Network(net).has_key(key)
    if result == True:
        print("\n" + Fore.GREEN + "  True: " + key + " is in the " + net + " Subnet!")
    else:
        print("\n" + Fore.RED + "  FALSE: " + key + " is not in the " + net + " Subnet!")


if __name__ == "__main__":
    args = parse_args()
    if args.type == 'summary':
        summary([args.target])
    if args.type == "range":
        range([args.target])
    if args.type == "isitin":
        key = args.target
        net = args.netblock
        isitin(net, key)
