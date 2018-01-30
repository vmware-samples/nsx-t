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

from util import auth
from util import getargs
from com.vmware.nsx.fabric.nodes_client import Status
from com.vmware.nsx.fabric_client import Nodes
from com.vmware.nsx.model_client import Node
from com.vmware.vapi.std.errors_client import NotFound

"""
This example shows how to obtain a list of all fabric nodes
and query their status.

Compatible with: NSX-T 2.1

APIs used:

List fabric nodes
GET /api/v1/fabric/nodes

Get fabric node status
GET /api/v1/fabric/nodes/<node-id>/status
"""


def main():
    args = getargs.getargs()
    stub_config = auth.get_session_auth_stub_config(args.user, args.password,
                                                    args.nsx_host,
                                                    args.tcp_port)

    # Create the services we'll need.
    fabricnodes_svc = Nodes(stub_config)
    status_svc = Status(stub_config)

    # List all of the fabric nodes
    result = fabricnodes_svc.list()

    # Iterate over the results
    for vs in result.results:
        fn = vs.convert_to(Node)
        print("Type: %s, Name: %s, id: %s" % (fn.resource_type,
                                              fn.display_name, fn.id))
        fn_status = status_svc.get(fn.id)
        print("    mp conn: %s, cp conn: %s" % (
            fn_status.mpa_connectivity_status,
            fn_status.lcp_connectivity_status))


if __name__ == "__main__":
    main()
