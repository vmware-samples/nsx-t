# NSX-T Automation using hierarchical API


## Overview

Creates the following items:
- Tier-0
- 2 Tier-1
- 1 Segment in each Tier-1 (2 in total)
- 4 Groups
- 3 Security Policies
- 4 Rules in total

## Requirements
* NSX-T configured with:
  - At least one Transport Zone
  - At least one Edge Cluster (with one or more Edges)

## Usage
The provided JSON can be used to both create and delete objects.

### Create
The provided code is sent as the request body for the API:

`PATCH /policy/api/v1/infra`


### Delete
The `marked_for_delete: false` has to be changed to `marked_for_delete: true` and the following API is sent:

`PATCH /policy/api/v1/infra`


**Note** - The provided JSON objects has references to Edge Clusters and Transport Zones here:

```
33:               },
34:              "edge_cluster_path": "/infra/sites/default/enforcement-points/default/edge-clusters/b666240d-269a-41d1-8187-98b58f88c239",
35:               "resource_type": "LocaleServices",
```

```
105:        "connectivity_path": "/infra/tier-1s/VMW-T1",
106:        "transport_zone_path": "/infra/sites/default/enforcement-points/default/transport-zones/d7f8d7d9-c7d4-497d-b482-980be8bd0d76",
107:        "advanced_config": {
```

```
130:         "connectivity_path": "/infra/tier-1s/Client-T1",
131:        "transport_zone_path": "/infra/sites/default/enforcement-points/default/transport-zones/d7f8d7d9-c7d4-497d-b482-980be8bd0d76",
132:        "advanced_config": {
```

The IDs in line `34`, `106`, `131` have to reflect the IDs in your environment. This has to be done for both **Creation** and **Deletion**.


## Sample Run:

