
#!/usr/bin/env python
#
# Configure NSX-T Lab
# Copyright (c) 2019 VMware, Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
##############################################################################
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

from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim, vmodl

# To be used only in case of access the lab through NAT rules
jumphost_ip = ""

nsx_ip = "192.168.110.201"
kvm_ip = "192.168.130.151"
vc_ip = "192.168.110.22"

kvm_ssh_port = 22
nsx_port = 443
vc_port = 443

# vCenter credentials
vc_username = "administrator@vsphere.local"
vc_password = "VMware1!"

# Supress SSL warning
requests.packages.urllib3.disable_warnings() 

# Supress SSH/Paramiko warnings
warnings.filterwarnings("ignore") 


# Headers. The Authorization is base64 encode of 'admin:<pass>'
# The below is for admin:VMware1!VMware1!
# TODO: calculate base64 string instead
headers = {
  'Authorization': 'Basic YWRtaW46Vk13YXJlMSFWTXdhcmUxIQ==',
  'Content-Type': 'application/json'
}

##############################################################################
# Housekeeping
##############################################################################
# Prints log messages
verbose = 0

# Pretty print POST response body on Success
print_response = 1

# Just display the API call and the request body (if any)
plan = 0

##############################################################################
# Helper functions
##############################################################################

# Generic Error Response
def raiseError(r):
    print("Error: %s" % json.dumps(r.json(), indent=4, sort_keys=True))
    exit()


# pretty print json
def print_json(text):
    print(json.dumps(text, indent=4, sort_keys=True))
    return True


# Generic pretty print Response
def pretty_response(r):
    if (print_response and not plan):
        try:
            print(json.dumps(r.json(), indent=4, sort_keys=True))
        except ValueError as e:
            return True
    return True


# Load json file
def load_json(file):
    with open('./request_body/' + file) as json_file:
        data = json.load(json_file)
        return data


# Log me
def log(msg):
    if (verbose):
        print(msg)


# NSX Manager IP/FQDN URL formatter
def nsx_url(uri):
    return 'https://' + nsx_ip + ':443' + uri


# Generic GET request
def get(uri, ignore_plan=False):
    if plan and ignore_plan == False:
        print("\nGET %s\n" % uri)
        return True

    r = requests.get(nsx_url(uri), verify=False, headers=headers)
    if r.status_code != 200:
        raiseError(r)
    return r


# Generic POST request. retry_with_thumbprint flag to retry if the initial POST response has a thumbprint
def post(uri, json_body, retry_with_thumbprint=False):
    if plan:
        print("\nPOST %s" % uri)
        print("Request-Body: \n%s\n" % json.dumps(json_body, indent=4, sort_keys=True))
        return True

    r = requests.post(nsx_url(uri), verify=False, headers=headers, json=json_body)
    if ((r.status_code != 201) and (r.status_code != 200)):
        if retry_with_thumbprint == False:
            raiseError(r)
        else:
            data = r.json()
            if 'already registered with NSX' in data['error_message']:
                return r
            if 'thumbprint' in data['error_message']:
                if "ValidCmThumbPrint" in data['error_data']:
                    thumbprint = data['error_data']['ValidCmThumbPrint']
                    # Add thumbprint to json_data and retry
                    json_body['credential']['thumbprint'] = thumbprint
                elif "ValidThumbPrint" in data['error_data']:
                    thumbprint = data['error_data']['ValidThumbPrint']
                    json_body['node_deployment_info']['host_credential']['thumbprint'] = thumbprint
                else:
                    raiseError(r)

                r = requests.post(nsx_url(uri), verify=False, headers=headers, json=json_body)
                if ((r.status_code != 201)) :
                    raiseError(r)
            else:
                raiseError(r)
    return r

# Generic PUT request. Usually returns a response body
def put(uri, json_body):
    if plan:
        print("\nPUT %s" % uri)
        print("Request-Body: \n%s\n" % json.dumps(json_body, indent=4, sort_keys=True))
        return True

    r = requests.put(nsx_url(uri), verify=False, headers=headers, json=json_body)
    if r.status_code != 200:
        raiseError(r)
    return r


# Generic PATCH request. Usually does not return a response body
def patch(uri, json_body):
    if plan:
        print("\nPATCH %s" % uri)
        print("Request-Body: \n%s\n" % json.dumps(json_body, indent=4, sort_keys=True))
        return True

    r = requests.patch(nsx_url(uri), verify=False, headers=headers, json=json_body)
    if r.status_code != 200:
        raiseError(r)
    return r


# Generic DELETE request. Does not return anything
def delete(uri):
    if plan:
        print("\nDELETE %s" % uri)
        return True
    r = requests.delete(nsx_url(uri), verify=False, headers=headers)
    if r.status_code != 200:
        raiseError(r)
    return True


##############################################################################
# vCenter Helper Functions
##############################################################################

# Get the vSphere Managed Object associated with a given text name
# Credit: https://github.com/vmware/vsphere-automation-sdk-python/blob/master/samples/vsphere/common/vim/helpers/vim_utils.py
def get_obj(content, vimtype, name):
    obj = None
    container = content.viewManager.CreateContainerView(content.rootFolder,
                                                        vimtype, True)
    for view in container.view:
        if view.name == name:
            obj = view
            break
    return obj


