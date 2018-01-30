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

import java.util.Arrays;
import java.util.List;
import java.util.Scanner;
import java.util.concurrent.TimeUnit;

import org.apache.commons.cli.CommandLine;

import com.vmware.nsx.LogicalPorts;
import com.vmware.nsx.LogicalSwitches;
import com.vmware.nsx.NsGroups;
import com.vmware.nsx.TransportZones;
import com.vmware.nsx.examples.util.ApiClientUtils;
import com.vmware.nsx.examples.util.CliUtils;
import com.vmware.nsx.model.EffectiveMemberResourceListResult;
import com.vmware.nsx.model.LogicalPort;
import com.vmware.nsx.model.NSGroupExpression;
import com.vmware.nsx.model.NSGroupTagExpression;
import com.vmware.nsx.model.ResourceReference;
import com.vmware.nsx.model.Tag;
import com.vmware.nsx.model.LogicalSwitch;
import com.vmware.nsx.model.NSGroup;
import com.vmware.nsx.model.TransportZone;
import com.vmware.nsx.ns_groups.EffectiveLogicalPortMembers;
import com.vmware.vapi.client.ApiClient;

/**
 * This example shows how to manage tags on NSX-T resources. Tags are arbitrary
 * metadata that you can set. They can be used as search criteria for groups,
 * which allows group membership to be dynamically determined.
 *
 * In this example, we'll create some logical ports and apply tags to them. Then
 * we'll create some groups and show how the group membership changes as new
 * ports are added, removed, or have their tags changed.
 *
 * In NSX-T, tags have a scope and a value. The scope allows you to define
 * different namespaces for whatever purpose you need. For example, a scope
 * "department" could be used in indicate which department "owns" a particular
 * resource.
 *
 * Groups can be the target of an applied_to in a firewall section. So, for
 * example, if you want to disable a set of logical ports (for example, where
 * you suspect some sort of security breach), you could define a firewall
 * section that blocks all traffic and apply it to a group whose members include
 * any ports with the tag "security" and scope "breach". When you add the
 * "security:breach" tag to a port, it will become a member of that group and
 * the block-all firewall policy will become effective.
 *
 *
 */

/*-
 * - APIs used:
 *
 * Create transport zone:
 * POST /api/v1/transport-zones
 *
 * Create logical switch:
 * POST /api/v1/logical-switches
 *
 * Create an NSGroup:
 * POST /api/v1/ns-groups
 *
 * Retrieve effective lport group membership:
 * GET /api/v1/ns-groups/<group-id>/effective-logical-port-members
 *
 * Create a logical port:
 * POST /api/v1/logical-ports
 *
 * Modify a logical port:
 * PUT /api/v1/logical-ports/<lport-id>
 *
 * Delete a logical port:
 * DELETE /api/v1/logical-ports/<lport-id>
 *
 * Delete an NSGroup:
 * DELETE /api/v1/ns-groups/<group-id>
 *
 * Delete a logical switch:
 * DELETE /api/v1/logical-switches/<lswitch-id>
 *
 * Delete a transport zone
 * DELETE /api/v1/transport-zones/<zone-id>
 *
 *
 */

public class Tagging {

