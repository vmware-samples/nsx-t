# NSX-T Automation with vRA

## Introduction
This is an example of a vRA Cloud Template which deploys a Shared Gateway with atteched Routed networks. 

vRA 8.3 and vRA Cloud offers support for a shared Gateway Object. The Gateway object can be connected, and most importantly, shared between on-demand networks within that deployment.  Once you add the Gateway object, click dragging between that object and the target network connects those objects.  At deployment time, a single T-1 Gateway will be created and shared among connected networks.  Shared Gateways work with the Outbound and Routed network types and multiple Gateways can still be created for each deployment.

## Overview
This Cloud Templates creates the following topology
![](../media/Shared-Gateway-Routed.png)

The following objects will be created:
- 1 Tier-1 Gateway
- 2 Segments connected to the Tier-1 Gateway

## Requirements
* NSX-T configured with:
  - At least one Transport Zone
  - At least one Edge Cluster (with one or more Edges)
  - Tier-0 Gateway pre-provisioned
  - vRA installed and configured with NSX-T. 
  - A Network Profile configured with on-demand networks, CIDR and Capability Tags.
  - Available VM Templates

## Usage

Cloud Templates are YAML type files which can be Imported/Copy-Pasted in the Cloud Template into your vRA to customize and deploy.