# Credit: https://github.com/vmware/pyvmomi/blob/master/sample/poweronvm.py
def WaitForTasks(tasks, si):
   # Given the service instance si and tasks, it returns after all the
   # tasks are complete

   pc = si.content.propertyCollector

   taskList = [str(task) for task in tasks]

   # Create filter
   objSpecs = [vmodl.query.PropertyCollector.ObjectSpec(obj=task)
                                                            for task in tasks]
   propSpec = vmodl.query.PropertyCollector.PropertySpec(type=vim.Task,
                                                         pathSet=[], all=True)
   filterSpec = vmodl.query.PropertyCollector.FilterSpec()
   filterSpec.objectSet = objSpecs
   filterSpec.propSet = [propSpec]
   filter = pc.CreateFilter(filterSpec, True)

   try:
      version, state = None, None

      # Loop looking for updates till the state moves to a completed state.
      while len(taskList):
         update = pc.WaitForUpdates(version)
         for filterSet in update.filterSet:
            for objSet in filterSet.objectSet:
               task = objSet.obj
               for change in objSet.changeSet:
                  if change.name == 'info':
                     state = change.val.state
                  elif change.name == 'info.state':
                     state = change.val
                  else:
                     continue

                  if not str(task) in taskList:
                     continue

                  if state == vim.TaskInfo.State.success:
                     # Remove task from taskList
                     taskList.remove(str(task))
                  elif state == vim.TaskInfo.State.error:
                     raise task.info.error
         # Move to next version
         version = update.version
   finally:
      if filter:
         filter.Destroy()


# Connect to vCenter and return the si object
def vcenter_connect():
    context = None
    if hasattr(ssl, '_create_unverified_context'):
        context = ssl._create_unverified_context()
    si = SmartConnect(host=vc_ip, port=vc_port,
                      user=vc_username, pwd=vc_password,
                      sslContext=context)
    if not si:
        log("Cannot connect to %s with %s, %s" % (vc_ip, vc_username, vc_password))

    return si


# Change Network backing to the vm. Assumes its a Opaque Network
# https://github.com/vmware/pyvmomi-community-samples/blob/master/samples/change_vm_vif.py
# https://github.com/vmware/pyvmomi-community-samples/blob/master/samples/add_nic_to_vm.py
def change_vm_network(vmname, network_name):
    try:
        si = vcenter_connect()
        content = si.content

        objView = content.viewManager.CreateContainerView(content.rootFolder,
                                                          [vim.VirtualMachine], True)
        vmList = objView.view
        objView.Destroy()

        for vm in vmList:
            device_change = []
            if vm.name == vmname:
                log("  +-- Configuring VM: " + vm.name + " with Network: " + network_name)
                for device in vm.config.hardware.device:
                    if isinstance(device, vim.vm.device.VirtualEthernetCard):
                        nicspec = vim.vm.device.VirtualDeviceSpec()
                        nicspec.operation = \
                            vim.vm.device.VirtualDeviceSpec.Operation.edit
                        nicspec.device = device
                        nicspec.device.wakeOnLanEnabled = True

                        network = get_obj(content, [vim.dvs.DistributedVirtualPortgroup],
                                       network_name)
                        dvs_port_connection = vim.dvs.PortConnection()
                        dvs_port_connection.portgroupKey = network.key
                        dvs_port_connection.switchUuid = \
                            network.config.distributedVirtualSwitch.uuid
                        nicspec.device.backing = \
                            vim.vm.device.VirtualEthernetCard.DistributedVirtualPortBackingInfo()
                        nicspec.device.backing.port = dvs_port_connection

                        nicspec.device.connectable = \
                            vim.vm.device.VirtualDevice.ConnectInfo()
                        nicspec.device.connectable.startConnected = True
                        nicspec.device.connectable.allowGuestControl = True
                        nicspec.device.connectable.connected = True
                        device_change.append(nicspec)
                        break

                config_spec = vim.vm.ConfigSpec(deviceChange=device_change)
                task = vm.ReconfigVM_Task(config_spec)
                tasks = []
                tasks.append(task)
                WaitForTasks(tasks, si)

    except vmodl.MethodFault as error:
        log("Could not change VM network. Cought vmodl fault: " + error.msg)
        return False

    return True


def power_on_vm(vmnames):
    log("  +-- Powering on VMs: " + ', '.join(vmnames))
    try:
        si = vcenter_connect()
        content = si.content
        objView = content.viewManager.CreateContainerView(content.rootFolder,
                                                          [vim.VirtualMachine], True)
        vmList = objView.view
        objView.Destroy()
        tasks = [vm.PowerOn() for vm in vmList if vm.name in vmnames]
        WaitForTasks(tasks, si)
    except vmodl.MethodFault as error:
        if (error.msg.find('Powered on')):
          return True
        log("Could not power On VMs. Cought vmodl fault: " + error.msg)
        return False

    return True


def power_off_vm(vmnames):
    log("  +-- Powering OFF VMs: " + ', '.join(vmnames))
    try:
        si = vcenter_connect()
        content = si.content
        objView = content.viewManager.CreateContainerView(content.rootFolder,
                                                          [vim.VirtualMachine], True)
        vmList = objView.view
        objView.Destroy()
        tasks = [vm.PowerOff() for vm in vmList if vm.name in vmnames]
        WaitForTasks(tasks, si)
    except vmodl.MethodFault as error:
        if (error.msg.find('Powered off')):
          return True
        log("Could not power OFF VMs. Cought vmodl fault: " + error.msg)
        return False

    return True



##############################################################################
# SHELL command workflows
##############################################################################

