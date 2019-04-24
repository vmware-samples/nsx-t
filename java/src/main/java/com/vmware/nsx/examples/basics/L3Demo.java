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

package com.vmware.nsx.examples.basics;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Scanner;

import org.apache.commons.cli.CommandLine;

import com.vmware.nsx.LogicalPorts;
import com.vmware.nsx.LogicalRouterPorts;
import com.vmware.nsx.LogicalRouters;
import com.vmware.nsx.LogicalSwitches;
import com.vmware.nsx.TransportZones;
import com.vmware.nsx.examples.util.ApiClientUtils;
import com.vmware.nsx.examples.util.CliUtils;
import com.vmware.nsx.firewall.Sections;
import com.vmware.nsx.model.FirewallRule;
import com.vmware.nsx.model.FirewallSection;
import com.vmware.nsx.model.FirewallService;
import com.vmware.nsx.model.IPSubnet;
import com.vmware.nsx.model.LogicalPort;
import com.vmware.nsx.model.LogicalRouterDownLinkPort;
import com.vmware.nsx.model.ResourceReference;
import com.vmware.nsx.model.FirewallSectionRuleList;
import com.vmware.nsx.model.LogicalRouter;
import com.vmware.nsx.model.LogicalSwitch;
import com.vmware.nsx.model.TransportZone;
import com.vmware.vapi.client.ApiClient;

/*
 * This example illustrates a basic layer-3 networking demo. It uses the NSX API
 * to create a simple 2-tier application network topology, where the
 * application's database server(s) are on one logical switch, and the web
 * server(s) are on a second logical switch. A logical router connects the web
 * tier and the db tier, and a firewall blocks all traffic between the networks
 * except for MS SQL server traffic and ICMP pings.
 *
 * This example only constructs the logical switches and routers. and
 * establishes the firewall rules. To actually connect VMs running databases and
 * web servers, you will need to provision VMs, install the correct software,
 * and attach network interfaces on the VMs to the logical switches created by
 * this example.
 *
 */

/*-
 *
 * Topology:
 *
 *                 +--------------+
 *     192.168.1.1 |              |192.168.2.1
 *           +-----|              |-------+
 *           |     |   lr-demo    |       |
 *           |     |              |       |
 *           |     +--------------+       |
 *           |                            |
 *           |                            |
 *   +-------|----+                +------|-----+
 *   |            |                |            |
 *   |   ls-db    |                |   ls-web   |
 *   +------------+                +------------+
 *   192.168.1.0/24                192.168.2.1/24
 *   APIs used:
 *
 * Create a transport zone:
 * POST /api/v1/transport-zones
 *
 * Create a logical switch:
 * POST /api/v1/logical-switches
 *
 * Create a logical router:
 * POST /api/v1/logical-routers
 *
 * Create a logical port:
 * POST /api/v1/logical-ports
 *
 * Create a logical router downlink port:
 * POST /api/v1/logical-router-ports
 *
 * Create a firewall section with rules:
 * POST /api/v1/firewall/sections?action=create_with_rules
 *
 * Update a firewall section:
 * PUT /api/v1/firewall/sections/<section-id>
 *
 * Delete a firewall section:
 * DELETE /api/v1/firewall/sections/<section-id>
 *
 * Delete a logical router port:
 * DELETE /api/v1/logical-router-ports/<logical-router-port-id>
 *
 * Delete a logical port:
 * DELETE /api/v1/logical-ports/<lport-id>
 *
 * Delete a logical router:
 * DELETE /api/v1/logical-routers/<logical-router-id>
 *
 * Delete a logical switch:
 * DELETE /api/v1/logical-switches/<lswitch-id>
 *
 * Delete a transport zone:
 * DELETE /api/v1/transport-zones/<zone-id>
 *
 */


public class L3Demo {

