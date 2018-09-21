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
package com.vmware.nsx.examples.authentication;

import com.vmware.nsx_vmc.client.VmcNsxClients;
import com.vmware.vapi.client.ApiClient;

/**
 * Helper class which provides methods for creating a new <code>ApiClient</code>
 * for VMC APIs
 */
public class VmcNsxAuthenticationHelper {
    public static final String CSP_AUTHORIZATION_URL = "/csp/gateway/am/api/auth/api-tokens/authorize";

    /**
     * Instantiates an ApiClient using a refresh token which can be used for
     * creating stubs.
     *
     * @param refreshToken
     *            refresh token of the user
     * @param verifyServerCertificate
     *            if true, verify the server's certificate
     * @param verifyServerHostname
     *            if true, verify the server's hostname
     * @return
     */
    public ApiClient newVmcNsxPolicyClient(String organizationId, String sddcId,
            String refreshToken, boolean verifyServerCertificate,
            boolean verifyServerHostname) {
        return VmcNsxClients.custom()
                .setRefreshToken(refreshToken.toCharArray())
                .setOrganizationId(organizationId).setSddcId(sddcId)
                .setVerifyServerCertificate(verifyServerCertificate)
                .setVerifyServerHostname(verifyServerHostname).build();
    }
}