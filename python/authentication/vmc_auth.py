#!/usr/bin/env python

"""
NSX-T SDK Sample Code

Copyright 2018 VMware, Inc.  All rights reserved

The BSD-2 license (the "License") set forth below applies to all
parts of the NSX-T SDK Sample Code project.  You may not use this
file except in compliance with the License.

BSD-2 License

Redistribution and use in source and binary forms, with or
without modification, are permitted provided that the following
conditions are met:

    Redistributions of source code must retain the above
    copyright notice, this list of conditions and the
    following disclaimer.

    Redistributions in binary form must reproduce the above
    copyright notice, this list of conditions and the
    following disclaimer in the documentation and/or other
    materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
"""

"""
This example shows how to obtain an authentication token to use
when making API calls against an NSX Manager in VMware Cloud
on AWS.

To run this example, you will need to open the VMware Cloud
Services Console, choose "View My Profile", and open the
"API Tokens" tab. If you do not have a Refresh Token, generate
one. Pass that as the -r (aka --refresh_token) argument to
this example.

Compatible with: NSX-T 2.1, 2.2

APIs used:

List domains:
GET /policy/api/v1/infra/domains
"""

import requests
import sys

from com.vmware.nsx_policy.infra_client import Domains
from util import getargs
from vmware.vapi.bindings.struct import PrettyPrinter
from vmware.vapi.lib import connect
from vmware.vapi.security.user_password import \
    create_user_password_security_context
from vmware.vapi.stdlib.client.factories import StubConfigurationFactory

VMC_AUTH_URL = (
    "https://console.cloud.vmware.com/csp/gateway/am/api/auth/api-tokens/authorize")


def main():
    # Read the command-line arguments. The args object will contain
    # 3 properties, args.nsx_host, args.tcp_port, and args.refresh_token.
    args = getargs.getargs()
    if args.refresh_token is None:
        sys.stderr.write(
            "Error: you must provide a refresh token for this example\n")
        sys.exit(1)

    # Obtain a token to use for authenticating to the NSX Manager. We
    # just use the python requests library directly.
    params = {"refresh_token", args.refresh_token}
    resp = requests.post("%s?refresh_token=%s" %
                         (VMC_AUTH_URL, args.refresh_token))
    resp.raise_for_status()  # Will raise exception if error
    resp_json = resp.json()
    # This is the access token you will pass with all NSX Manager API requests
    access_token = resp_json["access_token"]

    # Create a session using the requests library. For more information on
    # requests, see http://docs.python-requests.org/en/master/
    session = requests.session()
    # Arrange for the requests library to send the bearer token header
    # with each request.
    session.headers["Authorization"] = "Bearer %s" % access_token

    # If your NSX API server is using its default self-signed certificate,
    # you will need the following line, otherwise the python ssl layer
    # will reject the server certificate. THIS IS UNSAFE and you should
    # normally verify the server certificate.
    session.verify = False

    # Set up the API connector
    nsx_url = 'https://%s:%s' % (args.nsx_host, args.tcp_port)
    resp = session.get("%s/api/v1/cluster" % nsx_url)
    connector = connect.get_requests_connector(
        session=session, msg_protocol='rest', url=nsx_url)
    stub_config = StubConfigurationFactory.new_std_configuration(connector)

    # Let's get a list of all Domains
    domains_svc = Domains(stub_config)
    domains = domains_svc.list()
    # Create a pretty printer to make the output look nice.
    pp = PrettyPrinter()
    pp.pprint(domains)


if __name__ == "__main__":
    main()
