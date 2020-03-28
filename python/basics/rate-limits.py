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
import time
from util import auth
from util import getargs
from com.vmware.nsx.model_client import ApiError
from com.vmware.vapi.std.errors_client import Error
from com.vmware.vapi.std.errors_client import ServiceUnavailable
from google.api_core.retry import Retry
from google.api_core.retry import if_exception_type

"""
This example shows how to implement backoff and retry when an API
call fails because of API rate-limiting. It makes use of the
Retry helper from the google core APIs.

To run this example, you will need to install google-api-core
with "pip install google-api-core".
"""


# Call the given API, retrying if the API fails with a ServiceUnavailble
# exception (both the 429 Too Many Requests and 503 Service Unavailable
# responses that the NSX-T API may return map to this exception).
# Initially back off for one tenth of a second. By default, the Retry
# will double the backoff interval each time up to a maximum of
# 60 seconds. For more information on Retry, see
# https://googleapis.dev/python/google-api-core/latest/retry.html

@Retry(predicate=if_exception_type(ServiceUnavailable), initial=0.1)
def call_api_with_retry(api, *args):
    return apply(api, args)


def main():
    args = getargs.getargs()
    api_client = auth.create_nsx_policy_api_client(
        args.user, args.password, args.nsx_host, args.tcp_port,
        auth_type=auth.SESSION_AUTH)

    while True:
        n = 0
        last = time.time()
        while time.time() - last < 1.0:
            call_api_with_retry(api_client.Infra.get)
            n += 1
            # API calls that take arguments:
            #
            # Since we use the python apply() method, you need
            # to pass the callable and its arguments as a list.
            # The usual way to call this API would be:
            # api_client.infra.Domains.get("default")
            #
            call_api_with_retry(api_client.infra.Domains.get, "default")
            n += 1

        print("%d calls/sec" % n)


if __name__ == "__main__":
    main()