# Execute a command on a (KVM) host. Note: Returns the stdout as string
def execute_command(host, port, username, password, command):
    ssh = paramiko.SSHClient()
    # Add hostkeys
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, port, username, password)
    time.sleep(5)
    stdin, stdout, stderr = ssh.exec_command(command)
    opt = stdout.readlines()
    opt = "".join(opt)
    err = stderr.readlines()
    err = "".join(err)
    return [ stdin, opt, err ]


##############################################################################
# Workflows
##############################################################################

def add_vcenter_compute_manager():
    log ("  +-- Adding Compute Managers")
    request_body = load_json('compute_manager.json')
    for item in request_body['compute_managers']:
        r = post('/api/v1/fabric/compute-managers', item, retry_with_thumbprint=True)
        pretty_response(r)
    check_compute_manager_status()
    return True


def delete_compute_managers():
    log ("  +-- Deleting Compute Manager")
    cm = {}
    r = get('/api/v1/fabric/compute-managers', ignore_plan=True)
    for item in r.json()['results']:
        cm[item['display_name']] = item['id']
    if cm:
        request_body = load_json('compute_manager.json')
        for item in request_body['compute_managers']:
            id = cm[item['display_name']]
            delete('/api/v1/fabric/compute-managers/' + id)


def create_transport_zone():
    log ("  +-- Creating Transport Zones")
    request_body = load_json('transport_zone.json')

    wait = 0
    e_tzs = []
    r = get('/api/v1/transport-zones')
    for i in r.json()['results']:
        e_tzs.append(i['display_name'])

    for item in request_body['transport_zones']:
        if (item['display_name'] not in e_tzs):
            r = post('/api/v1/transport-zones', item)
            pretty_response(r)
            wait = 1

    # Segment creation uses the TZ.
    if (wait):
        time.sleep(60)

    return True


def delete_transport_zone():
    log ("  +-- Deleting Transport Zones")
    tz = {}
    r = get('/api/v1/transport-zones', ignore_plan=True)
    if (r.json()['result_count'] == 2):
        return True

    for item in r.json()['results']:
        tz[item['display_name']] = item['id']
    if tz:
        request_body = load_json('transport_zone.json')
        for item in request_body['transport_zones']:
            id = tz[item['display_name']]
            delete('/api/v1/transport-zones/' + id)
    return True


def define_TEP_IP_pool():
    # Creating TEP Pool requires 2 API calls! One to create the pool and one to create the subnet in it
    # The corresponding json file reflects this
    log("  +-- Creating IP Pool for TEPs")
    request_body = load_json('ip_pools.json')
    for item in request_body['ip_pools']:
        display_name = item['display_name']
        api = "/policy/api/v1/infra/ip-pools/" + display_name
        r = patch(api, item)
        pretty_response(r)

    for item in request_body['ip-subnets']:
        api = "/policy/api/v1/infra/ip-pools/" + item['parent'] + "/ip-subnets/" + item['subnets']['display_name']
        r = patch(api, item['subnets'])
        pretty_response(r)

    # No easy way to check for realization. Without the sleep TNP creation
    # could fail
    time.sleep(120)
    return True


def delete_TEP_IP_pool():
    log ("  +-- Delete IP Pool")
    request_body = load_json('ip_pools.json')
    for item in request_body['ip-subnets']:
        api = "/policy/api/v1/infra/ip-pools/" + item['parent'] + "/ip-subnets/" + item['subnets']['display_name']
        delete(api)
    for item in request_body['ip_pools']:
        display_name = item['display_name']
        delete('/policy/api/v1/infra/ip-pools/' + display_name)


def create_transport_node_profile():
    log("  +-- Creating Transport Node Profiles")

    # Get all IP Pools and save IDs in a dict
    ip_p_ids = {}
    r = get('/api/v1/pools/ip-pools', ignore_plan=True)
    for ip_p_item in r.json()['results']:
        ip_p_ids[ip_p_item['display_name']] = ip_p_item['id']

    request_body = load_json('transport_node_profiles.json')
    for item in request_body['transport_node_profiles']:
        for hs_item in item['host_switch_spec']['host_switches']:
            # Change IP Pool Name to ID
            hs_item['ip_assignment_spec']['ip_pool_id'] = ip_p_ids[hs_item['ip_assignment_spec']['ip_pool_id']]

        api = "/api/v1/transport-node-profiles"
        r = post(api, item)
        pretty_response(r)
    
    return True


def delete_transport_node_profile():
    log("  +-- Delete Transport Node Profile")
    r = get('/api/v1/transport-node-profiles', ignore_plan=True)
    tnp = {}
    for item in r.json()['results']:
        tnp[item['display_name']] = item['id']
    # Only if there is anything to delete
    if tnp.keys():
        request_body = load_json('transport_node_profiles.json')
        for item in request_body['transport_node_profiles']:
            id = tnp[item['display_name']]
            delete('/api/v1/transport-node-profiles/' + id)
    return True


def wait_for(api, key, value, results, interval=5):
    # Wait for the status to become "success"
    max_wait_time = 60 # in minutes
    elapsed_time = 0
    while elapsed_time < max_wait_time:
        r = get(api, ignore_plan=True)
        if (results):
            total = r.json()['result_count']
            result = 0
            for item in r.json()['results']:
                log ("      -- Waiting for %s, Got %s" % (value, item[key]))
                if (item[key] == value):
                    result = result + 1
            log ("      -- success: %s, total %s" % (result, total))
            if (result == total):
                return True
        else:
            item = r.json()
            log ("      -- Waiting for %s, Got %s" % (value, item[key]))
            if (item[key] == value):
                return True

        # Sleep before checking
        secs = 60 * interval
        log ("      -- sleeping for %s secs" % secs)
        time.sleep(secs)
        elapsed_time = elapsed_time + interval

    log("ERROR: Operation not complete after waiting for an hour")
    sys.exit(2)

