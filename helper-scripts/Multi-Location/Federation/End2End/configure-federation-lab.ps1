# Copyright 2017-2021 VMware, Inc.  All rights reserved
#
# The BSD-2 license (the "License") set forth below applies to all
# parts of the NSX-T SDK Sample Code project.  You may not use this
# file except in compliance with the License.
# BSD-2 License
# Redistribution and use in source and binary forms, with or
# without modification, are permitted provided that the following
# conditions are met:
#     Redistributions of source code must retain the above
#     copyright notice, this list of conditions and the
#     following disclaimer.
#     Redistributions in binary form must reproduce the above
#     copyright notice, this list of conditions and the
#     following disclaimer in the documentation and/or other
#     materials provided with the distribution.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
# CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
# USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
# AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# Deploys a Federation lab
#
# Sites: NY, Paris, London
# Each site has:
#   1 NSX
#   1 VC
#   2 ESXi
#    - 1 VM in each ESXi
#   1 Edge
#
# Logical Objects:
# Tier-0s:
#    - Global-T0 (Spans Ny, Paris, London) with BGP
#
# Tier-1s:
#    - Global-T1
#    - Ny-T1 with NAT
#    - Paris-T1 with NAT
#    - London-T1 with NAT
#    - Paris-London-T1 NAT
#
# Segments:
#    - Global-Segment
#    - Ny-Segment
#    - Paris-Segment
#    - London-Segment
#
# Groups:
#    - Ny-Group
#    - Paris-Group
#
# Security Policy:
#    - Ny-Paris Policy
#      Rules:
#          - ALLOW SSH from Ny to Paris
#          - ALLOW ICMP from Ny to Paris
#
Set-PowerCLIConfiguration -Scope User -ParticipateInCEIP $true -Confirm:$false
Set-PowerCLIConfiguration -InvalidCertificateAction Ignore -Confirm:$false



# Debug
$DEBUG = 1
$verboseLogFile = "./deploy.log"

# Physical Lab details
$p_vc = "172.16.200.6"
$p_vc_user = "administrator@vmware.local"
$p_vc_pass = "VMware1!"

# Absolute path to OVAs
$VCVAInstallerPath = "/media/disk2/iso"
$NestedESXiApplianceOVA = "/media/disk2/Nested_ESXi7.0_Appliance_Template_v1.ova"

$vc_license = "XXXXX"
$vsphere_license = "XXXXX"
$nsx_license = "XXXXX"

# Deploys only 1 site with GM. Set to 0 for full deployment
$small = 0

# Nested vCenters
$vc_ny = [pscustomobject] @{
  "network" = "VM Network"
  "cluster" = "Management"
  "datastore" = "datastore36"
  "size" = "tiny"
  "display_name" = "vcenter7-ny"
  "ip_address" = "172.16.200.37"
  "username" = "administrator@vsphere.local"
  "root_password" = $p_vc_pass
  "sso_password" = $p_vc_pass
  "dns" = "172.16.200.8"
  "prefix" = "27"
  "gateway" = "172.16.200.33"
  "hostname" = "172.16.200.37"
  "enable_var" = $true
  "domainname" = "vsphere.local"
  "host" = "172.16.200.36"
  "ntp" = $host
  "license" = $vc_license
}

$vc_paris = [pscustomobject] @{
    "network" = "VM Network"
    "cluster" = "Management"
    "datastore" = "datastore36"
    "size" = "tiny"
    "display_name" = "vcenter7-paris"
    "ip_address" = "172.16.200.38"
    "username" = "administrator@vsphere.local"
    "root_password" = $p_vc_pass
    "sso_password" = $p_vc_pass
    "dns" = "172.16.200.8"
    "prefix" = "27"
    "gateway" = "172.16.200.33"
    "hostname" = "172.16.200.38"
    "enable_var" = $true
    "domainname" = "vsphere.local"
    "host" = "172.16.200.36"
    "ntp" = $host
    "license" = $vc_license
}

$vc_london = [pscustomobject] @{
    "network" = "VM Network"
    "cluster" = "Management"
    "datastore" = "datastore36"
    "size" = "tiny"
    "display_name" = "vcenter7-london"
    "ip_address" = "172.16.200.39"
    "username" = "administrator@vsphere.local"
    "root_password" = $p_vc_pass
    "sso_password" = $p_vc_pass
    "dns" = "172.16.200.8"
    "prefix" = "27"
    "gateway" = "172.16.200.33"
    "hostname" = "172.16.200.39"
    "enable_var" = $true
    "domainname" = "vsphere.local"
    "host" = "172.16.200.36"
    "ntp" = $host
    "license" = $vc_license
}

if ($small -eq 1) {
    $nested_vcs = $vc_ny
} else {
    $nested_vcs = $vc_ny, $vc_paris, $vc_london
}

# Common vCenter info
$VCVADatacenter = "datacenter"
$VCVAClusters = "workload-cluster1", "workload-cluster2"
$VCVAVDS = "vds7"

# Common ESXi hosts
$NestedESXivCPU = "4"
$NestedESXivMEM = "12" #GB
$NestedESXiCapacityvDisk = "100" #GB
$NSXVTEPNetwork = "lab-dvpg"


# Common NSX LM deployment vars
$p_nsx_ova = "/media/disk2/nsx-unified-appliance-3.1.0.0.0.17026751.ova"
$p_datacenter = "Datacenter"
$p_cluster = "Management"
$p_datastore = "datastore36"
$p_host = "172.16.200.36"
$p_nsx_size = "small"
$p_nsx_role = "NSX Manager"
$p_nsx_vm_network = "VM Network"
$p_nsx_netmask = "255.255.255.224"
$p_nsx_gateway = "172.16.200.33"
$p_nsx_dns = "10.116.1.201"
$p_nsx_domain = "mylab.local"
$p_nsx_ntp = "172.16.200.8"
$p_nsx_user = "admin"
$p_nsx_audit_user = "audit"
$p_nsx_password = "myPassword1!myPassword1!"
$p_nsx_license = $nsx_license


$nsx_ny = [pscustomobject] @{
    "hostname" = "nsx-ny.mylab.local"
    "display_name" = "nsx-ny"
    "ip" = "172.16.200.41"
    "ova" = $p_nsx_ova
    "datacenter" = $p_datacenter
    "cluster" = $p_cluster
    "datastore" = $p_datastore
    "host" = $p_host
    "size" = $p_nsx_size
    "role" = $p_nsx_role
    "mgmt_network" = $p_nsx_vm_network
    "netmask" = $p_nsx_netmask
    "gateway" = $p_nsx_gateway
    "dns" = $p_nsx_dns
    "domain" = $p_nsx_domain
    "ntp" = $p_nsx_ntp
    "user" = $p_nsx_user
    "password" = $p_nsx_password
    "license" = $p_nsx_license
    "thumbprint" = ""
    "vcenter" = $vc_ny
}

$nsx_paris = [pscustomobject] @{
    "hostname" = "nsx-london.mylab.local"
    "display_name" = "nsx-paris"
    "ip" = "172.16.200.42"
    "ova" = $p_nsx_ova
    "datacenter" = $p_datacenter
    "cluster" = $p_cluster
    "datastore" = $p_datastore
    "host" = $p_host
    "size" = $p_nsx_size
    "role" = $p_nsx_role
    "mgmt_network" = $p_nsx_vm_network
    "netmask" = $p_nsx_netmask
    "gateway" = $p_nsx_gateway
    "dns" = $p_nsx_dns
    "domain" = $p_nsx_domain
    "ntp" = $p_nsx_ntp
    "user" = $p_nsx_user
    "password" = $p_nsx_password
    "license" = $p_nsx_license
    "thumbprint" = ""
    "vcenter" = $vc_paris
}

$nsx_london = [pscustomobject] @{
    "hostname" = "nsx-paris.mylab.local"
    "display_name" = "nsx-london"
    "ip" = "172.16.200.43"
    "ova" = $p_nsx_ova
    "datacenter" = $p_datacenter
    "cluster" = $p_cluster
    "datastore" = $p_datastore
    "host" = $p_host
    "size" = $p_nsx_size
    "role" = $p_nsx_role
    "mgmt_network" = $p_nsx_vm_network
    "netmask" = $p_nsx_netmask
    "gateway" = $p_nsx_gateway
    "dns" = $p_nsx_dns
    "domain" = $p_nsx_domain
    "ntp" = $p_nsx_ntp
    "user" = $p_nsx_user
    "password" = $p_nsx_password
    "license" = $p_nsx_license
    "thumbprint" = ""
    "vcenter" = $vc_london
}

if ($small -eq 1) {
    $nsx_mgrs = $nsx_ny
} else {
    $nsx_mgrs = $nsx_ny, $nsx_paris, $nsx_london
}

$esx1_ny = [pscustomobject] @{
    "name" = "esx1-ny"
    "ip"   = "172.16.200.10"
    "netmask" = "255.255.255.224"
    "gateway" = "172.16.200.1"
    "datastore" = "datastore7"
    "host"   = "172.16.200.7"
    "cluster" = "Management"
    "nestedCluster" = "workload-cluster1"
    "nesteddatastore" = "datastore1ny"
    "vdsType" = "vds"
    "vcenter" = "vcenter7-ny"
}

$esx2_ny = [pscustomobject] @{
    "name" = "esx2-ny"
    "ip"   = "172.16.200.11"
    "netmask" = "255.255.255.224"
    "gateway" = "172.16.200.1"
    "datastore" = "datastore5"
    "host"   = "172.16.200.5"
    "cluster" = "Management"
    "nestedCluster" = "workload-cluster2"
    "nestedDatastore" = "datastore2ny"
    "vdsType" = "nvds"
    "vcenter" = "vcenter7-ny"
}

$esx1_paris = [pscustomobject] @{
    "name" = "esx1-paris"
    "ip"   = "172.16.200.12"
    "netmask" = "255.255.255.224"
    "gateway" = "172.16.200.1"
    "datastore" = "datastore7"
    "host"   = "172.16.200.7"
    "cluster" = "Management"
    "nestedCluster" = "workload-cluster1"
    "nestedDatastore" = "datastore1paris"
    "vdsType" = "vds"
    "vcenter" = "vcenter7-paris"
}

