/*
 * NSX-T SDK Sample Code
 *
 * Copyright 2017 VMware, Inc.  All rights reserved
 *
 * The BSD-2 license (the "License") set forth below applies to all
 * parts of the NSX-T SDK Sample Code project.  You may not use this
 * file except in compliance with the License.
 *
 * BSD-2 License
 *
 * Redistribution and use in source and binary forms, with or
 * without modification, are permitted provided that the following
 * conditions are met:
 *
 *     Redistributions of source code must retain the above
 *     copyright notice, this list of conditions and the
 *     following disclaimer.
 *
 *     Redistributions in binary form must reproduce the above
 *     copyright notice, this list of conditions and the
 *     following disclaimer in the documentation and/or other
 *     materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
 * CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
 * INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
 * MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 * LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
 * USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
 * AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
 * LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
 * ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 */

package com.vmware.nsx.examples.basics;

import java.util.Scanner;

import org.apache.commons.cli.CommandLine;

import com.vmware.nsx.TransportZones;
import com.vmware.nsx.examples.util.ApiClientUtils;
import com.vmware.nsx.examples.util.CliUtils;
import com.vmware.nsx.model.TransportZone;
import com.vmware.nsx.model.TransportZoneListResult;
import com.vmware.vapi.client.ApiClient;

/*-
 * This example shows basic CRUD (create, read, update, and delete) operations.
 * Using one of the simplest NSX resource types, a Transport Zone, we will show
 * how create, read, update, and delete operations are performed.
 *
 * APIs used:
 *
 * List transport zones:
 * GET /api/v1/transport-zones
 *
 * Create a transport zone:
 * POST /api/v1/transport-zones
 *
 * Read a transport zone:
 * POST /api/v1/transport-zones/<zone-id>
 *
 * Update a transport zone:
 * PUT /api/v1/transport-zones/<zone-id>
 *
 * Delete a transport zone:
 * DELETE /api/v1/transport-zones/<zone-id>
 */
public class Crud {

    public static void main(String[] args) {
        CommandLine cmd = CliUtils.parseArgs(args);
        String uri = "https://" + cmd.getOptionValue("nsx_host") + ":"
                + cmd.getOptionValue("tcp_port", "443");
        ApiClient apiClient = ApiClientUtils.createApiClient(uri,
                cmd.getOptionValue("user"),
                cmd.getOptionValue("password").toCharArray());

        // Create the Transportzones service we'll need.
        TransportZones zoneService = apiClient.createStub(TransportZones.class);

        // First, list all transport zones. If your NSX installation has
        // just been installed, this should return an empty list.
        TransportZoneListResult zones = zoneService.list(null, null, null, null, null, null, null, null, null, null);
        System.out.println("Initial list of transport zones - " + zones.getResultCount() + " zones");
        System.out.println(zones);

        // Create a transport tone.
        TransportZone transportZone = new TransportZone.Builder()
                .setDisplayName("My Transport Zone")
                .setDescription(
                        "Transport zone for basic create/read/update/delete demo")
                .build();
        TransportZone resultTZ = zoneService.create(transportZone);
        System.out
                .println("Transport zone created. id is %s" + resultTZ.getId());

        // Save the id, which uniquely identifies the resource we created.
        String tzId = resultTZ.getId();

        // Read that transport zone.
        TransportZone readTZ = zoneService.get(tzId);
        System.out.println("Re-read the transport zone");
        System.out.println(readTZ);

        // List all transport zones again. The newly created transport
        // zone will be in the list.
        zones = zoneService.list(null, null, null, null, null, null, null, null, null, null);
        System.out.println("Updated list of transport zones - " + zones.getResultCount() + " zones");
        System.out.println(zones);

        System.out.println("You can now examine the list of transport zones in the");
        System.out.println("NSX manager if you wish. Press enter to continue.");
        Scanner scanner = new Scanner(System.in);
        scanner.nextLine();
        scanner.close();

        // Update the transport zone.
        readTZ.setDisplayName("Updated description for transport zone");
        TransportZone updatedTZ = zoneService.update(tzId, readTZ);
        System.out.println(
                "After updating description. Note that the revision property is automatically updated.");
        System.out.println(updatedTZ);

        // Update the transport zone again.
        //
        // Note that NSX insists that clients always operate on up-to-date
        // data. To enforce this, every resource in NSX has a "revision"
        // property that is automatically maintained by NSX and is
        // incremented each time the resource is updated. If a client
        // submits an update operation, and the revision property in the
        // payload provided by the client does not match the revision
        // stored on the server, another update must have happened since
        // the client last read the resource, and the client's copy is
        // therefore stale.  In this case, the server will return a 412
        // Precondition Failed error. This is intended to prevent clients
        // from clobbering each other's updates. To recover from this
        // error, the client must re-read the resource, apply any desired
        // updates, and perform another update operation.
        updatedTZ.setDescription("Updated description again for transport zone");
        updatedTZ = zoneService.update(tzId, updatedTZ);
        System.out.println("After updating description again.");
        System.out.println(updatedTZ);

        // Delete the transport zone.
        zoneService.delete(tzId);
    }

}
