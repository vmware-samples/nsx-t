# Variables

# NSX Manager
variable "nsx_manager" {
  default = "10.29.12.206"
}

# Username & Password for NSX-T Manager
variable "username" {
  default = "admin"
}

variable "password" {
  default = "password"
}

# Transport Zones
variable "vlan_tz" {
  default = "VLAN_TZ"
}

variable "overlay_tz" {
  default = "Overlay-TZ"
}

# Enter Edge Nodes & Edge Cluster Display Name. Required for external interfaces.
variable "edge_node_1" {
  default = "edge-01"
}

variable "edge_node_2" {
  default = "edge-02"
}

variable "edge_cluster_vrf" {
  default = "edge-cluster-vrf"
}

# Segment Names
variable "nsx_segment_web" {
  default = "VM-Segment-Web"
}
variable "nsx_segment_app" {
  default = "VM-Segment-App"
}

variable "nsx_segment_db" {
  default = "VM-Segment-DB"
}

# Security Group names. 
variable "nsx_group_web" {
  default = "Web Servers"
}

variable "nsx_group_app" {
  default = "App Servers"
}

variable "nsx_group_db" {
  default = "DB Servers"
}

variable "nsx_group_blue" {
  default = "Blue Application"
}

variable "nsx_group_red" {
  default = "Red Application"
}
