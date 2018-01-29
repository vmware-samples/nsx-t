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
from com.vmware.nsx.model_client import TransportZone
from com.vmware.vapi.std.errors_client import NotFound

"""
This example shows basic CRUD (create, read, update, delete) operations.
Using one of the simplest NSX resource types, a Transport Zone, we will
show how create, read, update, and delete operations are performed.

APIs used:

List transport zones:
GET /api/v1/transport-zones

Create a transport zone:
POST /api/v1/transport-zones

Read a transport zone:
POST /api/v1/transport-zones/<zone-id>

Update a transport zone:
PUT /api/v1/transport-zones/<zone-id>

Delete a transport zone:
DELETE /api/v1/transport-zones/<zone-id>
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

    # First, list all transport zones. If your NSX installation has
    # just been installed, this should return an empty list.
    tzs = transportzones_svc.list()
    print("Initial list of transport zones - %d zones" % tzs.result_count)
    pp.pprint(tzs)

    # Create a transport zone.
    new_tz = TransportZone(
        transport_type=TransportZone.TRANSPORT_TYPE_OVERLAY,
        display_name="My transport zone",
        description="Transport zone for basic create/read/update/delete demo",
        host_switch_name="hostswitch1"
    )
    result_tz = transportzones_svc.create(new_tz)
    print("Transport zone created. id is %s" % result_tz.id)

    # Save the id, which uniquely identifies the resource we created.
    tz_id = result_tz.id

    # Read that transport zone.
    read_tz = transportzones_svc.get(tz_id)
    print("Re-read the transport zone")
    pp.pprint(read_tz)

    # List all transport zones again. The newly created transport
    # zone will be in the list.
    tzs = transportzones_svc.list()
    print("Updated list of transport zones - %d zones" % tzs.result_count)
    pp.pprint(tzs)

    print("You can now examine the list of transport zones in the")
    print("NSX manager if you wish. Press enter to continue.")
    sys.stdin.readline()

    # Update the transport zone.
    read_tz.description = "Updated description for transport zone"
    updated_tz = transportzones_svc.update(tz_id, read_tz)
    print("After updating description. Note that the revision property is "
          "automatically updated.")
    pp.pprint(updated_tz)

    # Update the transport zone again.
    #
    # Note that NSX insists that clients always operate on up-to-date
    # data. To enforce this, every resource in NSX has a "revision"
    # property that is automatically maintained by NSX and is
    # incremented each time the resource is updated. If a client
    # submits an update operation, and the revision property in the
    # payload provided by the client does not match the revision
    # stored on the server, another update must have happened since
    # the client last read the resource, and the client's copy is
    # therefore stale.  In this case, the server will return a 412
    # Precondition Failed error. This is intended to prevent clients
    # from clobbering each other's updates. To recover from this
    # error, the client must re-read the resource, apply any desired
    # updates, and perform another update operation.
    updated_tz.description = "Updated description again for transport zone"
    updated_tz = transportzones_svc.update(tz_id, updated_tz)
    print("After updating description again.")
    pp.pprint(updated_tz)

    # Delete the transport zone.
    transportzones_svc.delete(tz_id)
    print("After deleting transport zone")

    # Now if we try to read the transport zone, we should get a
    # 404 Not Found error. This example also shows how you can
    # check for and handle specific errors from the NSX API.
    try:
        read_tz = transportzones_svc.get(tz_id)
    except NotFound:
        print("Transport zone is gone, as expected")


if __name__ == "__main__":
    main()
