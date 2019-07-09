#!/usr/bin/env python

"""
NSX-T SDK Sample Code

Copyright 2019 VMware, Inc.  All rights reserved

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

import sys

from com.vmware.nsx import pools_client
from com.vmware.nsx.model_client import AllocationIpAddress
from com.vmware.nsx.model_client import ApiError
from com.vmware.nsx.model_client import IpPool
from com.vmware.nsx.model_client import IpPoolRange
from com.vmware.nsx.model_client import IpPoolSubnet
from com.vmware.nsx.pools_client import IpPools
from com.vmware.vapi.std.errors_client import Error
from com.vmware.vapi.std.errors_client import NotFound
from util import auth
from util import getargs
from vmware.vapi.bindings.struct import PrettyPrinter

"""
This example shows how to create an IP Pool and allocate/deallocate
an address from that pool.

APIs used:

POST /api/v1/pools/ip-pools

POST /api/v1/pools/ip-pools/<ip-pool-id>?action=ALLOCATE

OST /api/v1/pools/ip-pools/<ip-pool-id>?action=RELEASE

"""


def main():
    args = getargs.getargs()

    # Create a pretty printer to make the output look nice.
    pp = PrettyPrinter()

    api_client = auth.create_nsx_api_client(args.user, args.password,
                                            args.nsx_host, args.tcp_port,
                                            auth_type=auth.SESSION_AUTH)

    # Create an IP Pool
    new_pool = IpPool(
        display_name="My IP Pool",
        description="IP Pool for IP Pool demo",
        subnets=[
            IpPoolSubnet(
                cidr="192.168.1.0/24",
                allocation_ranges=[
                    IpPoolRange(start="192.168.1.10", end="192.168.1.20")
                ]
            )
        ]
    )
    result_pool = api_client.pools.IpPools.create(new_pool)
    print("IP Pool created. id is %s" % result_pool.id)

    # Allocate an IP address
    alloc = AllocationIpAddress(allocation_id="192.168.1.11")
    api_client.pools.IpPools.allocateorrelease(
        pool_id=result_pool.id,
        allocation_ip_address=alloc,
        action=api_client.pools.IpPools.ALLOCATEORRELEASE_ACTION_ALLOCATE
    )

    # Show the allocations
    allocs = api_client.pools.ip_pools.Allocations.list(result_pool.id)
    pp.pprint(allocs)

    # Deallocate the IP address
    api_client.pools.IpPools.allocateorrelease(
        pool_id=result_pool.id,
        allocation_ip_address=alloc,
        action=api_client.pools.IpPools.ALLOCATEORRELEASE_ACTION_RELEASE
    )

if __name__ == "__main__":
    main()
