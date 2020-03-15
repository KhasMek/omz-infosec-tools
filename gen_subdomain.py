#!/usr/bin/python3

"""
Read in a url, or file of urls and output a
cleaned and sorted list (or file) of subdomains.

Why? Well, you can then feed this list in for additional permutations (s3/azure/etc.)
for example.

TODO:
  -permutations removal needs some improvment with regards to:
    - speed
    - accuracy
"""

import argparse
import sys
import re
import threading
import tldextract


aws_regions = [
    "af-south-1",
    "ap-east-1",
    "ap-northeast-1",
    "ap-northeast-2",
    "ap-northeast-3",
    "ap-south-1",
    "ap-southeast-1",
    "ap-southeast-2",
    "ca-central-1",
    "cn-north-1",
    "cn-northwest-1",
    "eu-central-1",
    "eu-north-1",
    "eu-west-1",
    "eu-west-2",
    "eu-west-3",
    "me-south-1",
    "sa-east-1",
    "us-east-1",
    "us-east-2",
    "us-gov-east-1",
    "us-gov-west-1",
    "us-west-1",
    "us-west-2"
]


def parse_args(print_help=False):
    argparser = argparse.ArgumentParser(prog='gen_subdomain')
    argparser.add_argument('target_type', help='Type of query to perform. \
                           (default: %(default)s)', default='file',
                           choices=['file', 'single'])
    argparser.add_argument('target', help='Target url or file of urls')
    argparser.add_argument('-o', '--output', help='Name of output file.', default=None)
    argparser.add_argument('-rp', '--remove_permutations', help='Remove permutations' +
                           'referenced from specified file', default=None)
    args = argparser.parse_args()
    if print_help:
        return argparser.print_help()
    else:
        return args


def file_target(target):
    subdomains = set()
    try:
        with open(target, 'r') as infile:
            for line in infile:
                if line.strip():
                    sd = single_target(line)
                    subdomains.add(sd)
    except FileNotFoundError:
        print("  ERROR! {} is not a file".format(target))
        sys.exit(0)
    return subdomains


def build_permutation_dict(permutation_file):
    permutations = {'prefix': set(), 'suffix': set()}
    with open(permutation_file, 'r') as infile:
        for line in infile:
            line = line.rstrip()
            if re.match(r'^\w+(_|\W)|\w+(_|\W)?$', line):
                permutations['prefix'].add(line)
            elif re.match(r'^(_|\W)\w+|(_|\W)\w+?$', line):
                permutations['suffix'].add(line)
            elif re.match(r'^\w+|(_|\W)\w+', line):
                permutations['prefix'].add(line)
                permutations['suffix'].add(line)
            else:
                print(" [!] ERROR: {} doesn't match any cases!!!".format(line))
    return permutations


def clean_aws(subd):
    for r in aws_regions:
        if re.match(r'.*' + r, subd):
            subd = re.sub(r'' + r, '', subd)
            subd = re.sub(r'(_|\W)$', '', subd)
    return subd


def rm_permutations(subdomains_list, permutation_file):
    old_subdomains = subdomains_list
    new_subdomains = set()
    permutations = build_permutation_dict(permutation_file)
    for subd in old_subdomains:
        # or should clean_aws(subd) be here? hmmmm...
        for p in permutations['prefix']:
            t = re.sub(r'^' + p, '', subd)
            # \.s?3?$ is to remove dangling s3 remnants (., .s, .s3) from the list
            t = re.sub(r'\.s?3?$', '', t)
            new_subdomains.add(t)
        for p in permutations['suffix']:
            t = re.sub(r'^' + p, '', subd)
            t = re.sub(r'\.s?3?$', '', t)
            new_subdomains.add(t)
    return new_subdomains


def single_target(target):
    ext = tldextract.extract(target)
    subdomain = ext.subdomain
    return subdomain


def write_output(subdomains, output):
    with open(output, 'w') as outfile:
        for subdomain in subdomains:
            outfile.write("%s\n" % subdomain)


def main(target_type, target, remove_permutations=None, output=None):
    if 'file' in target_type:
        subdomain_list = file_target(target)
    elif 'single' in target_type:
        subdomain_list = [single_target(target)]
    print(" [-] Domains: {}".format(len(subdomain_list)))
    if remove_permutations:
        subdomain_list = [clean_aws(sd) for sd in subdomain_list]
        subdomain_list = rm_permutations(subdomain_list, remove_permutations)
        print(" [-] Domains after permutation cleanup: {}".format(len(subdomain_list)))
    if output:
        write_output(subdomain_list, output)
    print(" [+] Analysis Complete. Be sure to manually analyze the data before using." +
          "This is beta software and shows.")


if __name__ == "__main__":
    args = parse_args()
    main(args.target_type, args.target, args.remove_permutations, args.output)