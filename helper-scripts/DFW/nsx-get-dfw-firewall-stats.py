#!/usr/bin/python

"""
NSX-T Sample Code
Copyright 2017-2020 VMware, Inc.  All rights reserved
The BSD-2 license (the "License") set forth below applies to all
parts of the NSX-T SDK Sample Code project.  You may not use this
file except in compliance with the License.
BSD-2 License
Redistribution and use in source and binary forms, with or
without modification, are permitted provided that the following
conditions are met:
    Redistributions of source code must retain the above
    copyright notice, this list of conditions and the
    following disclaimer.
    Redistributions in binary form must reproduce the above
    copyright notice, this list of conditions and the
    following disclaimer in the documentation and/or other
    materials provided with the distribution.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
"""

################################################################################
# Summary: Script to print all DFW rules which has a Zero (0) hit count
# Usage: python nsx-get-dfw-firewall-stats.py
#
# Note: The script prints the output on the stdout. By default, it only prints
#       the rule ID for rules which has a 0 hit count. To print all the rules
#       and its hit count, set DISPLAY_ALL_STATS to 1
# ##############################################################################

import re
import sys
import ssl
import json
import time
import paramiko
import textwrap
import argparse
import requests
import warnings

# Supress SSL warning
requests.packages.urllib3.disable_warnings()

# Supress SSH/Paramiko warnings
warnings.filterwarnings("ignore")

# Set to 1 to see all Rules and its stats
DISPLAY_ALL_STATS = 0

debug = 1
nsx_ip = "192.168.200.41"
headers = {
  # The authorization here is base64 encoding of the password
  'Authorization': 'Basic YWRtaW46bXlQYXNzd29yZDEhbXlQYXNzd29yZDEh',
  'Content-Type': 'application/json'
}

def log(msg):
    if (debug):
        print (msg)

def nsx_url(uri):
    return 'https://' + nsx_ip + ':443' + uri


def raiseError(r):
    print("Error: %s" % json.dumps(r.json(), indent=4, sort_keys=True))
    exit()


def get(uri):
    r = requests.get(nsx_url(uri), verify=False, headers=headers)
    if r.status_code != 200:
        raiseError(r)
    return r


# Main

r = get('/policy/api/v1/infra/domains/default/security-policies')
for policy in r.json()['results']:
    policy_name = policy['display_name']
    policy_id = policy['id']
    if (policy['category'] == "Ethernet"):
        continue
    uri ='/policy/api/v1/infra/domains/default/security-policies' + "/" + policy_id + "/statistics"
    res = get(uri)
    print ("Policy: " + policy_name)
    print ("  |")
    for stats in res.json()['results']:
        stat_res = stats['statistics']['results']
        used = 1
        for item in stat_res:
            rule_id = item['internal_rule_id']
            hit_count = item['hit_count']
            if (DISPLAY_ALL_STATS == 1):
                print ("  +-- Rule ID: " + rule_id + " Counter: " + str(hit_count))
                used = 0
            else:
                if (hit_count == 0):
                    print ("  +-- Rule ID: " + rule_id + " Counter: " + str(hit_count))
                    used = 0
    if (used == 1):
        print ("  +-- All rules used")
    print ("")

