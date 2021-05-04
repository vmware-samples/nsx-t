# Fast-Forward script to configure the lab
Based on vApp Template: NSBU-2020-NSXT-3.1
For NSX-T 3.1
     
     usage: configure_lab.py [-h] [-w N [N ...] | -d N [N ...] | -a] [-p] [-v] [-r]
                             [-c]
     
     Fast-Forward script to completely configure Lab: NSBU-2020-NSXT-3.0-V7
     
     optional arguments:
       -h, --help            show this help message and exit
       -w N [N ...], --workflow N [N ...]
                             Select one or more number corresponding to the action to perform:
                               1: Setup Infra
                               2: Configure Switching and Routing
       -d N [N ...], --deleteworkflow N [N ...]
                             Select one or more number corresponding to the action to perform:
                               1. Delete Switching and Routing config
                               2. Delete Infra config
       -a, --all             Run everything! Mutually exclusive with -w/--workflow
       -p, --plan            Print only the REST calls with request body if applicable
       -v, --verbose         Print Verbose log messages
       -r, --response        Pretty Print Response Body on success of a call
       -c, --cleanup         Cleanup all entities!

## PreRequisits

* NSX-T Manager (Single Node or Cluster) is installed

* vSphere environment is available with Management Cluster and Compute Cluster


## Typical Usage

### Setup

* Just configure everything (Can be run multiple times without issues)
>   python3 configure_lab.py -a

* Run first module to just prep NSX (create TN, Edges, Clusters)
>   python3 configure_lab.py -w 1

* Run module to configure Switching and Routing (needs the first module to be run)
>   python3 configure_lab.py -w 2


### Cleanup/Reset

* Just reset the Switching and Routing
> python3 configure_lab.py -d 1

* Just reset the Infra configuration (unprep Hosts, delete Edges, remove compute manager)
> python3 configure_lab.py -d 2

* Delete everything/Reset lab to clean state
> python3 configure_lab.py -c

## Notes:
- The script configures the lab completely
- Stops when the first error is encountered

## Dependencies:
- python3
- pyVmomi: pip install pyvmomi
  - On Mac, the install could clash with existing 'six' package. Try: pip install --ignore-installed pyvmomi
- paramiko: Needed to connect to KVM hosts and execute commands

## Run output

$ python3 configure_lab.py -a
    
    
    [ Running all workflows ]
    
    Setup infra
      |
      +-- Adding Compute Managers
      +-- Waiting for compute manager to be registered
          -- Waiting for success, Got success
          -- Waiting for REGISTERED, Got REGISTERED
      +-- Creating IP Pool for TEPs
      +-- Creating Transport Zones
      +-- Creating Transport Node Profiles
      +-- Prepping ESX Compute Clusters
      +-- Creating Segment: left-seg
      +-- Creating Segment: right-seg
      +-- Adding Transport Nodes
      +-- Wait for Transport Nodes to be registered
          -- Waiting for success, Got success
          -- Waiting for success, Got success
          -- Waiting for success, Got success
          -- Waiting for success, Got success
          -- Waiting for success, Got success
          -- success: 5, total 5
      +-- Creating Edge Cluster
    Configuring Switching and Routing
      |
      +-- Updating global routing config to include IPv6
      +-- Creating Tier-1 Gateway: T1-GW
      +-- Creating Tier-1 Gateway: T1-GW2
      +-- Creating Segment: web-seg
      +-- Creating Segment: app-seg
      +-- Creating Segment: db-seg
      +-- Creating Segment: vm-seg
      +-- Configuring VM: app-01a with Network: app-seg
      +-- Configuring VM: web-01a with Network: web-seg
      +-- Configuring VM: web-02a with Network: web-seg
      +-- Configuring VM: vm-01a with Network: vm-seg
      +-- Powering on VMs: app-01a, web-01a, web-02a, vm-01a
      +-- Starting KVM VM: db-01a
      +-- Starting KVM VM: web-03a
      +-- Configuring Segment Ports for KVM VMs
      +-- Creating Tier0 GW
      +-- Attaching to Tier1
      +-- Attaching to Tier1
      +-- Setting Route Re-distribution rules
      +-- Creating interfaces on Tier0
      +-- Setting up BGP
      +-- Setting up BGP Neighbors
      +-- Updating Tier-1s with Edge Cluster


$ python3 configure_lab.py -w 1

    Setup infra
      |
      +-- Adding Compute Managers
      +-- Waiting for compute manager to be registered
          -- Waiting for success, Got success
          -- Waiting for REGISTERED, Got REGISTERED
      +-- Creating IP Pool for TEPs
      +-- Creating Transport Zones
      +-- Creating Transport Node Profiles
      +-- Prepping ESX Compute Clusters
      +-- Creating Segment: left-seg
      +-- Creating Segment: right-seg
      +-- Adding Transport Nodes
      +-- Wait for Transport Nodes to be registered
          -- Waiting for success, Got success
          -- Waiting for success, Got success
          -- Waiting for success, Got success
          -- Waiting for success, Got success
          -- Waiting for success, Got success
          -- success: 5, total 5
      +-- Creating Edge Cluster


