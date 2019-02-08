/*
 * NSX-T SDK Sample Code
 *
 * Copyright 2019 VMware, Inc. All rights reserved
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

import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.security.KeyStore;
import java.security.KeyStoreException;
import java.security.NoSuchAlgorithmException;
import java.security.cert.CertificateException;

import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.DefaultParser;
import org.apache.commons.cli.HelpFormatter;
import org.apache.commons.cli.Option;
import org.apache.commons.cli.Options;
import org.apache.commons.cli.ParseException;

import com.vmware.nsx.TransportZones;
import com.vmware.nsx.model.TransportZoneListResult;
import com.vmware.vapi.bindings.StubConfiguration;
import com.vmware.vapi.client.ApiClient;
import com.vmware.vapi.client.ApiClients;
import com.vmware.vapi.client.Configuration;
import com.vmware.vapi.internal.protocol.RestProtocol;
import com.vmware.vapi.internal.protocol.client.rest.authn.BasicAuthenticationAppender;
import com.vmware.vapi.protocol.HttpConfiguration;
import com.vmware.vapi.protocol.HttpConfiguration.KeyStoreConfig;
import com.vmware.vapi.protocol.HttpConfiguration.SslConfiguration;

/*
 * This example shows how to use TLS client certificates to authenticate
 * to the NSX-T manager. This is useful when you want to have some
 * service authenticate to NSX-T, but you don't want to store the
 * admin password on the service, where it could be subject to theft.
 *
 * To utilize the capability, you need to do the following:
 *
 * 1) Create or obtain a certificate to use for the client. A
 *    self-signed certificate is fine for this purpose.
 * 2) Import the certificate into NSX-T.
 * 3) Create a principal identity in NSX-T. A principal identity
 *    associates the certificate with a short name which is
 *    logged in access logs, and an NSX-T role. When a client
 *    presents the associated certificate in the TLS handshake,
 *    NSX-T allows that client to call any APIs allowed by the
 *    associated role, and logs the short name in its access logs.
 *
 * Example:
 *
 * 1) Create a certificate using the java keytool command:
 *    keytool -genkey -keyalg RSA -alias client -keystore keystore.jks \
 *      -storepass password -validity 360 -keysize 2048 \
 *      -dname "CN=My Client, OU=My Org, O=Acme, L=Palo Alto, ST=CA, C=US"
 *    will create a Java keystore named keystore.jks, protected with the
 *    password "password", and will place a self-signed certificate
 *    with alias "client" and an associated private key in that keystore.
 *
 * 2) Extract a PEM-formatted certificate:
 *    keytool -export -alias client -keystore self-signed.jks -rfc \
 *      -file client.pem
 *    will extract the public certificate in PEM format in the file
 *    named "client.pem".
 *    Upload this certificate to NSX-T with the
 *    POST /api/v1/trust-management/certificates API:
 *    curl -u admin:<admin_password> -H "Content-Type: application/json" \
 *      -X POST -d payload \
 *      "https://<mgr-ip>/api/v1/trust-management/certificate?action=import"
 *    where the file "payload" contains:
 *    {"pem_encoded": <contents of client.pem>}
 *
 * 3) The import step above will return a JSON payload containing the
 *    id of the imported certificate, like the following:
 *    {
 *      "id" : "9594f73e-1a97-443c-9797-17b41293ba5d",
 *      "pem_encoded": <contents you uploaded>
 *    }
 *    Now, create the principal identity. Call the following API:
 *    POST /api/v1/trust-management/principal-identities
 *    with a payload like the following:
 *    {
 *      "name": "my_client",
 *      "display_name": "Automation client identity for my cool app",
 *      "certificate_id": "9594f73e-1a97-443c-9797-17b41293ba5d",
 *      "role": "enterprise_admin"
 *    }
 *    You can use other NSX-T roles  than enterprise_admin, as long
 *    as the role has sufficient access permissions to perform the API
 *    calls your client needs to make.
 *    }
 *
 *  Now, if a client presents the certificate in the keystore generated
 *  in step 1, it will get enterprise_admin permissions, and access log
 *  entries will show the username as "my_client". The Java code below
 *  shows you how to create an API client that presents the certificate
 *  when the TLS connection is established.
 *
 *  If you followed the example above, the correct command-line
 *  arguments to run the example will be:
 *
 *  -n <your-nxt-manager-ip-or-hostname>
 *  -k  "/full/path/to/keystore.jks"
 *  -a "client"
 *  -p password
 */

