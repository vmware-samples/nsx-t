#!/usr/bin/env python
"""
* *******************************************************
* Copyright (c) VMware, Inc. 2017. All Rights Reserved.
* SPDX-License-Identifier: BSD-2
* *******************************************************
*
* DISCLAIMER. THIS PROGRAM IS PROVIDED TO YOU "AS IS" WITHOUT
* WARRANTIES OR CONDITIONS OF ANY KIND, WHETHER ORAL OR WRITTEN,
* EXPRESS OR IMPLIED. THE AUTHOR SPECIFICALLY DISCLAIMS ANY IMPLIED
* WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY,
* NON-INFRINGEMENT AND FITNESS FOR A PARTICULAR PURPOSE.
"""
from util import auth
from util import getargs
from com.vmware.nsx.fabric.nodes_client import Status
from com.vmware.nsx.fabric_client import Nodes
from com.vmware.nsx.model_client import Node
from com.vmware.vapi.std.errors_client import NotFound

"""
This example shows how to obtain a list of all fabric nodes
and query their status.

APIs used:

List fabric nodes
GET /api/v1/fabric/nodes

Get fabric node status
GET /api/v1/fabric/nodes/<node-id>/status
"""


def main():
    args = getargs.getargs()
    stub_config = auth.get_session_auth_stub_config(args.user, args.password,
                                                    args.nsx_host,
                                                    args.tcp_port)

    # Create the services we'll need.
    fabricnodes_svc = Nodes(stub_config)
    status_svc = Status(stub_config)

    # List all of the fabric nodes
    result = fabricnodes_svc.list()

    # Iterate over the results
    for vs in result.results:
        fn = vs.convert_to(Node)
        print("Type: %s, Name: %s, id: %s" % (fn.resource_type,
                                              fn.display_name, fn.id))
        fn_status = status_svc.get(fn.id)
        print("    mp conn: %s, cp conn: %s" % (
            fn_status.mpa_connectivity_status,
            fn_status.lcp_connectivity_status))


if __name__ == "__main__":
    main()
