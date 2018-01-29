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

import requests

from vmware.vapi.lib import connect
from vmware.vapi.security.user_password import \
    create_user_password_security_context
from vmware.vapi.stdlib.client.factories import StubConfigurationFactory


def get_basic_auth_stub_config(user, password, nsx_host, tcp_port=443):
    """
    Create a stub configuration that uses HTTP basic authentication.
    """
    session = requests.session()

    # Since the NSX manager default certificate is self-signed,
    # we disable verification. This is dangerous and real code
    # should verify that it is talking to a valid server.
    session.verify = False
    requests.packages.urllib3.disable_warnings()

    nsx_url = 'https://%s:%s' % (nsx_host, tcp_port)
    connector = connect.get_requests_connector(
        session=session, msg_protocol='rest', url=nsx_url)
    stub_config = StubConfigurationFactory.new_std_configuration(connector)
    security_context = create_user_password_security_context(
        user, password)
    connector.set_security_context(security_context)
    return stub_config


def get_session_auth_stub_config(user, password, nsx_host, tcp_port=443):
    """
    Create a stub configuration that uses session-based authentication.
    Session authentication is more efficient, since the server only
    needs to perform authentication of the username/password one time.
    """
    session = requests.session()

    # Since the NSX manager default certificate is self-signed,
    # we disable verification. This is dangerous and real code
    # should verify that it is talking to a valid server.
    session.verify = False
    requests.packages.urllib3.disable_warnings()
    nsx_url = 'https://%s:%s' % (nsx_host, tcp_port)
    resp = session.post(nsx_url + "/api/session/create",
                        data={"j_username": user, "j_password": password})
    if resp.status_code != requests.codes.ok:
        resp.raise_for_status()

    # Set the Cookie and X-XSRF-TOKEN headers
    session.headers["Cookie"] = resp.headers.get("Set-Cookie")
    session.headers["X-XSRF-TOKEN"] = resp.headers.get("X-XSRF-TOKEN")

    connector = connect.get_requests_connector(
        session=session, msg_protocol='rest', url=nsx_url)
    stub_config = StubConfigurationFactory.new_std_configuration(connector)
    return stub_config