def check_tn_state():
    log ("  +-- Wait for Transport Nodes to be registered")
    return wait_for('/api/v1/transport-nodes/state', 'state', 'success', results=True, interval=5)


def sync_enforcement_point():
    empty_json = {}
    post('/policy/api/v1/infra/sites/default/enforcement-points/default?action=full-sync', empty_json)


def prepare_compute_cluster():
    log("  +-- Prepping ESX Compute Clusters")
    comp_collection_ids = {}
    transport_node_profile_ids = {}

    # Get all Cluster info
    r = get('/api/v1/fabric/compute-collections', ignore_plan=True)
    for comp_coll in r.json()['results']:
        comp_collection_ids[comp_coll['display_name']] = comp_coll['external_id']

    # Get TNP info
    r = get('/api/v1/transport-node-profiles', ignore_plan=True)
    for tnp in r.json()['results']:
        transport_node_profile_ids[tnp['display_name']] = tnp['id']

    request_body = load_json('compute_cluster.json')
    for item in request_body['compute-clusters']:

        c = get('/api/v1/transport-node-collections')
        for tnc in c.json()['results']:
            if (tnc['display_name'] == item['display_name']):
                return True

        # Change names to IDs
        item['compute_collection_id'] = comp_collection_ids[item['compute_collection_id']]
        item['transport_node_profile_id'] = transport_node_profile_ids[item['transport_node_profile_id']]

        # Prep the Cluster
        r = post('/api/v1/transport-node-collections', item)
        pretty_response(r)

    check_tn_state()

    return True


def delete_compute_cluster():
    log("  +-- Deleting ESX Compute Cluster")

    # Get all Cluster info
    comp_collection_ids = {}
    r = get('/api/v1/fabric/compute-collections', ignore_plan=True)
    if (r.json()['result_count'] == 0):
        return True

    for comp_coll in r.json()['results']:
        comp_collection_ids[comp_coll['display_name']] = comp_coll['external_id']

    request_body = load_json('compute_cluster.json')
    for item in request_body['compute-clusters']:
        compute_collection_id = comp_collection_ids[item['compute_collection_id']]
        uri = "/api/v1/fabric/compute-collections/" + compute_collection_id + "?action=remove_nsx"
        r = post(uri, item)
        pretty_response(r)
    time.sleep(20)
    return True


def add_transport_node():
    log ("  +-- Adding Transport Nodes")

    si = vcenter_connect()
    content = si.content

    tns = []
    r = get('/api/v1/transport-nodes/', ignore_plan=True)
    for tn_items in r.json()['results']:
        tns.append(tn_items['display_name'])

    # Get all Hostswitchs and save IDs in a dict
    hs_ids = {}
    r = get('/api/v1/host-switch-profiles?include_system_owned=True', ignore_plan=True)
    for hs_item in r.json()['results']:
        hs_ids[hs_item['display_name']] = hs_item['id']

    # Get all Transport Zones and save IDs in a dict
    tz_ids = {}
    r = get('/api/v1/transport-zones', ignore_plan=True)
    for tz_item in r.json()['results']:
        tz_ids[tz_item['display_name']] = tz_item['id']

    # Get all IP Pools and save IDs in a dict
    ip_p_ids = {}
    r = get('/api/v1/pools/ip-pools', ignore_plan=True)
    for ip_p_item in r.json()['results']:
        ip_p_ids[ip_p_item['display_name']] = ip_p_item['id']

    # Get all Compute Manager IDs in a dict
    compute_managers = {}
    r = get('/api/v1/fabric/compute-managers', ignore_plan=True)
    for c_m in r.json()['results']:
        compute_managers[c_m['display_name']] = c_m['id']

    request_body = load_json("add_transport_node.json")
    for item in request_body['host_transport_nodes']:
        for hs_item in item['host_switch_spec']['host_switches']:
            # Change Hostswitch names to IDs
            for hs_profile_ids in hs_item['host_switch_profile_ids']:
                hs_profile_ids['value'] = hs_ids[hs_profile_ids['value']] 

            # Change IP Pool Name to ID
            hs_item['ip_assignment_spec']['ip_pool_id'] = ip_p_ids[hs_item['ip_assignment_spec']['ip_pool_id']]

            # Change Transport Zone name to ID
            for tz_item in hs_item['transport_zone_endpoints']:
              tz_item['transport_zone_id'] = tz_ids[tz_item['transport_zone_id']]

        # Change Compute Manager Name to ID in case of Edge deployment 
        # The if blocks are needed as the KVM transport node json does not have deployment_config key
        if "deployment_config" in item['node_deployment_info']:    
            if "vc_id" in item['node_deployment_info']['deployment_config']['vm_deployment_config']:
                vc = item['node_deployment_info']['deployment_config']['vm_deployment_config']['vc_id']
                item['node_deployment_info']['deployment_config']['vm_deployment_config']['vc_id'] = compute_managers[vc]

                # Assumes MoIDs are given for Cluster, Storage, Host, Management and Data networks

        if (item['display_name'] not in tns):
            r = post('/api/v1/transport-nodes', item, retry_with_thumbprint=True)
            pretty_response(r)

    check_tn_state()
    sync_enforcement_point()

    return True


