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

import com.vmware.nsx.examples.util.ApiClientUtils;
import com.vmware.nsx.examples.util.CliUtils;
import com.vmware.nsx.fabric.Nodes;
import com.vmware.nsx.fabric.nodes.Status;
import com.vmware.nsx.model.Node;
import com.vmware.nsx.model.NodeListResult;
import com.vmware.nsx.model.NodeStatus;
import com.vmware.vapi.bindings.Structure;
import com.vmware.vapi.client.ApiClient;

/*-
 * This example shows how to obtain a list of all fabric nodes and query their
 * status.
 *
 * APIs used:
 *
 * List fabric nodes
 * GET /api/v1/fabric/nodes
 *
 * Get fabric node status
 * GET /api/v1/fabric/nodes/<node-id>/status
 */

public class FabricNodes {

    public static void main(String[] args) throws InterruptedException {
        CommandLine cmd = CliUtils.parseArgs(args);
        String uri = "https://" + cmd.getOptionValue("nsx_host") + ":"
                + cmd.getOptionValue("tcp_port", "443");
        ApiClient apiClient = ApiClientUtils.createApiClient(uri,
                cmd.getOptionValue("user"),
                cmd.getOptionValue("password").toCharArray());

        // Create the services we'll need.
        Nodes fabricNodesService = apiClient.createStub(Nodes.class);
        Status statusService = apiClient.createStub(Status.class);

        NodeListResult result = fabricNodesService.list(null, null, null, null,
                null, null, null, null, null, null, null);
        for (Structure rawNode : result.getResults()) {
            // Nodes are polymorphic, so we need to convert to a concrete type
            Node fabricNode = rawNode._convertTo(Node.class);
            System.out.println("Type: " + fabricNode.getResourceType()
                    + ", Name: " + fabricNode.getDisplayName() + ", id: "
                    + fabricNode.getId());
            NodeStatus nodeStatus = statusService.get(fabricNode.getId(),
                    "realtime");
            System.out.println("    mp conn: "
                    + nodeStatus.getMpaConnectivityStatus() + ", cp conn: "
                    + nodeStatus.getLcpConnectivityStatus());
        }
    }

}
