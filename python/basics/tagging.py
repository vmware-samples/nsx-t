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
import sys
import time

from util import auth
from util import getargs

from com.vmware.nsx_client import LogicalPorts
from com.vmware.nsx_client import LogicalSwitches
from com.vmware.nsx_client import NsGroups
from com.vmware.nsx_client import TransportZones
from com.vmware.nsx.model_client import LogicalPort
from com.vmware.nsx.model_client import LogicalSwitch
from com.vmware.nsx.model_client import NSGroup
from com.vmware.nsx.model_client import NSGroupExpression
from com.vmware.nsx.model_client import NSGroupTagExpression
from com.vmware.nsx.model_client import Tag
from com.vmware.nsx.model_client import TransportZone
from com.vmware.nsx.ns_groups_client import EffectiveLogicalPortMembers
from com.vmware.vapi.std.errors_client import NotFound
from vmware.vapi.bindings.struct import PrettyPrinter

"""
This example shows how to manage tags on NSX-T resources.
Tags are arbitrary metadata that you can set. They can
be used as search criteria for groups, which allows group
membership to be dynamically determined.

In this example, we'll create some logical ports and apply
tags to them. Then we'll create some groups and show how
the group membership changes as new ports are added,
removed, or have their tags changed.

In NSX-T, tags have a scope and a value. The scope allows
you to define different namespaces for whatever purpose
you need. For example, a scope "department" could be
used in indicate which department "owns" a particular
resource.

Groups can be the target of an applied_to in a firewall
section. So, for example, if you want to disable a set of
logical ports (for example, where you suspect some sort
of security breach), you could define a firewall section
that blocks all traffic and apply it to a group whose
members include any ports with the tag "security" and
scope "breach". When you add the "security:breach" tag
to a port, it will become a member of that group and
the block-all firewall policy will become effective.

APIs used:

Create transport zone:
POST /api/v1/transport-zones

Create logical switch:
POST /api/v1/logical-switches

Create an NSGroup:
POST /api/v1/ns-groups

Retrieve effective lport group membership:
GET /api/v1/ns-groups/<group-id>/effective-logical-port-members

Create a logical port:
POST /api/v1/logical-ports

Modify a logical port:
PUT /api/v1/logical-ports/<lport-id>

Delete a logical port:
DELETE /api/v1/logical-ports/<lport-id>

Delete an NSGroup:
DELETE /api/v1/ns-groups/<group-id>

Delete a logical switch:
DELETE /api/v1/logical-switches/<lswitch-id>

Delete a transport zone
DELETE /api/v1/transport-zones/<zone-id>

"""


def print_group_effective_members(group_name, group):
    print("Group %s, member count = %d" % (group_name, group.result_count))
    eff_mbrs_results = group.results
    for eff_mbr in eff_mbrs_results:
        print("  %s id %s" % (eff_mbr.target_display_name, eff_mbr.target_id))


