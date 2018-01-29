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

from com.vmware.nsx_client import LogicalPorts
from com.vmware.nsx_client import LogicalRouterPorts
from com.vmware.nsx_client import LogicalRouters
from com.vmware.nsx_client import LogicalSwitches
from com.vmware.nsx import logical_ports_client
from com.vmware.nsx.logical_router_ports import statistics_client
from com.vmware.nsx import logical_switches_client
from com.vmware.nsx.model_client import LogicalRouterPort
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

"""
This example shows how to get statistics and counters for various
logical entities in an NSX-T environment.

APIs used:

List logical switches:
GET /api/v1/logical-switches

Get logical switch statistics:
GET /api/v1/logical-switches/<lswitch-id>/statistics

List logical ports:
GET /api/v1/logical-ports

Get logical port statistics:
GET /api/v1/logical-ports/<lport-id>/statistics

List logical router ports:
GET /api/v1/logical-router-ports

Get logical router port statistics:
GET /api/v1/logical-router-ports/<logical-router-port-id>/statistics
"""


def print_l2_stats(stats):
    """
    Print the counters from layer 2 statistics (used by logical switches
    and logical ports).
    """
    print(" Rx packets: total=%s, dropped=%s, multicast_broadcast=%s" % (
          stats.rx_packets.total, stats.rx_packets.dropped,
          stats.rx_packets.multicast_broadcast))
    print(" Rx bytes: total=%s, dropped=%s, multicast_broadcast=%s" % (
          stats.rx_bytes.total, stats.rx_bytes.dropped,
          stats.rx_bytes.multicast_broadcast))
    print(" Tx packets: total=%s, dropped=%s, multicast_broadcast=%s" % (
          stats.tx_packets.total, stats.tx_packets.dropped,
          stats.tx_packets.multicast_broadcast))
    print(" Tx bytes: total=%s, dropped=%s, multicast_broadcast=%s" % (
          stats.tx_bytes.total, stats.tx_bytes.dropped,
          stats.tx_bytes.multicast_broadcast))
    if stats.dropped_by_security_packets is None:
        print(" Packets dropped by security: None")
    else:
        print(" Packets dropped by security")
        dropped = stats.dropped_by_security_packets
        print("    BPDU filter: %d" % dropped.bpdu_filter_dropped)
        print("    DHCP client IPv4: %d" % dropped.dhcp_client_dropped_ipv4)
        print("    DHCP client IPv6: %d" % dropped.dhcp_client_dropped_ipv6)
        print("    DHCP server IPv4: %d" % dropped.dhcp_server_dropped_ipv4)
        print("    DHCP server IPv6: %d" % dropped.dhcp_server_dropped_ipv6)
        if dropped.spoof_guard_dropped is not None:
            print("    Spoof Guard")
            for ctr in dropped.spoof_guard_dropped:
                print("     %s: %s" % (ctr.packet_type, ctr.counter))
    if stats.mac_learning is not None:
        print(" MAC learning: dropped: %s, allowed; %s" % (
              (stats.mac_learning.mac_not_learned_packets_dropped,
               stats.mac_learning.mac_not_learned_packets_allowed)))


def print_lrp_stats(stats):
    """
    Print the counters from a logical router port.
    """
    print(" Rx: packets=%s, bytes=%s, dropped packets=%s" %
          (stats.rx.total_packets, stats.rx.total_bytes,
           stats.rx.dropped_packets))
    print(" Tx: packets=%s, bytes=%s, dropped packets=%s" %
          (stats.tx.total_packets, stats.tx.total_bytes,
           stats.tx.dropped_packets))


def main():
    args = getargs.getargs()
    stub_config = auth.get_session_auth_stub_config(args.user, args.password,
                                                    args.nsx_host,
                                                    args.tcp_port)

    pp = PrettyPrinter()

    # Instantiate all the services we'll need.
    ls_svc = LogicalSwitches(stub_config)
    ls_statistics_svc = logical_switches_client.Statistics(stub_config)
    lp_svc = LogicalPorts(stub_config)
    lp_statistics_svc = logical_ports_client.Statistics(stub_config)
    lrp_svc = LogicalRouterPorts(stub_config)
    lrp_statistics_svc = statistics_client.Summary(stub_config)

    # Find all logical switches and show statistics for each.
    all_ls = ls_svc.list()
    print("***** Showing statistics for %d logical switches" %
          all_ls.result_count)
    for ls in all_ls.results:
        print("Logical switch %s (id %s)" % (ls.display_name, ls.id))
        # Retrieve the statistics for the switch
        stats = ls_statistics_svc.get(ls.id)
        print_l2_stats(stats)
        print("")

    # Find all logical ports and show statistics for each.
    all_lps = lp_svc.list()
    print("***** Showing statistics for %d logical ports" %
          all_lps.result_count)
    for lp in all_lps.results:
        # Show the port's name and id, the logical switch it's on,
        # and what it's attached to, if anything.
        print("Logical port %s (id %s)" % (lp.display_name, lp.id))
        print(" On switch %s" % lp.logical_switch_id)
        attachment = ("None" if lp.attachment is None else
                      "%s %s" % (lp.attachment.attachment_type,
                                 lp.attachment.id))
        print(" Attached to: %s" % attachment)

        # Retrieve the statistics for the port.
        if lp.attachment and lp.attachment.attachment_type == "VIF":
            stats = lp_statistics_svc.get(lp.id, source="realtime")
        else:
            stats = lp_statistics_svc.get(lp.id)
        print_l2_stats(stats)
        print("")

    # Find all logical router ports and show statistics for each.
    all_lrps = lrp_svc.list()
    print("***** Showing statistics for %d logical router ports" %
          all_lrps.result_count)
    for lrp in all_lrps.results:
        # Show the port's type, name and id and what it's attached to,
        # if anything.
        # Since logical router ports are polymorphic, convert to the
        # base class so we can retrieve the type information.
        lrp = lrp.convert_to(LogicalRouterPort)
        print("%s %s (id %s)" % (lrp.resource_type, lrp.display_name, lrp.id))
        stats = lrp_statistics_svc.get(lrp.id, source="cached")
        print_lrp_stats(stats)


if __name__ == "__main__":
    main()