$esx2_paris = [pscustomobject] @{
    "name" = "esx2-paris"
    "ip"   = "172.16.200.13"
    "netmask" = "255.255.255.224"
    "gateway" = "172.16.200.1"
    "datastore" = "datastore4"
    "host"   = "172.16.200.4"
    "cluster" = "Management"
    "nestedCluster" = "workload-cluster2"
    "nestedDatastore" = "datastore2paris"
    "vdsType" = "nvds"
    "vcenter" = "vcenter7-paris"
}

$esx1_london = [pscustomobject] @{
    "name" = "esx1-london"
    "ip"   = "172.16.200.14"
    "netmask" = "255.255.255.224"
    "gateway" = "172.16.200.1"
    "datastore" = "datastore5"
    "host"   = "172.16.200.5"
    "cluster" = "Management"
    "nestedCluster" = "workload-cluster1"
    "nestedDatastore" = "datastore1london"
    "vdsType" = "vds"
    "vcenter" = "vcenter7-london"
}

$esx2_london = [pscustomobject] @{
    "name" = "esx2-london"
    "ip"   = "172.16.200.15"
    "netmask" = "255.255.255.224"
    "gateway" = "172.16.200.1"
    "datastore" = "datastore7"
    "host"   = "172.16.200.7"
    "cluster" = "Management"
    "nestedCluster" = "workload-cluster2"
    "nestedDatastore" = "datastore2london"
    "vdsType" = "nvds"
    "vcenter" = "vcenter7-london"
}

if ($small -eq 1) {
    $nested_esxis = $esx1_ny, $esx2_ny
} else {
    $nested_esxis = $esx1_ny, $esx2_ny, $esx1_paris, $esx2_paris, $esx1_london, $esx2_london
}


# Custom TZs currently not used
$overlay_tz = [PSCustomObject]@{
    "name" = "Overlay-TZ"
    "type" = "OVERLAY"
}

$vlan_tz = [pscustomobject] @{
    "name" = "VLAN-TZ"
    "type" = "VLAN"
}

$tzs = $overlay_tz, $vlan_tz

$p_tep_ip_pool_name = "TEP-IP-Pool"
$p_rtep_ip_pool_name = "RTEP-IP-Pool"


#
# TEP_IPs and RTEP_IPs across locations are on the same network here
# In a typical environment, they are separate routed networks
#

$tep_ip_ny = [pscustomobject] @{
    "name" = $p_tep_ip_pool_name
    "description" = "ip-pool-ny"
    "nsx" = "nsx-ny"
    "start" = "172.16.1.10"
    "end" = "172.16.1.19"
    "cidr" = "172.16.1.0/24"
    "gateway" = "172.16.1.1"
}

$rtep_ip_ny = [pscustomobject] @{
    "name" = $p_rtep_ip_pool_name
    "description" = "RTEP-ip-pool-ny"
    "nsx" = "nsx-ny"
    "start" = "172.17.1.10"
    "end" = "172.17.1.19"
    "cidr" = "172.17.1.0/24"
    "gateway" = "172.17.1.1"
}

$tep_ip_paris = [pscustomobject] @{
    "name" = $p_tep_ip_pool_name
    "description" = "ip-pool-paris"
    "nsx" = "nsx-paris"
    "start" = "172.16.1.20"
    "end" = "172.16.1.29"
    "cidr" = "172.16.1.0/24"
    "gateway" = "172.16.1.1"
}

$rtep_ip_paris = [pscustomobject] @{
    "name" = $p_rtep_ip_pool_name
    "description" = "RTEP-ip-pool-paris"
    "nsx" = "nsx-paris"
    "start" = "172.17.1.20"
    "end" = "172.17.1.29"
    "cidr" = "172.17.1.0/24"
    "gateway" = "172.17.1.1"
}

$tep_ip_london = [pscustomobject] @{
    "name" = $p_tep_ip_pool_name
    "description" = "ip-pool-london"
    "nsx" = "nsx-london"
    "start" = "172.16.1.30"
    "end" = "172.16.1.39"
    "cidr" = "172.16.1.0/24"
    "gateway" = "172.16.1.1"
}

$rtep_ip_london = [pscustomobject] @{
    "name" = $p_rtep_ip_pool_name
    "description" = "RTEP-ip-pool-london"
    "nsx" = "nsx-london"
    "start" = "172.17.1.30"
    "end" = "172.17.1.39"
    "cidr" = "172.17.1.0/24"
    "gateway" = "172.17.1.1"
}

if ($small -eq 1) {
    $tep_ips = $tep_ip_ny, $rtep_ip_ny
} else {
    $tep_ips = $tep_ip_ny, $tep_ip_paris, $tep_ip_london, $rtep_ip_ny, $rtep_ip_paris, $rtep_ip_london
}

# Used by both Host and Edge Transport Nodes
$uplink_profile = [pscustomobject] @{
    "display_name" = "Lab_Uplink_Profile"
    "description" = "Uplink Profile used by both Edge and Host TNs"
    "transport_vlan" = 231
    "uplink" = "uplink-1"
}

# Common Edge VM details
$edge_ova = "/media/disk2/nsx-edge-3.1.0.0.0.17025839.ova"
$edge_size = "small"
$edge_mgmt_network = "VM Network"
$edge_tep_network = "lab-dvpg"
$edge_netmask = "255.255.255.224"
$edge_gateway = "172.16.200.1"
$edge_dns = $p_nsx_dns
$edge_domain = $p_nsx_domain
$edge_ntp = $p_nsx_ntp
$edge_user = $p_nsx_user
$edge_audit_user = $p_nsx_audit_user
$edge_password = $p_nsx_password
$edge_cluster = "Management"
$edge_datacenter = "Datacenter"
$edge_vcpu = "4"
$edge_vmem = "8"
$edge_tep_ip_pool = "TEP-IP-Pool"
$edge_overlay_tz = "nsx-overlay-transportzone"
$edge_vlan_tz = "nsx-vlan-transportzone"
$edge_rtep_tz = "system-owned-vlan-transport-zone-for-rtep"
$edge_uplink_profile = $uplink_profile.display_name
$edge_pnic = "fp-eth0"
$edge_uplink = "uplink-1"
$edge_rtep_vlan = "230"
$edge_rtep_ip_pool = "RTEP-IP-Pool"



$edge_ny = [pscustomobject] @{
    "ova" = $edge_ova
    "name" = "edge-ny"
    "ip" = "172.16.200.17"
    "size" = $edge_size
    "mgmt_network" = $edge_mgmt_network
    "tep_network" = $edge_tep_network
    "hostname" = "edge-ny.lab.local"
    "netmask" = $edge_netmask
    "gateway" = $edge_gateway
    "dns" = $edge_dns
    "domain" = $edge_domain
    "ntp" = $edge_ntp
    "user" = $edge_user
    "password" = $edge_password
    "nsx_ip" = $nsx_ny.ip
    "nsx_user" = $nsx_ny.user
    "nsx_password" = $nsx_ny.password
    "nsx_thumbprint" = $nsx_ny.thumbprint
    "ssh_enabled" = $true
    "audit_user" = $edge_audit_user
    "cluster" = $edge_cluster
    "datacenter" = $edge_datacenter
    "host" = "172.16.200.4"
    "vmem" = $edge_vmem
    "vcpu" = $edge_vcpu
    "tep_ip_pool" = $edge_tep_ip_pool
    "overlay_tz" = $edge_overlay_tz
    "vlan_tz" = $edge_vlan_tz
    "rtep_tz" = $edge_rtep_tz
    "uplink_profile" = $edge_uplink_profile
    "pnic" = $edge_pnic
    "uplink" = $edge_uplink
    "rtep_vlan" = $edge_rtep_vlan
    "rtep_ip_pool" = $edge_rtep_ip_pool
}

$edge_paris = [pscustomobject] @{
    "ova" = $edge_ova
    "name" = "edge-paris"
    "ip" = "172.16.200.18"
    "size" = $edge_size
    "mgmt_network" = $edge_mgmt_network
    "tep_network" = $edge_tep_network
    "hostname" = "edge-paris.lab.local"
    "netmask" = $edge_netmask
    "gateway" = $edge_gateway
    "dns" = $edge_dns
    "domain" = $edge_domain
    "ntp" = $edge_ntp
    "user" = $edge_user
    "password" = $edge_password
    "nsx_ip" = $nsx_paris.ip
    "nsx_user" = $nsx_paris.user
    "nsx_password" = $nsx_paris.password
    "nsx_thumbprint" = $nsx_paris.thumbprint
    "ssh_enabled" = $true
    "audit_user" = $edge_audit_user
    "cluster" = $edge_cluster
    "datacenter" = $edge_datacenter
    "host" = "172.16.200.5"
    "vmem" = $edge_vmem
    "vcpu" = $edge_vcpu
    "tep_ip_pool" = $edge_tep_ip_pool
    "overlay_tz" = $edge_overlay_tz
    "vlan_tz" = $edge_vlan_tz
    "rtep_tz" = $edge_rtep_tz
    "uplink_profile" = $edge_uplink_profile
    "pnic" = $edge_pnic
    "uplink" = $edge_uplink
    "rtep_vlan" = $edge_rtep_vlan
    "rtep_ip_pool" = $edge_rtep_ip_pool
}