$ python3 configure_lab.py -w 2

    Configuring Switching and Routing
      |
      +-- Updating global routing config to include IPv6
      +-- Creating Tier-1 Gateway: T1-GW
      +-- Creating Tier-1 Gateway: T1-GW2
      +-- Creating Segment: web-seg
      +-- Creating Segment: app-seg
      +-- Creating Segment: db-seg
      +-- Creating Segment: vm-seg
      +-- Configuring VM: app-01a with Network: app-seg
      +-- Configuring VM: web-01a with Network: web-seg
      +-- Configuring VM: web-02a with Network: web-seg
      +-- Configuring VM: vm-01a with Network: vm-seg
      +-- Powering on VMs: app-01a, web-01a, web-02a, vm-01a
      +-- Starting KVM VM: db-01a
      +-- Starting KVM VM: web-03a
      +-- Configuring Segment Ports for KVM VMs
      +-- Creating Tier0 GW
      +-- Attaching to Tier1
      +-- Attaching to Tier1
      +-- Setting Route Re-distribution rules
      +-- Creating interfaces on Tier0
      +-- Setting up BGP
      +-- Setting up BGP Neighbors
      +-- Updating Tier-1s with Edge Cluster

$ python3 configure_lab.py -c

    [ Cleaning up all entities ]
    
    Reset switching and routing
      |
      +-- Deleting Segment Ports for KVM VMs
      +-- Stopping KVM VM: db-01a
      +-- Stopping KVM VM: web-03a
      +-- Powering OFF VMs: app-01a, web-01a, web-02a, vm-01a
      +-- Configuring VM: app-01a with Network: LabNet
      +-- Configuring VM: web-01a with Network: LabNet
      +-- Configuring VM: web-02a with Network: LabNet
      +-- Configuring VM: vm-01a with Network: LabNet
      +-- Deleting Segment: web-seg
      +-- Deleting Segment: app-seg
      +-- Deleting Segment: db-seg
      +-- Deleting Segment: vm-seg
      +-- Resetting global routing config to back to just IPv4
      +-- Deleting Tier-1 Gateway: T1-GW
      +-- Deleting Tier-1 Gateway: T1-GW2
      +-- Disconnecting Tier1
      +-- Disconnecting Tier1
      +-- Deleting BGP neighbors
      +-- Deleting Interfaces
      +-- Deleting locale services
      +-- Deleting Tier0 GW
    Deleting Infra
      |
      +-- Delete Edge Cluster: EdgeCluster
      +-- Deleting Standalone and Edge Transport Nodes
      +-- Deleting Segment: left-seg
      +-- Deleting Segment: right-seg
      +-- Deleting ESX Compute Cluster
      +-- Deleting Transport Node Profile: compute-TNP
      +-- Deleting Transport Zone: nsx-uplinks-vlan-transportzone
      +-- Deleting IP Pool Subnet: TEP-pool-subnets
      +-- Deleting IP Pool: TEP-pool
     +--  Deleting Compute Manager: vCenter


$ python3 configure_lab.py -d 1

    Reset switching and routing
      |
      +-- Deleting Segment Ports for KVM VMs
      +-- Stopping KVM VM: db-01a
      +-- Stopping KVM VM: web-03a
      +-- Powering OFF VMs: app-01a, web-01a, web-02a, vm-01a
      +-- Configuring VM: app-01a with Network: LabNet
      +-- Configuring VM: web-01a with Network: LabNet
      +-- Configuring VM: web-02a with Network: LabNet
      +-- Configuring VM: vm-01a with Network: LabNet
      +-- Deleting Segment: web-seg
      +-- Deleting Segment: app-seg
      +-- Deleting Segment: db-seg
      +-- Deleting Segment: vm-seg
      +-- Resetting global routing config to back to just IPv4
      +-- Deleting Tier-1 Gateway: T1-GW
      +-- Deleting Tier-1 Gateway: T1-GW2
      +-- Disconnecting Tier1
      +-- Disconnecting Tier1
      +-- Deleting BGP neighbors
      +-- Deleting Interfaces
      +-- Deleting locale services
      +-- Deleting Tier0 GW


$ python3 configure_lab.py -d 2

    Deleting Infra
      |
      +-- Deleting Standalone and Edge Transport Nodes
      +-- Deleting Segment: left-seg
      +-- Deleting Segment: right-seg
      +-- Deleting ESX Compute Cluster
      +-- Deleting Transport Node Profile: compute-TNP
      +-- Deleting IP Pool Subnet: TEP-pool-subnets
      +-- Deleting IP Pool: TEP-pool

