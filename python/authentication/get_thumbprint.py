#!/usr/bin/env python

"""
NSX-T SDK Sample Code

Copyright 2018-2019 VMware, Inc.  All rights reserved

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

import hashlib
import socket
import ssl
import sys

"""
This example shows how to determine the "thumbprint" of an
NSX API service endpoint. The thumbprint is the hexidecimal
representation of a SHA256 digest of the server certificate.

This will work with any TLS service endpoint, not just the
NSX-T API service.
"""


def main():
    if len(sys.argv) < 3:
        sys.stderr.write("Usage: %s hostname-or-ip-address port\n" %
                         sys.argv[0])
        sys.stderr.write("Example: %s 10.3.44.12 443\n" %
                         sys.argv[0])
        sys.exit(1)

    # Since we are only displaying the server's certificate and
    # not actually connecting, turning off certificate validation
    # is safe.
    try:
        ssl._create_default_https_context = ssl._create_unverified_context
    except Exception as ex:
        pass  # Assume older python where default was to not verify

    s = socket.socket()
    conn = ssl.wrap_socket(s)
    try:
        conn.connect((sys.argv[1], int(sys.argv[2])))
        conn_thumbprint = hashlib.sha256(conn.getpeercert(True)).hexdigest()
        print(conn_thumbprint)
    finally:
        if conn is not None:
            conn.close()

if __name__ == "__main__":
    main()