$edge_london = [pscustomobject] @{
    "ova" = $edge_ova
    "name" = "edge-london"
    "ip" = "172.16.200.19"
    "size" = $edge_size
    "mgmt_network" = $edge_mgmt_network
    "tep_network" = $edge_tep_network
    "hostname" = "edge-london.lab.local"
    "netmask" = $edge_netmask
    "gateway" = $edge_gateway
    "dns" = $edge_dns
    "domain" = $edge_domain
    "ntp" = $edge_ntp
    "user" = $edge_user
    "password" = $edge_password
    "nsx_ip" = $nsx_london.ip
    "nsx_user" = $nsx_london.user
    "nsx_password" = $nsx_london.password
    "nsx_thumbprint" = $nsx_london.thumbprint
    "ssh_enabled" = $true
    "audit_user" = $edge_audit_user
    "cluster" = $edge_cluster
    "datacenter" = $edge_datacenter
    "host" = "172.16.200.7"
    "vmem" = $edge_vmem
    "vcpu" = $edge_vcpu
    "tep_ip_pool" = $edge_tep_ip_pool
    "overlay_tz" = $edge_overlay_tz
    "vlan_tz" = $edge_vlan_tz
    "rtep_tz" = $edge_rtep_tz
    "uplink_profile" = $edge_uplink_profile
    "pnic" = $edge_pnic
    "uplink" = $edge_uplink
    "rtep_vlan" = $edge_rtep_vlan
    "rtep_ip_pool" = $edge_rtep_ip_pool
}

if ($small -eq 1) {
    $edges = $edge_ny
} else {
    $edges = $edge_ny, $edge_paris, $edge_london
}

$nsx_gm = [pscustomobject] @{
    "hostname" = "nsx-gm.mylab.local"
    "display_name" = "nsx-gm"
    "ip" = "172.16.200.40"
    "ova" = "/media/disk2/nsx-unified-appliance-3.1.0.0.0.17061454.ova"
    "datacenter" = $p_datacenter
    "cluster" = $p_cluster
    "datastore" = $p_datastore
    "host" = $p_host
    "size" = $p_nsx_size
    "role" = "NSX Global Manager"
    "mgmt_network" = $p_nsx_vm_network
    "netmask" = $p_nsx_netmask
    "gateway" = $p_nsx_gateway
    "dns" = $p_nsx_dns
    "domain" = $p_nsx_domain
    "ntp" = $p_nsx_ntp
    "user" = $p_nsx_user
    "password" = $p_nsx_password
    "license" = $p_nsx_license
    "thumbprint" = ""
}

$site_ny = [pscustomobject] @{
    "name" = "nsx-ny"
    "ip" = $nsx_ny.ip
    "thumbprint" = ""
}

$site_paris = [pscustomobject] @{
    "name" = "nsx-paris"
    "ip" = $nsx_paris.ip
    "thumbprint" = ""
}

$site_london = [pscustomobject] @{
    "name" = "nsx-london"
    "ip" = $nsx_london.ip
    "thumbprint" = ""
}

if ($small -eq 1) {
    $sites = $site_ny
} else {
    $sites = $site_ny, $site_paris, $site_london
}

$region = [pscustomobject] @{
    "name" = "nsx-europe"
    "sites" = @("nsx-paris", "nsx-london")
}

if ($small -eq 1) {
    $regions = @()
} else {
    $regions = @($region)
}

$tnp_overlay_tz = "nsx-overlay-transportzone"
$tnp_uplink_profile = $uplink_profile.display_name
$tnp_uplink_name = "uplink-1"
$tnp_vds_uplink_name = "uplink1"
$tnp_vds = "VDS7_TNP"
$tnp_nvds = "NVDS_TNP"
$tnps = @("VDS7_TNP", "NVDS_TNP")


$tnc1 = [pscustomobject] @{
    "display_name" = "cluster1"
    "transport_node_profile_name" = $tnp_vds
    "cluster_name" = "workload-cluster1"

}

$tnc2 = [pscustomobject] @{
    "display_name" = "cluster2"
    "transport_node_profile_name" = $tnp_nvds
    "cluster_name" = "workload-cluster2"
}

$tncs = $tnc1, $tnc2

# Common VM params
$vm_ova = "/var/www/html/centos-base.ova"
$vm_network = "Global-Subnet"

$ny_vm1 = [pscustomobject] @{
    "display_name" = "web1"
    "vc" = $vc_ny
    "ova" = $vm_ova
    "esx" = $esx1_ny
    "network" = $vm_network
}

$ny_vm2 = [pscustomobject] @{
    "display_name" = "web2"
    "vc" = $vc_ny
    "ova" = $vm_ova
    "esx" = $esx2_ny
    "network" = $vm_network
}

$paris_vm1 = [pscustomobject] @{
    "display_name" = "app1"
    "vc" = $vc_paris
    "ova" = $vm_ova
    "esx" = $esx1_paris
    "network" = $vm_network
}

$paris_vm2 = [pscustomobject] @{
    "display_name" = "app2"
    "vc" = $vc_paris
    "ova" = $vm_ova
    "esx" = $esx2_paris
    "network" = $vm_network
}

$london_vm1 = [pscustomobject] @{
    "display_name" = "app3"
    "vc" = $vc_london
    "ova" = $vm_ova
    "esx" = $esx1_london
    "network" = $vm_network
}

$london_vm2 = [pscustomobject] @{
    "display_name" = "db1"
    "vc" = $vc_london
    "ova" = $vm_ova
    "esx" = $esx2_london
}

if ($small -eq 1) {
    $vms = $ny_vm1, $ny_vm2
} else {
    $vms = $ny_vm1, $ny_vm2, $paris_vm1, $paris_vm2, $london_vm1, $london_vm2
}

Function Debug($msg) {
    if ($DEBUG -eq 1) {
        Write-Host -ForegroundColor Cyan "$msg"
    }
}

Function Error($msg) {
    Write-Host -ForegroundColor Red "$msg"
    exit
}


Function deployvCenter($vi) {
    if (!(Test-Path $VCVAInstallerPath)) {
        Error "Unable to find $VCVAInstallerPath ..."
    } else {
        Debug "Found vCenter OVA: $VCVAInstallerPath"
    }
    
    foreach ($vc in $nested_vcs) {
        $exists = get-vm -Server $vi -name $vc.display_name -ErrorAction SilentlyContinue
        $name = $vc.display_name
        If ($exists) {
            Debug "vCenter $name already exists. Skipping deployment ..."  
            continue
        }

        $datastore = Get-Datastore -Server $vi -Name $vc.datastore
        $cluster = Get-Cluster -Server $vi -Name $vc.cluster
        $datacenter = $cluster | Get-Datacenter
        $vmhost = Get-VMHost -Name $vc.host

        #    $config = (Get-Content -Raw "$($VCVAInstallerPath)/vcsa-cli-installer/templates/install/embedded_vCSA_on_VC.json") | convertfrom-json
        $config = (Get-Content -Raw "./embedded_vCSA_on_VC.json") | convertfrom-json

        $config.'new_vcsa'.vc.hostname = $p_vc
        $config.'new_vcsa'.vc.username = $p_vc_user
        $config.'new_vcsa'.vc.password = $p_vc_pass
        $config.'new_vcsa'.vc.deployment_network = $vc.network
        $config.'new_vcsa'.vc.datastore = $vc.datastore
        $config.'new_vcsa'.vc.datacenter = $datacenter.name
        $config.'new_vcsa'.vc.target = $vc.cluster
        $config.'new_vcsa'.appliance.thin_disk_mode = $true
        $config.'new_vcsa'.appliance.deployment_option = $vc.size
        $config.'new_vcsa'.appliance.name = $vc.display_name
        $config.'new_vcsa'.network.ip_family = "ipv4"
        $config.'new_vcsa'.network.mode = "static"
        $config.'new_vcsa'.network.ip = $vc.ip_address
        $config.'new_vcsa'.network.dns_servers[0] = $vc.dns
        $config.'new_vcsa'.network.prefix = $vc.prefix
        $config.'new_vcsa'.network.gateway = $vc.gateway
        $config.'new_vcsa'.network.system_name = $vc.ip_address
        $config.'new_vcsa'.os.password = $vc.root_password
        $config.'new_vcsa'.os.ssh_enable = $true
        $config.'new_vcsa'.sso.password = $vc.sso_password
        $config.'new_vcsa'.sso.domain_name = $vc.domain_name
    
        $config | ConvertTo-Json | Set-Content -Path "/tmp/jsontemplate.json"
        Debug "Installing VCVA $name"
        Invoke-Expression "$($VCVAInstallerPath)/vcsa-cli-installer/lin64/vcsa-deploy install --no-esx-ssl-verify --accept-eula --acknowledge-ceip /tmp/jsontemplate.json"| Out-File -Append  -LiteralPath $verboseLogFile

    }
}

Function assignLicenseTovCenter($conn, $vc) {
    $licenses = @($vc.license, $vsphere_license)

    Debug "Assigning License to vCenter $($vc.ip_address)"
    $licensemanager = get-view ($conn.ExtensionData.Content.LicenseManager)
    foreach ($license in $licenses) {
        $lic = $licensemanager.AddLicense($license, $null)
        $x = $licensemanager.AddLicense
    }

    $licenseassignmentmanager = get-view ($licensemanager.licenseAssignmentManager)
    $lic = $licenseAssignmentmanager.UpdateAssignedLicense($conn.InstanceUuid, $vc.license, $null)
}

