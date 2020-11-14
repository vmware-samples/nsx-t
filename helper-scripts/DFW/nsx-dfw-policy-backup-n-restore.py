#!/usr/bin/env python
# Requires Python 3.x
# Summary: Script to GET PER VM DFW rules programmed in the datapath.
# Usecase: Helps to monitor rules against supported rule per vnic (4K).

################################################################################
import requests
from requests.auth import HTTPBasicAuth
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import argparse
import re

################################################################################
###  Define Arguments for the script.
################################################################################

parser = argparse.ArgumentParser(description='NSX DFW Policy Backup & Restore- DFW Policies, Groups, Services & Profiles ')
parser.add_argument('--nsx-mgr-ip', dest="ip",
                   help="NSX Manager IP", required=True)
parser.add_argument('--operation', dest="operation",
                   help="What operation - backup or restore", required=True)
parser.add_argument('--user', dest="user",
                   help="NSX Username, default: admin",
                   default="admin", required=False)
parser.add_argument('--password', dest="password",
                   help="NSX Password, default: Admin!23Admin",
                   default="Admin!23Admin", required=False)
parser.add_argument('--backupfile', dest="backupfile",
                   help=" DFW Policy Backup File name, default: nsx-dfw-backup.json",
                   default="nsx-dfw-backup.json", required=False)
args = parser.parse_args()

################################################################################
###  REST API function using python "requests" module
################################################################################
def rest_api_call (method, endpoint, data=None, ip=args.ip, user=args.user, password=args.password):
    url = "https://%s%s" % (ip, endpoint)
    # To remove ssl-warnings bug. even with cert verification is set as false
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    headers = {'Content-Type': 'application/json'}
    res = requests.request(
        method=method,
        url=url,
        auth=HTTPBasicAuth(user, password),
        headers=headers,
        data=data,
        verify=False
    )
    try:
        res.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise e
    if len(res.content) > 0:
        response = res.json()
        return response

################################################################################
###  Backup NSX VM Tags, and save as json file (VM Name, Tags, Instance UUID)
################################################################################

def backup_nsx_dfw_policy(backupfile: str):
    # Send API Request to NSX Manager to get DFW Policy inventory
    #endpoint = "/policy/api/v1/infra?base_path=/infra/domains/default&type_filter=SecurityPolicy;Group"
    endpoint = "/policy/api/v1/infra?filter=Type-Domain|SecurityPolicy|Rule|Group"
    res = rest_api_call(method= 'GET', endpoint = endpoint)
    with open(backupfile, 'w') as bkdata:
        # Save the resonse dictionary in python to a json file.
        # Use option indent to save json in more readable format
        json.dump(res, bkdata, indent=4)
    print("\n      >>> NSX DFW Policy Backup completed and saved as [%s]. Backup includes DFW policy, Rules & Groups.\n" % backupfile)
    #  To Count number of Security Policy, Rules & Groups
    #  Open DFW backup file
    f = open(backupfile, "r")
    lines = f.readlines()
    f.close()
    # Count pattern "ChildSecurityPolicy" for Total Policy Count
    search_for_policy = 'ChildSecurityPolicy'
    # Count pattern "Rule_id for Total Policy Count
    search_for_rule = 'rule_id'
    # Count pattern "ChildGroup" for Total Policy Count
    search_for_group = 'ChildGroup'
    # Intialize counter variable
    pcount, rcount, gcount = 0, 0, 0
    for line in lines:
        line = line.strip().lower().split()
        for words in line:
            if words.find(search_for_policy.lower()) != -1:
                pcount +=1
        for words in line:
            if words.find(search_for_rule.lower()) != -1:
                rcount +=1
        for words in line:
            if words.find(search_for_group.lower()) != -1:
                gcount +=1
    print("      >>> NSX DFW Config Summary: %s Policy, %s Rules, %s Group\n" % (pcount, rcount, gcount))

################################################################################
### Run "backup" or "restore" nsx-vm-tag based on user input to "--operation"
################################################################################
if __name__ == "__main__":
    backup_nsx_dfw_policy(args.backupfile)
