#!/usr/bin/env python

"""
NSX-T SDK Sample Code

Copyright 2017 VMware, Inc.  All rights reserved

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

import sys

from com.vmware.nsx_client import LogicalPorts
from com.vmware.nsx_client import LogicalRouterPorts
from com.vmware.nsx_client import LogicalRouters
from com.vmware.nsx_client import LogicalSwitches
from com.vmware.nsx_client import TransportZones
from com.vmware.nsx.firewall_client import Sections
from com.vmware.nsx.model_client import FirewallRule
from com.vmware.nsx.model_client import FirewallSection
from com.vmware.nsx.model_client import FirewallSectionRuleList
from com.vmware.nsx.model_client import FirewallService
from com.vmware.nsx.model_client import IPSubnet
from com.vmware.nsx.model_client import LogicalPort
from com.vmware.nsx.model_client import LogicalRouter
from com.vmware.nsx.model_client import LogicalRouterDownLinkPort
from com.vmware.nsx.model_client import LogicalRouterPort
from com.vmware.nsx.model_client import LogicalSwitch
from com.vmware.nsx.model_client import ResourceReference
from com.vmware.nsx.model_client import TransportZone
from com.vmware.vapi.std.errors_client import NotFound
from util import auth
from util import getargs
from vmware.vapi.bindings.struct import PrettyPrinter

"""
This example illustrates a basic layer-3 networking demo. It uses the NSX API
to create a simple 2-tier application network topology, where the
application's database server(s) are on one logical switch, and the web
server(s) are on a second logical switch. A logical router connects the web
tier and the db tier, and a firewall blocks all traffic between the networks
except for MS SQL server traffic and ICMP pings.

This example only constructs the logical switches and routers. and
establishes the firewall rules. To actually connect VMs running databases and
web servers, you will need to provision VMs, install the correct software,
and attach network interfaces on the VMs to the logical switches created by
this example.

Topology:

                +--------------+
    192.168.1.1 |              |192.168.2.1
          +-----|              |-------+
          |     |   lr-demo    |       |
          |     |              |       |
          |     +--------------+       |
          |                            |
          |                            |
  +-------|----+                +------|-----+
  |            |                |            |
  |   ls-db    |                |   ls-web   |
  +------------+                +------------+
  192.168.1.0/24                192.168.2.1/24

Compatible with: NSX-T 2.1

APIs used:

Create a trasport zone:
POST /api/v1/transport-zones

Create a logical switch:
POST /api/v1/logical-switches

Create a logical router:
POST /api/v1/logical-routers

Create a logical port:
POST /api/v1/logical-ports

Create a logical router downlink port:
POST /api/v1/logical-router-ports

Create a firewall section with rules:
POST /api/v1/firewall/sections?action=create_with_rules

Update a firewall section:
PUT /api/v1/firewall/sections/<section-id>

Delete a firewall section:
DELETE /api/v1/firewall/sections/<section-id>

Delete a logical router port:
DELETE /api/v1/logical-router-ports/<logical-router-port-id>

Delete a logical port:
DELETE /api/v1/logical-ports/<lport-id>

Delete a logical router:
DELETE /api/v1/logical-routers/<logical-router-id>

Delete a logical switch:
DELETE /api/v1/logical-switches/<lswitch-id>