Function deployNestedESXiHosts($vc) {
    if (!(Test-Path $NestedESXiApplianceOVA)) {
        Error "Unable to find $NestedESXiApplianceOVA ..."
    } else {
        Debug "Found ESXi OVA: $NestedESXiApplianceOVA"
    }

    Debug "Connecting to Management vCenter Server $VIServer ..."

    foreach ($esx in $nested_esxis) {
        $name = $esx.name
        $ip   = $esx.ip
        $netmask = $esx.netmask
        $gateway = $esx.gateway
        $datastore = Get-Datastore -Server $vc -Name $esx.datastore
        $vmhost = Get-VMHost -Name $esx.host
        $cluster = Get-Cluster -Server $vc -Name $esx.cluster

        Debug "Deploying $name with $ip on $vmhost, $datastore"

        $ovfconfig = Get-OvfConfiguration $NestedESXiApplianceOVA
        $networkMapLabel = ($ovfconfig.ToHashTable().keys | where {$_ -Match "NetworkMapping"}).replace("NetworkMapping.","").replace("-","_").replace(" ","_")
        $ovfconfig.NetworkMapping.$networkMapLabel.value = $VMNetwork

        $ovfconfig.common.guestinfo.hostname.value = $name
        $ovfconfig.common.guestinfo.ipaddress.value = $ip
        $ovfconfig.common.guestinfo.netmask.value = $netmask
        $ovfconfig.common.guestinfo.gateway.value = $gateway
        $ovfconfig.common.guestinfo.dns.value = $esx.dns
        $ovfconfig.common.guestinfo.domain.value = $esx.domain
        $ovfconfig.common.guestinfo.password.value = $p_vc_pass
        $ovfconfig.common.guestinfo.ssh.value = $true

        $exists = Get-VM -Server $vc -name $name -ErrorAction SilentlyContinue  
        If ($exists) {  
             Debug "ESXi host with name $name already  exists. Skipping ..."  
             continue
        }
        Debug "Deploying Nested ESXi VM $name ..."
        $vm = Import-VApp -Server $vc `
                          -Source $NestedESXiApplianceOVA `
                          -OvfConfiguration $ovfconfig `
                          -Name $name `
                          -Location $cluster `
                          -VMHost $vmhost `
                          -Datastore $datastore `
                          -DiskStorageFormat thin `
                          -ErrorAction Stop

        Debug "Updating Network Adapter 2 to $NSXVTEPNetwork ..."
        $myNetworkAdapters = Get-NetworkAdapter -VM $vm -Name "Network adapter 2"
        $myVDPortGroup = Get-VDPortgroup -Name $NSXVTEPNetwork
        Set-NetworkAdapter -NetworkAdapter $myNetworkAdapters -Portgroup $myVDPortGroup -Confirm:$false | Out-File -Append -LiteralPath $verboseLogFile

  
        Debug "Updating vCPU Count to $NestedESXivCPU & vMEM to $NestedESXivMEM GB ..."
        Set-VM -Server $vc -VM $vm -NumCpu $NestedESXivCPU `
               -MemoryGB $NestedESXivMEM -Confirm:$false -ErrorAction Stop | Out-File -Append `
               -LiteralPath $verboseLogFile

        Get-HardDisk -Server $vc -VM $vm -Name "Hard disk 3" `
                     -ErrorAction Stop | Set-HardDisk -CapacityGB $NestedESXiCapacityvDisk `
                     -Confirm:$false | Out-File -Append -LiteralPath $verboseLogFile

        Debug "Powering On $vmname ..."
        $vm | Start-Vm -RunAsync | Out-Null
    }
}

Function createDatacenterCluster($conn, $vc) {
    $d = Get-Datacenter -Server $conn $VCVADatacenter -ErrorAction Ignore
    if( -Not $d) {
        Debug "Creating Datacenter $VCVADatacenter in $($vc.ip_address)"
        New-Datacenter -Server $conn -Name $VCVADatacenter -Location (Get-Folder -Type Datacenter -Server $conn) | Out-File -Append -LiteralPath $verboseLogFile
    } else {
        Debug "Datacenter $VCVADatacenter already exists in $($vc.ip_address). Skipping ..."
    }
    $d = Get-Datacenter -Server $conn $VCVADatacenter -ErrorAction Ignore
    foreach ($cluster in $VCVAClusters) {
        $c = Get-Cluster -Server $conn $cluster -ErrorAction Ignore
        if ( -Not $c) {
            Debug "Creating Cluster $cluster in $($vc.ip_address)"
            New-Cluster -Server $conn -Name $cluster -Location $d | Out-File -Append -LiteralPath  $verboseLogFile
        } else {
            Debug "Cluster $cluster already exists in $($vc.ip_address). Skipping ..."
        }
    }
}

Function addESXiHostsToVC($conn, $vc) {
    foreach ($esx in $nested_esxis) {
        if ($esx.vcenter -eq $vc.display_name) {
            $h = Get-VMHost -Server $conn -Name $esx.ip -ErrorAction Ignore
            if (-Not $h) {
                Debug "Adding $($esx.ip) in $($vc.display_name) under cluster $($esx.nestedCluster)"
                $c = Get-Cluster -Server $conn -Name $esx.nestedCluster
                Add-VMHost -Server $conn -Location $c -User "root" -Password $p_vc_pass -Name $esx.ip -Force | Out-File -Append -Literal $verboseLogFile
            } else {
                Debug "Host $($esx.ip) already in $($vc.display_name). Skipping ..."
            }
        }
    }
}

Function createDatastoresOnNestedESXis($conn, $vc) {
    foreach ($esx in $nested_esxis) {
        $ds = Get-Datastore -Server $conn -VMHost $esx.ip -Name $esx.nestedDatastore -ErrorAction Ignore
        if ( -Not $ds) {
            if ($esx.vcenter -eq $vc.display_name) {
                $luns = Get-ScsiLun -Server $conn -VMHost $esx.ip -LunType disk
                foreach ($lun in $luns) {
                    if ($lun.CapacityGB -eq 100) {
                        Debug "Creating Datastore $($esx.nestedDatastore) on $($esx.ip)"
                        New-Datastore -Server $conn -VMHost $esx.ip -Name $esx.nestedDatastore -Path $lun.CanonicalName -VMFS | Out-File -Append -Literalpath $verboseLogFile
                    }
                }
            }
        } else {
            Debug "Datastore $($esx.nestedDatastore) exists. Skipping ..."
        }
    }
}

Function createAndConfigureVDS($conn, $vc) {

    $vds = Get-VDSwitch -Server $conn -Name $VCVAVDS -ErrorAction Ignore
    if (-Not $vds) {
        Debug "Creating new VDS $VCVAVDS on $($vc.ip_address)"
        $vds = New-VDSwitch -Server $conn -Name $VCVAVDS -Location (Get-DataCenter -Name $VCVADatacenter) -Mtu 1600
    } else {
        Debug "VDS $VCVAVDS already exists. Skipping ..."
    }

    foreach ($esx in $nested_esxis) {
        if ($esx.vcenter -eq $vc.display_name) {
            if ($esx.vdsType -eq "vds" ) {
                $vmhost = Get-VMHost -Server $conn -Name $esx.ip -ErrorAction Ignore
                $vds = $vmhost | Get-VDSwitch
                if ($vds.name -eq $VCVAVDS) {
                    Debug "Host $($esx.ip) already part of VDS $VCVAVDS. Skipping ..."
                } else {
                    Debug "Adding $vmhost to $VCVAVDS"
                    $vds = Get-VDSwitch -Server $conn -Name $VCVAVDS
                    $vds | Add-VDSwitchVMHost -Server $conn -VMHost $vmhost | Out-Null
        
                    $vmhostNetworkAdapter = Get-VMHost -Server $conn $vmhost | Get-VMHostNetworkAdapter -Physical -Name vmnic1
                    $vds | Add-VDSwitchPhysicalNetworkAdapter -Server $conn -VMHostNetworkAdapter $vmhostNetworkAdapter -Confirm:$false
                }
            }
        }
    }
}

Function assignLicenseToESXi ($conn, $vc) {
    $hosts = Get-VMHost -Server $conn
    foreach ($h in $hosts) {
        Debug "Setting vSphere license to $($h.name)"
        $lic = Set-VMHost -VMHost $h -LicenseKey $vsphere_license
    }
}

Function vcenter_config() {
    $p_vi_connection = Connect-VIServer $p_vc -User $p_vc_user -Password $p_vc_pass -WarningAction SilentlyContinue

    deployvCenter $p_vi_connection
    deployNestedESXiHosts $p_vi_connection
    
    Disconnect-VIServer $p_vi_connection -Confirm:$false
    
    foreach ($vc in $nested_vcs) {
        Debug "Connecting to $($vc.display_name)"
        $vc_connection = Connect-VIServer $vc.ip_address -User $vc.username -Password $p_vc_pass -WarningAction SilentlyContinue
    
        assignLicenseTovCenter $vc_connection $vc
        createDatacenterCluster $vc_connection $vc
        addESXiHostsToVC $vc_connection $vc
        createDatastoresOnNestedESXis $vc_connection $vc
        createAndConfigureVDS $vc_connection $vc
        assignLicenseToESXI $vc_connection $vc

        Disconnect-VIServer $vc_connection -Confirm:$false
    }
}

Function deploy_nsx($nsx, $vc) {

    $datastore = Get-Datastore -Server $vc -Name $nsx.datastore | Select-Object -First 1
    $cluster = Get-Cluster -Server $vc -Name $nsx.cluster
    $datacenter = $cluster | Get-Datacenter
    $vmhost = Get-VMHost -Server $vc -Name $nsx.host

    $vm = Get-VM -Server $vc -name $nsx.display_name -ErrorAction SilentlyContinue
    if ($vm) {
        Write-Host "NSX Manager $($nsx.display_name) exists. Skipping ..."
    } else {
        Write-Host "Deploying NSX Manager $($nsx.display_name)"
        $nsx_ovf_config = Get-OvfConfiguration $nsx.ova
        $nsx_ovf_config.DeploymentOption.Value = $nsx.size
        $nsx_ovf_config.NetworkMapping.Network_1.value = $nsx.mgmt_network
        $nsx_ovf_config.Common.nsx_role.Value = $nsx.role
        $nsx_ovf_config.Common.nsx_hostname.Value = $nsx.hostname
        $nsx_ovf_config.Common.nsx_ip_0.Value = $nsx.ip
        $nsx_ovf_config.Common.nsx_netmask_0.Value = $nsx.netmask
        $nsx_ovf_config.Common.nsx_gateway_0.Value = $nsx.gateway
        $nsx_ovf_config.Common.nsx_dns1_0.Value = $nsx.dns
        $nsx_ovf_config.Common.nsx_domain_0.Value = $nsx.domain
        $nsx_ovf_config.Common.nsx_ntp_0.Value = $nsx.ntp
        $nsx_ovf_config.Common.nsx_isSSHEnabled.Value = $true
        $nsx_ovf_config.Common.nsx_allowSSHRootLogin.Value = $true
        $nsx_ovf_config.Common.nsx_passwd_0.Value = $nsx.password
        $nsx_ovf_config.Common.nsx_cli_username.Value = "admin"
        $nsx_ovf_config.Common.nsx_cli_passwd_0.Value = $nsx.password
        $nsx_ovf_config.Common.nsx_cli_audit_username.Value = "audit"
        $nsx_ovf_config.Common.nsx_cli_audit_passwd_0.Value = $nsx.password
        
        $vm = Import-VApp -Server $vc -Source $nsx.ova -OvfConfiguration $nsx_ovf_config `
                          -Name $nsx.display_name -Location $cluster -VMHost $vmhost `
                          -Datastore $nsx.datastore -DiskStorageFormat thin -Force
        if (-Not $vm) {
            exit
        }
        
        # Reducing vMEM, vCPU
        Set-VM -Server $vc -VM $vm -NumCpu "4" -MemoryGB "16" -Confirm:$false | Out-Null

        # Disable vCPU Reservation
        Get-VM -Server $vc -Name $vm | Get-VMResourceConfiguration | Set-VMResourceConfiguration -CpuReservationMhz 0 | Out-Null
    
        $vm | Start-Vm -RunAsync | Out-Null
    }
}