def delete_transport_node():
    log ("  +-- Deleting Host and Edge Transport Nodes")
    transport_nodes = []
    request_body = load_json('add_transport_node.json')
    for item in request_body['host_transport_nodes']:
        transport_nodes.append(item['node_deployment_info']['display_name'])

    transport_node_ids = []
    r = get('/api/v1/transport-nodes')
    for tn_item in r.json()['results']:
        for tn in transport_nodes:
            if tn == tn_item['node_deployment_info']['display_name']:
                transport_node_ids.append(tn_item['node_id'])
                transport_nodes.remove(tn)

    for id in transport_node_ids:
        delete('/api/v1/transport-nodes/' + id)
        time.sleep(30)

    return True


def create_edge_cluster():
    log("  +-- Creating Edge Cluster")

    existing_clusters = []
    r = get('/api/v1/edge-clusters')
    for c in r.json()['results']:
        existing_clusters.append(c['display_name'])

    # Get Cluster Profile IDs
    edge_cluster_profile_id = {}
    r = get('/api/v1/cluster-profiles', ignore_plan=True)
    for c_p in r.json()['results']:
        edge_cluster_profile_id[c_p['display_name']] = c_p['id']

    # Get Edge Node IDs
    edge_node_id = {}
    r = get('/api/v1/transport-nodes?node_types=EdgeNode', ignore_plan=True)
    for e_n in r.json()['results']:
        edge_node_id[e_n['display_name']] = e_n['id']

    request_body = load_json('edge_cluster.json')
    for item in request_body['edge_clusters']:
        item['cluster_profile_bindings'][0]['profile_id'] = edge_cluster_profile_id[item['cluster_profile_bindings'][0]['profile_id']]

        for member in item['members']:
            member['transport_node_id'] = edge_node_id[member['display_name']]

        if (item['display_name'] not in existing_clusters):
            r = post('/api/v1/edge-clusters', item)
            pretty_response(r)

    return True


def delete_edge_cluster():
    log("  +-- Delete Edge Cluster")
    edge_cluster_ids = {}
    r = get('/api/v1/edge-clusters', ignore_plan=True)
    if (r.json()['result_count'] == 0):
        return True

    for e_c in r.json()['results']:
        edge_cluster_ids[e_c['display_name']] = e_c['id']

    request_body = load_json('edge_cluster.json')
    for item in request_body['edge_clusters']:
        cluster_id = edge_cluster_ids[item['display_name']]
        delete('/api/v1/edge-clusters/' + cluster_id)

    return True


def create_segments(paramfile):
    tz_paths = {}
    r = get('/policy/api/v1/infra/sites/default/enforcement-points/default/transport-zones', ignore_plan=True)
    for tz_item in r.json()['results']:
        tz_paths[tz_item['display_name']] = tz_item['path']

    request_body = load_json(paramfile)
    for item in request_body['segments']:
        log("  +-- Creating Segment: " + item['display_name'])
        item['transport_zone_path'] = tz_paths[item['transport_zone_path']]

        r = patch('/policy/api/v1/infra/segments/' + item['display_name'], item)
        pretty_response(r)

    # So that the DVPGs are created on vCenter
    time.sleep(10)
    return True


def delete_segments(paramfile):
    log("  +-- Delete Segments")
    # So that the VIF attachments are gone. There is a better way to do this.
    time.sleep(60)
    request_body = load_json(paramfile)
    for item in request_body['segments']:
        delete('/policy/api/v1/infra/segments/' + item['display_name'])

    return True


def update_global_routing_config():
    log("  +-- Updating global routing config to include IPv6")

    uri = '/policy/api/v1/infra/global-config'
    config_request_body = {}
    config_request_body['l3_forwarding_mode'] = "IPV4_AND_IPV6"
    config_request_body['resource_type'] = "GlobalConfig"
    r = patch(uri, config_request_body)
    pretty_response(r)

    return True


def reset_global_routing_config():
    log("  +-- Resetting global routing config to back to just IPv4")

    uri = '/policy/api/v1/infra/global-config'
    config_request_body = {}
    config_request_body['l3_forwarding_mode'] = "IPV4_ONLY"
    config_request_body['resource_type'] = "GlobalConfig"
    r = patch(uri, config_request_body)
    pretty_response(r)
    return True


def create_tier1s():
    request_body = load_json("create_tier1s.json")
    for item in request_body['tier-1s']:
        log("  +-- Creating Tier-1 Gateway: " + item['display_name'])
        r = patch('/policy/api/v1/infra/tier-1s/' + item['display_name'], item)
        pretty_response(r)

    return True


def delete_tier1s():
    log ("  +-- Delete Tier1")
    request_body = load_json("create_tier1s.json")

    r = get('/policy/api/v1/infra/tier-1s', ignore_plan=True)
    if (r.json()['result_count'] == 0):
        return True

    for item in request_body['tier-1s']:
        r = get('/policy/api/v1/infra/tier-1s/' + item['display_name'] + '/locale-services/', ignore_plan=True)
        for ls in r.json()['results']:
            uri = "/policy/api/v1/infra/tier-1s/" + item['display_name'] + "/locale-services/" + ls['id']
            delete(uri)
            time.sleep(30)

        delete('/policy/api/v1/infra/tier-1s/' + item['display_name'])

    return True


