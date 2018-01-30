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

import org.apache.commons.cli.CommandLine;

import com.vmware.nsx.TransportZones;
import com.vmware.nsx.examples.util.ApiClientUtils;
import com.vmware.nsx.examples.util.CliUtils;
import com.vmware.nsx.model.ApiError;
import com.vmware.nsx.model.TransportZone;
import com.vmware.vapi.client.ApiClient;
import com.vmware.vapi.std.errors.Error;

/*-
 * This example shows how to catch and process errors from NSX
 * API calls.
 *
 * APIs used:
 *
 * Create a transport zone:
 * POST /api/v1/transport-zones
 */
public class ErrorHandling {

    public static void main(String[] args) {
        CommandLine cmd = CliUtils.parseArgs(args);
        String uri = "https://" + cmd.getOptionValue("nsx_host") + ":"
                + cmd.getOptionValue("tcp_port", "443");
        ApiClient apiClient = ApiClientUtils.createApiClient(uri,
                cmd.getOptionValue("user"),
                cmd.getOptionValue("password").toCharArray());

        // Create the Transportzones service we'll need.
        TransportZones zoneService = apiClient.createStub(TransportZones.class);

        // Create a transport zone, but intentionally pass an incorrect
        // overlay type, so we cause an error.
        TransportZone transportZone = new TransportZone.Builder(
                "zappa")  // Invalid overlay type
                        .setDisplayName("My Transport Zone")
                        .setDescription(
                                "Transport zone for error handling demo")
                        .setHostSwitchName("hostswitch1").build();
        try {
            zoneService.create(transportZone);
        } catch (Error ex) {
            ApiError ae = ex.getData()._convertTo(ApiError.class);
            System.out.println("An error occurred: " + ae.getErrorMessage());
        }
    }
}
