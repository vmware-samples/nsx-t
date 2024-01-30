#!/usr/bin/env python
# Requires Python 3.x
# Replace Cert in LB-Monitor
# Author: Dimitri Desmidt
# version 1.0
# January 2024
# This script is neither supported nor endorsed by VMware/Broadcom but meant as an example

'''
Script to replace cert in existing LB-monitor

Validated with: NSX-T 4.1
'''

import requests
import json
import datetime
import ssl
import time
import os.path
import argparse

# Input information
'''
nsx_manager='192.168.110.201'
nsx_user='admin'
nsx_password='VMware1!VMware1!'
lb_monitor_id='monitor2'
old_nsx_cert_path='/infra/certificates/www1'
new_nsx_cert_name='newcert'
new_cert_file='newcert.crt'
new_key_file='newcert.key'
'''
# python replace_cert_in_nsx_monitor.py -nsx_manager 192.168.110.201 -nsx_user admin -nsx_password VMware1!VMware1! -lb_monitor_id monitor2 -old_nsx_cert_path /infra/certificates/www1 -new_nsx_cert_name newcert -new_cert_file newcert.crt -new_key_file newcert.key
parser = argparse.ArgumentParser()
parser.add_argument("-nsx_manager", help="REQUIRED - NSX Manager IP/FQDN (e.g. 192.168.110.201)", type=str, required=True)
parser.add_argument("-nsx_user", default="admin", help="OPTIONAL - NSX Manager user (default = admin)", type=str)
parser.add_argument("-nsx_password", help="REQUIRED - NSX Manager password", type=str, required=True)
parser.add_argument("-lb_monitor_id", help="REQUIRED - NSX LB MONITOR ID (usually LB MONITOR name)", type=str, required=True)
parser.add_argument("-old_nsx_cert_path", help="REQUIRED - NSX old cert path (usually /infra/certificates/xxx)", type=str, required=True)
parser.add_argument("-new_nsx_cert_name", help="REQUIRED - NSX LB MONITOR new cert name (e.g. newcert)", type=str, required=True)
parser.add_argument("-new_cert_file", help="REQUIRED - NSX LB MONITOR new cert file(e.g. newcert.crt)", type=str, required=True)
parser.add_argument("-new_key_file", help="REQUIRED - NSX LB MONITOR new key file (e.g. newcert.key)", type=str, required=True)
args = parser.parse_args()
nsx_manager = args.nsx_manager
nsx_user = args.nsx_user
nsx_password = args.nsx_password
lb_monitor_id = args.lb_monitor_id
old_nsx_cert_path = args.old_nsx_cert_path
new_nsx_cert_name = args.new_nsx_cert_name
new_cert_file = args.new_cert_file
new_key_file = args.new_key_file

######################################################################################################
# Don't change things below
######################################################################################################
start_time= datetime.datetime.now()

#remove the self certificate warnings
requests.packages.urllib3.disable_warnings()

# headers for NSX-T Restful API calls
headers = {'Content-type': 'application/json', 'Accept': 'application/json'}

def nsx_check_cert_path_present (mgr, cert_path):
    certs = nsx_get_call(mgr, '/api/v1/trust-management/certificates')
    certs_list = [certs][0]['results']
    cert_path_present = 'false'
    for certificate in certs_list:
        if "tags" in certificate:
            if certificate['tags'][0]['tag'] == cert_path:
                cert_path_present = 'true'
    return cert_path_present

def nsx_get_call (mgr, uri):
    try:
        response = requests.get('https://'+mgr+uri, verify=False, auth=(nsx_user, nsx_password), headers=headers, stream=True)
    except requests.exceptions.Timeout:
        print ("GET uri " + uri + "    Timeout")
        return 'error'
    except requests.exceptions.ConnectionError:
        print ("GET uri " + uri + "    ConnectionError")
        return 'error'
    if "20" not in str(response.status_code):
        print ("GET uri " + uri + " response status code: "+str(response.status_code))
        print (response.text)
        return 'error'
    #As the answer is in JSON format, create the proper object
    json_response=json.loads(response.text)
    return json_response

def nsx_put_call (mgr, uri, payload):
    try:
        response = requests.put('https://'+mgr+uri, verify=False, auth=(nsx_user, nsx_password), headers=headers, stream=True, data=json.dumps(payload))
    except requests.exceptions.Timeout:
        print ("PUT uri " + uri + "    Timeout")
        return 'error'
    except requests.exceptions.ConnectionError:
        print ("PUT uri " + uri + "    ConnectionError")
        return 'error'
    if "20" not in str(response.status_code):
        print ("PUT uri " + uri + " response status code: "+str(response.status_code))
        print (response.text)
        return 'error'
    #As the answer is in JSON format, create the proper object
    json_response=json.loads(response.text)
    return json_response

def nsx_patch_call (mgr, uri, payload):
    try:
        response = requests.patch('https://'+mgr+uri, verify=False, auth=(nsx_user, nsx_password), headers=headers, stream=True, data=json.dumps(payload))
    except requests.exceptions.Timeout:
        print ("PATCH uri " + uri + "    Timeout")
        return 'error'
    except requests.exceptions.ConnectionError:
        print ("PATCH uri " + uri + "    ConnectionError")
        return 'error'
    if "20" not in str(response.status_code):
        print ("PATCH uri " + uri + " response status code: "+str(response.status_code))
        print (response.text)
        return 'error'
    return 'OK'