Function is_manager_up ($nsx) {
    $pair = "admin:$($nsx.password)"
    $bytes = [System.Text.Encoding]::ASCII.GetBytes($pair)
    $base64 = [System.Convert]::ToBase64String($bytes)
    $headers = @{
        "Authorization" = "basic $base64"
        "Content-Type" = "application/json"
    }

    $resp = Invoke-WebRequest -Uri "https://$($nsx.ip)/api/v1/cluster-manager/status" -Method GET -Headers $headers -SkipCertificateCheck
    if ($resp.Content.Contains('overall_status')) {
        $r = $resp | convertfrom-json
        if ($r.overall_status -eq "STABLE") {
            Debug "Manager $($nsx.display_name) is UP"
            return 1
        }
    }
    return 0
}
Function wait_for_manager ($nsx) {
    $count = 0
    Debug "Waiting for $($nsx.display_name) to be ready ..."
    do {
        $bool = is_manager_up $nsx
        $count ++
        if ($bool -eq 0) {
            Debug "Retry after 1 minute ..."
            Start-Sleep -s 60 # Sleep 60 secs
        }
    } until ($bool -eq 1 -or $count -eq 10) # Wait for max 10 mins per NSX

    if ($bool -eq 0) {
        Debug "Timeout waiting for Manager $($nsx.display_name) to be ready! Abort! ..."
        exit
    }

}

Function assign_license ($n, $nsx) {
    $eulaService = Get-NsxtService -Server $n -Name "com.vmware.nsx.eula.accept"
    $eulaService.create()

    $LicenseService = Get-NsxtService -Server $n -Name "com.vmware.nsx.licenses"
    $LicenseSpec = $LicenseService.Help.create.license.Create()
    $LicenseSpec.license_key = $nsx.license
    Debug "Assigning license to $($nsx.display_name)"
    $LicenseResult = $LicenseService.create($LicenseSpec)
}

Function accept_eula_ceip ($n, $nsx) {
    Debug "Accepting EULA on $($nsx.display_name)"
    $eulaService = Get-NsxtService -Server $n -Name "com.vmware.nsx.eula.accept"
    $eulaService.create()

    Debug "Accepting CEIP on $($nsx.display_name)"
    $ceipAgreementService = Get-NsxtService -Server $n -Name "com.vmware.nsx.telemetry.agreement"
    $ceipAgreementSpec = $ceipAgreementService.get()
    $ceipAgreementSpec.telemetry_agreement_displayed = $true
    $agreementResult = $ceipAgreementService.update($ceipAgreementSpec)
}

Function create_transport_zone ($n, $nsx, $tzs) {
    foreach ($tz in $tzs) {
        $tz_service = Get-NsxtService -Server $n -Name "com.vmware.nsx.transport_zones"
        $t = $tz_service.list().results | WHere-Object { $_.display_name -eq $tz.name}
        if ($t) {
            Debug "Transport Zone $($tz.name) already exists. Skipping ..."
            continue
        }
        $tz_spec = $tz_service.help.create.transport_zone.Create()
        $tz_spec.display_name = $tz.name
        $tz_spec.transport_type = $tz.type
        Debug "Creating $($tz.name) on $($nsx.display_name)"
        $transport_zone = $tz_service.create($tz_spec)
    }
}

Function create_tep_ips ($n, $nsx, $tep_ips) {
    foreach ($tep_ip in $tep_ips) {
        if ($tep_ip.nsx -eq $nsx.display_name) {

            $ip_pool_service = Get-NsxtPolicyService -Server $n -Name "com.vmware.nsx_policy.infra.ip_pools"
            $ip_pool = ($ip_pool_service.list().results | Where-Object { $_.display_name -eq $tep_ip.name })
            if ($ip_pool) {
                Debug "IP Pool $($tep_ip.name) found on $($nsx.display_name). Skipping ..."
                continue
            }

            $subnet_service = Get-NsxtPolicyService -Server $n -Name "com.vmware.nsx_policy.infra.ip_pools.ip_subnets"
            $subnet_spec = $subnet_service.Help.patch.ip_address_pool_subnet.ip_address_pool_static_subnet.Create()
            $allocation_spec = $subnet_service.Help.patch.ip_address_pool_subnet.ip_address_pool_static_subnet.allocation_ranges.Element.Create()
            $allocation_spec.start = $tep_ip.start
            $allocation_spec.end = $tep_ip.end
            $result = $subnet_spec.allocation_ranges.Add($allocation_spec)
            $subnet_spec.cidr = $tep_ip.cidr
            $subnet_spec.gateway_ip = $tep_ip.gateway
            $subnet_spec.display_name = $tep_ip.name + "_subnet"

            $ip_pool_spec = $ip_pool_service.Help.patch.ip_address_pool.Create()
            $ip_pool_spec.display_name = $tep_ip.name
            $ip_pool_spec.description = $teip_ip.description
            Debug ("Creating IP Pool $($tep_ip.name) to $($nsx.display_name) ...")
            $result = $ip_pool_service.patch($tep_ip.name, $ip_pool_spec)
            $result = $subnet_service.patch($tep_ip.name, $subnet_spec.display_name, $subnet_spec)

        }
    }
}

Function create_uplink_profile ($n, $nsx, $uplink_profile) {
    $upservice = Get-NsxtService -Server $n -Name "com.vmware.nsx.host_switch_profiles"
    $upprofile = ($upservice.list().results | Where-Object { $_.display_name -eq $uplink_profile.display_name})
    if ($upprofile) {
        Debug "Uplink Profile $($uplink_profile.display_name) found on $($nsx.display_name). Skipping ..."
        continue
    }

    $uplink = [pscustomobject] @{
        "uplink_name" = $uplink_profile.uplink
        "uplink_type" = "PNIC"
    }
    $teaming = [pscustomobject] @{
        "policy" = "FAILOVER_ORDER"
        "active_list" = @($uplink)
    }
    $upspec = $upservice.Help.create.base_host_switch_profile.uplink_host_switch_profile.Create()
    $upspec.display_name = $uplink_profile.display_name
    $upspec.description = $uplink_profile.description
    $upspec.transport_vlan = $uplink_profile.transport_vlan
    $upspec.teaming = $teaming

    Debug "Creating Uplink Profile $($uplink_profile.display_name) on $($nsx.display_name)"
    $upp = $upservice.Create($upspec)
}

Function deploy_edge_vm ($edge, $vc) {
    $edge_vm = Get-VM -Server $vc -Name $edge.name -ErrorAction SilentlyContinue
    if ($edge_vm) {
        Debug "Edge $($edge.name) exist. Skipping ..."
        return
    }
    Debug "Connecting to $($edge.nsx_ip) ..."
    $n = Connect-NsxtServer -Server $edge.nsx_ip -Username $p_nsx_user -Password $p_nsx_password -WarningAction SilentlyContinue
    $nsx_id = ((Get-NsxtService -Server $n -Name "com.vmware.nsx.cluster.nodes").list().results | where-object {$_.manager_role -ne $null}).id
    $edge.nsx_thumbprint = (Get-NsxtService -Server $n -Name "com.vmware.nsx.cluster.nodes").get($nsx_id).manager_role.api_listen_addr.certificate_sha256_thumbprint

    $ova_config = Get-OvfConfiguration -Server $vc $edge.ova
    $ova_config.DeploymentOption.Value = $edge.size
    $ova_config.NetworkMapping.Network_0.value = $edge.mgmt_network
    $ova_config.NetworkMapping.Network_1.value = $edge.tep_network
    $ova_config.NetworkMapping.Network_2.value = $edge.mgmt_network
    $ova_config.NetworkMapping.Network_3.value = $edge.mgmt_network
    $ova_config.Common.nsx_hostname.Value = $edge.hostname
    $ova_config.Common.nsx_ip_0.value = $edge.ip
    $ova_config.Common.nsx_netmask_0.value = $edge.netmask
    $ova_config.Common.nsx_gateway_0.value = $edge.gateway
    $ova_config.Common.nsx_dns1_0.Value = $edge.dns
    $ova_config.Common.nsx_domain_0.Value = $edge.domain
    $ova_config.Common.nsx_ntp_0.value = $edge.ntp
    $ova_config.Common.mpUser.value = $edge.user
    $ova_config.Common.mpPassword.value = $edge_password
    $ova_config.Common.mpIp.value = $edge.nsx_ip
    $ova_config.Common.mpThumbprint.value = $edge.nsx_thumbprint
    $ova_config.Common.nsx_isSSHEnabled.value = $true
    $ova_config.Common.nsx_allowSSHRootLogin.Value = $true
    $ova_config.Common.nsx_passwd_0.value = $edge.password
    $ova_config.Common.nsx_cli_username.value = $edge.user
    $ova_config.Common.nsx_cli_passwd_0.value = $edge.password
    $ova_config.Common.nsx_cli_audit_username.value = $edge.user
    $ova_config.Common.nsx_cli_audit_passwd_0.value = $edge.password

    $vmhost = Get-VMhost -Server $vc -Name $edge.host
    $datastore = $vmhost | Get-Datastore

    Debug "Deploy Edge $($edge.name)"
    $edge_vm = Import-VApp -Server $vc -Source $edge.ova -OvfCOnfiguration $ova_config -Name $edge.name -Location $edge.cluster -VMHost $vmhost -Datastore $datastore -DiskStorageFormat thin -Force
    $result = Set-VM -Server $vi -VM $edge_vm -NumCpu $edge.vcpu -MemoryGB $edge.vmem -Confirm:$false | Out-File -Append -LiteralPath $verboseLogFile
    $edge_vm | Start-Vm -RunAsync | Out-Null

    Disconnect-NsxtServer -Server $edge.nsx_ip -Confirm:$false
}