def configure_vm_network_and_poweron():
    vm_net_map = {
        "app-01a": "app-seg",
        "web-01a": "web-seg",
        "web-02a": "web-seg",
        "vm-01a":  "vm-seg"
    }
    for vmname in vm_net_map.keys():
        change_vm_network(vmname, vm_net_map[vmname])
    power_on_vm(vm_net_map.keys())

    return True


def reset_vm_network_and_poweroff():
    vm_net_map = {
        "app-01a": "LabNet",
        "web-01a": "LabNet",
        "web-02a": "LabNet",
        "vm-01a": "LabNet"
    }
    power_off_vm(vm_net_map.keys())
    for vmname in vm_net_map.keys():
        change_vm_network(vmname, vm_net_map[vmname])
    time.sleep(10)
    return True


def poweron_kvm_vms():
    kvm_vms = [ "db-01a", "web-03a" ]
    for vm in kvm_vms:
        log("  +-- Starting KVM VM: " + vm)
        command = 'virsh start ' + vm
        [stdin, stdout, stderr] = execute_command(kvm_ip, kvm_ssh_port, "vmware", "VMware1!", command)
        if "already active" in stderr:
            continue

        if not "started" in stdout:
            log("Could not start VM %s: %s" % (vm, stderr))
            sys.exit(2)

    return True


def poweroff_kvm_vms():
    kvm_vms = [ "db-01a", "web-03a" ]
    for vm in kvm_vms:
        log("  +-- Stopping KVM VM: " + vm)
        command = 'virsh destroy ' + vm
        [stdin, stdout, stderr] = execute_command(kvm_ip, kvm_ssh_port, "vmware", "VMware1!", command)
        if "not running" in stderr:
            continue
        if not "destroyed" in stdout:
            log("Could not destroy VM %s: %s" % (vm, stderr))
            sys.exit(2)

    return True


def configure_kvm_segment_ports():
    log("  +-- Configuring Segment Ports for KVM VMs")
    request_body = load_json("segment_ports.json")
    for item in request_body['segment-ports']:
        switchport_name = item['display_name']
        path = item['path']
        # /infra/segments/web-seg/ports/web-vm
        parts = path.split("/")
        segment_name = parts[3]

        command = 'virsh dumpxml ' + item['display_name'] + ' | grep interfaceid'
        [stdin, stdout, stderr] = execute_command(kvm_ip, kvm_ssh_port, "vmware", "VMware1!", command)
        # stdout has interface id like: <parameters interfaceid='57601300-2e82-48c4-8c27-1e961ac70e81'/>
        start = "=\'"
        end = "\'/"
        vif_id = (stdout.split(start))[1].split(end)[0]

        uri = "/policy/api/v1/infra/segments/" + segment_name + "/ports/" + switchport_name
        item['attachment']['id'] = vif_id
        r = patch(uri, item)
        pretty_response(r)

    return True


def delete_kvm_segment_ports():
    log("  +-- Deleting Segment Ports for KVM VMs")
    request_body = load_json("segment_ports.json")
    for item in request_body['segment-ports']:
        switchport_name = item['display_name']
        path = item['path']
        # /infra/segments/web-seg/ports/web-vm
        parts = path.split("/")
        segment_name = parts[3]
        uri = "/policy/api/v1/infra/segments/" + segment_name + "/ports/" + switchport_name
        r = delete(uri)
    return True


def create_tier0():
    log("  +-- Creating Tier0 GW")
    marked_for_delete = "false"

    # Get Edge IDs and Edge Cluster ID
    # Assumes only 1
    edge_node_id = {}
    r = get('/api/v1/edge-clusters', ignore_plan=True)
    ec = r.json()['results'][0]
    for e_n in ec['members']:
        edge_node_id[e_n['display_name']] = str(e_n['member_index'])

    edge_cluster_id = r.json()['results'][0]['id']

    # Assumes only 1 item
    request_body = load_json('create_tier0.json')
    for item in request_body['tier0s']:
        tier0_id = item['id']
        r = patch('/policy/api/v1/infra/tier-0s/' + item['display_name'], item)
        pretty_response(r)

        # Connect to Tier-1
        tier1_body = load_json('create_tier1s.json')
        for t1 in tier1_body['tier-1s']:
            log("  +-- Attaching to Tier1")
            t1['tier0_path'] = "/infra/tier-0s/" + item['id']
            rt = patch('/policy/api/v1/infra/tier-1s/' + t1['display_name'], t1)
            pretty_response(rt)

    # Sync enforcement point
    r =  post('/policy/api/v1/infra/sites/default/enforcement-points/default?action=reload', {})
    pretty_response(r)

    base_uri = ""
    # Assumes only 1 item
    log('  +-- Setting Route Re-distribution rules')
    for ls in request_body['localeservices']:
        ls['edge_cluster_path'] = '/infra/sites/default/enforcement-points/default/edge-clusters/' + edge_cluster_id
        uri = '/policy/api/v1/infra/tier-0s/' + tier0_id + '/locale-services/' + ls['id']
        base_uri = uri
        r = patch(uri, ls)
        pretty_response(r)

    # Interfaces
    log('  +-- Creating interfaces on Tier0')
    for iface in request_body['interfaces']:
        if (iface['edge_path'] == "EDGE1_PATH"):
            edge_path = '/infra/sites/default/enforcement-points/default/edge-clusters/' + edge_cluster_id + \
                        '/edge-nodes/' + edge_node_id['edgenode-01a']
        elif (iface['edge_path'] == "EDGE2_PATH"):
            edge_path = '/infra/sites/default/enforcement-points/default/edge-clusters/' + edge_cluster_id + \
                        '/edge-nodes/' + edge_node_id['edgenode-02a']
        iface['edge_path'] = edge_path
        uri = base_uri + '/interfaces/' + iface['id']
        r = patch(uri, iface)
        pretty_response(r)

    log('  +-- Setting up BGP')
    for bgp in request_body['bgpconfig']:
        uri = base_uri + '/bgp/'
        r = patch(uri, bgp)
        pretty_response(r)

    log('  +-- Setting up BGP Neighbors')
    for bgpn in request_body['bgpneighbors']:
        uri = base_uri + '/bgp/neighbors/' + bgpn['id']
        r = patch(uri, bgpn)
        pretty_response(r)

    return True


