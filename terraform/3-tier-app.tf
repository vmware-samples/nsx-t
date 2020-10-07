# Copyright 2017-2020 VMware, Inc.  All rights reserved
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

provider "nsxt" {
  host                  = "10.114.200.41"
  username              = "admin"
  password              = "myPassword1!myPassword1!"
  allow_unverified_ssl  = true
  max_retries           = 10
  retry_min_delay       = 500
  retry_max_delay       = 5000
  retry_on_status_codes = [429]
}


data "nsxt_policy_edge_cluster" "demo" {
  display_name = "Edge-Cluster-01"
}

data "nsxt_policy_transport_zone" "overlay_tz" {
  display_name = "Overlay-TZ"
}

resource "nsxt_policy_tier0_gateway" "TF-3Tier-T0" {
  nsx_id       = "TF-3Tier-T0"
  display_name = "TF-3Tier-T0"
 ha_mode      = "ACTIVE_ACTIVE"
}


resource "nsxt_policy_tier1_gateway" "TF-VMW-T1" {
  nsx_id                    = "TF-VMW-T1"
  display_name              = "TF-VMW-T1"
  edge_cluster_path         = data.nsxt_policy_edge_cluster.demo.path
  failover_mode             = "NON_PREEMPTIVE"
  default_rule_logging      = "false"
  enable_firewall           = "true"
  force_whitelisting        = "false"
  tier0_path                = nsxt_policy_tier0_gateway.TF-3Tier-T0.path
  route_advertisement_types = ["TIER1_NAT", "TIER1_LB_VIP", "TIER1_LB_SNAT", "TIER1_DNS_FORWARDER_IP", "TIER1_CONNECTED", "TIER1_STATIC_ROUTES", "TIER1_IPSEC_LOCAL_ENDPOINT"]
  pool_allocation           = "ROUTING"
}

resource "nsxt_policy_tier1_gateway" "TF-Client-T1" {
  nsx_id                    = "TF-Client-T1"
  display_name              = "TF-Client-T1"
  edge_cluster_path         = data.nsxt_policy_edge_cluster.demo.path
  failover_mode             = "NON_PREEMPTIVE"
  default_rule_logging      = "false"
  enable_firewall           = "true"
  force_whitelisting        = "false"
  tier0_path                = nsxt_policy_tier0_gateway.TF-3Tier-T0.path
  route_advertisement_types = ["TIER1_LB_VIP", "TIER1_LB_SNAT", "TIER1_DNS_FORWARDER_IP", "TIER1_CONNECTED", "TIER1_STATIC_ROUTES", "TIER1_IPSEC_LOCAL_ENDPOINT"]
  pool_allocation           = "ROUTING"
}

resource "nsxt_policy_segment" "TF-3Tier" {
  nsx_id              = "TF-3Tier"
  display_name        = "TF-3Tier"
  connectivity_path   = nsxt_policy_tier1_gateway.TF-VMW-T1.path
  transport_zone_path = data.nsxt_policy_transport_zone.overlay_tz.path

  subnet {
    cidr = "192.30.10.1/24"
  }

  advanced_config {
    connectivity = "ON"
  }
}

resource "nsxt_policy_segment" "TF-Client" {
  nsx_id              = "TF-Client"
  display_name        = "TF-Client"
  connectivity_path   = nsxt_policy_tier1_gateway.TF-Client-T1.path
  transport_zone_path = data.nsxt_policy_transport_zone.overlay_tz.path

  subnet {
    cidr = "192.30.50.1/24"
  }

  advanced_config {
    connectivity = "ON"
  }
}

resource "nsxt_policy_group" "TF-all-vms" {
  nsx_id       = "TF-all-vms"
  display_name = "TF-all-vms"
  criteria {
    condition {
      member_type = "VirtualMachine"
      key         = "Tag"
      operator    = "EQUALS"
      value       = "nsx"
    }
  }
}

resource "nsxt_policy_group" "TF-db-vms" {
  nsx_id       = "TF-db-vms"
  display_name = "TF-db-vms"
  criteria {
    condition {
      member_type = "VirtualMachine"
      key         = "Tag"
      operator    = "EQUALS"
      value       = "db"
    }
  }
}

resource "nsxt_policy_group" "TF-web-vms" {
  nsx_id       = "TF-web-vms"
  display_name = "TF-web-vms"
  criteria {
    condition {
      member_type = "VirtualMachine"
      key         = "Tag"
      operator    = "EQUALS"
      value       = "web"
    }
  }
}

resource "nsxt_policy_group" "TF-app-vms" {
  nsx_id       = "TF-app-vms"
  display_name = "TF-app-vms"
  criteria {
    condition {
      member_type = "VirtualMachine"
      key         = "Tag"
      operator    = "EQUALS"
      value       = "app"
    }
  }
}

data "nsxt_policy_service" "http" {
  display_name = "HTTP"
}

data "nsxt_policy_service" "https" {
  display_name = "HTTPS"
}

data "nsxt_policy_service" "mysql" {
  display_name = "MySQL"
}

data "nsxt_policy_service" "ssh" {
  display_name = "SSH"
}

data "nsxt_policy_service" "icmp_all" {
  display_name = "ICMP ALL"
}

resource "nsxt_policy_security_policy" "TF-Allow-SQL" {
  display_name = "TF-Allow-SQL"
  category     = "Application"
  rule {
    display_name       = "allow-mysql"
    action             = "ALLOW"
    destination_groups = [nsxt_policy_group.TF-db-vms.path]
    services           = [data.nsxt_policy_service.mysql.path]
  }
}

resource "nsxt_policy_security_policy" "TF-Allow-HTTP" {
  display_name = "TF-Allow-browsing"
  category     = "Application"
  rule {
    display_name       = "allow-80-443"
    action             = "ALLOW"
    destination_groups = [nsxt_policy_group.TF-web-vms.path]
    services           = [data.nsxt_policy_service.http.path, data.nsxt_policy_service.https.path]
  }
}

resource "nsxt_policy_security_policy" "TF-Ops" {
  display_name = "TF-Ops"
  category     = "Infrastructure"
  rule {
    display_name       = "Allow-SSH"
    action             = "REJECT"
    destination_groups = [nsxt_policy_group.TF-all-vms.path]
    services           = [data.nsxt_policy_service.ssh.path]
  }

  rule {
    display_name       = "Allow-ICMP"
    action             = "ALLOW"
    destination_groups = [nsxt_policy_group.TF-all-vms.path]
    services           = [data.nsxt_policy_service.icmp_all.path]
  }
}
