#!/usr/bin/env python
# Requires Python 3.x
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
def rest_api_call (ip, method, endpoint, data, user, password):
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

def backup_nsx_vm_tags(ip: str, user: str, password: str, backupfile: str):
    # Send API Request to NSX Manager to get VM inventory
    endpoint = "/api/v1/fabric/virtual-machines"
    res = rest_api_call(ip,
        'GET',
        endpoint,
        None,
        user=user,
        password=password)
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

def restore_nsx_vm_tags(ip: str, user: str, password: str, backupfile: str):
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
                rest_api_call(ip,
                    'POST',
                    endpoint,
                    body,
                    user=user,
                    password=password)
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
                         %(vm["external_id"],
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
        backup_nsx_vm_tags(args.ip,args.user,args.password,args.backupfile)
    if "restore" in args.operation:
        restore_nsx_vm_tags(args.ip,args.user,args.password,args.backupfile)

################################################################################
