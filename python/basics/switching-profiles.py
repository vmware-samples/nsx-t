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
from util import auth
from util import getargs
from vmware.vapi.bindings.struct import PrettyPrinter
from com.vmware.nsx import model_client
from com.vmware.nsx.model_client import QosSwitchingProfile
from com.vmware.vapi.std.errors_client import NotFound

"""
This example shows how to create several different types of
switching profile.

Compatible with: NSX-T 2.1 and later

APIs used:

List switching profiles
GET /api/v1/switching-profiles

Create a switching profile:
POST /api/v1/switching-profiles

Read a switching profile
GET /api/v1/switching-profiles/<switching-profile-id>

Delete a switching profile:
DELETE /api/v1/switching-profiles/<switching-profile-id>

Note that switching profiles are polymorphic. There are
several different types of switching profile (e.g.
QosSwitchingProfile, SpoofGuardSwitchingProfile) that
inherit from the common SwitchingProfile base type.
This example shows how to convert from the base type
to the concrete type.
"""


def main():
    args = getargs.getargs()

    # Create a pretty printer to make the output look nice.
    pp = PrettyPrinter()

    api_client = auth.create_nsx_api_client(args.user, args.password,
                                            args.nsx_host, args.tcp_port,
                                            auth_type=auth.SESSION_AUTH)

    # First, list all switching profiles.
    swps = api_client.SwitchingProfiles.list()
    print("Initial list of switching profiles - %d profiles" %
          swps.result_count)
    # Since switching profiles are polymorphic, we need to convert
    # each profile to its concrete class
    for raw_profile in swps.results:
        concrete_type_name = raw_profile.to_dict()["resource_type"]
        concrete_type = getattr(model_client, concrete_type_name)
        profile = raw_profile.convert_to(concrete_type)
        pp.pprint(profile)

    # Create a new QOS switching profile
    new_profile = QosSwitchingProfile(
        class_of_service=None,
        dscp=None,
        shaper_configuration=None,
        description="",
        display_name="My QoS Policy",
        tags=[]
    )
    result_profile = api_client.SwitchingProfiles.create(
        new_profile).convert_to(QosSwitchingProfile)
    print("Switching profile created. id is %s" % result_profile.id)

    # Save the id, which uniquely identifies the resource we created.
    profile_id = result_profile.id

    # Read that switching profile.
    read_profile = api_client.SwitchingProfiles.get(
        profile_id).convert_to(QosSwitchingProfile)
    print("Re-read the QOS switching profile")
    pp.pprint(read_profile)

    # Delete the switching profile
    api_client.SwitchingProfiles.delete(profile_id)
    print("After deleting QOS switching profile")

if __name__ == "__main__":
    main()
