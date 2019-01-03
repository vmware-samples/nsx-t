#!/usr/bin/env python

import sys
from util import auth
from util import getargs
from vmware.vapi.bindings.struct import PrettyPrinter
from com.vmware.nsx.model_client import TelemetryConfig
from com.vmware.vapi.std.errors_client import NotFound


def main():
    args = getargs.getargs()

    api_client = auth.create_nsx_api_client(args.user, args.password,
                                            args.nsx_host, args.tcp_port,
                                            auth_type=auth.SESSION_AUTH)

    # Create a pretty printer to make the output look nice.
    pp = PrettyPrinter()

    t = api_client.telemetry.Config.get()
    pp.pprint(t)


if __name__ == "__main__":
    main()
