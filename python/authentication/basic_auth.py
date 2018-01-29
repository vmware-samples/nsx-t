#!/usr/bin/env python
"""
* *******************************************************
* Copyright (c) VMware, Inc. 2017. All Rights Reserved.
* SPDX-License-Identifier: BSD-2
* *******************************************************
*
* DISCLAIMER. THIS PROGRAM IS PROVIDED TO YOU "AS IS" WITHOUT
* WARRANTIES OR CONDITIONS OF ANY KIND, WHETHER ORAL OR WRITTEN,
* EXPRESS OR IMPLIED. THE AUTHOR SPECIFICALLY DISCLAIMS ANY IMPLIED
* WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY,
* NON-INFRINGEMENT AND FITNESS FOR A PARTICULAR PURPOSE.
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
