#!/usr/bin/env python
"""
"""

from com.vmware.vapi.std.errors_client import NotFound
from util import auth
from util import getargs
from vmware.vapi.bindings.struct import PrettyPrinter

"""
* *******************************************************
* Copyright (c) VMware, Inc. 2017. All Rights Reserved.
* SPDX-License-Identifier: MIT
* *******************************************************
*
* DISCLAIMER. THIS PROGRAM IS PROVIDED TO YOU "AS IS" WITHOUT
* WARRANTIES OR CONDITIONS OF ANY KIND, WHETHER ORAL OR WRITTEN,
* EXPRESS OR IMPLIED. THE AUTHOR SPECIFICALLY DISCLAIMS ANY IMPLIED
* WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY,
* NON-INFRINGEMENT AND FITNESS FOR A PARTICULAR PURPOSE.
"""
import time

from com.vmware.nsx.fabric import nodes_client
from com.vmware.nsx.fabric.nodes import network_client
from com.vmware.nsx.fabric.nodes.network import interfaces_client
from com.vmware.nsx import fabric_client
from com.vmware.nsx.model_client import EdgeNode
from com.vmware.nsx.model_client import HostNode
from com.vmware.nsx.model_client import Node

"""
This example shows how to get statistics and counters for the fabric
nodes (hosts and edges) in an NSX-T environment. Overall status
and network interface information are displayed. APIs used:

List fabric nodes:
GET /api/v1/fabric/nodes

Get fabric node status:
GET /api/v1/fabric/nodes/<node-id>/status

List fabric node interfaces:
GET /api/v1/fabric/nodes/<node-id>/interfaces

Get fabric node interface statistics:
GET /api/v1/fabric/nodes/<node-id>/interfaces/<interface-id>/stats
"""


def print_host_node_properties(node):
    """
    Print proeprties specific to host nodes.
    """
    print("  OS: %s %s" % (node.os_type, node.os_version))
    print("  Discovered node ID: %s" % node.discovered_node_id)
    print("  Compute manager: %s" % node.managed_by_server)


def print_edge_node_properties(node):
    """
    Print proeprties specific to edge nodes.
    """
    print("  Deployment Type: %s" % node.deployment_type)
    print("  Allocation List: %s" % node.allocation_list)


def print_node(node):
    """
    Print node configuration and status.
    """
    print("====== %s id %s:" % (node.resource_type, node.id))
    pp.pprint(node)


def print_node_status(node, status):
    """
    Print some of the node's interesting status information.
    """
    print("====== Status for %s id %s:" % (node.resource_type, node.id))
    pp.pprint(status)


def print_interface_and_stats(node, interface, if_stats):
    """
    Print the given interface's configuration and statistics.
    """
    print("====== %s interface info for %s id %s:" %
          (interface.interface_id, node.resource_type, node.id))
    pp.pprint(interface)
    pp.pprint(if_stats)


pp = PrettyPrinter()


def main():
    args = getargs.getargs()
    stub_config = auth.get_session_auth_stub_config(args.user, args.password,
                                                    args.nsx_host,
                                                    args.tcp_port)
    # Instantiate all the services we'll need.
    fn_svc = fabric_client.Nodes(stub_config)
    fnstatus_svc = nodes_client.Status(stub_config)
    interfaces_svc = network_client.Interfaces(stub_config)
    interface_stats_svc = interfaces_client.Stats(stub_config)

    # Find all fabric nodes and print a summary of each node's
    # operational state
    all_raw_fns = fn_svc.list()
    print("***** Showing summaries for %d fabric nodes" %
          all_raw_fns.result_count)
    all_fns = []
    for raw_fn in all_raw_fns.results:
        # Fabric Nodes are polymorphic, so convert to a concrete class
        node_type = raw_fn.convert_to(Node).resource_type
        if node_type == "HostNode":
            all_fns.append(raw_fn.convert_to(HostNode))
        elif node_type == "EdgeNode":
            all_fns.append(raw_fn.convert_to(EdgeNode))
    for fn in all_fns:
        print_node(fn)
        print_node_status(fn, fnstatus_svc.get(fn.id, source="realtime"))
        interfaces = interfaces_svc.list(fn.id)
        print("    Interfaces:")
        for interface in interfaces.results:
            if_stats = interface_stats_svc.get(fn.id, interface.interface_id)
            print_interface_and_stats(fn, interface, if_stats)
        print("")

if __name__ == "__main__":
    main()