Delete a transport zone:
DELETE /api/v1/transport-zones/<zone-id>
"""


def main():
    args = getargs.getargs()
    stub_config = auth.get_session_auth_stub_config(args.user, args.password,
                                                    args.nsx_host,
                                                    args.tcp_port)

    pp = PrettyPrinter()

    # Instantiate all the services we'll need.
    transportzones_svc = TransportZones(stub_config)
    logicalswitches_svc = LogicalSwitches(stub_config)
    logicalrouters_svc = LogicalRouters(stub_config)
    logicalrouterports_svc = LogicalRouterPorts(stub_config)
    logicalports_svc = LogicalPorts(stub_config)
    fwsections_svc = Sections(stub_config)

    # Create a transport zone
    new_tz = TransportZone(
        transport_type=TransportZone.TRANSPORT_TYPE_OVERLAY,
        display_name="Two Tier App Demo Transport Zone",
        description="Transport zone for two-tier app demo",
        host_switch_name="hostswitch"
    )
    demo_tz = transportzones_svc.create(new_tz)

    # Create a logical switch for the db tier
    new_ls = LogicalSwitch(
        transport_zone_id=demo_tz.id,
        admin_state=LogicalSwitch.ADMIN_STATE_UP,
        replication_mode=LogicalSwitch.REPLICATION_MODE_MTEP,
        display_name="ls-db",
    )
    db_ls = logicalswitches_svc.create(new_ls)

    # Create a logical switch for the web tier
    new_ls = LogicalSwitch(
        transport_zone_id=demo_tz.id,
        admin_state=LogicalSwitch.ADMIN_STATE_UP,
        replication_mode=LogicalSwitch.REPLICATION_MODE_MTEP,
        display_name="ls-web",
    )
    web_ls = logicalswitches_svc.create(new_ls)

    # Create a logical router that will route traffic between
    # the web and db tiers
    new_lr = LogicalRouter(
        router_type=LogicalRouter.ROUTER_TYPE_TIER1,
        display_name="lr-demo",
        failover_mode=LogicalRouter.FAILOVER_MODE_PREEMPTIVE
    )
    lr = logicalrouters_svc.create(new_lr)

    # Create a logical port on the db and web logical switches. We
    # will attach the logical router to those ports so that it can
    # route between the logical switches.
    # Logical port on the db logical switch
    new_lp = LogicalPort(
        admin_state=LogicalPort.ADMIN_STATE_UP,
        logical_switch_id=db_ls.id,
        display_name="dbTierUplinkToRouter"
    )
    db_port_on_ls = logicalports_svc.create(new_lp)

    # Logical port on the web logical switch
    new_lp = LogicalPort(
        admin_state=LogicalPort.ADMIN_STATE_UP,
        logical_switch_id=web_ls.id,
        display_name="webTierUplinkToRouter"
    )
    web_port_on_ls = logicalports_svc.create(new_lp)

    # Populate a logical router downlink port payload and configure
    # the port with the CIDR 192.168.1.1/24. We will attach this
    # port to the db tier's logical switch.
    new_lr_port = LogicalRouterDownLinkPort(
        subnets=[IPSubnet(ip_addresses=["192.168.1.1"], prefix_length=24)],
        linked_logical_switch_port_id=ResourceReference(
            target_id=db_port_on_ls.id),
        resource_type="LogicalRouterDownLinkPort",
        logical_router_id=lr.id
    )
    # Create the downlink port
    lr_port_for_db_tier = logicalrouterports_svc.create(new_lr_port)
    # Convert to concrete type
    lr_port_for_db_tier = lr_port_for_db_tier.convert_to(
        LogicalRouterDownLinkPort)

    # Populate a logical router downlink port payload and configure
    # the port with the CIDR 192.168.2.1/24. We will attach this
    # port to the web tier's logical switch.
    new_lr_port = LogicalRouterDownLinkPort(
        subnets=[IPSubnet(ip_addresses=["192.168.2.1"], prefix_length=24)],
        linked_logical_switch_port_id=ResourceReference(
            target_id=web_port_on_ls.id),
        resource_type="LogicalRouterDownLinkPort",
        logical_router_id=lr.id
    )
    # Create the downlink port
    lr_port_for_web_tier = logicalrouterports_svc.create(new_lr_port)
    lr_port_for_web_tier = lr_port_for_web_tier.convert_to(
        LogicalRouterDownLinkPort)

    # Now establish a firewall policy that only allows MSSQL
    # server traffic and ICMP traffic in and out of the db tier's
    # logical switch.

    # Create 3 firewall rules. The first will allow traffic used
    # by MS SQL Server to pass. This rule references a built-in
    # ns service group that includes all the common ports used by
    # the MSSQL Server. The ID is common to all NSX installations.
    MSSQL_SERVER_NS_GROUP_ID = "5a6d380a-6d28-4e3f-b705-489f463ae6ad"
    ms_sql_rule = FirewallRule(
        action=FirewallRule.ACTION_ALLOW,
        display_name="Allow MSSQL Server",
        ip_protocol=FirewallRule.IP_PROTOCOL_IPV4_IPV6,
        services=[
            FirewallService(
                target_type="NSServiceGroup",
                target_id=MSSQL_SERVER_NS_GROUP_ID
            )
        ]
    )

    # The second rule will allow ICMP echo requests and responses.
    ICMP_ECHO_REQUEST_NS_SVC_ID = "5531a880-61aa-42cc-ba4b-13b9ea611e2f"
    ICMP_ECHO_REPLY_NS_SVC_ID = "c54b2d86-6327-41ff-a3fc-c67171b6ba63"
    icmp_rule = FirewallRule(
        action=FirewallRule.ACTION_ALLOW,
        display_name="Allow ICMP Echo",
        ip_protocol=FirewallRule.IP_PROTOCOL_IPV4_IPV6,
        services=[
            FirewallService(
                target_type="NSService",
                target_id=ICMP_ECHO_REQUEST_NS_SVC_ID
            ),
            FirewallService(
                target_type="NSService",
                target_id=ICMP_ECHO_REPLY_NS_SVC_ID
            )
        ]
    )

    # The third rule will drop all traffic not passed by the previous
    # rules.
    block_all_rule = FirewallRule(
        action=FirewallRule.ACTION_DROP,
        display_name="Drop all",
        ip_protocol=FirewallRule.IP_PROTOCOL_IPV4_IPV6
    )

    # Add all rules to a new firewall section and create the section.
    rule_list = FirewallSectionRuleList(
        rules=[ms_sql_rule, icmp_rule, block_all_rule],
        section_type=FirewallSection.SECTION_TYPE_LAYER3,
        stateful=True,
        display_name="MSSQL Server",
        description="Only allow MSSQL server traffic"
    )
    demo_section = fwsections_svc.createwithrules(
        rule_list, None, operation="insert_top")

    # Re-read the firewall section so that we are operating on up-to-date
    # data.
    section = fwsections_svc.get(demo_section.id)

    # Make the firewall section apply to the db tier logical
    # switch. This enables the firewall policy on all logical
    # ports attached to the db tier logical switch.
    section.applied_tos = [
        ResourceReference(target_id=db_ls.id,
                          target_type="LogicalSwitch")
    ]
    fwsections_svc.update(section.id, section)

    print("At this point you may attach VMs for the db tier to the db")
    print("logical switch and VMs for the web tier to the web logical")
    print("switch. The network interfaces should be configured as")
    print("follows:")
    print("db tier:")
    print("    IP address: in the range 192.168.1.2-254")
    print("    Netmask: 255.255.255.0")
    print("    Default route: 192.168.1.1")
    print("web tier:")
    print("    IP address: in the range 192.168.2.2-254")
    print("    Netmask: 255.255.255.0")
    print("    Default route: 192.168.2.1")
    print("Logical switch IDs:")
    print("    %s: %s" % (db_ls.display_name, db_ls.id))
    print("    %s: %s" % (web_ls.display_name, web_ls.id))
    print("Transport zone: %s: %s" % (demo_tz.display_name, demo_tz.id))

    print("Press enter to delete all resources created for this example.")
    sys.stdin.readline()

    fwsections_svc.delete(section.id, cascade=True)
    logicalrouterports_svc.delete(lr_port_for_web_tier.id)
    logicalrouterports_svc.delete(lr_port_for_db_tier.id)
    logicalports_svc.delete(web_port_on_ls.id)
    logicalports_svc.delete(db_port_on_ls.id)
    logicalrouters_svc.delete(lr.id)
    logicalswitches_svc.delete(web_ls.id)
    logicalswitches_svc.delete(db_ls.id)
    transportzones_svc.delete(demo_tz.id)

if __name__ == "__main__":
    main()
