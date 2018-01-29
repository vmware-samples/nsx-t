#!/usr/bin/env python
"""
"""

import argparse


def getargs():
    return get_arg_parser().parse_args()


def get_arg_parser():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-n', '--nsx_host', type=str, required=True,
                            help='NSX host to connect to')
    arg_parser.add_argument('-t', '--tcp_port', type=int, default=443,
                            help='TCP port for NSX server')
    arg_parser.add_argument('-u', '--user', type=str, default="admin",
                            help='User to authenticate as')
    arg_parser.add_argument('-p', '--password', type=str, required=True,
                            help='Password')
    return arg_parser
