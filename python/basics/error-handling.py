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
from util import auth
from util import getargs
from vmware.vapi.bindings.struct import PrettyPrinter
from com.vmware.nsx_client import TransportZones
from com.vmware.nsx.model_client import ApiError
from com.vmware.nsx.model_client import TransportZone
from com.vmware.vapi.std.errors_client import Error

"""
This example shows how to catch and process errors from NSX
API calls

Compatible with: NSX-T 2.1

APIs used:

Create a transport zone:
POST /api/v1/transport-zones
"""


def main():
    args = getargs.getargs()
    stub_config = auth.get_session_auth_stub_config(args.user, args.password,
                                                    args.nsx_host,
                                                    args.tcp_port)

    # Create a pretty printer to make the output look nice.
    pp = PrettyPrinter()

    # Create the service we'll need.
    transportzones_svc = TransportZones(stub_config)

    # Create a transport zone, but intentionally pass an incorrect
    # overlay type, so we cause an error.
    new_tz = TransportZone(
        transport_type="zappa",  # invalid overlay type
        display_name="My transport zone",
        description="Transport zone for error handling demo",
        host_switch_name="hostswitch1"
    )
    try:
        result_tz = transportzones_svc.create(new_tz)
    except Error as ex:
        api_error = ex.data.convert_to(ApiError)
        print "An error occurred: %s" % api_error.error_message


if __name__ == "__main__":
    main()
