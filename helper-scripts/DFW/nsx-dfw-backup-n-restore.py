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
                   help="NSX Password, default: VMware!23VMware",
                   default="VMware!23VMware", required=False)
parser.add_argument('--backupfileprefix', dest="backupfileprefix",
                   help="Prefix backup file with- default nsx-dfw-<object-type>.json",
                   default="nsx", required=False)
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
###  Backup NSX DFW DFW L4 Services
################################################################################

def backup_nsx_dfw_services(backupfileprefix):
    backupfile = (backupfileprefix+'-services-bkup.json')
    # Send API Request to NSX Manager to get DFW Policy inventory
    #endpoint = "/policy/api/v1/infra?base_path=/infra/domains/default&type_filter=SecurityPolicy;Group"
    endpoint = "/policy/api/v1/infra?filter=Type-Service"
    res = rest_api_call(method= 'GET', endpoint = endpoint)
    with open(backupfile, 'w') as bkdata:
        # Save the resonse dictionary in python to a json file.
        # Use option indent to save json in more readable format
        json.dump(res, bkdata, indent=4)
    #  To Count number of Security Policy, Rules & Groups
    #  Open DFW backup file
    f = open(backupfile, "r")
    lines = f.readlines()
    f.close()
    print("\n   NSX DFW L4 services Backup saved as [%s]" % backupfile)

################################################################################
###  Backup NSX DFW L7 Profiles
################################################################################

def backup_nsx_dfw_context_profiles(backupfileprefix):
    backupfile = (backupfileprefix+'-context-profiles-bkup.json')
    # Send API Request to NSX Manager to get DFW Policy inventory
    #endpoint = "/policy/api/v1/infra?base_path=/infra/domains/default&type_filter=SecurityPolicy;Group"
    endpoint = "/policy/api/v1/infra?filter=Type-ContextProfile"
    res = rest_api_call(method= 'GET', endpoint = endpoint)
    with open(backupfile, 'w') as bkdata:
        # Save the resonse dictionary in python to a json file.
        # Use option indent to save json in more readable format
        json.dump(res, bkdata, indent=4)
    #  To Count number of Security Policy, Rules & Groups
    #  Open DFW backup file
    f = open(backupfile, "r")
    lines = f.readlines()
    f.close()
    print("\n   NSX DFW L7 context-profiles Backup saved as [%s]" % backupfile)

################################################################################
###  Backup NSX DFW Policy, Rules with GROUPS.
################################################################################

def backup_nsx_dfw_policy_n_group(backupfileprefix):
    backupfile = (backupfileprefix+'-policy-n-group-bkup.json')
    # Send API Request to NSX Manager to get DFW Policy inventory
    #endpoint = "/policy/api/v1/infra?base_path=/infra/domains/default&type_filter=SecurityPolicy;Group"
    endpoint = "/policy/api/v1/infra?filter=Type-Domain|SecurityPolicy|Rule|Group"
    res = rest_api_call(method= 'GET', endpoint = endpoint)
    with open(backupfile, 'w') as bkdata:
        # Save the resonse dictionary in python to a json file.
        # Use option indent to save json in more readable format
        json.dump(res, bkdata, indent=4)
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
    print("\n   NSX DFW Policy & Group Backup saved as [%s]" % backupfile)
    print("\n   NSX DFW Backup has %s Policy, %s Rules, %s Group\n" % (pcount, rcount, gcount))

################################################################################
###  Restore NSX DFW L4 Services
################################################################################

def restore_nsx_dfw_services(backupfileprefix):
    backupfile = (backupfileprefix+'-services-bkup.json')
    # 'Read' JSON encoded data from backup file and convert to python dict
    with open(backupfile, 'r') as bkdata:
        backup_data = json.load(bkdata)
    # NSX API to send entire L4 Services config in one PATCH call with backupfile as body
    endpoint = "/policy/api/v1/infra"
    # Convert body to JSON string, as module needs the body as string.
    body = json.dumps(backup_data)
    try:
        rest_api_call(method='PATCH', endpoint = endpoint, data=body)
        print("\n   SUCCESS - NSX DFW L4 Services")
    except Exception as ex:
        err_res_cont = json.loads(ex.response.content)
        # Grep error_message to identify issue
        err_msg = err_res_cont["error_message"]
        print("\n    FAILURE - NSX DFW L4 Services with error: [%s]\n" %(err_msg))

################################################################################
###  Restore NSX DFW L7 Context-Profile
################################################################################

def restore_nsx_dfw_context_profiles(backupfileprefix):
    backupfile = (backupfileprefix+'-context-profiles-bkup.json')
    # 'Read' JSON encoded data from backup file and convert to python dict
    with open(backupfile, 'r') as bkdata:
        backup_data = json.load(bkdata)
    # NSX API to send entire L4 Services config in one PATCH call with backupfile as body
    endpoint = "/policy/api/v1/infra"
    # Convert body to JSON string, as module needs the body as string.
    body = json.dumps(backup_data)
    try:
        rest_api_call(method='PATCH', endpoint = endpoint, data=body)
        print("\n   SUCCESS - NSX DFW L7 Services Restore")
    except Exception as ex:
        err_res_cont = json.loads(ex.response.content)
        # Grep error_message to identify issue
        err_msg = err_res_cont["error_message"]
        print("\n    FAILURE - NSX DFW L7 Services Restore with error: [%s]\n" %(err_msg))

################################################################################
###  Restore NSX DFW Policy, Rules with GROUPS.
################################################################################

def restore_nsx_dfw_policy_n_group(backupfileprefix):
    backupfile = (backupfileprefix+'-policy-n-group-bkup.json')
    # 'Read' JSON encoded data from backup file and convert to python dict
    with open(backupfile, 'r') as bkdata:
        backup_data = json.load(bkdata)
    # NSX API to send entire Policy And Group config in one PATCH call with backupfile as body
    endpoint = "/policy/api/v1/infra"
    # Convert body to JSON string, as module needs the body as string.
    body = json.dumps(backup_data)
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
    try:
        rest_api_call(method='PATCH', endpoint = endpoint, data=body)
        print("\n   SUCCESS - NSX DFW Policy & Group Restore: %s Policy, %s Rules, %s Group\n" % (pcount, rcount, gcount))
    except Exception as ex:
        err_res_cont = json.loads(ex.response.content)
        # Grep error_message to identify issue
        err_msg = err_res_cont["error_message"]
        print("\n    FAILURE - NSX DFW Policy & Group Restore with error: [%s]\n" %(err_msg))

################################################################################
### Run "backup" or "restore" DFW policy backup based on user input to "--operation"
################################################################################

if __name__ == "__main__":
    if "backup" in args.operation:
        backup_nsx_dfw_services(args.backupfileprefix)
        backup_nsx_dfw_context_profiles(args.backupfileprefix)
        backup_nsx_dfw_policy_n_group(args.backupfileprefix)
    if "restore" in args.operation:
        # Some Policy API bug with Service Patch call, so disabling this funtion for now
        #restore_nsx_dfw_services(args.backupfileprefix)
        restore_nsx_dfw_context_profiles(args.backupfileprefix)
        restore_nsx_dfw_policy_n_group(args.backupfileprefix)
