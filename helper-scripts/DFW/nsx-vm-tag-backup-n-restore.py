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
# Summary: Script to backup NSX VM Tags and restore it based on Instance UUID.
# Usecase:To re-assign NSX VM tags to VMware SRM recovered VM's on another site.
# HOW: VMware SRM preserves the Instance UUID between protected and recovery VM.
#      NSX uses this VM Instance-UUID for tag backup and re-assigning.
# Usage: python3 nsx-vm-tag-backup-n-restore.py
#                              --nsx-mgr-ip <ip>
#                              --operation [backup|restore]
#                              [--user <usr>]
#                              [--password <pwd>]
#                              [--backupfile <name>]
################################################################################

import requests
from requests.auth import HTTPBasicAuth
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import argparse

################################################################################
###  Define Arguments for the script.
################################################################################

parser = argparse.ArgumentParser(description='NSX VM Tag Backup & Restore Script')
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
parser.add_argument('--backupfile', dest="backupfile",
                   help="NSX VM Tag Backup File Name, default: nsx-vm-tag-bkup.json",
                   default="nsx-vm-tag-bkup.json", required=False)

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

def backup_nsx_vm_tags(backupfile):
    # Send API Request to NSX Manager to get VM inventory
    endpoint = "/api/v1/fabric/virtual-machines"
    res = rest_api_call(method= 'GET', endpoint = endpoint)
    # Serialize/Encode Response dict into JSON String format.
    # Need this conversion for write operation below
    backup_data = json.dumps(res["results"], indent=4)
    #  Open NSX VM Inventory backup file for 'write'
    with open(backupfile, 'w') as bkdata:
        bkdata.write(backup_data)
    print("NSX VM Tag Backup file: [%s]" % backupfile)

################################################################################
###  Restore NSX VM Tags from Backup based on Instance UUID/External ID
################################################################################

def restore_nsx_vm_tags(backupfile):
    # 'Read' JSON encoded data from backup file and convert to python dict
    with open(backupfile, 'r') as bkdata:
        backup_data = json.load(bkdata)
    # NSX API for Add VM Tag based on External_id
    endpoint = "/api/v1/fabric/virtual-machines?action=add_tags"
    for vm in backup_data:
        #If Tag exists for a VM in backup,then use UUID to restore the tag(s)
        if "tags" in vm:
            body = {
               "external_id": vm["external_id"],
               "tags": vm["tags"]
            }
            # Convert body to JSON string, as module needs the body as string.
            body = json.dumps(body)
            try:
                rest_api_call(method='POST', endpoint = endpoint, data=body)
                print("SUCCESS - NSX Tag Restore for VM %s: %s %s"
                      %(vm["display_name"],
                      vm["external_id"],
                      vm["tags"]))
            # Add Tag may fail if VM (UUID) does't exists in restored nsx
            except Exception as ex:
                # Convert JSON.output into python.dic
                err_res_cont = json.loads(ex.response.content)
                # Grep error_message to identify issue
                err_msg = err_res_cont["error_message"]
                print("FAILURE - NSX Tag Restore for VM %s: %s with [%s]"
                         %(vm["display_name"],
                           vm["external_id"],
                           err_msg)
                      )
        # If no Tag exists for a VM (UUID) in backup,ignore those VM for restore
        else:
            print ("No NSX Tag exists for VM %s: %s" %
                               (vm["display_name"], vm["external_id"]))

################################################################################
### Run "backup" or "restore" nsx-vm-tag based on user input to "--operation"
################################################################################

if __name__ == "__main__":
    if "backup" in args.operation:
        backup_nsx_vm_tags(args.backupfile)
    if "restore" in args.operation:
        restore_nsx_vm_tags(args.backupfile)

################################################################################
"""
Script RUN Output:

Backup NSX VM Tag:

    bhatg@bhatg-a02 DFW % python nsx-vm-tag-backup-n-restore.py --nsx-mgr-ip 10.114.208.136 --operation backup
    NSX VM Tag Backup file: [nsx-vm-tag-bkup.json]
    bhatg@bhatg-a02 DFW %


Restore NSX VM Tag:

    bhatg@bhatg-a02 DFW % python nsx-vm-tag-backup-n-restore.py --nsx-mgr-ip 10.114.208.136 --operation restore
    FAILURE - NSX Tag Restore for VM DEV-MRS-APP-01: 9990df46-2a81-4a9f-c4f3-2e180ea2bc23 with [The requested object : VirtualMachineContainer/9990df46-2a81-4a9f-c4f3-2e180ea2bc23 could not be found. Object identifiers are case sensitive.]
    SUCCESS - NSX Tag Restore for VM DEV-MRS-DB-01: 502df3a3-96a4-f494-6e55-8485c1bd052c []
    SUCCESS - NSX Tag Restore for VM DEV-MRS-WEB-01: 50205fa9-47fb-488a-a3e3-c5e079fdd432 [{u'scope': u'prod-dmz', u'tag': u'app-2-web'}]
    No NSX Tag exists for VM ESX-MGMT-EDGE-01: 5020e5a4-19e1-1fa6-1e2d-6ac61af4eab4
    SUCCESS - NSX Tag Restore for VM PROD-MRS-APP-01: 50209b5f-cdb7-43de-abbb-8d0ef5bbca99 [{u'scope': u'', u'tag': u'abc'}]
    SUCCESS - NSX Tag Restore for VM PROD-MRS-DB-01: 502092e1-11b7-10d3-56c5-e0da4687b5d2 [{u'scope': u'PROD', u'tag': u'MRS-APP-DB'}, {u'scope': u'', u'tag': u'abc'}]
    SUCCESS - NSX Tag Restore for VM PROD-MRS-WEB-01: 50201b5c-ac3e-a725-d70a-86b2efadef05 [{u'scope': u'', u'tag': u'ganapathi'}, {u'scope': u'', u'tag': u'abc'}]
    No NSX Tag exists for VM SRM-TEST-01: 5020821f-d0b8-a4e1-0090-80f58a4e49eb
    No NSX Tag exists for VM dc02-nsx-mgr-a1.dg.corp.local: 50206e41-e423-a4f3-0ea5-4989a70b645d
    No NSX Tag exists for VM dc02-nsx-mgr-a2.dg.corp.local: 50208f44-e205-d2f5-1342-bfcdb81e7d84
    No NSX Tag exists for VM dc02-nsx-mgr-a3.dg.corp.local: 50208fbc-5b70-cb3a-e3c5-9f56df5af2ec
    No NSX Tag exists for VM nsx-edgevm-1: 50208357-8b18-28af-bfad-2b45fef388df
    No NSX Tag exists for VM nsx-edgevm-2: 5020147c-c94b-c173-9033-76161bd9a253
    No NSX Tag exists for VM nsx-edgevm-3: 50200c4b-0102-28f9-4b45-a6ae18b3df7f
    No NSX Tag exists for VM nsx-edgevm-4: 50205dff-15b5-d84c-87d7-fa3b0d81f4b3
    No NSX Tag exists for VM vcenter2.dg.vsphere.local: 520f8291-5339-6b37-b760-6af91710c9e4
    bhatg@bhatg-a02 DFW %

"""
