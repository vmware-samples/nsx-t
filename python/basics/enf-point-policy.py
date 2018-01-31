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

import random
import sys

from util import auth
from util import getargs

from com.vmware.nsx.model_client import ApiError
from com.vmware.nsx_policy_client import Infra
from com.vmware.nsx_policy.infra_client import DeploymentZones
from com.vmware.nsx_policy.infra.deployment_zones_client import (
    EnforcementPoints)
from com.vmware.vapi.std.errors_client import NotFound
from com.vmware.nsx_policy.model_client import EnforcementPoint
from com.vmware.nsx_policy.model_client import NSXTConnectionInfo
from com.vmware.vapi.std.errors_client import Error
from vmware.vapi.bindings.struct import PrettyPrinter

"""
This example shows how to create a deployment zone and
configure an enforcement point in the NSX Policy service.

Compatible with: NSX-T 2.2

APIs used:

"""


def main():
    arg_parser = getargs.get_arg_parser()
    arg_parser.add_argument("-s", "--remote_enforcement_point", type=str,
                            required=True,
                            help="remote enforcement point (nsx-t manager "
                            "ip address or hostname)")
    arg_parser.add_argument("-r", "--remote_login_user", type=str,
                            required=True, help="remote login username")
    arg_parser.add_argument("-c", "--remote_login_password", type=str,
                            required=True, help="remote login password")
    arg_parser.add_argument("-f", "--remote_ssl_thumbprint", type=str,
                            required=True,
                            help="remote ssl SHA256 thumbprint")
    args = arg_parser.parse_args()
    stub_config = auth.get_basic_auth_stub_config(args.user, args.password,
                                                  args.nsx_host,
                                                  args.tcp_port)

    # Create a pretty printer to make the output look nice.
    pp = PrettyPrinter()

    # Create the services we'll need.
    infra_svc = Infra(stub_config)
    dz_svc = DeploymentZones(stub_config)
    ep_svc = EnforcementPoints(stub_config)

    DEFAULT_DZ_ID = "default"
    # Read the default deployment zone
    default_dz = dz_svc.get(DEFAULT_DZ_ID)

    # Print the current enforcement points
    print "Initial enforcement points: "
    pp.pprint(default_dz.enforcement_points)

    # Register an enforcement point
    conn_info = NSXTConnectionInfo(
        enforcement_point_address=args.remote_enforcement_point,
        thumbprint=args.remote_ssl_thumbprint,
        username=args.remote_login_user,
        password=args.remote_login_password,
    )
    ep = EnforcementPoint(
        description="Example Enforcement Point",
        connection_info=conn_info,
    )

    try:
        ep_svc.patch(DEFAULT_DZ_ID, "example", ep)
    except Error as ex:
        import pdb; pdb.set_trace()
        api_error = ex.data.convert_to(ApiError)
        print "An error occurred: %s" % api_error.error_message

    eps = ep_svc.list(DEFAULT_DZ_ID)
    pp.pprint(eps)

    print("You can now examine the enforcement points in the")
    print("NSX policy service if you wish. Press enter to continue.")
    sys.stdin.readline()

    # Delete the enforcement point
    ep_svc.delete(DEFAULT_DZ_ID, "example")
    print("After deleting enforcement point")

if __name__ == "__main__":
    main()
