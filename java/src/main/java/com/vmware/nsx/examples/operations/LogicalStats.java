/*
 * NSX-T SDK Sample Code
 *
 * Copyright 2017 VMware, Inc.  All rights reserved
 *
 * The BSD-2 license (the "License") set forth below applies to all
 * parts of the NSX-T SDK Sample Code project.  You may not use this
 * file except in compliance with the License.
 *
 * BSD-2 License
 *
 * Redistribution and use in source and binary forms, with or
 * without modification, are permitted provided that the following
 * conditions are met:
 *
 *     Redistributions of source code must retain the above
 *     copyright notice, this list of conditions and the
 *     following disclaimer.
 *
 *     Redistributions in binary form must reproduce the above
 *     copyright notice, this list of conditions and the
 *     following disclaimer in the documentation and/or other
 *     materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
 * CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
 * INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
 * MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 * LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
 * USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
 * AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 * LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
 * ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 */

package com.vmware.nsx.examples.operations;

import org.apache.commons.cli.CommandLine;

import com.vmware.nsx.LogicalPorts;
import com.vmware.nsx.LogicalRouterPorts;
import com.vmware.nsx.LogicalSwitches;
import com.vmware.nsx.examples.util.ApiClientUtils;
import com.vmware.nsx.examples.util.CliUtils;
import com.vmware.nsx.model.LogicalPort;
import com.vmware.nsx.model.LogicalRouterPort;
import com.vmware.nsx.model.PacketTypeAndCounter;
import com.vmware.nsx.model.PacketsDroppedBySecurity;
import com.vmware.nsx.model.LogicalPortListResult;
import com.vmware.nsx.model.LogicalPortStatistics;
import com.vmware.nsx.model.LogicalRouterPortListResult;
import com.vmware.nsx.model.LogicalRouterPortStatisticsSummary;
import com.vmware.nsx.model.LogicalSwitch;
import com.vmware.nsx.model.LogicalSwitchListResult;
import com.vmware.nsx.model.LogicalSwitchStatistics;
import com.vmware.vapi.bindings.Structure;
import com.vmware.vapi.client.ApiClient;

/*-
 * This example shows how to get statistics and counters for various logical
 * entities in an NSX-T environment.
 *
 * APIs used:
 *
 * List logical switches:
 * GET /api/v1/logical-switches
 *
 * Get logical switch statistics:
 * GET /api/v1/logical-switches/<lswitch-id>/statistics
 *
 * List logical ports:
 * GET /api/v1/logical-ports
 *
 * Get logical port statistics:
 * GET /api/v1/logical-ports/<lport-id>/statistics
 *
 * List logical router ports:
 * GET /api/v1/logical-router-ports
 *
 * Get logical router port statistics:
 * GET /api/v1/logical-router-ports/<logical-router-port-id>/statistics
 *
 */

public class LogicalStats {

    public static void main(String[] args) throws InterruptedException {
        CommandLine cmd = CliUtils.parseArgs(args);
        String uri = "https://" + cmd.getOptionValue("nsx_host") + ":"
                + cmd.getOptionValue("tcp_port", "443");
        ApiClient apiClient = ApiClientUtils.createApiClient(uri,
                cmd.getOptionValue("user"),
                cmd.getOptionValue("password").toCharArray());

        // Instantiate all the services we'll need.
        LogicalSwitches lsService = apiClient.createStub(LogicalSwitches.class);
        com.vmware.nsx.logical_switches.Statistics lsStatisticsService = apiClient
                .createStub(com.vmware.nsx.logical_switches.Statistics.class);
        LogicalPorts lpService = apiClient.createStub(LogicalPorts.class);
        com.vmware.nsx.logical_ports.Statistics lpStatisticsService = apiClient
                .createStub(com.vmware.nsx.logical_ports.Statistics.class);
        LogicalRouterPorts lrpService = apiClient
                .createStub(LogicalRouterPorts.class);
        com.vmware.nsx.logical_router_ports.statistics.Summary lrpStatisticsSummaryService = apiClient
                .createStub(
                        com.vmware.nsx.logical_router_ports.statistics.Summary.class);

        // Find all logical switches and show statistics for each.
        LogicalSwitchListResult allLs = lsService.list(null, null, null, null,
                null, null, null, null, null, null, null, null, null);
        System.out.println("***** Showing statistics for "
                + allLs.getResultCount() + " logical switches");
        for (LogicalSwitch ls : allLs.getResults()) {
            System.out.println("Logical switch " + ls.getDisplayName() + "(id "
                    + ls.getId() + ")");

            // Retrieve the statistics for the switch
            LogicalSwitchStatistics stats = lsStatisticsService.get(ls.getId(),
                    null, null, null);
            printLogicalSwitchStats(stats);
            System.out.println();
        }

        // Find all logical ports and show statistics for each.
        LogicalPortListResult allLp = lpService.list(null, null, null, null,
                null, null, null, null, null, null, null, null, null, null, null);
        System.out.println("***** Showing statistics for "
                + allLp.getResultCount() + " logical ports");
        for (LogicalPort lp : allLp.getResults()) {
            System.out.println("Logical port " + lp.getDisplayName() + "(id "
                    + lp.getId() + ")");
            System.out.println(" On switch " + lp.getLogicalSwitchId());
            String attachment = lp.getAttachment() == null ? "None"
                    : lp.getAttachment().getAttachmentType() + " "
                            + lp.getAttachment().getId();
            System.out.println(" Attached to " + attachment);

            // Retrieve the statistics for the port
            LogicalPortStatistics stats;
            if (lp.getAttachment() != null
                    && lp.getAttachment().getAttachmentType().equals("VIF")) {
                // Only VIF attachments support realtime stats
                stats = lpStatisticsService.get(lp.getId(), "realtime");
            } else {
                stats = lpStatisticsService.get(lp.getId(), null);
            }
            printLogicalPortStats(stats);
        }
    }

