#
# Terraform Config to create the following:
#   Tier0, Tier1, 2 Segments, Groups and DFW rules
#
# Used by vPOD template: XXX
#

terraform {
  required_providers {
    nsxt = {
      source = "vmware/nsxt"
    }
  }
}

provider "nsxt" {
  host                  = "nsxapp-01a.corp.local"
  username              = "admin"
  password              = "VMware1!VMware1!"
  allow_unverified_ssl  = true
  max_retries           = 10
  retry_min_delay       = 500
  retry_max_delay       = 5000
  retry_on_status_codes = [429]
}

data "nsxt_policy_edge_cluster" "edgecluster" {
  display_name = "EdgeCluster"
}

data "nsxt_policy_transport_zone" "vlantz" {
  display_name = "nsx-uplinks-vlan-transportzone"
}

data "nsxt_policy_transport_zone" "overlaytz" {
  display_name = "nsx-overlay-transportzone"
}

data "nsxt_policy_edge_node" "edgenode1" {
  edge_cluster_path = data.nsxt_policy_edge_cluster.edgecluster.path
  member_index      = 0
}

data "nsxt_policy_edge_node" "edgenode2" {
  edge_cluster_path = data.nsxt_policy_edge_cluster.edgecluster.path
  member_index      = 1
}

data "nsxt_policy_tier0_gateway" "t0-paris" {
  display_name = "T0-Paris"
}

resource "nsxt_policy_tier1_gateway" "t1-paris" {
  display_name              = "T1-Paris"
  edge_cluster_path         = data.nsxt_policy_edge_cluster.edgecluster.path
  failover_mode             = "NON_PREEMPTIVE"
  tier0_path                = data.nsxt_policy_tier0_gateway.t0-paris.path
  pool_allocation           = "ROUTING"
  route_advertisement_types = ["TIER1_STATIC_ROUTES", "TIER1_CONNECTED", "TIER1_NAT", "TIER1_LB_VIP", "TIER1_LB_SNAT", "TIER1_DNS_FORWARDER_IP", "TIER1_IPSEC_LOCAL_ENDPOINT"]
}

resource "nsxt_policy_nat_rule" "nat-web01" {
  display_name         = "NAT-WEB01"
  action               = "DNAT"
  gateway_path         = nsxt_policy_tier1_gateway.t1-paris.path
  destination_networks = ["88.88.88.88"]
  translated_networks  = ["172.16.10.11"]
}

resource "nsxt_policy_segment" "web-seg" {
  display_name        = "web-seg"
  connectivity_path   = nsxt_policy_tier1_gateway.t1-paris.path
  transport_zone_path = data.nsxt_policy_transport_zone.overlaytz.path
  subnet {
    cidr = "172.16.10.1/24"
  }
  advanced_config {
    connectivity = "ON"
  }
}

resource "nsxt_policy_segment" "db-seg" {
  display_name        = "db-seg"
  connectivity_path   = nsxt_policy_tier1_gateway.t1-paris.path
  transport_zone_path = data.nsxt_policy_transport_zone.overlaytz.path
  subnet {
    cidr = "172.16.20.1/24"
  }
  advanced_config {
    connectivity = "ON"
  }
}

resource "nsxt_policy_group" "db-vm-group" {
  display_name = "DB-VM-Group"
  criteria {
    condition {
      member_type = "VirtualMachine"
      key         = "Name"
      operator    = "STARTSWITH"
      value       = "DB"
    }
  }
}

resource "nsxt_policy_group" "mgmt-ip-ipset" {
  display_name = "Mgmt-IP-ipset"
  criteria {
    ipaddress_expression {
      ip_addresses = ["192.168.110.10"]
    }
  }
}

resource "nsxt_policy_group" "web-vm-group" {
  display_name = "Web-VM-Group"
  criteria {
    condition {
      member_type = "VirtualMachine"
      key         = "Name"
      operator    = "STARTSWITH"
      value       = "Web"
    }
  }
}

data "nsxt_policy_service" "ssh" {
  display_name = "SSH"
}

data "nsxt_policy_service" "icmp-all" {
  display_name = "ICMP ALL"
}

data "nsxt_policy_service" "https" {
  display_name = "HTTPS"
}

data "nsxt_policy_service" "mysql" {
  display_name = "MySQL"
}

resource "nsxt_policy_security_policy" "management-access" {
  display_name = "Management Access"
  category     = "Infrastructure"
  rule {
    display_name       = "Management SSH + ICMP"
    source_groups      = [nsxt_policy_group.mgmt-ip-ipset.path]
    destination_groups = [nsxt_policy_group.db-vm-group.path, nsxt_policy_group.web-vm-group.path]
    services           = [data.nsxt_policy_service.ssh.path, data.nsxt_policy_service.icmp-all.path]
    scope              = [nsxt_policy_group.db-vm-group.path, nsxt_policy_group.web-vm-group.path]
    action             = "ALLOW"
  }
}

resource "nsxt_policy_security_policy" "two-tier-app" {
  display_name = "2Tier App"
  category     = "Application"
  rule {
    display_name       = "Any to Web"
    destination_groups = [nsxt_policy_group.web-vm-group.path]
    services           = [data.nsxt_policy_service.https.path, data.nsxt_policy_service.icmp-all.path]
    scope              = [nsxt_policy_group.web-vm-group.path]
    action             = "ALLOW"
  }
  rule {
    display_name       = "Web to DB"
    source_groups      = [nsxt_policy_group.web-vm-group.path]
    destination_groups = [nsxt_policy_group.db-vm-group.path]
    services           = [data.nsxt_policy_service.mysql.path]
    scope              = [nsxt_policy_group.db-vm-group.path, nsxt_policy_group.web-vm-group.path]
    action             = "ALLOW"
  }
  rule {
    display_name       = "Deny All"
    scope              = [nsxt_policy_group.db-vm-group.path, nsxt_policy_group.web-vm-group.path]
    action             = "REJECT"
  }
}