def delete_tier0():
    log ("  +-- Delete Tier0")
    request_body = load_json('create_tier0.json')

    tier0_id = request_body['tier0s'][0]['id']
    ls_id = request_body['localeservices'][0]['id']
    base_uri = '/policy/api/v1/infra/tier-0s/' + tier0_id + '/locale-services/' + ls_id

    log('  +-- Deleting BGP neighbors')
    for bgpn in request_body['bgpneighbors']:
        uri = base_uri + '/bgp/neighbors/' + bgpn['id']
        delete(uri)

    log("  +-- Deleting Interfaces")
    for iface in request_body['interfaces']:
        uri = base_uri + '/interfaces/' + iface['id']
        delete(uri)

    log ("  +-- Deleting locale services")
    delete(base_uri)

    log("  +-- Deleting Tier0 GW")
    for item in request_body['tier0s']:
        delete('/policy/api/v1/infra/tier-0s/' + item['id'])

    return True



def configure_edge_bridge_profile():
    log("Configure Edge Bridge Profile")

    edge_cluster_info = {}
    r = get('/api/v1/edge-clusters', ignore_plan=True)
    for e_c in r.json()['results']:
        cluster_name = e_c['display_name']
        edge_cluster_info[cluster_name] = {}
        edge_cluster_info[cluster_name]['members'] = {}
        edge_cluster_info[cluster_name]['id'] = e_c['id']
        for m in e_c['members']:
            member_name = m['display_name']
            edge_cluster_info[cluster_name]['members'][member_name] = {}
            edge_cluster_info[cluster_name]['members'][member_name]['name'] = member_name
            edge_cluster_info[cluster_name]['members'][member_name]['id'] = m['transport_node_id']
            edge_cluster_info[cluster_name]['members'][member_name]['member_index'] = m['member_index']

    request_body = load_json("edge_bridge_profile.json")
    for item in request_body['edge-bridge-profile']:
        cluster_name = item['edge_cluster_id']
        item['edge_cluster_id'] = edge_cluster_info[item['edge_cluster_id']]['id']
        members = item['edge_cluster_member_indexes']

        for index, member_name in enumerate(members):
            members[index] = edge_cluster_info[cluster_name]['members'][member_name]['member_index']

    r = post('/api/v1/bridge-endpoint-profiles', item)
    pretty_response(r)

    return True


def delete_edge_bridge_profile():
    log("  +-- Delete Edge Bridge Profile")
    edge_profile_ids = {}
    r = get('/api/v1/bridge-endpoint-profiles', ignore_plan=True)
    for edge_profiles in r.json()['results']:
        edge_profile_ids[edge_profiles['display_name']] = edge_profiles['id']

    request_body = load_json("edge_bridge_profile.json")
    for item in request_body['edge-bridge-profile']:
        id = edge_profile_ids[item['display_name']]
        r = delete('/api/v1/bridge-endpoint-profiles/' + id)

    return True


def check_compute_manager_status():
    log ("  +-- Waiting for compute manager to be registered")
    r = get('/api/v1/fabric/compute-managers', ignore_plan=True)
    compute_managers = {}
    for c_m in r.json()['results']:
        compute_managers[c_m['display_name']] = c_m['id']

    request_body = load_json("compute_manager.json")

    for item in request_body['compute_managers']:
      cm_id = compute_managers[item['display_name']]

      api = "/api/v1/fabric/compute-managers/" + cm_id + "/state"
      wait_for(api, 'state', 'success', results=False, interval=1)

      api = "/api/v1/fabric/compute-managers/" + cm_id + "/status"
      wait_for(api, 'registration_status', 'REGISTERED', results=False, interval=1)


