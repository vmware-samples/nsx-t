# Copyright 2017-2021 VMware, Inc.  All rights reserved
#
# The BSD-2 license (the "License") set forth below applies to all
# parts of the NSX-T SDK Sample Code project.  You may not use this
# file except in compliance with the License.
# BSD-2 License
# Redistribution and use in source and binary forms, with or
# without modification, are permitted provided that the following
# conditions are met:
#     Redistributions of source code must retain the above
#     copyright notice, this list of conditions and the
#     following disclaimer.
#     Redistributions in binary form must reproduce the above
#     copyright notice, this list of conditions and the
#     following disclaimer in the documentation and/or other
#     materials provided with the distribution.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
# CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF
# USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
# AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

# Cleanup the lab

Set-PowerCLIConfiguration -Scope User -ParticipateInCEIP $true -Confirm:$false
Set-PowerCLIConfiguration -InvalidCertificateAction Ignore -Confirm:$false

# Debug
$DEBUG = 1
$verboseLogFile = "./deploy.log"

# Physical Lab details
$p_vc = "172.16.200.6"
$p_vc_user = "administrator@vsphere.local"
$p_vc_pass = "VMware1!"

Function Debug($msg) {
    if ($DEBUG -eq 1) {
        Write-Host -ForegroundColor Cyan "$msg"
    }
}

Function Error($msg) {
    Write-Host -ForegroundColor Red "$msg"
    exit
}


$vms = @(
    "edge-ny", "edge-paris", "edge-london",
    "esx1-ny", "esx2-ny",
    "esx1-paris", "esx2-paris",
    "esx1-london", "esx2-london",
    "nsx-ny", "nsx-paris", "nsx-london",
    "nsx-gm",
    "vcenter7-ny", "vcenter7-paris", "vcenter7-london"
)

Debug "The folling VMs will be Powered OFF and deleted from disk:"
foreach ($v in $vms) {
    Debug "    - $v"
}
Debug ""
$ans = Read-Host "Are you sure you want to continue? ([y/Y] Yes; [n/N] No) [No]"
if ($ans -eq 'y' -or $ans -eq 'yes') {
    $p_vi_connection = Connect-VIServer $p_vc -User $p_vc_user -Password $p_vc_pass -WarningAction SilentlyContinue
    foreach ($v in $vms) {
        $vm = Get-VM -Server $vi -Name $v -ErrorAction SilentlyContinue
        if ($vm) {
            Debug "Stopping VM $v"
            $x = Stop-VM -Kill $v -Confirm:$false -ErrorAction  SilentlyContinue | Out-Null
            Start-Sleep 60
            $vm = Get-VM -Server $vi -Name $v -ErrorAction SilentlyContinue
            Debug "Deleting VM $v. State: $($vm.powerstate)"
            $x = $vm | Remove-VM -DeletePermanently -Confirm:$false -ErrorAction SilentlyContinue | Out-Null
        } else {
            Debug "VM: $v not found. Skipping ..."
        }
    }
    Disconnect-VIServer $p_vi_connection -Confirm:$false
}