    private static void printLogicalPortStats(LogicalPortStatistics stats) {
        System.out.println(" Rx packets: total="
                + stats.getRxPackets().getTotal() + ", dropped="
                + stats.getRxPackets().getDropped() + ", multicast_broadcast="
                + stats.getRxPackets().getMulticastBroadcast());
        System.out.println(" Rx bytes: total=" + stats.getRxBytes().getTotal()
                + ". dropped=" + stats.getRxBytes().getDropped()
                + ", multicast_broadcast="
                + stats.getRxBytes().getMulticastBroadcast());
        System.out.println(" Tx packets: total="
                + stats.getTxPackets().getTotal() + ", dropped="
                + stats.getTxPackets().getDropped() + ", multicast_broadcast="
                + stats.getTxPackets().getMulticastBroadcast());
        System.out.println(" Tx bytes: total=" + stats.getTxBytes().getTotal()
                + ". dropped=" + stats.getTxBytes().getDropped()
                + ", multicast_broadcast="
                + stats.getTxBytes().getMulticastBroadcast());
        if (stats.getDroppedBySecurityPackets() == null) {
            System.out.println(" Packets dropped by security: None");
        } else {
            System.out.println(" Packets dropped by security:");
            PacketsDroppedBySecurity dropped = stats.getDroppedBySecurityPackets();
            System.out.println("    BPDU filter: " +  dropped.getBpduFilterDropped());
            System.out.println("    DHCP client IPv4: " + dropped.getDhcpClientDroppedIpv4());
            System.out.println("    DHCP client IPv6: " + dropped.getDhcpClientDroppedIpv6());
            System.out.println("    DHCP server IPv4: " + dropped.getDhcpServerDroppedIpv4());
            System.out.println("    DHCP server IPv6: " + dropped.getDhcpServerDroppedIpv6());
            if (dropped.getSpoofGuardDropped() != null) {
                System.out.println("    Spoof Guard");
                for (PacketTypeAndCounter ctr : dropped.getSpoofGuardDropped()) {
                    System.out.println("     " + ctr.getPacketType() + ": " + ctr.getCounter());
                }
            }
        }
    }

    private static void printLogicalSwitchStats(LogicalSwitchStatistics stats) {
        System.out.println(" Rx packets: total="
                + stats.getRxPackets().getTotal() + ", dropped="
                + stats.getRxPackets().getDropped() + ", multicast_broadcast="
                + stats.getRxPackets().getMulticastBroadcast());
        System.out.println(" Rx bytes: total=" + stats.getRxBytes().getTotal()
                + ". dropped=" + stats.getRxBytes().getDropped()
                + ", multicast_broadcast="
                + stats.getRxBytes().getMulticastBroadcast());
        System.out.println(" Tx packets: total="
                + stats.getTxPackets().getTotal() + ", dropped="
                + stats.getTxPackets().getDropped() + ", multicast_broadcast="
                + stats.getTxPackets().getMulticastBroadcast());
        System.out.println(" Tx bytes: total=" + stats.getTxBytes().getTotal()
                + ". dropped=" + stats.getTxBytes().getDropped()
                + ", multicast_broadcast="
                + stats.getTxBytes().getMulticastBroadcast());
        if (stats.getDroppedBySecurityPackets() == null) {
            System.out.println(" Packets dropped by security: None");
        } else {
            System.out.println(" Packets dropped by security:");
            PacketsDroppedBySecurity dropped = stats.getDroppedBySecurityPackets();
            System.out.println("    BPDU filter: " +  dropped.getBpduFilterDropped());
            System.out.println("    DHCP client IPv4: " + dropped.getDhcpClientDroppedIpv4());
            System.out.println("    DHCP client IPv6: " + dropped.getDhcpClientDroppedIpv6());
            System.out.println("    DHCP server IPv4: " + dropped.getDhcpServerDroppedIpv4());
            System.out.println("    DHCP server IPv6: " + dropped.getDhcpServerDroppedIpv6());
            if (dropped.getSpoofGuardDropped() != null) {
                System.out.println("    Spoof Guard");
                for (PacketTypeAndCounter ctr : dropped.getSpoofGuardDropped()) {
                    System.out.println("     " + ctr.getPacketType() + ": " + ctr.getCounter());
                }
            }
        }
    }
}
