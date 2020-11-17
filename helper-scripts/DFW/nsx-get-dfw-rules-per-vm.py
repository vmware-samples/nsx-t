#!/usr/bin/env python
# Requires Python 3.x

"""
NSX-T SDK Sample Code
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



"""
Sample output of script:

bhatg@bhatg-a02 DFW % python nsx-get-dfw-rules-per-vm.py --nsx-mgr-ip 10.114.208.136

    NSX Manager system wide DFW config summary: 11 Policy, 34 Rules, 27 Group

---------------------------------------------------------------------------------
                  Total NSX DFW datapath Rule Count per VM VNIC
          Counts only Rules based on Applied-To field for given VM VNIC
 Use applied-to to define scope of policy and to remove unrelated policy from VM
---------------------------------------------------------------------------------
 Rule-Count ------ VM-VNIC
        23   --->  DC02-GOLDEN-IMAGE/DC02-GOLDEN-IMAGE.vmx@18a2b527-e79c-4bcf-98d0-1373a2970376
        23   --->  DC02-PROD-MRS-APP-01/DC02-PROD-MRS-APP-01.vmx@bb7b1e58-f5c7-4fe8-80bb-b123e39b07b8
        23   --->  DC02-PROD-MRS-APP-02/DC02-PROD-MRS-APP-02.vmx@18a2b527-e79c-4bcf-98d0-1373a2970376
        31   --->  DC02-PROD-MRS-DB-01/DC02-PROD-MRS-DB-01.vmx@18a2b527-e79c-4bcf-98d0-1373a2970376
        31   --->  DC02-PROD-MRS-WEB-01/DC02-PROD-MRS-WEB-01.vmx@18a2b527-e79c-4bcf-98d0-1373a2970376
        23   --->  DEV-MRS-WEB-01/DEV-MRS-WEB-01.vmx@bb7b1e58-f5c7-4fe8-80bb-b123e39b07b8
        19   --->  nsx-edgevm-1/nsx-edgevm-1.vmx@bdfcc848-2fd8-42c2-afb2-c53c79ef8c30
        19   --->  nsx-edgevm-2/nsx-edgevm-2.vmx@bdfcc848-2fd8-42c2-afb2-c53c79ef8c30
        19   --->  nsx-edgevm-3/nsx-edgevm-3.vmx@bdfcc848-2fd8-42c2-afb2-c53c79ef8c30
        19   --->  nsx-edgevm-3/nsx-edgevm-3.vmx@bdfcc848-2fd8-42c2-afb2-c53c79ef8c30
        19   --->  nsx-edgevm-3/nsx-edgevm-3.vmx@bdfcc848-2fd8-42c2-afb2-c53c79ef8c30
        19   --->  nsx-edgevm-4/nsx-edgevm-4.vmx@bdfcc848-2fd8-42c2-afb2-c53c79ef8c30
        19   --->  nsx-edgevm-4/nsx-edgevm-4.vmx@bdfcc848-2fd8-42c2-afb2-c53c79ef8c30
        23   --->  vcenter2.dg.vsphere.local/vcenter2.dg.vsphere.local.vmx@a8fc1054-3569-4c35-a07c-5f512c37a472
-----------------------------------------------------------------------------------------------
 This count is very close aproximaion to the rules in the datapath per VNIC with following caveat:
1) It also counts disabled rules.
2) If a rule has TCP & UDP services/ports together, e.g TCP {1,2,3} UDP (5,6}- Script counts as one but datapath would have 2 rules
    one with UDP & TCP port set
3) If a rule has Multiple L7 Context-Profiles- Script counts as one but datapath would have N rules, one for each of the L7 profile
bhatg@bhatg-a02 DFW %


bhatg@bhatg-a02 DFW % python nsx-get-dfw-rules-per-vm.py --nsx-mgr-ip 10.114.208.136 --aboverulelimitonly yes --fwrulelimit 20

    NSX Manager system wide DFW config summary: 11 Policy, 34 Rules, 27 Group

---------------------------------------------------------------------------------
                   VM-NIC having DFW Rules count above 20
          Counts only Rules based on Applied-To field for given VM VNIC
 Use Applied-To to define scope of policy and to remove unrelated policy from VM
---------------------------------------------------------------------------------
 Rule-Count ------ VM-VNIC
        23   --->  DC02-GOLDEN-IMAGE/DC02-GOLDEN-IMAGE.vmx@18a2b527-e79c-4bcf-98d0-1373a2970376
        23   --->  DC02-PROD-MRS-APP-01/DC02-PROD-MRS-APP-01.vmx@bb7b1e58-f5c7-4fe8-80bb-b123e39b07b8
        23   --->  DC02-PROD-MRS-APP-02/DC02-PROD-MRS-APP-02.vmx@18a2b527-e79c-4bcf-98d0-1373a2970376
        31   --->  DC02-PROD-MRS-DB-01/DC02-PROD-MRS-DB-01.vmx@18a2b527-e79c-4bcf-98d0-1373a2970376
        31   --->  DC02-PROD-MRS-WEB-01/DC02-PROD-MRS-WEB-01.vmx@18a2b527-e79c-4bcf-98d0-1373a2970376
        23   --->  DEV-MRS-WEB-01/DEV-MRS-WEB-01.vmx@bb7b1e58-f5c7-4fe8-80bb-b123e39b07b8
        23   --->  vcenter2.dg.vsphere.local/vcenter2.dg.vsphere.local.vmx@a8fc1054-3569-4c35-a07c-5f512c37a472
-----------------------------------------------------------------------------------------------
 This count is very close aproximaion to the rules in the datapath per VNIC with following caveat:
1) It also counts disabled rules.
2) If a rule has TCP & UDP services/ports together, e.g TCP {1,2,3} UDP (5,6}- Script counts as one but datapath would have 2 rules
    one with UDP & TCP port set
3) If a rule has Multiple L7 Context-Profiles- Script counts as one but datapath would have N rules, one for each of the L7 profile

"""
