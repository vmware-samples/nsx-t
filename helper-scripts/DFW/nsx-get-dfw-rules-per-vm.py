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

################################################################################
###  Get All NSX Logical Ports. Includes all VM VNIC ports
################################################################################

def nsx_get_dfw_rule_per_lport():
    # Get All Logical ports
    res = nsx_get_all_logical_ports()
    # API to get FW Rule per logical port
    vmcrossrulelimit = {}
    lplist_abovelimit = []
    if "no" in (args.aboverulelimitonly):
        print("---------------------------------------------------------------------------------")
        print("                  Total NSX DFW datapath Rule Count per VM VNIC")
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
               print("\t%s   --->  %s" % (rc,lp["display_name"]))
    if "yes" in (args.aboverulelimitonly):
        print("---------------------------------------------------------------------------------")
        print("                   VM-NIC having DFW Rules count above %s " % args.fwrulelimit)
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

################################################################################
### Get DFW Rule per VNIC
################################################################################

if __name__ == "__main__":
    nsx_get_dfw_rule_per_lport()