public class TlsClientAuthentication {

    public static ApiClient apiClient = null;

    public static ApiClient createApiClient(String mgrUrl, String keystorePath,
            String keystoreAlias, String keystorePassword) {

        // SSL and HTTP configuration
        SslConfiguration.Builder sslConfigBuilder = new SslConfiguration.Builder();

        // Since the NSX manager default certificate is self-signed,
        // we disable verification. This is dangerous and real code
        // should verify that it is talking to a valid server.
        // Production code should not include the next two calls.
        sslConfigBuilder.disableCertificateValidation()
                .disableHostnameVerification();

        KeyStore keyStore;
        try {
            keyStore = KeyStore.getInstance("JKS");
            keyStore.load(new FileInputStream(keystorePath),
                    keystorePassword.toCharArray());
            KeyStoreConfig keyStoreConfig = new KeyStoreConfig(keystoreAlias,
                    keystorePassword);

            SslConfiguration sslConfig = sslConfigBuilder.setKeyStore(keyStore)
                    .setKeyStoreConfig(keyStoreConfig).getConfig();

            HttpConfiguration httpConfig = new HttpConfiguration.Builder()
                    .setSslConfiguration(sslConfig).getConfig();

            StubConfiguration stubConfig = new StubConfiguration();

            Configuration.Builder configBuilder = new Configuration.Builder()
                    .register(Configuration.HTTP_CONFIG_CFG, httpConfig)
                    .register(Configuration.STUB_CONFIG_CFG, stubConfig)
                    .register(RestProtocol.REST_REQUEST_AUTHENTICATOR_CFG,
                            new BasicAuthenticationAppender());
            Configuration config = configBuilder.build();

            apiClient = ApiClients.newRestClient(mgrUrl, config);

            return apiClient;
        } catch (KeyStoreException e) {
            e.printStackTrace();
        } catch (NoSuchAlgorithmException e) {
            e.printStackTrace();
        } catch (CertificateException e) {
            e.printStackTrace();
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }
        return null;
    }

    public static void main(String[] args) {
        Options options = new Options();
        Option option = new Option("n", "nsx_host", true,
                "NSX host to connect to");
        option.setRequired(true);
        options.addOption(option);
        option = new Option("t", "tcp_port", false,
                "TCP port for NSX server (optional, defaults to 443)");
        options.addOption(option);
        option = new Option("k", "keystore_file", true,
                "Name of the keystore file containing the certificate to use");
        option.setRequired(true);
        options.addOption(option);
        option = new Option("a", "keystore_alias", true,
                "Alias in the keystore file of the certificate to use");
        option.setRequired(true);
        options.addOption(option);
        option = new Option("p", "keystore_password", true,
                "Password for the keystore file");
        option.setRequired(true);
        options.addOption(option);
        option = new Option("h", "help", false, "Get help");
        options.addOption(option);
        CommandLineParser parser = new DefaultParser();
        HelpFormatter formatter = new HelpFormatter();

        CommandLine cmd;
        try {
            cmd = parser.parse(options, args);
            String mgrUrl = "https://" + cmd.getOptionValue("nsx_host") + ":"
                    + cmd.getOptionValue("tcp_port", "443");
            ApiClient client = createApiClient(mgrUrl,
                    cmd.getOptionValue("keystore_file"),
                    cmd.getOptionValue("keystore_alias"),
                    cmd.getOptionValue("keystore_password"));
            if (apiClient == null) {
                System.err.println("Unable to create API client");
            }

            TransportZones zoneService = apiClient
                    .createStub(TransportZones.class);
            TransportZoneListResult zones = zoneService.list(null, null, null,
                    null, null, null, null, null);
            System.out.println("Initial list of transport zones - "
                    + zones.getResultCount() + " zones");
            System.out.println(zones);
        } catch (ParseException e) {
            formatter.printHelp("Demo", options);
            System.exit(1);
        }
    }
}
