#!/usr/bin/env python

"""
NSX-T SDK Sample Code

Copyright 2017-2019 VMware, Inc.  All rights reserved

The BSD-2 license (the "License") set forth below applies to all
parts of the NSX-T SDK Sample Code project.  You may not use this
file except in compliance with the License.

BSD-2 License

Redistribution and use in source and binary forms, with or
without modification, are permitted provided that the following
conditions are met:

    Redistributions of source code must retain the above
    copyright notice, this list of conditions and the
    following disclaimer.

    Redistributions in binary form must reproduce the above
    copyright notice, this list of conditions and the
    following disclaimer in the documentation and/or other
    materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
"""

from com.vmware.nsx.model_client import LogicalRouterPort
from com.vmware.vapi.std.errors_client import NotFound
from util import auth
from util import getargs
from vmware.vapi.bindings.struct import PrettyPrinter

"""
This example shows how to get statistics and counters for various
logical entities in an NSX-T environment.

Compatible with: NSX-T 2.1

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
    api_client = auth.create_nsx_api_client(args.user, args.password,
                                            args.nsx_host, args.tcp_port,
                                            auth_type=auth.SESSION_AUTH)
    pp = PrettyPrinter()

    # Find all logical switches and show statistics for each.
    all_ls = api_client.LogicalSwitches.list()
    print("***** Showing statistics for %d logical switches" %
          all_ls.result_count)
    for ls in all_ls.results:
        print("Logical switch %s (id %s)" % (ls.display_name, ls.id))
        # Retrieve the statistics for the switch
        stats = api_client.logical_switches.Statistics.get(ls.id)
        print_l2_stats(stats)
        print("")

    # Find all logical ports and show statistics for each.
    all_lps = api_client.LogicalPorts.list()
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
            stats = api_client.logical_ports.Statistics.get(
                lp.id, source="cached")
        else:
            stats = api_client.logical_ports.Statistice.get(lp.id)
        print_l2_stats(stats)
        print("")

    # Find all logical router ports and show statistics for each.
    all_lrps = api_client.LogicalRouterPorts.list()
    print("***** Showing statistics for %d logical router ports" %
          all_lrps.result_count)
    for lrp in all_lrps.results:
        # Show the port's type, name and id and what it's attached to,
        # if anything.
        # Since logical router ports are polymorphic, convert to the
        # base class so we can retrieve the type information.
        lrp = lrp.convert_to(LogicalRouterPort)
        print("%s %s (id %s)" % (lrp.resource_type, lrp.display_name, lrp.id))
        stats = api_client.logical_router_ports.Statistics.get(
            lrp.id, source="cached")
        print_lrp_stats(stats)


if __name__ == "__main__":
    main()
