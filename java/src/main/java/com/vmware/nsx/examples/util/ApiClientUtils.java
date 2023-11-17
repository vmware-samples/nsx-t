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

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.UnsupportedEncodingException;
import java.security.KeyManagementException;
import java.security.KeyStoreException;
import java.security.NoSuchAlgorithmException;
import javax.net.ssl.SSLContext;

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
import org.apache.http.Header;
import org.apache.http.HttpResponse;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.conn.ssl.NoopHostnameVerifier;
import org.apache.http.conn.ssl.SSLConnectionSocketFactory;
import org.apache.http.conn.ssl.TrustSelfSignedStrategy;
import org.apache.http.entity.StringEntity;
import org.apache.http.impl.client.HttpClients;
import org.apache.http.ssl.SSLContexts;

public class ApiClientUtils {
    public static ApiClient apiClient = null;
    public static final int RESPONSE_TIMEOUT_SECONDS = 60;  // Maximum time to wait for a response

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
                .setSoTimeout(RESPONSE_TIMEOUT_SECONDS * 1000)
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

    public static ApiClient createApiClientWithSessionAuthentication(String mgrUrl, String username,
                                            char[] password) throws NoSuchAlgorithmException, KeyStoreException, KeyManagementException {
        System.setProperty("jsse.enableSNIExtension", "false");

        // Get a session id by calling POST /api/session/create
        // Since the NSX manager default certificate is self-signed,
        // we disable verification. This is dangerous and real code
        // should verify that it is talking to a valid server.
        SSLContext sslcontext = SSLContexts.custom().loadTrustMaterial(null,
                new TrustSelfSignedStrategy()).build();
        SSLConnectionSocketFactory sslsf = new SSLConnectionSocketFactory(sslcontext,
                new String[] {"TLSv1.3", "TLSv1.2"}, null, new NoopHostnameVerifier());
        HttpClient client = HttpClients.custom().setSSLSocketFactory(sslsf).build();

        String sessionUrl = mgrUrl + "/api/session/create";
        String sessionId = null;
        String xsrfToken = null;
        HttpPost sessionIdRequest = new HttpPost(sessionUrl);
        StringEntity input;
        try {
            input = new StringEntity("j_username=" + new String(username) + "&j_password=" + new String(password));
        } catch (UnsupportedEncodingException e) {
            throw new RuntimeException("Unable to get session: encoding error");
        }
        input.setContentType("application/x-www-form-urlencoded");
        sessionIdRequest.setEntity(input);

        // Read session creation response
        HttpResponse response;
        try {
            response = client.execute(sessionIdRequest);
            if (response.getStatusLine().getStatusCode() != 200) {
                throw new RuntimeException("Unable to get session, HTTP error " + response.getStatusLine().getStatusCode());
            }
        } catch (IOException e) {
            throw new RuntimeException("Unable to get session: I/O error");
        }

        Header[] cookies = response.getHeaders("set-cookie");
        if (cookies != null && cookies.length > 0) {
            sessionId = cookies[0].getValue();
        }
        Header[] xsrfTokens = response.getHeaders("x-xsrf-token");
        if (xsrfTokens != null && xsrfTokens.length > 0) {
            xsrfToken = xsrfTokens[0].getValue();
        }

        try {
            ByteArrayOutputStream result = new ByteArrayOutputStream();
            byte[] buffer = new byte[1024];

            while(true) {
                int length;
                if ((length = response.getEntity().getContent().read(buffer)) == -1) {
                    break;
                }

                result.write(buffer, 0, length);
            }
        } catch (IOException | IllegalStateException var19) {
            throw new RuntimeException("Unable to get session: unable to read response");
        }

        // SSL and HTTP configuration for the API client stub
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
                .setSoTimeout(RESPONSE_TIMEOUT_SECONDS * 1000)
                .setSslConfiguration(sslConfig)
                .getConfig();

        StubConfiguration stubConfig = new StubConfiguration();
        SecurityContext securityContext = SecurityContextFactory
                .createSessionSecurityContext(sessionId.toCharArray());
        stubConfig.setSecurityContext(securityContext);

        Configuration.Builder configBuilder = new Configuration.Builder()
                .register(Configuration.HTTP_CONFIG_CFG, httpConfig)
                .register(Configuration.STUB_CONFIG_CFG, stubConfig)
                .register(RestProtocol.REST_REQUEST_AUTHENTICATOR_CFG, new NsxSessionAuthAuthenticationAppender(xsrfToken));
        Configuration config = configBuilder.build();

        // TODO add retry context and implement getting a new session

        apiClient = ApiClients.newRestClient(mgrUrl, config);

        return apiClient;
    }

    public static void tearDownApiClient() throws IOException {
        if (apiClient != null) {
            apiClient.close();
        }
    }
}
