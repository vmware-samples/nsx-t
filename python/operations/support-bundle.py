#!/usr/bin/env python
"""
* **********************************************************
* Copyright (c) VMware, Inc. 2017-2019. All Rights Reserved.
* SPDX-License-Identifier: BSD-2
* **********************************************************
*
* DISCLAIMER. THIS PROGRAM IS PROVIDED TO YOU "AS IS" WITHOUT
* WARRANTIES OR CONDITIONS OF ANY KIND, WHETHER ORAL OR WRITTEN,
* EXPRESS OR IMPLIED. THE AUTHOR SPECIFICALLY DISCLAIMS ANY IMPLIED
* WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY,
* NON-INFRINGEMENT AND FITNESS FOR A PARTICULAR PURPOSE.
"""

from util import auth
from util import getargs
from com.vmware.nsx.model_client import ApiError
from com.vmware.nsx.model_client import SupportBundleRequest
from com.vmware.nsx.model_client import SupportBundleRemoteFileServer
from com.vmware.nsx.model_client import SupportBundleFileTransferProtocol
from com.vmware.nsx.model_client import (
    SupportBundleFileTransferAuthenticationScheme)
from com.vmware.vapi.std.errors_client import Error
from vmware.vapi.bindings.struct import PrettyPrinter

"""
This example shows how to collect a support bundle and
send it to a remote file server using scp.

Compatible with: NSX-T 2.1

APIs used:

Collect support bundles from registered cluster and fabric nodes
POST Path:/api/v1/administration/support-bundles?action=collect
"""


def main():
    arg_parser = getargs.get_arg_parser()
    arg_parser.add_argument("-s", "--remote_ssh_server", type=str,
                            required=True, help="remote ssh server")
    arg_parser.add_argument("-w", "--remote_ssh_user", type=str,
                            required=True, help="remote ssh username")
    arg_parser.add_argument("-c", "--remote_ssh_password", type=str,
                            required=True, help="remote ssh password")
    arg_parser.add_argument("-f", "--remote_ssh_fingerprint", type=str,
                            required=True,
                            help="remote ssh SHA256 fingerprint")
    args = arg_parser.parse_args()
    api_client = auth.create_nsx_api_client(args.user, args.password,
                                            args.nsx_host, args.tcp_port,
                                            auth_type=auth.SESSION_AUTH)
    pp = PrettyPrinter()

    # Get the UUID of the manager node we're talking to. We'll
    # request a support bundle from it.
    mgr_node = api_client.cluster.Nodes.get("self")
    mgr_uuid = mgr_node.id
    print(mgr_uuid)

    protocol = SupportBundleFileTransferProtocol(
        name="SCP",
        authentication_scheme=SupportBundleFileTransferAuthenticationScheme(
            scheme_name="PASSWORD",
            username=args.remote_ssh_user,
            password=args.remote_ssh_password
        ),
        ssh_fingerprint=args.remote_ssh_fingerprint
    )
    rfs = SupportBundleRemoteFileServer(
        directory_path="/tmp",
        server=args.remote_ssh_server,
        protocol=protocol
    )

    sb_request = SupportBundleRequest(
        log_age_limit=1,
        nodes=[mgr_uuid],
        remote_file_server=rfs
    )
    try:
        resp = api_client.administration.SupportBundles.collect(sb_request)
        pp.pprint(resp)
    except Error as ex:
        api_error = ex.data.convert_to(ApiError)
        print("An error occurred: %s" % api_error.error_message)


if __name__ == "__main__":
    main()
