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

from util import auth
from util import getargs
from com.vmware.nsx.administration_client import SupportBundles
from com.vmware.nsx.model_client import SupportBundleRequest
from com.vmware.nsx.model_client import SupportBundleRemoteFileServer
from com.vmware.nsx.model_client import SupportBundleFileTransferProtocol
from com.vmware.nsx.model_client import SupportBundleFileTransferAuthenticationScheme
from com.vmware.nsx.cluster_client import Nodes
from vmware.vapi.bindings.struct import PrettyPrinter

"""
* *******************************************************
* Copyright (c) VMware, Inc. 2017. All Rights Reserved.
* SPDX-License-Identifier: MIT
* *******************************************************
*
* DISCLAIMER. THIS PROGRAM IS PROVIDED TO YOU "AS IS" WITHOUT
* WARRANTIES OR CONDITIONS OF ANY KIND, WHETHER ORAL OR WRITTEN,
* EXPRESS OR IMPLIED. THE AUTHOR SPECIFICALLY DISCLAIMS ANY IMPLIED
* WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY,
* NON-INFRINGEMENT AND FITNESS FOR A PARTICULAR PURPOSE.
"""

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
    arg_parser.add_argument("-r", "--remote_ssh_user", type=str,
                            required=True, help="remote ssh username")
    arg_parser.add_argument("-c", "--remote_ssh_password", type=str,
                            required=True, help="remote ssh password")
    arg_parser.add_argument("-f", "--remote_ssh_fingerprint", type=str,
                            required=True,
                            help="remote ssh SHA256 fingerprint")
    args = arg_parser.parse_args()
    stub_config = auth.get_session_auth_stub_config(args.user, args.password,
                                                    args.nsx_host,
                                                    args.tcp_port)

    pp = PrettyPrinter()

    # Instantiate all the services we'll need.
    sb_svc = SupportBundles(stub_config)
    cl_node_svc = Nodes(stub_config)

    # Get the UUID of the manager node we're talking to. We'll
    # request a support bundle from it.
    mgr_node = cl_node_svc.get("self")
    mgr_uuid = mgr_node.id
    print mgr_uuid

    rfs = SupportBundleRemoteFileServer(
        directory_path="/tmp",
        server=args.remote_ssh_server,
        protocol=SupportBundleFileTransferProtocol(
            name="SCP",
            authentication_scheme=SupportBundleFileTransferAuthenticationScheme(
                scheme_name="PASSWORD",
                username=args.remote_ssh_user,
                password=args.remote_ssh_password
            ),
            ssh_fingerprint=args.remote_ssh_fingerprint
        )
    )
  
    sb_request = SupportBundleRequest(
        log_age_limit=1,
        nodes=[mgr_uuid],
        remote_file_server=rfs
    )
    resp = sb_svc.collect(sb_request)
    pp.pprint(resp)


if __name__ == "__main__":
    main()