def update_tier1():
    log("  +-- Updating Tier-1s with Edge Cluster and Route Distribution")

    # Get Edge IDs and Edge Cluster ID
    # Assumes only 1
    edge_node_id = {}
    r = get('/api/v1/edge-clusters', ignore_plan=True)
    ec = r.json()['results'][0]
    for e_n in ec['members']:
        edge_node_id[e_n['display_name']] = str(e_n['member_index'])

    edge_cluster_id = r.json()['results'][0]['id']

    request_body = load_json("create_tier1s.json")

    for item in request_body['tier-1s']:
      # Update Route distribution
      item['route_advertisement_types'] = []
      item['route_advertisement_types'].append('TIER1_IPSEC_LOCAL_ENDPOINT')
      item['route_advertisement_types'].append('TIER1_CONNECTED')
      item['route_advertisement_types'].append('TIER1_NAT')
      uri = "/policy/api/v1/infra/tier-1s/" + item['display_name']
      r = patch(uri, item)
      pretty_response(r)

      # Update Edge Cluster (as a locale-service)
      json_body = {}
      json_body['edge_cluster_path'] = '/infra/sites/default/enforcement-points/default/edge-clusters/' + edge_cluster_id
      edge_paths = []
      edge_path1 = '/infra/sites/default/enforcement-points/default/edge-clusters/' + edge_cluster_id + \
                  '/edge-nodes/' + edge_node_id['edgenode-01a']
      edge_paths.append(edge_path1)
      edge_path2 = '/infra/sites/default/enforcement-points/default/edge-clusters/' + edge_cluster_id + \
                  '/edge-nodes/' + edge_node_id['edgenode-02a']
      edge_paths.append(edge_path2)
      json_body['preferred_edge_paths'] = edge_paths

      uri = "/policy/api/v1/infra/tier-1s/" + item['display_name'] + "/locale-services/"

      r = get(uri, ignore_plan=True)
      if r.json()['result_count'] == 0:
        uri = uri + "ls1"
      else:
        ls_id = ""
        for item in r.json()['results']:
          ls_id = item['id']
        uri = uri + ls_id

      r = patch(uri, json_body)
      pretty_response(r)


def setup_infra():
    print("Setup infra")
    log("  |")
    add_vcenter_compute_manager()
    define_TEP_IP_pool()
    create_transport_zone()
    create_transport_node_profile()
    prepare_compute_cluster()
    create_segments('create_segments_for_edges.json')
    add_transport_node()
    create_edge_cluster()
    return True


def delete_infra():
    print("Deleting Infra")
    log ("  |")
    time.sleep(60)
    delete_edge_cluster()
    delete_transport_node()
    delete_segments('create_segments_for_edges.json')
    delete_compute_cluster()
    delete_transport_node_profile()
    delete_transport_zone()
    delete_TEP_IP_pool()
    delete_compute_managers() 
    return True


def configure_switching_and_routing():
    print("Configuring Switching and Routing")
    log("  |")
    update_global_routing_config()
    create_tier1s()
    create_segments('create_l3_segments.json')
    configure_vm_network_and_poweron()
    poweron_kvm_vms()
    configure_kvm_segment_ports()
    create_tier0()
    update_tier1()
    return True


def delete_switching_and_routing():
    print ("Reset switching and routing")
    log("  |")
    delete_kvm_segment_ports()
    poweroff_kvm_vms()
    reset_vm_network_and_poweroff()
    delete_segments('create_l3_segments.json')
    reset_global_routing_config()
    delete_tier1s()
    delete_tier0()
    return True

##############################################################################
# Main
##############################################################################

parser = argparse.ArgumentParser(description='Fast-Forward script to completely configure Lab: NSBU-2020-NSXT-3.0-V7',
                                 formatter_class=argparse.RawTextHelpFormatter)
group = parser.add_mutually_exclusive_group()
group.add_argument('-w', '--workflow', metavar='N', type=str, nargs='+',
                    help=textwrap.dedent('''\
Select one or more number corresponding to the action to perform:
  1: Setup Infra
  2: Configure Switching and Routing
'''))
group.add_argument('-d', '--deleteworkflow', metavar='N', type=str, nargs='+',
                    help=textwrap.dedent('''\
Select one or more number corresponding to the action to perform:
  1. Delete Switching and Routing config
  2. Delete Infra config
'''))
group.add_argument('-a', '--all', dest='all', action='store_true', help='Run everything! Mutually exclusive with -w/--workflow')
parser.add_argument('-p', '--plan', dest='plan', action='store_true', default=False,
                    help='Print only the REST calls with request body if applicable')
parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', default=True,
                    help='Print Verbose log messages')
parser.add_argument('-r', '--response', dest='print_response', action='store_true', default=False,
                    help='Pretty Print Response Body on success of a call')
parser.add_argument('-c', '--cleanup', dest='cleanup', action='store_true', default=False,
                    help='Cleanup all entities!')
args = parser.parse_args()


# Housekeeping
plan = args.plan
verbose = args.verbose
print_response = args.print_response

worklist = []
deletelist = []

# List of supported workflows
work_function = {
    '1': setup_infra,
    '2': configure_switching_and_routing
}

delete_function = {
    '1': delete_switching_and_routing,
    '2': delete_infra,
}

# Do nothing if no arguments are passed
if len(sys.argv)==1:
    sys.exit(1)

# Cleanup if specified and exit
if args.cleanup:
    print('\n[ Cleaning up all entities ]\n')
    for k in sorted(delete_function):
        delete_function[k]()
    sys.exit(0)

# Do everything if specified
if args.all:
    print('\n[ Running all workflows ]\n')
    for k in sorted(work_function):
        work_function[k]()
    sys.exit(0)

if (args.workflow):
    # Run only specified workflows but validate first
    for work in args.workflow:
        if work not in work_function:
            print('Error: \'%s\' Invalid choice!' % work)
            parser.print_help()
            exit()
        worklist.append(work)

    for work in sorted(worklist):
        work_function[work]()
    sys.exit(0)

if (args.deleteworkflow):
    # Run only the specified delete workflows but validate first
    for delwork in args.deleteworkflow:
        if delwork not in delete_function:
            print('Error: \'%s\' Invalid choice!' % delwork)
            parser.print_help()
            exit()
        deletelist.append(delwork)

    for delwork in sorted(deletelist):
        delete_function[delwork]()
    sys.exit(0)

