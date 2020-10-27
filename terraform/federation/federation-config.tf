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


# Default provider connects to Global Manager
provider "nsxt" {
  host                 = "192.168.200.40"
  username             = "admin"
  password             = "myPassword1!myPassword1!"
  global_manager       = "true"
  allow_unverified_ssl = true
}

# Provider aliasing for Local Manager
provider "nsxt" {
  alias                = "ny"
  host                 = "192.168.200.41"
  username             = "admin"
  password             = "myPassword1!myPassword1!"
  allow_unverified_ssl = true
}

# Transport Zone on Local Manager
data "nsxt_policy_transport_zone" "default_tz" {
  provider     = nsxt.ny
  display_name = "nsx-overlay-transportzone"
}

# Segment on Local Manager
resource "nsxt_policy_segment" "ny_segment" {
  provider            = nsxt.ny
  display_name        = "TF-segment-ny"
  description         = "Segment via Terraform"
  transport_zone_path = data.nsxt_policy_transport_zone.default_tz.path
  subnet {
    cidr = "10.10.0.1/24"
  }
  advanced_config {
    connectivity = "ON"
  }
}


#
# Global Manager objects
#

data "nsxt_policy_site" "ny" {
  display_name = "nsx-ny"
}

data "nsxt_policy_site" "paris" {
  display_name = "nsx-paris"
}

data "nsxt_policy_site" "london" {
  display_name = "nsx-london"
}

data "nsxt_policy_edge_cluster" "ny" {
  display_name = "Edge-Cluster"
  site_path    = data.nsxt_policy_site.ny.path
}


data "nsxt_policy_edge_cluster" "paris" {
  display_name = "Edge-Cluster"
  site_path    = data.nsxt_policy_site.paris.path
}

data "nsxt_policy_edge_cluster" "london" {
  display_name = "Edge-Cluster"
  site_path    = data.nsxt_policy_site.london.path
}

data "nsxt_policy_edge_node" "london_edge1" {
  edge_cluster_path = data.nsxt_policy_edge_cluster.london.path
  member_index      = 0
}

resource "nsxt_policy_tier0_gateway" "global_T0" {
  description   = "Tier-0 with Global scope"
  display_name  = "T0-Global"
  failover_mode = "PREEMPTIVE"

  locale_service {
    edge_cluster_path = data.nsxt_policy_edge_cluster.paris.path
  }

  locale_service {
    edge_cluster_path    = data.nsxt_policy_edge_cluster.london.path
    preferred_edge_paths = [data.nsxt_policy_edge_node.london_edge1.path]
  }

  locale_service {
    edge_cluster_path = data.nsxt_policy_edge_cluster.ny.path
  }

  tag {
    scope = "color"
    tag   = "blue"
  }

}


