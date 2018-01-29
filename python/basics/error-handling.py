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
