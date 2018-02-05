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

import os

from util import auth
from util import getargs

from com.vmware.nsx.model_client import ApiError
from com.vmware.nsx.model_client import CopyFromRemoteFileProperties
from com.vmware.nsx.model_client import CopyToRemoteFileProperties
from com.vmware.nsx.model_client import PasswordAuthenticationScheme
from com.vmware.nsx.model_client import ScpProtocol
from com.vmware.nsx.node_client import FileStore
from com.vmware.vapi.std.errors_client import Error
from vmware.vapi.bindings.struct import PrettyPrinter

"""
This example shows how to copy files to and from an NSX
node's file store.

Compatible with: NSX-T 2.1

APIs used:

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
    arg_parser.add_argument("-g", "--remote_file_path", type=str,
                            required=True,
                            help="full path name of remote file to copy")
    args = arg_parser.parse_args()
    stub_config = auth.get_session_auth_stub_config(args.user, args.password,
                                                    args.nsx_host,
                                                    args.tcp_port)

    pp = PrettyPrinter()

    # Instantiate all the services we'll need.
    fs_svc = FileStore(stub_config)

    local_file_name = os.path.basename(args.remote_file_path)

    # Copy a file from a remote server to the NSX node
    protocol = ScpProtocol(
        name="scp",
        authentication_scheme=PasswordAuthenticationScheme(
            scheme_name="password",
            username=args.remote_ssh_user,
            password=args.remote_ssh_password
        ),
        ssh_fingerprint=args.remote_ssh_fingerprint
    )
    remote_properties = CopyFromRemoteFileProperties(
        port=22,
        server=args.remote_ssh_server,
        uri=args.remote_file_path,
        protocol=protocol
    )
    try:
        fs_svc.copyfromremotefile(local_file_name, remote_properties)
        print("Copied %s from %s to nsx node %s" %
              (local_file_name, args.remote_ssh_server, args.nsx_host))
    except Error as ex:
        api_error = ex.data.convert_to(ApiError)
        print("An error occurred: %s" % api_error.error_message)

    # Then copy that file back from the NSX node
    remote_properties = CopyToRemoteFileProperties(
        port=22,
        server=args.remote_ssh_server,
        uri=args.remote_file_path,
        protocol=protocol
    )
    try:
        fs_svc.copytoremotefile(local_file_name, remote_properties)
        print("Copied %s from nsx_node %s to %s" %
              (local_file_name, args.nsx_host, args.remote_ssh_server))
    except Error as ex:
        api_error = ex.data.convert_to(ApiError)
        print("An error occurred: %s" % api_error.error_message)



if __name__ == "__main__":
    main()
