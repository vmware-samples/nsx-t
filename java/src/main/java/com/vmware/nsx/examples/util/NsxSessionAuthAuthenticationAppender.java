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

import com.vmware.vapi.core.ExecutionContext;
import com.vmware.vapi.data.DataValue;
import com.vmware.vapi.internal.protocol.client.rpc.HttpRequest;
import com.vmware.vapi.protocol.client.http.RequestPreProcessor;
import com.vmware.vapi.security.SessionSecurityContext;

/*
  RestClientApiProvider has methods for managing RequestPreProcessors. Class is
  ProcessorManager, method is setPostProcessors.
 */
public class NsxSessionAuthAuthenticationAppender implements RequestPreProcessor {
    private static final String SESSION_HEADER_NAME = "Cookie";
    private static final String XSRF_TOKEN_HEADER_NAME = "X-Xsrf-Token";
    private String xsrfToken;

    public NsxSessionAuthAuthenticationAppender(String xsrfToken) {
        this.xsrfToken = xsrfToken;
    }

    @Override
    public HttpRequest handle(String serviceId, String operationId,
            HttpRequest request, DataValue params,
            ExecutionContext executionContext) {
        char[] sessionId = (char [])executionContext.retrieveSecurityContext().getProperty(SessionSecurityContext.SESSION_ID_KEY);
        request.addHeader(SESSION_HEADER_NAME, new String(sessionId));
        request.addHeader(XSRF_TOKEN_HEADER_NAME, xsrfToken);
        return request;
    }
}
