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

import random
import sys
from util import auth
from util import getargs
from vmware.vapi.bindings.struct import PrettyPrinter
from com.vmware.nsx_policy_client import Infra
from com.vmware.nsx_policy.infra_client import Domains
from com.vmware.nsx_policy.model_client import Domain
from com.vmware.vapi.std.errors_client import NotFound

"""
This example shows how to create a basic domain in the
NSX Policy service.

APIs used:

List infra domains:
GET /policy/api/v1/infra/domains

Create a new infra domain
POST /policy/api/v1/infra/domains

Read an infra domain:
GET /policy/api/v1/infra/domains/<domain-id>

Update an infra domain:
POST /policy/api/v1/infra/domains/<domain-id>

Delete an infra domain:
DELETE /policy/api/v1/infra/domains/<domain-id>
"""


def main():
    args = getargs.getargs()
    stub_config = auth.get_basic_auth_stub_config(args.user, args.password,
                                                  args.nsx_host,
                                                  args.tcp_port)

    # Create a pretty printer to make the output look nice.
    pp = PrettyPrinter()

    # Create the services we'll need.
    infra_svc = Infra(stub_config)
    domains_svc = Domains(stub_config)

    # First, retrieve /infra and the domains in /infra. If your NSX
    # policy service has just been installed, there will be no domains.
    infra = infra_svc.get()
    print("Initial state of /infra")
    pp.pprint(infra)
    domains = domains_svc.list()
    print("All domains: total of %d domains" % domains.result_count)

    # Create a domain with a random id
    domain_id = "Domain_%d" % random.choice(range(10000))
    domain = Domain(
        id=domain_id,
        display_name=domain_id,
        # Note: the revision should not be required, but for
        # now it must be provided on initial object creation.
        revision=0
    )
    domains_svc.update(domain_id, domain)
    print("Domain %s created." % domain_id)

    # Read that domain
    read_domain = domains_svc.get(domain_id)
    print("Re-read the domain")
    pp.pprint(read_domain)

    # List all domains again. The newly created domain
    # will be in the list.
    domains = domains_svc.list()
    print("All domains: total of %d domains" % domains.result_count)

    print("You can now examine the infra and domains in the")
    print("NSX policy service if you wish. Press enter to continue.")
    sys.stdin.readline()

    # Update the domain. The NSX policy API only supports a create API,
    # so to update an existing resource, just call the create method
    # again, passing the properties you wish to update.
    read_domain.description = "Updated description for transport zone"
    domains_svc.update(domain_id, read_domain)

    # Re-read the domain
    read_domain = domains_svc.get(domain_id)
    print("Domain after updating")
    pp.pprint(read_domain)

    # Delete the domain
    domains_svc.delete(domain_id)
    print("After deleting domain")

    # Now if we try to read the domain, we should get a
    # 404 Not Found error. This example also shows how you can
    # check for and handle specific errors from the NSX Policy API.
    try:
        read_domain = domains_svc.get(domain_id)
    except NotFound:
        print("Domain is gone, as expected")


if __name__ == "__main__":
    main()