def nsx_check_cert_not_present (mgr, payload):
    customer_cert = [payload][0]['pem_encoded']
    certs = nsx_get_call(mgr, '/api/v1/trust-management/certificates')
    certs_list = [certs][0]['results']
    nsx_new_cert_path = 'false'
    for certificate in certs_list:
        cert_in_list = certificate['pem_encoded']
        if cert_in_list == customer_cert:
            nsx_new_cert_path = certificate['tags'][0]['tag']
            print ('    Note: Cert was already present')
    return nsx_new_cert_path

def nsx_add_cert (mgr, uri, payload):
    nsx_new_cert_path = nsx_check_cert_not_present(mgr, payload)
    if nsx_new_cert_path == 'false':
        json_response = nsx_put_call(mgr, uri, payload)
        nsx_new_cert_path = json_response['path']
    return nsx_new_cert_path

def nsx_replace_cert_in_monitor (mgr, uri, old_nsx_cert_path, nsx_new_cert_path):
    nsx_monitor_config = nsx_get_call(mgr, uri)
    result = 'no_change_done'
    for nsx_monitor_config_field in nsx_monitor_config:
        value = nsx_monitor_config[nsx_monitor_config_field]
        if type(value) is str:
            if value == old_nsx_cert_path:
                nsx_monitor_config[nsx_monitor_config_field] = nsx_new_cert_path
                result = 'change_done'
                print ('  - changed cert in '   +str(nsx_monitor_config_field))
        if type(value) is dict:
            for key_dict, value_dict in value.items():
                if type(value_dict) is list:
                    i = 0
                    for entry in value_dict:
                        if str(entry) == old_nsx_cert_path:
                            nsx_monitor_config[nsx_monitor_config_field][key_dict][i] = nsx_new_cert_path
                            result = 'change_done'
                            print ('  - changed cert in '   +str(nsx_monitor_config_field) + ' - ' + key_dict)
                        i = i+1
                elif str(value_dict) == old_nsx_cert_path:
                    nsx_monitor_config[nsx_monitor_config_field][key_dict] = nsx_new_cert_path
                    result = 'change_done'
                    print ('  - changed cert in '   +str(nsx_monitor_config_field))
    if result == 'change_done':
        result = nsx_patch_call(mgr, uri, nsx_monitor_config)
    else:
        print ('  - Old cert not present in monitor')
    return result



##########################################
#Script to replace cert in existing LB-MONITOR
##########################################
print ('')

#Validate inputs
if nsx_get_call(nsx_manager, '/policy/api/v1/infra/lb-monitor-profiles/'+lb_monitor_id) == 'error':
    print ('  lb_monitor_id '+ lb_monitor_id +' does not exist')
    print ('  or nsx_manager '+ nsx_manager +' is incorrect')
    exit()

if nsx_check_cert_path_present (nsx_manager, old_nsx_cert_path) == 'false':
    print ('  old_nsx_cert_path '+ old_nsx_cert_path +' does not exist in NSX Manager Certificates')
    exit()

if os.path.isfile(new_cert_file):
    cert_file = open(new_cert_file, 'r').read()
else:
    print ('  file '+ new_cert_file +' does not exist')
    exit()

if os.path.isfile(new_key_file):
    key_file = open(new_key_file, 'r').read()
else:
    print ('  file '+ new_key_file +' does not exist')
    exit()


print ('=========================================')
print ('Script to replace cert in existing LB-Monitor')
print ('=========================================')
print ('  nsx_manager ='+ nsx_manager)
print ('  nsx_user ='+ nsx_user)
print ('  nsx_password ='+ nsx_password)
print ('  lb_monitor_id ='+ lb_monitor_id)
print ('  old_nsx_cert_path ='+ old_nsx_cert_path)
print ('  new_nsx_cert_name ='+ new_nsx_cert_name)
print ('  new_cert_file ='+ new_cert_file)
print ('  new_key_file ='+ new_key_file)
print ('')
print ('')
print ('. Goal is to replace')
print ('--------------------')
print ('  - oldcert = '+ old_nsx_cert_path)
print ('  - in monitor = '+ lb_monitor_id)
print ('  - with new cert = '+ new_nsx_cert_name)
print ('')


#add new cert in NSX Manager
print ('1. Import new cert')
payload ={'pem_encoded': cert_file, 'private_key': key_file, 'display_name': new_nsx_cert_name}
nsx_new_cert_path = nsx_add_cert(nsx_manager, '/policy/api/v1/infra/certificates/'+new_nsx_cert_name, payload)
print ('  - nsx_new_cert_path = '+nsx_new_cert_path)
print ('')

#replace cert in monitor
print ('2. Replace in monitor '+ lb_monitor_id + ' the old cert ('+ old_nsx_cert_path +') with new cert ('+ nsx_new_cert_path +')')
result = nsx_replace_cert_in_monitor(nsx_manager, '/policy/api/v1/infra/lb-monitor-profiles/'+lb_monitor_id, old_nsx_cert_path, nsx_new_cert_path)




end_time= datetime.datetime.now()
print ('')
print ('')
print ('script started at ' + start_time.strftime("%Y-%m-%d %H:%M:%S"))
print ('script ended at ' + end_time.strftime("%Y-%m-%d %H:%M:%S"))
total_time = end_time - start_time
print ('total time '+str(total_time).split(".")[0])


