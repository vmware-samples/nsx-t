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
from com.vmware.nsx.logical_ports_client import ForwardingPath
from com.vmware.vapi.std.errors_client import NotFound
from util import auth
from util import getargs
from vmware.vapi.bindings.struct import PrettyPrinter

"""
This example shows how to retrieve the forwarding path between
two logical ports.

Compatible with: NSX-T 2.1

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
        if port not in lp_ids:
            print("Logical port %s not found" % port)
            fail = True
    if fail:
        sys.exit(1)
    print("Checking forwarding path between %s and %s" %
          (args.port1, args.port2))
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