Function is_edge_node_ready ($node_id, $tn_state_service) {
  if ($tn_state_service.get($node_id).state -eq "success") {
      return $true
  } else {
      return $false
  }
}

Function get_default_edge_uplink_profile ($edge) {
    $pair = "$($edge.nsx_user):$($edge.nsx_password)"
    $bytes = [System.Text.Encoding]::ASCII.GetBytes($pair)
    $base64 = [System.Convert]::ToBase64String($bytes)

    $headers = @{
        "Authorization" = "basic $base64"
        "Content-Type" = "application/json"
    }

    $url = "https://$($edge.nsx_ip)/api/v1/host-switch-profiles?include_system_owned=true&hostswitch_profile_type=UplinkHostSwitchProfile"
    $response = Invoke-WebRequest -Uri $url -Method GET -Headers $headers -SkipCertificateCheck

    $hsps = $response.Content | ConvertFrom-Json -Depth 10

    foreach ($hsp in $hsps.results) {
        if ($hsp.display_name -eq $edge.uplink_profile) {
            return $hsp.id
        }
    }
    return ""
}

Function create_edge_tn ($edge) {
    Debug "Connecting to NSX $($edge.nsx_ip)"
    $n = Connect-NsxtServer -Server $edge.nsx_ip -Username $edge.nsx_user -Password $edge.nsx_password -WarningAction SilentlyContinue

    $tn_service = Get-NsxtService -Server $n -Name "com.vmware.nsx.transport_nodes"
    $tn_state_service = Get-NsxtService -Server $n -Name "com.vmware.nsx.transport_nodes.state"

    $edge_cluster_service = Get-NsxtService -Server $n -Name "com.vmware.nsx.edge_clusters"
    $edge_cluster_state_service = Get-NsxtService -Server $n -Name "com.vmware.nsx.edge_clusters.state"

    $edge_members_spec = $edge_cluster_service.help.create.edge_cluster.members.Create()

    $edge_nodes = $tn_service.list().results | Where-Object {$_.node_deployment_info.resource_type -eq "EdgeNode"}
    # Need to get the MP UUID of the TEP IP Pool. Use the MP class here instead of the Policy class
    $ip_pool = (Get-NsxtService -Server $n -Name "com.vmware.nsx.pools.ip_pools").list().results | Where-Object {$_.display_name -eq $edge.tep_ip_pool}
    $rtep_ip_pool = (Get-NsxtService -Server $n -Name "com.vmware.nsx.pools.ip_pools").list().results | Where-Object {$_.display_name -eq $edge.rtep_ip_pool}
    $overlay_tz = (Get-NsxtService -Server $n -Name "com.vmware.nsx.transport_zones").list().results | Where-Object {$_.display_name -eq $edge.overlay_tz}
    $vlan_tz = (Get-NsxtService -Server $n -Name "com.vmware.nsx.transport_zones").list().results | Where-Object {$_.display_name -eq $edge.vlan_tz}
    $rtep_tz = (Get-NsxtService -Server $n -Name "com.vmware.nsx.transport_zones").list($null,$true).results | Where-Object {$_.display_name -eq $edge.rtep_tz}
    $uplink_profile = (Get-NsxtService -Server $n -Name "com.vmware.nsx.host_switch_profiles").list().results | Where-Object {$_.display_name -eq $edge.uplink_profile}
    $uplink_profile_id = $uplink_profile.id

    foreach ($node in $edge_nodes) {
        if ($node.host_switch_spec) {
            if (is_edge_node_ready $node.node_id $tn_state_service) {
                Debug "Edge $($edge.name) ready. Skipping ..."
            }
        } else {
            $ip_assignment_spec = [pscustomobject] @{
                "resource_type" = "StaticIpPoolSpec";
                "ip_pool_id" = $ip_pool.id;
            }

            $rtep_ip_assignment_spec = [pscustomobject] @{
                "resource_type" = "StaticIpPoolSpec";
                "ip_pool_id" = $rtep_ip_pool.id;
            }

            $overlay_tz_id = [PSCustomObject] @{
                "transport_zone_id" = $overlay_tz.id
            }

            $vlan_tz_id = [PSCustomObject] @{
                "transport_zone_id" = $vlan_tz.id
            }

            $rtep_tz_id = [PSCustomObject] @{
                "transport_zone_id" = $rtep_tz.id
            }

            $host_switch = [pscustomobject] @{
                "host_switch_name" = "nsxvswitch";
                "host_switch_mode" = "STANDARD";
                "ip_assignment_spec" = $ip_assignment_spec
                "pnics" = @(@{"device_name"=$edge.pnic; "uplink_name"=$edge.uplink;})
                "host_switch_profile_ids" = @(@{"key"="UplinkHostSwitchProfile";"value"=$uplink_profile_id})
                "transport_zone_endpoints" = @($overlay_tz_id, $vlan_tz_id, $rtep_tz_id)
            }

            $json = [pscustomobject] @{
                "resource_type" = "TransportNode";
                "node_id" = $node.id;
                "display_name" = $node.display_name;
                "host_switch_spec" = [pscustomobject] @{
                    "resource_type" = "StandardHostSwitchSpec";
                    "host_switches" = @($host_switch)
                };
                "remote_tunnel_endpoint" = [pscustomobject] @{
                    "host_switch_name" = "nsxvswitch";
                    "rtep_vlan" = $edge.rtep_vlan;
                    "ip_assignment_spec" = $rtep_ip_assignment_spec
                };
            }

            $body = $json | ConvertTo-Json -Depth 10

            $pair = "$($edge.nsx_user):$($edge.nsx_password)"
            $bytes = [System.Text.Encoding]::ASCII.GetBytes($pair)
            $base64 = [System.Convert]::ToBase64String($bytes)

            $headers = @{
                "Authorization" = "basic $base64"
                "Content-Type" = "application/json"
            }

            $tn_url = "https://$($edge.nsx_ip)/api/v1/transport-nodes"
            try {
                $request = Invoke-WebRequest -Uri $tn_url -Body $body -Method POST -Headers $headers -SkipCertificateCheck
            } catch {
                Debug "Error during Edge ${$edge.name} Transport Node creation"
                Debug "`n($_.Exception.Message)`n"
                exit
            }
            if ($request.StatusCode -eq 201) {
                Debug "Successfully Created Edge Transport Node ${$edge.name}"
            } else {
                Debug "Unknown State during ${$edge.name} Transport Node creation: $requests"
                exit
            }
        }
    }
    Disconnect-NsxtServer -Server $edge.nsx_ip -Confirm:$false
}

Function create_edge_cluster ($edge) {
    Debug "Connecting to NSX $($edge.nsx_ip)"
    $n = Connect-NsxtServer -Server $edge.nsx_ip -Username $edge.nsx_user -Password $edge.nsx_password -WarningAction SilentlyContinue

    $tn_service = Get-NsxtService -Server $n -Name "com.vmware.nsx.transport_nodes"
    $tn_state_service = Get-NsxtService -Server $n -Name "com.vmware.nsx.transport_nodes.state"

    $edge_cluster_service = Get-NsxtService -Server $n -Name "com.vmware.nsx.edge_clusters"
    $edge_cluster_state_service = Get-NsxtService -Server $n -Name "com.vmware.nsx.edge_clusters.state"

    $edge_members_spec = $edge_cluster_service.help.create.edge_cluster.members.Create()
    $edge_nodes = $tn_service.list().results | Where-Object {$_.node_deployment_info.resource_type -eq "EdgeNode"}

    foreach ($node in $edge_nodes) {
        $edge_node_member_spec = $edge_cluster_service.help.create.edge_cluster.members.Element.Create()
        $edge_node_member_spec.transport_node_id = $node.id
        $result = $edge_members_spec.Add($edge_node_member_spec)
    }

    $edge_cluster_spec = $edge_cluster_service.help.create.edge_cluster.Create()
    $edge_cluster_spec.display_name = "Edge-Cluster"
    $edge_cluster_spec.members = $edge_members_spec
    if ($edge_cluster_service.list().results[0].display_name -eq "Edge-Cluster") {
        Debug "Edge Cluster created. Skipping ..."
    } else {
        $edge_cluster = $edge_cluster_service.Create($edge_cluster_spec)

        $edge_state = $edge_cluster_state_service.get($edge_cluster.id)
        $maxCount=5
        $count=0
        while($edge_state.state -ne "in_sync") {
            Debug "Edge Cluster has not been realized, sleeping for 10 seconds ..."
            Start-Sleep -Seconds 10
            $edge_state = $edge_cluster_state_service.get($edge_cluster.id)
    
            if($count -eq $maxCount) {
                Debug "Time out during Edge Cluster realization! exiting ..."
                exit
            } else {
                $count++
            }
        }
        # Need to force Policy API sync to ensure Edge Cluster details are available for later use
        $reload_Op = (Get-NsxtPolicyService -Server $n -Name "com.vmware.nsx_policy.infra.sites.enforcement_points").reload("default","default")
        Debug "Edge Cluster has been realized"
    } 
    Disconnect-NsxtServer -Server $edge.nsx_ip -Confirm:$false
}

