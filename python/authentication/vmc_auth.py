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

Compatible with: NSX-T 2.1, 2.2, 2.3, 2.4 (however, requires
the NSX-T 2.4 python SDK)

APIs used:

List domains:
GET /policy/api/v1/infra/domains
"""

import argparse
import requests
import sys

from com.vmware.nsx_policy.infra_client import Domains
from com.vmware.nsx_policy_client_for_vmc import create_nsx_policy_client_for_vmc
from vmware.vapi.bindings.struct import PrettyPrinter
from vmware.vapi.lib import connect
from vmware.vapi.security.user_password import \
    create_user_password_security_context
from vmware.vapi.stdlib.client.factories import StubConfigurationFactory


def main():
    # Read the command-line arguments.
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-o', '--org_id', type=str, required=True,
                            help='VMC Organization ID')
    arg_parser.add_argument('-s', '--sddc_id', type=str, required=True,
                            help='VMC Software Defined Datacenter ID')
    arg_parser.add_argument('-r', '--refresh_token', type=str, required=True,
                            help='Refresh token')
    args = arg_parser.parse_args()

    vmc_client = create_nsx_policy_client_for_vmc(
        args.refresh_token, args.org_id, args.sddc_id)

    # Let's get a list of all Domains
    domains = vmc_client.infra.Domains.list()
    # Create a pretty printer to make the output look nice.
    pp = PrettyPrinter()
    pp.pprint(domains)


if __name__ == "__main__":
    main()
