#!/usr/bin/env python

"""
NSX-T SDK Sample Code

Copyright 2018-2019 VMware, Inc.  All rights reserved

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

import argparse
import pprint
import requests

from com.vmware import nsx_client
from vmware.vapi.bindings.struct import PrettyPrinter
from vmware.vapi.bindings.stub import ApiClient
from vmware.vapi.lib import connect
from vmware.vapi.stdlib.client.factories import StubConfigurationFactory


def main():
    # Read the command-line arguments.
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-n', '--nsx_host', type=str, required=True,
                            help='NSX host to connect to')
    arg_parser.add_argument('-t', '--tcp_port', type=int, default=443,
                            help='TCP port for NSX server')
    arg_parser.add_argument('-c', '--client_certificate', type=str,
                            required=True,
                            help='Name of PEM file containing client '
                            'certificate and private key')
    args = arg_parser.parse_args()

    # Create a session using the requests library. For more information on
    # requests, see http://docs.python-requests.org/en/master/
    session = requests.session()

    # If your NSX API server is using its default self-signed certificate,
    # you will need the following line, otherwise the python ssl layer
    # will reject the server certificate. THIS IS UNSAFE and you should
    # normally verify the server certificate.
    session.verify = False

    # Configure the requests library to supply a client certificate
    session.cert = args.client_certificate

    # Set up the API connector and client
    nsx_url = 'https://%s:%s' % (args.nsx_host, args.tcp_port)
    connector = connect.get_requests_connector(
        session=session, msg_protocol='rest', url=nsx_url)
    stub_config = StubConfigurationFactory.new_std_configuration(connector)
    stub_factory = nsx_client.StubFactory(stub_config)
    api_client = ApiClient(stub_factory)

    # Now any API calls we make should authenticate to NSX using
    # the client certificate. Let's get a list of all Transport Zones.
    tzs = api_client.TransportZones.list()
    # Create a pretty printer to make the output look nice.
    pp = PrettyPrinter()
    pp.pprint(tzs)


if __name__ == "__main__":
    main()