Function edge_config () {
    Debug "Connecting to $p_vc ..."
    $p_vi_connection = Connect-VIServer $p_vc -User $p_vc_user -Password $p_vc_pass -WarningAction SilentlyContinue 

    foreach ($edge in $edges) {
        deploy_edge_vm $edge $p_vi_connection
        create_edge_tn $edge
        create_edge_cluster $edge
    }
}

Function nsx_config() {
  $p_vi_connection = Connect-VIServer $p_vc -User $p_vc_user -Password $p_vc_pass -WarningAction SilentlyContinue

  foreach ($nsx in $nsx_mgrs) {
      deploy_nsx $nsx $p_vi_connection
  }

  foreach ($nsx in $nsx_mgrs) {
      wait_for_manager $nsx
  }

  foreach ($nsx in $nsx_mgrs) {
      Debug "Connecting to NSX Manager $($nsx.display_name)"

      $n = Connect-NsxtServer -Server $nsx.ip -Username $nsx.user -Password $nsx.password -WarningAction SilentlyContinue

      assign_license $n $nsx
      accept_eula_ceip $n $nsx
      create_tep_ips $n $nsx $tep_ips
      create_uplink_profile $n $nsx $uplink_profile

      Disconnect-NsxtServer -Server $nsx.ip -Confirm:$false
  }

  Disconnect-VIServer $p_vi_connection -Confirm:$false
}


Function patch ($url, $user, $pass, $body) {

    $pair = "$($user):$($pass)"
    $bytes = [System.Text.Encoding]::ASCII.GetBytes($pair)
    $base64 = [System.Convert]::ToBase64String($bytes)

    $headers = @{
        "Authorization" = "basic $base64"
        "Content-Type" = "application/json"
    }

    try {
        $request = Invoke-WebRequest -Uri $url -Body $body -Method PATCH -Headers $headers -SkipCertificateCheck
    } catch {
        Debug "Error when doing a PATCH on $url with $body"
        Debug "`n($_.Exception.Message)`n"
        exit
    }
    if ($request.StatusCode -eq 201 -or $request.StatusCode -eq 200) {
        Debug "Successfully ran PATCH $url"
    } else {
        Debug "Unknown State during PATCH $url : $requests"
        exit
    }
}

Function put ($url, $user, $pass, $body) {

    $pair = "$($user):$($pass)"
    $bytes = [System.Text.Encoding]::ASCII.GetBytes($pair)
    $base64 = [System.Convert]::ToBase64String($bytes)

    $headers = @{
        "Authorization" = "basic $base64"
        "Content-Type" = "application/json"
    }

    try {
        $request = Invoke-WebRequest -Uri $url -Body $body -Method PUT -Headers $headers -SkipCertificateCheck
    } catch {
        Debug "Error when doing a PUT $url with $body"
        Debug "`n($_.Exception.Message)`n"
        exit
    }
    if ($request.StatusCode -eq 201 -or $request.StatusCode -eq 200) {
        Debug "Successfully ran PUT $url"
    } else {
        Debug "Unknown State during PUT $url : $requests"
        exit
    }
}

Function post ($url, $user, $pass, $body, $return_error=$false) {
    $pair = "$($user):$($pass)"
    $bytes = [System.Text.Encoding]::ASCII.GetBytes($pair)
    $base64 = [System.Convert]::ToBase64String($bytes)

    $headers = @{
        "Authorization" = "basic $base64"
        "Content-Type" = "application/json"
    }

    try {
        $request = Invoke-WebRequest -Uri $url -Body $body -Method POST -Headers $headers -SkipCertificateCheck 
    } catch {
        if ($return_error) {
            return "`n($_)`n"
            return "`n($_.Exception.Message)`n"
        }
        Debug "Error when doing a PUT $url with $body"
        Debug "`n($_.Exception.Message)`n"
        exit
    }

    if ($request.StatusCode -eq 201 -or $request.StatusCode -eq 200) {
        Debug "Successfully ran POST $url"
    } else {
        Debug "Unknown State during PUT $url : $requests"
        exit
    }

}

Function get ($url, $user, $pass) {
    $pair = "$($user):$($pass)"
    $bytes = [System.Text.Encoding]::ASCII.GetBytes($pair)
    $base64 = [System.Convert]::ToBase64String($bytes)

    $headers = @{
        "Authorization" = "basic $base64"
        "Content-Type" = "application/json"
    }

    try {
        $response = Invoke-WebRequest -Uri $url -Method GET -Headers $headers -SkipCertificateCheck
    } catch {
        Debug "Error when doing GET $url"
        Debug "`n($_.Exception.Message)`n"
        exit
    }
    return $response
}

Function enable_gm_service ($nsx_gm) {
    Debug "Enable Global Manager service ..."

    $id = "GM"
    $json = [pscustomobject] @{
        "id" = $id;
        "mode" = "ACTIVE"
    }

    $body = $json | ConvertTo-Json -Depth 10
    $gm_url = "https://$($nsx_gm.ip)/global-manager/api/v1/global-infra/global-managers/$id"

    patch $gm_url $nsx_gm.user $nsx_gm.password $body
}


Function get_thumbprints () {
    foreach ($site in $sites) {
        $url = "https://$($site.ip)/api/v1/cluster/nodes"

        $result = get $url $p_nsx_user $p_nsx_password
        $data = $result.Content
        $j = ConvertFrom-Json $data
        foreach ($r in $j.results) {
            if ($r.manager_role) {
                $site.thumbprint = $r.manager_role.api_listen_addr.certificate_sha256_thumbprint
                break
            }
        }
    }
}

Function add_locations() {
    foreach ($site in $sites) {
        $url = "https://$($nsx_gm.ip)/global-manager/api/v1/global-infra/sites"
        $result = get $url $p_nsx_user $p_nsx_password
        $j = ConvertFrom-json $result.Content
        $found = 0
        foreach ($r in $j.results) {
            if ($r.display_name -eq $site.name) {
                $found = 1
                break
            }
        }

        if ($found) {
            Debug "Site $($site.name) found. Skipping ..."
        } else {
            $url = "https://$($nsx_gm.ip)/global-manager/api/v1/global-infra/sites/$($site.name)"
            $sci = [pscustomobject] @{
                "fqdn" = $site.ip
                "username" = $p_nsx_user
                "password" = $p_nsx_password
                "thumbprint" = $site.thumbprint
            }
            $json = [pscustomobject] @{
                "display_name" = $site.name
                "site_connection_info" = @($sci)
            }
            $body = ConvertTo-Json $json
            $r = put $url $p_nsx_user $p_nsx_password $body
        }
    }
}

Function get_enforcement_point_path ($site_name) {
    $url = "https://$($nsx_gm.ip)/global-manager/api/v1/global-infra/sites/$site_name/enforcement-points"
    $r = get $url $p_nsx_user $p_nsx_password
    $j = ConvertFrom-Json $r.Content
    return $j.results[0].path
}

Function add_regions () {
    $site_to_path = @{}
    foreach ($site in $sites) {
        $path = get_enforcement_point_path $($site.name)
        $site_to_path[$($site.name)] = $path
    }

    foreach ($region in $regions) {
        $url = "https://$($nsx_gm.ip)/global-manager/api/v1/global-infra/domains"
        $r = get $url $p_nsx_user $p_nsx_password
        $j = ConvertFrom-Json $r.Content
        $found = 0
        foreach ($r_obj in $j.results) {
            if ($r_obj.display_name -eq $region.name) {
                Debug "Region $($region.name) found. Skipping ..."
                $found = 1
                break
            }
        }
        if ($found) {
            continue
        }

        $json = [pscustomobject] @{
            "display_name" = $region.name
        } 
        $body = ConvertTo-Json $json
        $url = "https://$($nsx_gm.ip)/global-manager/api/v1/global-infra/domains/$($region.name)"
        $r = patch $url $p_nsx_user $p_nsx_password $body

        foreach ($site in $region.sites) {
            $path = $site_to_path[$site]
            $url = "https://$($nsx_gm.ip)/global-manager/api/v1/global-infra/domains/$($region.name)/domain-deployment-maps/$site"
            $json = [pscustomobject] @{
                "display_name" = $site
                "enforcement_point_path" = $path
            }
            $body = ConvertTo-Json $json
            $r = patch $url $p_nsx_user $p_nsx_password $body
        }
    }
}

Function nsx_gm_config() {
    $p_vi_connection = Connect-VIServer $p_vc -User $p_vc_user -Password $p_vc_pass -WarningAction SilentlyContinue

    deploy_nsx $nsx_gm $p_vi_connection
    Start-Sleep 180
    wait_for_manager $nsx_gm

    Debug "Connecting to NSX Manager $($nsx_gm.display_name)"
    $n = Connect-NsxtServer -Server $nsx_gm.ip -Username $nsx_gm.user -Password $nsx_gm.password -WarningAction SilentlyContinue

    assign_license $n $nsx_gm
    accept_eula_ceip $n $nsx_gm
    enable_gm_service $nsx_gm
    get_thumbprints
    add_locations
    add_regions

    Disconnect-NsxtServer -Server $nsx_gm.ip -Confirm:$false

    Disconnect-VIServer $p_vi_connection -Confirm:$false
}

Function register_compute_managers () {
    foreach ($nsx in $nsx_mgrs) {
        $vc = $nsx.vcenter
        $url = "https://$($nsx.ip)/api/v1/fabric/compute-managers"
        $res = get $url $nsx.user $nsx.password
        $j = ConvertFrom-Json $res
        $found = 0
        foreach ($r_obj in $j.results) {
            if ($r_obj.display_name -eq $vc.display_name) {
                Debug "Compute Manager $($vc.display_name) found. Skipping ..."
                $found = 1
                break
            }
        }
        if ($found) {
            continue
        }

        $json = [pscustomobject] @{
            "display_name" = $vc.display_name
            "server" = $vc.ip_address
            "origin_type" = "vCenter"
            "credential" = [pscustomobject] @{
                "credential_type" = "UsernamePasswordLoginCredential"
                "username" = $vc.username
                "password" = $vc.root_password
                "thumbprint" = ""
            }
        }
        $body = ConvertTo-Json $json
        $res = post $url $nsx.user $nsx.password $body $true

        # See if response has Thumbprint
        if ($res.Contains("ValidCmThumbPrint")) {
            $res = $res.Replace("(","")
            $res = $res.Replace(")","")
            $j = ConvertFrom-Json $res

            $json.credential.thumbprint = $j.error_data.ValidCmThumbPrint
            $body = ConvertTo-Json $json

            # Retry with Thumbprint
            $res = post $url $nsx.user $nsx.password $body

        } else {
            Debug "Unknown error during POST $url"
            Debug $res
            exit
        }
    }
}

