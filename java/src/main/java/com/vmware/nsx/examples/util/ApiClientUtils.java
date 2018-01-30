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

package com.vmware.nsx.examples.util;

import java.io.IOException;

import com.vmware.vapi.bindings.StubConfiguration;
import com.vmware.vapi.cis.authn.SecurityContextFactory;
import com.vmware.vapi.client.ApiClient;
import com.vmware.vapi.client.ApiClients;
import com.vmware.vapi.client.Configuration;
import com.vmware.vapi.core.ExecutionContext.SecurityContext;
import com.vmware.vapi.internal.protocol.RestProtocol;
import com.vmware.vapi.internal.protocol.client.rest.authn.BasicAuthenticationAppender;
import com.vmware.vapi.protocol.HttpConfiguration;
import com.vmware.vapi.protocol.HttpConfiguration.SslConfiguration;

public class ApiClientUtils {
    public static ApiClient apiClient = null;

    public static ApiClient createApiClient(String mgrUrl, String username,
            char[] password) {
        System.setProperty("jsse.enableSNIExtension", "false");

        // SSL and HTTP configuration
        SslConfiguration.Builder sslConfigBuilder = new SslConfiguration.Builder();

        // Since the NSX manager default certificate is self-signed,
        // we disable verification. This is dangerous and real code
        // should verify that it is talking to a valid server.
        // Production code should not include the next two calls.
        sslConfigBuilder
                .disableCertificateValidation()
                .disableHostnameVerification();

        SslConfiguration sslConfig = sslConfigBuilder.getConfig();

        HttpConfiguration httpConfig = new HttpConfiguration.Builder()
                .setSslConfiguration(sslConfig).getConfig();

        StubConfiguration stubConfig = new StubConfiguration();
        SecurityContext securityContext = SecurityContextFactory
                .createUserPassSecurityContext(username, password);
        stubConfig.setSecurityContext(securityContext);

        Configuration.Builder configBuilder = new Configuration.Builder()
                .register(Configuration.HTTP_CONFIG_CFG, httpConfig)
                .register(Configuration.STUB_CONFIG_CFG, stubConfig)
                .register(RestProtocol.REST_REQUEST_AUTHENTICATOR_CFG, new BasicAuthenticationAppender());
        Configuration config = configBuilder.build();

        apiClient = ApiClients.newRestClient(mgrUrl, config);

        return apiClient;
    }

    public static void tearDownApiClient() throws IOException {
        if (apiClient != null) {
            apiClient.close();
        }
    }
}
