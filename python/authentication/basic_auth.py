#!/usr/bin/env python

"""
NSX-T SDK Sample Code

Copyright 2017 VMware, Inc.  All rights reserved

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

import pprint
import requests

from com.vmware.nsx_client import TransportZones
from util import getargs
from vmware.vapi.bindings.struct import PrettyPrinter
from vmware.vapi.lib import connect
from vmware.vapi.security.user_password import \
    create_user_password_security_context
from vmware.vapi.stdlib.client.factories import StubConfigurationFactory


def main():
    # Read the command-line arguments. The args object will contain
    # 4 properties, args.nsx_host, args.tcp_port, args.user, and
    # args.password.
    args = getargs.getargs()

    # Create a session using the requests library. For more information on
    # requests, see http://docs.python-requests.org/en/master/
    session = requests.session()

    # If your NSX API server is using its default self-signed certificate,
    # you will need the following line, otherwise the python ssl layer
    # will reject the server certificate. THIS IS UNSAFE and you should
    # normally verify the server certificate.
    session.verify = False

    # Set up the API connector and security context
    nsx_url = 'https://%s:%s' % (args.nsx_host, args.tcp_port)
    connector = connect.get_requests_connector(
        session=session, msg_protocol='rest', url=nsx_url)
    stub_config = StubConfigurationFactory.new_std_configuration(connector)
    security_context = create_user_password_security_context(
        args.user, args.password)
    connector.set_security_context(security_context)

    # Now any API calls we make should authenticate to NSX using
    # HTTP Basic Authentication. Let's get a list of all Transport Zones.
    transportzones_svc = TransportZones(stub_config)
    tzs = transportzones_svc.list()
    # Create a pretty printer to make the output look nice.
    pp = PrettyPrinter()
    pp.pprint(tzs)


if __name__ == "__main__":
    main()