    public static void main(String[] args) throws InterruptedException {
        CommandLine cmd = CliUtils.parseArgs(args);
        String uri = "https://" + cmd.getOptionValue("nsx_host") + ":"
                + cmd.getOptionValue("tcp_port", "443");
        ApiClient apiClient = ApiClientUtils.createApiClient(uri,
                cmd.getOptionValue("user"),
                cmd.getOptionValue("password").toCharArray());

        // Create the services we'll need.
        TransportZones transportZonesService = apiClient
                .createStub(TransportZones.class);
        LogicalSwitches logicalSwitchesService = apiClient
                .createStub(LogicalSwitches.class);
        LogicalPorts logicalPortsService = apiClient
                .createStub(LogicalPorts.class);
        NsGroups nsGroupsService = apiClient.createStub(NsGroups.class);
        EffectiveLogicalPortMembers effectiveLogicalPortMembersService = apiClient
                .createStub(EffectiveLogicalPortMembers.class);

        // Create a transport zone and logical switch. We only
        // need these so we can create logical ports. They aren't
        // part of the demo.
        TransportZone tz = new TransportZone.Builder(
                TransportZone.TRANSPORT_TYPE_OVERLAY)
                        .setDisplayName("Tagging Demo Transport Zone")
                        .setDescription("Transport zone for tagging demo")
                        .setHostSwitchName("hostswitch").build();
        tz = transportZonesService.create(tz);
        LogicalSwitch ls = new LogicalSwitch.Builder(
                LogicalSwitch.ADMIN_STATE_UP, tz.getId())
                        .setReplicationMode(LogicalSwitch.REPLICATION_MODE_MTEP)
                        .setDisplayName("ls-tag-demo").build();
        ls = logicalSwitchesService.create(ls);

        // First, create a new group whose members are any logical
        // ports with a tag scope of "color" and tag value of "green"
        NSGroupTagExpression expression = new NSGroupTagExpression.Builder(
                "LogicalPort", "NSGroupTagExpression").setScopeOp("EQUALS")
                        .setScope("color").setTagOp("EQUALS").setTag("green")
                        .build();
        NSGroup group = new NSGroup.Builder()
                .setDisplayName("Green Logical Ports")
                .setDescription(
                        "All logical ports with scope=color and tag=green")
                .setMembershipCriteria(Arrays.asList(expression._convertTo(NSGroupExpression.class))).build();
        NSGroup greenGroup = nsGroupsService.create(group);

        // Now create another group for color:yellow logical ports.
        expression = new NSGroupTagExpression.Builder(
                "LogicalPort", "NSGroupTagExpression").setScopeOp("EQUALS")
                        .setScope("color").setTagOp("EQUALS").setTag("green")
                        .build();
        group = new NSGroup.Builder()
                .setDisplayName("Yellow Logical Ports")
                .setDescription(
                        "All logical ports with scope=color and tag=yellow")
                .setMembershipCriteria(Arrays.asList(expression._convertTo(NSGroupExpression.class))).build();
        NSGroup yellowGroup = nsGroupsService.create(group);

        // Now get the list of effective members (that is, logical ports
        // with color:green). There should be no effective members yet.
        System.out.println("Before creating any lports:");
        printGroupEffectiveMembers("green group",
                effectiveLogicalPortMembersService.list(greenGroup.getId(),
                        null, null, null, null, null));
        printGroupEffectiveMembers("yellow group",
                effectiveLogicalPortMembersService.list(yellowGroup.getId(),
                        null, null, null, null, null));

        // Create a logical port with color:green
        Tag tag = new Tag.Builder().setScope("color").setTag("green").build();
        LogicalPort lPort = new LogicalPort.Builder(LogicalPort.ADMIN_STATE_UP,
                ls.getId()).setDisplayName("tagging-demo-lp1")
                        .setTags(Arrays.asList(tag)).build();
        lPort = logicalPortsService.create(lPort);
        System.out.println("Logical port for this test has id " + lPort.getId());

        // Group membership is computed asynchronously in the NSX
        // manager. Wait a bit.
        TimeUnit.SECONDS.sleep(2);

        // Find the effective members of the green and yellow groups.
        // Notice that the logical port is in the green group.
        System.out.println("After creating green lport:");
        printGroupEffectiveMembers("green group",
                effectiveLogicalPortMembersService.list(greenGroup.getId(),
                        null, null, null, null, null));
        printGroupEffectiveMembers("yellow group",
                effectiveLogicalPortMembersService.list(yellowGroup.getId(),
                        null, null, null, null, null));

        // Now modify the logical port's color to yellow.
        tag = new Tag.Builder().setScope("color").setTag("yellow").build();
        LogicalPort lp2 = logicalPortsService.get(lPort.getId());
        lp2.setTags(Arrays.asList(tag));
        logicalPortsService.update(lp2.getId(), lp2);

        // Wait for group recalculation
        TimeUnit.SECONDS.sleep(2);

        // Find the effective members of the green and yellow groups.
        // Notice that the logical port is now in the yellow group
        // and no longer in the green group.
        System.out.println("After changing lport color to yellow:");
        printGroupEffectiveMembers("green group",
                effectiveLogicalPortMembersService.list(greenGroup.getId(),
                        null, null, null, null, null));
        printGroupEffectiveMembers("yellow group",
                effectiveLogicalPortMembersService.list(yellowGroup.getId(),
                        null, null, null, null, null));

        // Now clear the tag
        LogicalPort lp3 = logicalPortsService.get(lPort.getId());
        lp3.setTags(null);
        logicalPortsService.update(lp3.getId(), lp3);

        // Wait for group recalculation
        TimeUnit.SECONDS.sleep(2);

        // The port should be in neither group
        System.out.println("After removing lport color tag:");
        printGroupEffectiveMembers("green group",
                effectiveLogicalPortMembersService.list(greenGroup.getId(),
                        null, null, null, null, null));
        printGroupEffectiveMembers("yellow group",
                effectiveLogicalPortMembersService.list(yellowGroup.getId(),
                        null, null, null, null, null));

        System.out.println("Press enter to delete all resources created for this example.");
        Scanner scanner = new Scanner(System.in);
        scanner.nextLine();
        scanner.close();

        // Delete all resources we created.
        logicalPortsService.delete(lPort.getId(), true);
        nsGroupsService.delete(greenGroup.getId(), true);
        nsGroupsService.delete(yellowGroup.getId(), true);
        logicalSwitchesService.delete(ls.getId(), true, true);
        transportZonesService.delete(tz.getId());
    }

    private static void printGroupEffectiveMembers(String groupName,
            EffectiveMemberResourceListResult group) {
        System.out.println("Group " + groupName + ", member count = " + group.getResultCount());
        List<ResourceReference> effMbrs = group.getResults();
        for (ResourceReference member: effMbrs) {
            System.out.println("  " + member.getTargetDisplayName() + " id " + member.getTargetId());
        }

    }

}
