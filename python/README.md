# *******************************************************
# Copyright VMware, Inc. 2017.  All Rights Reserved.
# SPDX-License-Identifier: BSD-2
# *******************************************************
#
# DISCLAIMER. THIS PROGRAM IS PROVIDED TO YOU "AS IS" WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, WHETHER ORAL OR WRITTEN,
# EXPRESS OR IMPLIED. THE AUTHOR SPECIFICALLY DISCLAIMS ANY IMPLIED
# WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY,
# NON-INFRINGEMENT AND FITNESS FOR A PARTICULAR PURPOSE.


Sample code for VMware NSX-T Python SDK
=======================================

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
    # For NSX-T 2.1, navigate to the VMware{code} website python SDK
    # site at:
    # https://my.vmware.com/web/vmware/details?downloadGroup=NSX-T-210-SDK-PYTHON&productId=673
    # Copy all SDK files to the lib directory in this repo.
 
    # 4) install the NSX-T SDK, and the vapi runtime
    pip install lib/*.whl

Preparing to run the samples
----------------------------

Be sure you are in the top level of the SDK examples, then add
the current directory to your PYTHONPATH:

    export PYTHONPATH=`pwd`

To run the samples, you need to have a working NSX-T manager
installed. To run the NSX policy SDK examples, you will need
to have a working NSX-T Policy appliance running.

Running the samples
-------------------

Each sample takes the following command-line arguments:

     -h,--help                     Get help  
     -n,--nsx_host <arg>           NSX host to connect to  
     -t,--tcp_port <arg>           TCP port for NSX server (optional, defaults  
                                   to 443)  
     -u,--user <arg>               User to authenticate as  
     -p,--password <arg>           Password  

The following samples are currently available:

**basics/crud.py**  
A basic demo showing how to perform create, read, update, delete,
and list operations using the NSX-T REST API.

**basics/crud-policy.py**  
A basic demo showing how to perform create, read, update, delete,
and list operations using the NSX-T Policy REST API.

**basics/fabric-nodes.py**  
Shows how to retrieve information on fabric nodes and their
current status.

**basics/l3-demo.py**  
A demonstration of layer 3 routing. This demo creates two logical
switches, attaches the switches via a logical router, then sets
a firewall policy that blocks all traffic except on ports used
by Microsoft SQL Server.

**basics/tagging.py**  
Shows how to set tags (arbitrary user-supplied metadata) on
NSX resources.

**operations/logical-stats.py**  
Shows how to retrieve status and statistics for NSX logical
entities like Logical Ports, Logical Router Ports,  and Logical
Switches.

**operations/physical-stats.py**  
Shows how to retrieve status and statistics for the physical
underlay of NSX, like the physical interfaces of Transport
Nodes.

Each sample has a comment block at the top with more information.

So, to run the crud.py example on host 10.162.18.202, authenticating
as user "admin" with password "Secret!23":

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
