#!/usr/bin/env python
"""
* *******************************************************
* Copyright (c) VMware, Inc. 2017. All Rights Reserved.
* SPDX-License-Identifier: BSD-2
* *******************************************************
*
* DISCLAIMER. THIS PROGRAM IS PROVIDED TO YOU "AS IS" WITHOUT
* WARRANTIES OR CONDITIONS OF ANY KIND, WHETHER ORAL OR WRITTEN,
* EXPRESS OR IMPLIED. THE AUTHOR SPECIFICALLY DISCLAIMS ANY IMPLIED
* WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY,
* NON-INFRINGEMENT AND FITNESS FOR A PARTICULAR PURPOSE.
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