Function create_transport_node_profiles () {
    foreach ($nsx in $nsx_mgrs) {
        Debug "Connecting to NSX $($nsx.display_name) to create Transport Node Profiles"
        $vc = $nsx.vcenter
        $n = Connect-NsxtServer -Server $nsx.ip -User $nsx.user -Password $nsx.password -WarningAction SilentlyContinue

        $vi = connect-viserver $vc.ip_address -User $vc.username -Password $vc.root_password -WarningAction SilentlyContinue
        $vds = (Get-VDSwitch -Server $vi -Name $VCVAVDS).ExtensionData
        Disconnect-VIServer $vi -Confirm:$false

        $ip_pool = (Get-NsxtService -Server $n -Name "com.vmware.nsx.pools.ip_pools").list().results | where-object { $_.display_name -eq $p_tep_ip_pool_name}
        $overlay_tz = (Get-NsxtService -Server $n -Name "com.vmware.nsx.transport_zones").list().results | Where-Object { $_.display_name -eq $tnp_overlay_tz}
        $uplink_profile = (Get-NsxtService -Server $n -Name "com.vmware.nsx.host_switch_profiles").list($null, $null, $null, $true).results | WHere-Object { $_.display_name -eq $tnp_uplink_profile}

        $ip_assignment_spec = [pscustomobject] @{
            "resource_type" = "StaticIpPoolSpec"
            "ip_pool_id" = $ip_pool.id
        }

        $tz_endpoints = @(@{"transport_zone_id" = $overlay_tz.id})

        foreach ($tnp_name in $tnps) {

            $tnp = (Get-NsxtService -Server $n -Name "com.vmware.nsx.transport_node_profiles").list().results | Where-Object {$_.display_name -eq $tnp_name}
            if ($tnp) {
                Debug "Transport Node Profile $tnp_name found on $($nsx.display_name). Skipping ..."
                continue
            }

            if ($tnp_name -eq "VDS7_TNP") {
                $host_switch = [pscustomobject] @{
                    "host_switch_name" = "nsxvswitch"
                    "host_switch_mode" = "STANDARD"
                    "host_switch_type" = "VDS"
                    "host_switch_id" = $vds.Uuid
                    "uplinks" = @(@{"uplink_name" = $tnp_uplink_name; "vds_uplink_name" = $tnp_vds_uplink_name})
                    "ip_assignment_spec" = $ip_assignment_spec
                    "host_switch_profile_ids" = @(@{"key" = "UplinkHostSwitchProfile"; "value" = $uplink_profile.id})
                    "transport_zone_endpoints" = $tz_endpoints
                }
            } elseif ($tnp_name -eq "NVDS_TNP") {
                $host_switch = [pscustomobject] @{
                    "host_switch_name" = "nsxvswitch"
                    "host_switch_mode" = "STANDARD"
                    "host_switch_type" = "NVDS"
                    "pnics" = @(@{"uplink_name" = $tnp_uplink_name; "device_name" = "vmnic1"})
                    "ip_assignment_spec" = $ip_assignment_spec
                    "host_switch_profile_ids" = @(@{"key" = "UplinkHostSwitchProfile"; "value" = $uplink_profile.id})
                    "transport_zone_endpoints" = $tz_endpoints
                }
            }
            $json = [pscustomobject] @{
                "resource_type" = "TransportNode"
                "display_name" = $tnp_name
                "host_switch_spec" = [pscustomobject] @{
                    "host_switches" = @($host_switch)
                    "resource_type" = "StandardHostSwitchSpec"
                }
            }

            $body = $json | ConvertTo-Json -Depth 10
            $url = "https://$($nsx.ip)/api/v1/transport-node-profiles"
            Debug "Creating Transport Node Profile $tnp_name"
            $res = post $url $nsx.user $nsx.password $body
        }
        Disconnect-NsxtServer -Server $n -Confirm:$false
    }
}

Function prep_cluster_for_nsx () {
    foreach ($nsx in $nsx_mgrs) {
        Debug "Connecting to NSX $($nsx.display_name) to prep clusters to NSX"
        $n = Connect-NsxtServer -Server $nsx.ip -User $nsx.user -Password $nsx.password -WarningAction SilentlyContinue
        $tnc_service = Get-NsxtService -Server $n -Name "com.vmware.nsx.transport_node_collections"
        foreach ($tnc in $tncs) {
            $tncollection = $tnc_service.list().results | Where-Object { $_.display_name -eq $tnc.display_name}
            if ($tncollection) {
                Debug "Transport Node Collection $($tnc.display_name) found on $($nsx.display_name). Skipping ..."
                continue
            } else {
                Debug "Creating Transport Node Collection $($tnc.display_name) on $($nsx.display_name)"
                $cc = (Get-NsxtService -Server $n -Name "com.vmware.nsx.fabric.compute_collections").list().results | Where-Object { $_.display_name -eq $tnc.cluster_name}
                $tnp = (Get-NsxtService -Server $n -Name "com.vmware.nsx.transport_node_profiles").list().results | Where-Object { $_.display_name -eq $tnc.transport_node_profile_name}
                $tnc_spec = $tnc_service.Help.create.transport_node_collection.Create()
                $tnc_spec.display_name = $tnc.display_name
                $tnc_spec.compute_collection_id = $cc.external_id
                $tnc_spec.transport_node_profile_id = $tnp.id
                $res = $tnc_service.create($tnc_spec)
            }
        }
    }
}

Function check_nsx_cluster_status() {
    foreach ($nsx in $nsx_mgrs) {
        Debug "Connecting to NSX $($nsx.display_name)"
        $n = Connect-NsxtServer -Server $nsx.ip -User $nsx.user -Password $nsx.password -WarningAction SilentlyContinue 
        $tncstate = Get-NsxtService -Server $n -Name "com.vmware.nsx.transport_node_collections.state"
        foreach ($tnc in (Get-NsxtService -Server $n -Name "com.vmware.nsx.transport_node_collections").list().results) {
            Debug "Checking status of Transprot Node Collection $($tnc.display_name)"
            $state = $tncstate.get($tnc.id)
            $count = 0
            $ready = 0
            do {
                if ($state -ne "SUCCESS") {
                    Debug "Cluster prepped for NSX"
                    $ready = 1
                }
                $count ++
                if ($ready -eq 0) {
                    Debug "Retry after 1 minute ..."
                    Start-Sleep -s 60 # Secs
                }
            } until ($ready -eq 1 -or $count -eq 10) # Max 10 mins per cluster

            if ($reqdy -eq 0) {
                Debug "Timeout waiting for Transport Node Collection $($tnc.display_name) to be ready on $($nsx.display_name)"
                exit
            }
        }
    }
}


Function deploy_VMs() {
    foreach ($vm in $vms) {
        $vc = $vm.vc
        $esx = $vm.esx
        $vi = Connect-VIServer -Server $vc.ip_address -User $vc.username -Password $vc.root_password -WarningAction SilentlyContinue

        $ovfconfig = Get-OvfConfiguration -Server $vi $vm.ova
        $cluster = Get-Cluster -Server $vi -Name $esx.nestedcluster
        $datastore = Get-Datastore -Server $vi -Name $esx.nesteddatastore
        $datacenter = $cluster | Get-Datacenter
        $h = Get-VMHost -Server $vi -Name $esx.ip
        $network = $vm.network
        $v = Get-VM -Server $vi -Name $vm.display_name -ErrorAction SilentlyContinue
        if ($v) {
            Debug "VM $($vm.display_name) found on $($vc.display_name). Skipping ..."
        } else {
            Debug "Deploying $($vm.display_name) on $($esx.name)"
            $v = Import-VApp -Server $vi -Source $vm.ova -OvfConfiguration $ovfconfig -Name $vm.display_name -Location $cluster -Datastore $datastore -VMHost $h -DiskStorageFormat thin
        }
        if ($v.PowerState -eq "PoweredOff") {
            Debug "Powering ON $($v.name)"
            $v | Start-Vm -RunAsync | Out-Null
        } else {
            Debug "VM $($v.name) Powered ON"
        }

        Disconnect-VIServer -Server $vi -Confirm:$false
    }
}

Function create_global_segment () {
    $seg = "Global-Segment"
    $subnets = [pscustomobject] @{
        "gateway_address" = "192.168.1.1/24"
    }
    $advanced_config = [pscustomobject] @{
        "connectivity" = "ON"
    }
    $json = [pscustomobject] @{
        "display_name" = $seg
        "subnets" = @($subnets)
        "connectivity_path" = "/global-infra/tier-1s/Global-T1"
        "advanced_config" = $advanced_config
    }
    $body = $json | ConvertTo-Json -Depth 10
    $url = "https://$($nsx_gm.ip)/global-manager/api/v1/global-infra/segments/$seg"
    Debug "Creating $seg"
    $res = patch $url $nsx_gm.user $nsx_gm.password $body
}

$start_time = Get-Date

vcenter_config
nsx_config
edge_config
nsx_gm_config
register_compute_managers
create_transport_node_profiles
prep_cluster_for_nsx
check_nsx_cluster_status

# Using Terraform to create logical objects
terraform apply --auto-approve

# Wait for GM - LM Sync
Start-Sleep 180

deploy_VMs

$end_time = Get-Date

$duration = [math]::Round((New-TimeSpan -Start $start_time -End $end_time).TotalMinutes,2)

Debug "NSX-T Federation Lab deployment Complete"
Debug "StartTime: $start_time"
Debug "  EndTime: $end_time"
Debug " Duration: $duration minutes"
