#!/usr/bin/env python
# Requires Python 3.x
# Summary: Script to GET PER VM DFW rules programmed in the datapath.
# Usecase: Helps to monitor rules against supported rule scale limit per vnic (4K).
# Usage: python nsx-get-dfw-rules-per-vm.py [-h] --nsx-mgr-ip IP
#                                           [--user USER]
#                                           [--password PASSWORD]
#                                           [--aboverulelimitonly ABOVERULELIMITONLY]
#                                           [--fwrulelimit FWRULELIMIT]
# Caveat: This count is very close aproximaion to the rules in the datapath per VNIC with following caveat:
#         1) It also counts disabled rules.
#         2) If a rule has TCP & UDP services/ports together, e.g TCP {1,2,3} UDP (5,6}- Script counts as
#            one but datapath would have 2 rules") one with UDP & TCP port set.
#         3) If a rule has Multiple L7 Context-Profiles- Script counts as one but datapath would have N rules,
#            one for each of the L7 profile.
################################################################################


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

parser = argparse.ArgumentParser(description='Get per VM DFW rules programmed in the datapath')
parser.add_argument('--nsx-mgr-ip', dest="ip",
                   help="NSX Manager IP", required=True)
parser.add_argument('--user', dest="user",
                   help="NSX Username, default: admin",
                   default="admin", required=False)
parser.add_argument('--password', dest="password",
                   help="NSX Password, default: VMware!23VMware",
                   default="VMware!23VMware", required=False)
parser.add_argument('--aboverulelimitonly', dest="aboverulelimitonly",
                   help="-yes- Lists only VM Rule count above --fwrulelimit, -no- all VM",
                   default="no", required=False)
parser.add_argument('--fwrulelimit', dest="fwrulelimit", type=int,
                   help="VM's with rule above this limit, if --aboverulelimitdonly is used, default 100",
                   default="100", required=False)

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
###  Get All NSX Logical Ports. Includes all VM VNIC ports
################################################################################

def nsx_get_all_logical_ports():
    # Get All Logical ports
    endpoint = "/api/v1/logical-ports"
    res = rest_api_call(method= 'GET', endpoint = endpoint)
    # Python dict with List of Logicalport details
    lpdict = (res["results"])
    #print(lpdict)
    return lpdict

###############################################################################
###  Count NSX DFW Policy, Rules and GROUPS.
################################################################################
def nsx_dfw_policy_count():
    # Send API Request to NSX Manager to get DFW Policy inventory
    #endpoint = "/policy/api/v1/infra?base_path=/infra/domains/default&type_filter=SecurityPolicy;Group"
    endpoint = "/policy/api/v1/infra?filter=Type-Domain|SecurityPolicy|Rule|Group"
    res = rest_api_call(method= 'GET', endpoint = endpoint)
    tempfile = "tempfile.json"
    with open(tempfile, 'w') as bkdata:
        # Save the resonse dictionary in python to a json file.
        # Use option indent to save json in more readable format
        json.dump(res, bkdata, indent=4)
    #print("\n      >>> NSX DFW Policy Backup completed and saved as [%s]. Backup includes DFW policy, Rules & Groups.\n" % backupfile)
    #  To Count number of Security Policy, Rules & Groups
    #  Open DFW backup file
    #  To Count number of Security Policy, Rules & Groups
    #  Open DFW backup file
    f = open(tempfile, "r")
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
    print("\n    NSX Manager system wide DFW config summary: %s Policy, %s Rules, %s Group\n" % (pcount, rcount, gcount))

################################################################################
###  Get All NSX Logical Ports. Includes all VM VNIC ports
################################################################################

def nsx_get_dfw_rule_per_lport():
    nsx_dfw_policy_count()
    # Get All Logical ports
    res = nsx_get_all_logical_ports()
    # API to get FW Rule per logical port
    vmcrossrulelimit = {}
    lplist_abovelimit = []
    if "no" in (args.aboverulelimitonly):
        print("---------------------------------------------------------------------------------")
        print("                  Total NSX DFW datapath Rule Count per VM VNIC")
        print("          Counts only Rules based on Applied-To field for given VM VNIC")
        print(" Use applied-to to define scope of policy and to remove unrelated policy from VM")
        print("---------------------------------------------------------------------------------")
        print(" Rule-Count ------ VM-VNIC")
        for lp in res:
            lpname = lp["display_name"]
            if re.search("vmx@", lpname):
               rc = 0
               endpoint = ("/api/v1/firewall/sections?applied_tos=%s&deep_search=true" % lp["internal_id"])
               res = rest_api_call(method = 'GET', endpoint = endpoint)
               # Python dict with List of Logicalport details
               lpdict = (res["results"])
               for policy in lpdict:
                   rc = rc + policy["rule_count"]
               print("\t%s   --->  %s" % (rc,lp["display_name"]))
    if "yes" in (args.aboverulelimitonly):
        print("---------------------------------------------------------------------------------")
        print("                   VM-NIC having DFW Rules count above %s " % args.fwrulelimit)
        print("          Counts only Rules based on Applied-To field for given VM VNIC")
        print(" Use Applied-To to define scope of policy and to remove unrelated policy from VM")
        print("---------------------------------------------------------------------------------")
        print(" Rule-Count ------ VM-VNIC")
        for lp in res:
            lpname = lp["display_name"]
            if re.search("vmx@", lpname):
               rc = 0
               endpoint = ("/api/v1/firewall/sections?applied_tos=%s&deep_search=true" % lp["internal_id"])
               res = rest_api_call(method = 'GET', endpoint = endpoint)
               # Python dict with List of Logicalport details
               lpdict = (res["results"])
               for policy in lpdict:
                   rc = rc + policy["rule_count"]
               #print("\t%s   --->  %s" % (rc,lp["display_name"]))
               if rc >= (args.fwrulelimit):
                  #print("high scale")
                  print("\t%s   --->  %s" % (rc,lp["display_name"]))
    # This counts is very close approxmation with following caveat
    # 1) disabled rules on the rule table counted - if it is applied to that VM based on Applied-to.
    # 2) Does't account for rule exapantion due to Multiple Context Profiles in a single rule or TCP/UDP services together in a rule.
    print("-----------------------------------------------------------------------------------------------")
    print(" This count is very close aproximaion to the rules in the datapath per VNIC with following caveat:")
    print("1) It also counts disabled rules.")
    print("2) If a rule has TCP & UDP services/ports together, e.g TCP {1,2,3} UDP (5,6}- Script counts as one but datapath would have 2 rules")
    print("    one with UDP & TCP port set")
    print("3) If a rule has Multiple L7 Context-Profiles- Script counts as one but datapath would have N rules, one for each of the L7 profile")

################################################################################
### Get DFW Rule per VNIC
################################################################################

if __name__ == "__main__":
    nsx_get_dfw_rule_per_lport()
