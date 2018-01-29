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
