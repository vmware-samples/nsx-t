/*
 * NSX-T SDK Sample Code
 *
 * Copyright 2023 VMware, Inc.  All rights reserved
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

import java.security.KeyManagementException;
import java.security.KeyStoreException;
import java.security.NoSuchAlgorithmException;
import java.util.Scanner;

import com.vmware.nsx.TransportZones;
import com.vmware.nsx.examples.util.ApiClientUtils;
import com.vmware.nsx.examples.util.CliUtils;
import com.vmware.nsx.model.TransportZone;
import com.vmware.nsx.model.TransportZoneListResult;
import com.vmware.nsx_policy.Infra;
import com.vmware.vapi.client.ApiClient;
import org.apache.commons.cli.CommandLine;

/*-
 * This example shows how to use API session authentication.
 *
 * APIs used:
 *
 * Get infra object:
 * GET /policy/api/v1/infra
 */
public class SessionAuth {

    public static void main(String[] args) throws NoSuchAlgorithmException, KeyStoreException, KeyManagementException {
        CommandLine cmd = CliUtils.parseArgs(args);
        String uri = "https://" + cmd.getOptionValue("nsx_host") + ":"
                + cmd.getOptionValue("tcp_port", "443");
        ApiClient apiClient = ApiClientUtils.createApiClientWithSessionAuthentication(
                uri,
                cmd.getOptionValue("user"),
                cmd.getOptionValue("password").toCharArray());

        // Get the infra object
        Infra infraService = apiClient.createStub(Infra.class);
        try {
            com.vmware.nsx_policy.model.Infra infra = infraService.get(null, null, null);
            System.out.println(infra);
        } catch (Exception e) {
            System.out.println("Encountered exception " + e.getMessage());
        }
    }
}