    public static void main(String[] args) {
        CommandLine cmd = CliUtils.parseArgs(args);
        String uri = "https://" + cmd.getOptionValue("nsx_host") + ":"
                + cmd.getOptionValue("tcp_port", "443");
        ApiClient apiClient = ApiClientUtils.createApiClient(uri,
                cmd.getOptionValue("user"),
                cmd.getOptionValue("password").toCharArray());

        // Create all of the services we'll need.
        TransportZones zoneService = apiClient.createStub(TransportZones.class);
        LogicalSwitches switchService = apiClient
                .createStub(LogicalSwitches.class);
        LogicalRouters routerService = apiClient
                .createStub(LogicalRouters.class);
        LogicalPorts portService = apiClient.createStub(LogicalPorts.class);
        LogicalRouterPorts lrportService = apiClient
                .createStub(LogicalRouterPorts.class);
        Sections fwSectionService = apiClient.createStub(Sections.class);

        // Create a transport tone.
        TransportZone newTZ = new TransportZone.Builder(
                TransportZone.TRANSPORT_TYPE_OVERLAY)
                        .setDisplayName("Two Tier App Demo Transport Zone")
                        .setDescription(
                                "Transport zone for two-tier app demo")
                        .setHostSwitchName("hostswitch")
                        .build();
        TransportZone demoTZ = zoneService.create(newTZ);

        // Create a logical switch for the db tier
        LogicalSwitch newLS = new LogicalSwitch.Builder(
                LogicalSwitch.ADMIN_STATE_UP, demoTZ.getId())
                        .setReplicationMode(
                                LogicalSwitch.REPLICATION_MODE_MTEP).setDisplayName("ls-db")
                        .build();
        LogicalSwitch dbLS = switchService.create(newLS);

        // Create a logical switch for the web tier
        newLS = new LogicalSwitch.Builder(
                LogicalSwitch.ADMIN_STATE_UP, demoTZ.getId())
                        .setReplicationMode(
                                LogicalSwitch.REPLICATION_MODE_MTEP).setDisplayName("ls-web")
                        .build();
        LogicalSwitch webLS = switchService.create(newLS);

        // Create a logical router that will route traffic between the web and db tiers
        LogicalRouter newRouter = new LogicalRouter.Builder(
                LogicalRouter.ROUTER_TYPE_TIER1).setDisplayName("lr-demo")
                        .setFailoverMode(LogicalRouter.FAILOVER_MODE_PREEMPTIVE)
                        .build();
        LogicalRouter lr = routerService.create(newRouter);

        // Create a logical port on the db and web logical switches. We
        // will attach the logical router to those ports so that it can
        // route between the logical switches.

        // Logical port on the db logical switch
        LogicalPort newLP = new LogicalPort.Builder(LogicalPort.ADMIN_STATE_UP,
                dbLS.getId()).setDisplayName("dbTierUplinkToRouter").build();
        LogicalPort dbPortOnLS = portService.create(newLP);

        // Logical port on the web logical switch
        newLP = new LogicalPort.Builder(LogicalPort.ADMIN_STATE_UP,
                webLS.getId()).setDisplayName("webTierUplinkToRouter").build();
        LogicalPort webPortOnLS = portService.create(newLP);

        // Populate a logical router downlink port payload and configure the
        // port with the CIDR 192.168.1.1/24. We will attach this port to the
        // db tier's logical switch.
        List<IPSubnet> subnets = new ArrayList<IPSubnet>();
        subnets.add(
                new IPSubnet.Builder(Arrays.asList("192.168.1.1"), 24).build());
        ResourceReference linkedLSPort = new ResourceReference.Builder()
                .setTargetId(dbPortOnLS.getId()).build();
        LogicalRouterDownLinkPort newLRPort = new LogicalRouterDownLinkPort.Builder(
                subnets, lr.getId())
                        .setLinkedLogicalSwitchPortId(linkedLSPort).build();
        // Create the downlink port
        LogicalRouterDownLinkPort lrPortForDbTier = lrportService
                .create(newLRPort)._convertTo(LogicalRouterDownLinkPort.class);

        // Populate a logical router downlink port payload and configure the
        // port with the CIDR 192.168.2.1/24. We will attach this port to the
        // web tier's logical switch.
        subnets = new ArrayList<IPSubnet>();
        subnets.add(
                new IPSubnet.Builder(Arrays.asList("192.168.2.1"), 24).build());
        linkedLSPort = new ResourceReference.Builder()
                .setTargetId(webPortOnLS.getId()).build();
        newLRPort = new LogicalRouterDownLinkPort.Builder(subnets, lr.getId())
                .setLinkedLogicalSwitchPortId(linkedLSPort).build();
        // Create the downlink port
        LogicalRouterDownLinkPort lrPortForWebTier = lrportService
                .create(newLRPort)._convertTo(LogicalRouterDownLinkPort.class);

        // Now establish a firewall policy that only allows MSSQL server traffic
        // and ICMP traffic in and out of the db tier's logical switch.

        // Create 3 firewall rules. The first will allow traffic used by
        // MS SQL Server to pass. This rule references a built-in
        // ns service group that includes all the common ports used
        // by the MSSQL Server. The ID is common to all NSX installations.
        final String MSSQL_SERVER_NS_GROUP_ID = "5a6d380a-6d28-4e3f-b705-489f463ae6ad";
        List<FirewallService> services = new ArrayList<FirewallService>();
        services.add(
                new FirewallService.Builder().setTargetType("NSServiceGroup")
                        .setTargetId(MSSQL_SERVER_NS_GROUP_ID).build());
        FirewallRule msSQLRule = new FirewallRule.Builder(
                FirewallRule.ACTION_ALLOW).setDisplayName("Allow MSSQL Server")
                        .setIpProtocol(FirewallRule.IP_PROTOCOL_IPV4_IPV6)
                        .setServices(services).build();

        // The second rule will allow ICMP echo requests and responses.
        final String ICMP_ECHO_REQUEST_NS_SVC_ID = "5531a880-61aa-42cc-ba4b-13b9ea611e2f";
        final String ICMP_ECHO_REPLY_NS_SVC_ID = "c54b2d86-6327-41ff-a3fc-c67171b6ba63";
        services = new ArrayList<FirewallService>();
        services.add(new FirewallService.Builder().setTargetType("NSService")
                .setTargetId(ICMP_ECHO_REQUEST_NS_SVC_ID).build());
        services.add(new FirewallService.Builder().setTargetType("NSService")
                .setTargetId(ICMP_ECHO_REPLY_NS_SVC_ID).build());
        FirewallRule icmpRule = new FirewallRule.Builder(
                FirewallRule.ACTION_ALLOW).setDisplayName("Allow ICMP Echo")
                        .setIpProtocol(FirewallRule.IP_PROTOCOL_IPV4_IPV6)
                        .setServices(services).build();

        // The third rule will drop all traffic not passed by the previous
        // rules.
        FirewallRule blockAllRule = new FirewallRule.Builder(
                FirewallRule.ACTION_DROP).setDisplayName("Drop all")
                        .setIpProtocol(FirewallRule.IP_PROTOCOL_IPV4_IPV6)
                        .build();

        // Add all rules to a new firewall section and create the section.
        FirewallSectionRuleList ruleList = new FirewallSectionRuleList.Builder(
                FirewallSection.SECTION_TYPE_LAYER3,
                true,
                Arrays.asList(msSQLRule, icmpRule, blockAllRule))
                        .setDisplayName("MSSQL Server")
                        .setDescription("Only allow MSSQL server traffic").build();
        FirewallSectionRuleList demoSection = fwSectionService.createwithrules(ruleList, null, "insert_top");

        // Re-read the firewall section so that we are operating on up-to-date
        // data.
        FirewallSection section = fwSectionService.get(demoSection.getId());

        // Make the firewall section apply to the db tier logical switch. This
        // enables the firewall policy on all logical ports attached to the
        // db tier logical switch.
        List<ResourceReference> appliedTos = new ArrayList<ResourceReference>();
        appliedTos.add(
                new ResourceReference.Builder().setTargetType("LogicalSwitch")
                        .setTargetId(dbLS.getId()).build());
        section.setAppliedTos(appliedTos);
        fwSectionService.update(section.getId(), section);

        System.out.println("At this point you may attach VMs for the db tier to the db");
        System.out.println("logical switch and VMs for the web tier to the web logical");
        System.out.println("switch. The network interfaces should be configured as");
        System.out.println("follows:");
        System.out.println("db tier:");
        System.out.println("    IP address: in the range 192.168.1.2-254");
        System.out.println("    Netmask: 255.255.255.0");
        System.out.println("    Default route: 192.168.1.1");
        System.out.println(" web tier:");
        System.out.println("    IP address: in the range 192.168.2.2-254");
        System.out.println("    Netmask: 255.255.255.0");
        System.out.println("    Default route: 192.168.2.1");
        System.out.println("Logical switch IDs:");
        System.out.println("    " + dbLS.getDisplayName() + ": " + dbLS.getId());
        System.out.println("    " + webLS.getDisplayName() + ": " + webLS.getId());
        System.out.println("Transport zone: " + demoTZ.getDisplayName() + ": " + demoTZ.getId());

        System.out.println("Press enter to delete all resources created for this example.");
        Scanner scanner = new Scanner(System.in);
        scanner.nextLine();
        scanner.close();

        fwSectionService.delete(section.getId(), true);
        lrportService.delete(lrPortForWebTier.getId(), true, true);
        lrportService.delete(lrPortForDbTier.getId(), true, true);
        lrportService.delete(webPortOnLS.getId(), true, true);
        lrportService.delete(dbPortOnLS.getId(), true, true);
        routerService.delete(lr.getId(), true, true);
        switchService.delete(webLS.getId(), true, true);
        switchService.delete(dbLS.getId(), true, true);
        zoneService.delete(demoTZ.getId());
    }
}
