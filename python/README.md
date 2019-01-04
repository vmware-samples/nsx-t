Sample code for VMware NSX-T Python SDK
=======================================

NSX-T SDK Sample Code

Copyright 2018 VMware, Inc.  All rights reserved

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

Overview
--------

This repository contains code samples for the NSX-T Python
SDK.

Installation
------------
To install the SDK samples, clone this git repository into a
directory in your file system. You also need to have Python
2.7 or later or Python 3.4 or later.

The easiest way to install the NSX-T python SDK and its dependencies
is to use Python virtualenv. This allows you to install the SDK
and its dependencies without having to alter your system python
libraries, and also doesn't require root privileges.

To set up the NSX-T python SDK using virtualenv, make sure that the
following are installed:

* python2, version 2.7.9 or later, or python3, version 3.4 or later
* virtualenv
* pip

To install the SDK and its dependencies, issue the following commands:

    # 1) install a virtual env into directory "venv"
    virtualenv venv

    # 2) activate the virtual environment
    source venv/bin/activate

    # 3) Copy the NSX-T SDKs and vapi runtime:
    # For NSX-T 2.3, navigate to the VMware{code} website python SDK
    # site at https://code.vmware.com/sdks and follow the
    # VMware NSX-T for Python link.
    # Copy all SDK files to the lib directory in this repo.
    # The complete list of files needed are:
    # nsx_python_sdk-2.3.0.0.0.10085514-doc.zip
    # nsx_python_sdk-2.3.0.0.0.10085514-py2.py3-none-any.whl
    # nsx_policy_python_sdk-2.3.0.0.0.10085514-doc.zip
    # nsx_policy_python_sdk-2.3.0.0.0.10085514-py2.py3-none-any.whl
    # vapi_common-2.9.0-py2.py3-none-any.whl
    # vapi_common_client-2.9.0-py2.py3-none-any.whl
    # vapi_runtime-2.9.0-py2.py3-none-any.whl

    # 4) install the NSX-T SDK, and the vapi runtime
    pip install lib/*.whl

Preparing to run the samples
----------------------------

Be sure you are in the top level of the SDK examples, then add
the current directory to your PYTHONPATH:

    export PYTHONPATH=`pwd`

To run the samples, you need to have a working NSX-T manager
installed.

Running the samples
-------------------

Each sample takes the following command-line arguments:

     -h,--help                     Get help
     -n,--nsx_host <arg>           NSX host to connect to
     -t,--tcp_port <arg>           TCP port for NSX server (optional, defaults
                                   to 443)
     -u,--user <arg>               User to authenticate as
     -p,--password <arg>           Password

Each sample has a comment block at the top with more information.

As an example, to run the crud.py example on host 10.162.18.202,
authenticating as user "admin" with password "Secret!23":

    python basics/crud.py -n 10.162.18.202 -u admin -p "Secret!23"

Cleaning Up
-----------

When you are finished with the virtual environment, you can
deactivate it by typing:

    deactivate


Troubleshooting
---------------

If you are running on MacOS, the following guides may help you get
python, pip, and virtualenv installed:

[Install Python on Mac OS X for development](http://exponential.io/blog/2015/02/11/install-python-on-mac-os-x-for-development/)
[Install virtualenv and virtualenvwrapper on Mac OS X](http://exponential.io/blog/2015/02/10/install-virtualenv-and-virtualenvwrapper-on-mac-os-x/)
