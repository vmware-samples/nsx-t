#!/usr/bin/env python
"""
"""

import sys

from com.vmware.nsx_client import LogicalPorts
from com.vmware.nsx.logical_ports_client import ForwardingPath
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
This example shows how to retrieve the forwarding path between
two logical ports.

APIs used:

List logical ports:
GET /api/v1/logical-ports

Get forwarding path between two logical ports:
GET /api/v1/logical-ports/<lport-id>/forwarding-path
"""


def main():
    arg_parser = getargs.get_arg_parser()
    arg_parser.add_argument("port1", metavar="PORT_ID_1", type=str, nargs="?",
                            help="Logical port 1")
    arg_parser.add_argument("port2", metavar="PORT_ID_2", type=str, nargs="?",
                            help="Logical port 2")
    args = arg_parser.parse_args()

    # Verify exactly 0 or 2 ports were given
    ports = [x for x in [args.port1, args.port2] if x is not None]
    if len(ports) not in (0, 2):
        arg_parser.error("Give exactly two logical port IDs, or none to "
                         "get a list of logical ports.")
        
    stub_config = auth.get_session_auth_stub_config(args.user, args.password,
                                                    args.nsx_host,
                                                    args.tcp_port)

    pp = PrettyPrinter()

    # Instantiate all the services we'll need.
    lp_svc = LogicalPorts(stub_config)
    forwardingpath_svc = ForwardingPath(stub_config)

    # Find all logical ports
    all_lps = lp_svc.list().results
    lp_ids = [lp.id for lp in all_lps]
    fail = False
    for port in ports:
        if not port in lp_ids:
            print("Logical port %s not found" % port)
            fail = True
    if fail:
        sys.exit(1)
    print("Checking forwarding path between %s and %s" % (args.port1, args.port2))
    if len(ports) == 0:
        # Print all the ports
        for lp in all_lps:
            # Show the port's name and id, the logical switch it's on,
            # and what it's attached to, if anything.
            print("Logical port %s (id %s)" % (lp.display_name, lp.id))
            print(" On switch %s" % lp.logical_switch_id)
            attachment = ("None" if lp.attachment is None else
                          "%s %s" % (lp.attachment.attachment_type,
                                     lp.attachment.id))
            print(" Attached to: %s" % attachment)

    else:
        # Print forwarding path
        path = forwardingpath_svc.get(ports[0], ports[1])
        pp.pprint(path)

if __name__ == "__main__":
    main()
