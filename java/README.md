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

Sample code for VMware NSX-T Java SDK
=====================================

Overview
--------

This repository contains code samples for the NSX-T Java
SDK.

Installation
------------
To install the SDK samples, clone this git repository into a
directory in your file system.

Then obtain the VMware NSX-T for Java SDK and the vapi runtime from
the VMware{code} website at https://code.vmware.com/sdks. Copy all the
jar files to the lib directory inside the java directory.

This is the list of files needed for NSX-T 2.2:

nsx-java-sdk-2.2.0.0.0.8680797-javadoc.jar
nsx-java-sdk-2.2.0.0.0.8680797.jar
vapi-authentication-2.9.0-javadoc.jar
vapi-authentication-2.9.0.jar
vapi-runtime-2.9.0-javadoc.jar
vapi-runtime-2.9.0.jar

You can then compile all of the samples with two maven commands:

    mvn initialize
    mvn install

Preparing to run the samples
----------------------------

To run the samples, you need to have a working NSX-T manager
installed.

Self-signed X.509 certificates
------------------------------

By default, the NSX-T manager creates a self-signed X.509
certificate during installation. The example code in
src/main/java/com/vmware/nsx/examples/util/ApiClientUtils.java
has code that disables checking the validity of the NSX-T
certificate. This is deigned to help you get started quickly with
the NSX-T Java SDK, but TURNING OFF CERTIFICATE CHECKING ALLOWS
THE CLIENT TO BE COMPROMISED VIA A MAN-IN-THE-MIDDLE ATTACK. In
production deployments you should always enable server certificate
verification in clients.

Running the samples
-------------------

All samples are placed in a single jar file named
"target/nsx-java-sdk-samples-1.0.jar". To run any sample, change
directory to the top-level directory of this git repository and
run the following command:

    java -cp target/nsx-java-sdk-samples-1.0.jar <main-class-name> \
        <program-arguments>

where <main-class-name> is the fully qualified class name of the
demo's Main method.

Each sample takes the following command-line arguments:

     -c,--cert_trust_store <arg>   Certificate trust store (optional, defaults
                                   to crypto/manager.jks)
     -h,--help                     Get help
     -n,--nsx_host <arg>           NSX host to connect to
     -p,--password <arg>           Password
     -t,--tcp_port <arg>           TCP port for NSX server (optional, defaults
                                   to 443)
     -u,--user <arg>               User to authenticate as

The following samples are currently available:

**com.vmware.nsx.examples.basics.Crud**
A basic demo showing how to perform create, read, update, delete,
and list operations using the NSX-T REST API.

**com.vmware.nsx.examples.basics.ErrorHandling**
Shows how to detect API errors and obtain detailed
information for the cause of the API error.

**com.vmware.nsx.examples.basics.FabricNodes**
Shows how to retrieve information on fabric nodes and their
current status. In order for this example to produce any output,
you must configure at least one fabric node.

**com.vmware.nsx.examples.basics.L3Demo**
A demonstration of layer 3 routing. This demo creates two logical
switches, attaches the switches via a logical router, then sets
a firewall policy that blocks all traffic except on ports used
by Microsoft SQL Server.

**com.vmware.nsx.examples.basics.NodeServices**
Shows how to list the various services that run on an NSX manager
node, how to retrieve their configuration and status, and
how to restart them.

**com.vmware.nsx.examples.basics.Tagging**
Shows how to set tags (arbitrary user-supplied metadata) on
NSX resources.

**com.vmware.nsx.examples.basics.Vmc**
Shows how to authenticate to NSX in VMware Cloud on AWS (VMC).
To authenticate, you provide your VMC organization ID,
the Software Defined Data Center (SDDC) ID, and your
VMC refresh token. The SDK then obtains and uses an
authentication token, refreshing it as needed.

**com.vmware.nsx.examples.operations.LogicalStats**
Shows how to retrieve status and statistics for NSX logical
entities like Logical Ports, Logical Router Ports,  and Logical
Switches.

**com.vmware.nsx.examples.operations.PhysicalStats**
Shows how to retrieve status and statistics for the physical
underlay of NSX, like the physical interfaces of Transport
Nodes. In order for this example to produce any output, you
must configure at least one transport node.

Each sample has a comment block at the top with more information.

So, to run the Crud example on host "manager1", authenticating
as user "admin" with password "Secret!23":

    java -cp target/nsx-java-sdk-samples-1.0.jar \
        com.vmware.nsx.examples.basics.Crud -n manager1 -u admin -p "Secret!23"