def main():
    args = getargs.getargs()
    stub_config = auth.get_session_auth_stub_config(args.user, args.password,
                                                    args.nsx_host,
                                                    args.tcp_port)

    # Create a pretty printer to make the output look nice.
    pp = PrettyPrinter()

    # Create the services we'll need.
    transportzones_svc = TransportZones(stub_config)
    logicalswitches_svc = LogicalSwitches(stub_config)
    logicalports_svc = LogicalPorts(stub_config)
    nsgroups_svc = NsGroups(stub_config)
    efflports_svc = EffectiveLogicalPortMembers(stub_config)

    # Create a transport zone and logical switch. We only
    # need these so we can create logical ports. They aren't
    # part of the demo.
    tz = TransportZone(
        transport_type=TransportZone.TRANSPORT_TYPE_OVERLAY,
        display_name="Tagging Demo Transport Zone",
        description="Transport zone for tagging demo",
        host_switch_name="hostswitch"
    )
    tz = transportzones_svc.create(tz)
    ls = LogicalSwitch(
        transport_zone_id=tz.id,
        admin_state=LogicalSwitch.ADMIN_STATE_UP,
        replication_mode=LogicalSwitch.REPLICATION_MODE_MTEP,
        display_name="ls-tag-demo",
    )
    ls = logicalswitches_svc.create(ls)

    # First, create a new group whose members are any logical
    # ports with a tag scope of "color" and tag value of "green"
    group = NSGroup(
        display_name="Green Logical Ports",
        description="All logical ports with scope=color and tag=green",
        membership_criteria=[
            NSGroupTagExpression(
                resource_type="NSGroupTagExpression",
                target_type="LogicalPort",
                scope_op="EQUALS",
                scope="color",
                tag_op="EQUALS",
                tag="green"
            )
        ]
    )
    green_group = nsgroups_svc.create(group)

    # Now create another group for color:yellow logical ports.
    group = NSGroup(
        display_name="Yellow Logical Ports",
        description="All logical ports with scope=color and tag=yellow",
        membership_criteria=[
            NSGroupTagExpression(
                resource_type="NSGroupTagExpression",
                target_type="LogicalPort",
                scope_op="EQUALS",
                scope="color",
                tag_op="EQUALS",
                tag="yellow"
            )
        ]
    )
    yellow_group = nsgroups_svc.create(group)

    # Now get the list of effective members (that is, logical ports
    # with color:green). There should be no effective members yet.
    print("Before creating any lports:")
    print_group_effective_members("green group",
                                  efflports_svc.list(green_group.id))
    print_group_effective_members("yellow group",
                                  efflports_svc.list(yellow_group.id))
    print("")

    # Create a logical port with color:green
    lport = LogicalPort(
        display_name="tagging-demo-lp1",
        admin_state=LogicalPort.ADMIN_STATE_UP,
        logical_switch_id=ls.id,
        tags=[
            Tag(scope="color", tag="green")
        ]
    )
    lport = logicalports_svc.create(lport)
    print("Logical port for this test has id %s" % lport.id)
    print("")

    # Group membership is computed asynchronously in the NSX
    # manager. Wait a bit.
    time.sleep(2.0)

    # Find the effective members of the green and yellow groups.
    # Notice that the logical port is in the green group.
    print("After creating green lport:")
    print_group_effective_members("green group",
                                  efflports_svc.list(green_group.id))
    print_group_effective_members("yellow group",
                                  efflports_svc.list(yellow_group.id))
    print("")

    # Now modify the logical port's color to yellow.
    lport = logicalports_svc.get(lport.id)
    lport.tags = [Tag(scope="color", tag="yellow")]
    logicalports_svc.update(lport.id, lport)

    # Wait for group recalculation
    time.sleep(2.0)

    # Find the effective members of the green and yellow groups.
    # Notice that the logical port is now in the yellow group
    # and no longer in the green group.
    print("After changing lport color to yellow:")
    print_group_effective_members("green group",
                                  efflports_svc.list(green_group.id))
    print_group_effective_members("yellow group",
                                  efflports_svc.list(yellow_group.id))
    print("")

    # Now clear the tag
    lport = logicalports_svc.get(lport.id)
    lport.tags = []
    logicalports_svc.update(lport.id, lport)

    # Wait for group recalculation
    time.sleep(2.0)

    # The port should be in neither group
    print("After removing lport color tag:")
    print_group_effective_members("green group",
                                  efflports_svc.list(green_group.id))
    print_group_effective_members("yellow group",
                                  efflports_svc.list(yellow_group.id))
    print("")

    print("Press enter to delete all resources created for this example.")
    sys.stdin.readline()

    # Delete all resources we created.
    logicalports_svc.delete(lport.id)
    nsgroups_svc.delete(green_group.id)
    nsgroups_svc.delete(yellow_group.id)
    logicalswitches_svc.delete(ls.id)
    transportzones_svc.delete(tz.id)


if __name__ == "__main__":
    main()
