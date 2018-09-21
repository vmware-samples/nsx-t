/*
 * NSX-T SDK Sample Code
 *
 * Copyright 2018 VMware, Inc. All rights reserved
 *
 * The BSD-2 license (the "License") set forth below applies to all parts of the
 * NSX-T SDK Sample Code project. You may not use this file except in compliance
 * with the License.
 *
 * BSD-2 License
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * Redistributions of source code must retain the above copyright notice, this
 * list of conditions and the following disclaimer.
 *
 * Redistributions in binary form must reproduce the above copyright notice,
 * this list of conditions and the following disclaimer in the documentation
 * and/or other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 */

package com.vmware.nsx.examples.basics;

import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.DefaultParser;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.Option;
import org.apache.commons.cli.Options;
import org.apache.commons.cli.ParseException;

import com.vmware.nsx.examples.authentication.VmcNsxAuthenticationHelper;
import com.vmware.nsx_policy.Infra;
import com.vmware.nsx_vmc_app.infra.LinkedVpcs;
import com.vmware.nsx_vmc_app.model.LinkedVpcsListResult;
import com.vmware.vapi.client.ApiClient;

/*-
 * This example shows how to authenticate to the VMC (VMware Cloud on AWS)
 * service, using a VMC refresh token to obtain an authentication token that
 * can then be used to authenticate to the NSX-T instance in a Software
 * Defined Data Center (SDDC).
 */
public class Vmc {

    public static String VMC_SERVER = "vmc.vmware.com";
    public static String CSP_SERVER = "console.cloud.vmware.com";

    public static void main(String[] args) {
        Options options = new Options();
        Option option;
        option = new Option("o", "organization_id", true,
                "ID of the VMC organization");
        option.setRequired(true);
        options.addOption(option);
        option = new Option("s", "sddc_id", true,
                "ID of the Software Defined Data Center (SDDC)");
        option.setRequired(true);
        options.addOption(option);
        option = new Option("r", "refresh_token", true, "Refresh token");
        option.setRequired(true);
        options.addOption(option);
        option = new Option("h", "help", false, "Get help");
        options.addOption(option);
        CommandLineParser parser = new DefaultParser();
        HelpFormatter formatter = new HelpFormatter();
        CommandLine cmd = null;

        try {
            cmd = parser.parse(options, args);
        } catch (ParseException e) {
            System.out.println(e.getMessage());
            formatter.printHelp("VMC Authentication Demo", options);
            System.exit(1);
        }

        // Create the API client. This client will automatically obtain
        // and use an authentication token from the VMC CSP service,
        // and will automatically refresh it when it expires.
        ApiClient apiClient = new VmcNsxAuthenticationHelper()
                .newVmcNsxPolicyClient(cmd.getOptionValue("organization_id"),
                        cmd.getOptionValue("sddc_id"),
                        cmd.getOptionValue("refresh_token"), false, false);

        // The API client can be used to call the NSX-T policy API...
        Infra infraService = apiClient.createStub(Infra.class);
        com.vmware.nsx_policy.model.Infra infra = infraService.get(null);
        System.out.println(infra);

        // ...as well as the NSX-T VMC app APIs.
        LinkedVpcs lvpcSvc = apiClient.createStub(LinkedVpcs.class);
        LinkedVpcsListResult results = lvpcSvc.list();
        System.out.println(results);
    }
}
