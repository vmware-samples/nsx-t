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

import java.util.ArrayList;
import java.util.Scanner;

import org.apache.commons.cli.CommandLine;

import com.vmware.nsx.examples.util.ApiClientUtils;
import com.vmware.nsx.examples.util.CliUtils;
import com.vmware.nsx_policy.Infra;
import com.vmware.nsx_policy.infra.Tier1s;
import com.vmware.nsx_policy.infra.tier_1s.Segments;
import com.vmware.nsx_policy.infra.tier_1s.segments.Ports;
import com.vmware.nsx_policy.model.Segment;
import com.vmware.nsx_policy.model.SegmentPort;
import com.vmware.nsx_policy.model.SegmentSubnet;
import com.vmware.nsx_policy.model.Tier1;
import com.vmware.vapi.client.ApiClient;

/*-

 */
public class CrudPolicy {

    public static void main(String[] args) {
        CommandLine cmd = CliUtils.parseArgs(args);
        String uri = "https://" + cmd.getOptionValue("nsx_host") + ":"
                + cmd.getOptionValue("tcp_port", "443");
        ApiClient apiClient = ApiClientUtils.createApiClient(uri,
                cmd.getOptionValue("user"),
                cmd.getOptionValue("password").toCharArray());
        
        Infra infraService = apiClient.createStub(Infra.class);
        Tier1s tier1sService = apiClient.createStub(Tier1s.class);
        Segments segmentsService = apiClient.createStub(Segments.class);
        Ports portsService = apiClient.createStub(Ports.class);
        
        Tier1 tier1 = new Tier1.Builder().setId("t1_test").build();
        tier1sService.update("t1_test", tier1);

        SegmentSubnet subnet = new SegmentSubnet.Builder()
        		.setGatewayAddress("192.168.1.1/24")
        		.setNetwork("192.168.0.0")
        		.build();
        ArrayList<SegmentSubnet> subnets = new ArrayList<SegmentSubnet>();
        subnets.add(subnet);
        Segment newSegment = new Segment.Builder()
        		.setSubnets(subnets)
        		.setTransportZonePath("/infra/sites/default/enforcement-points/default/transport-zones/c1e7f78b-07b3-47c4-85f1-8fdde6acc54d")
        		.build();
        segmentsService.update("t1_test", "062b4bd3-8cca-413b-85bf-0f03c1adbb7b", newSegment);
        
        SegmentPort segmentPort = new SegmentPort.Builder()
        		.build();
        portsService.update("t1_test", "062b4bd3-8cca-413b-85bf-0f03c1adbb7b", "1898fac0-18ea-4dc3-a560-5c9ed4811bb5", segmentPort);
        
        System.out.println("Press enter to delete all resources created for this example.");
        Scanner scanner = new Scanner(System.in);
        scanner.nextLine();
        scanner.close();
        
        // Tear down
        portsService.delete("t1_test", "062b4bd3-8cca-413b-85bf-0f03c1adbb7b", "1898fac0-18ea-4dc3-a560-5c9ed4811bb5");
        segmentsService.delete("t1_test", "062b4bd3-8cca-413b-85bf-0f03c1adbb7b");
        tier1sService.delete("t1_test");
        
    }
}
