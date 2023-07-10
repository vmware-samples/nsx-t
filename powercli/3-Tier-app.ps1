# Copyright 2017-2022 VMware, Inc.  All rights reserved
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

Set-PowerCLIConfiguration -Scope User -ParticipateInCEIP $true -Confirm:$false | Out-Null
Set-PowerCLIConfiguration -Scope User -InvalidCertificateAction:Ignore -Confirm:$false | Out-Null

$NSX_IP = "10.221.109.5"
$NSX_User = "admin"
$NSX_Password = "VMware1!VMware1!"

Write-Host "Connecting to NSX Manager ..."
$n = Connect-NsxServer -Server $NSX_IP -User $NSX_User -Password $NSX_Password

function createT0($T0GatewayName, $EdgeClusterName) {
    $t0s = Invoke-ListTier0s -Server $n
    $t0 = $t0s.Results | where {$_.DisplayName -eq $T0GatewayName}
    if ($t0) {
        Write-Host "T0 Gateway $T0GatewayName already exists."
    } else {
        $t0 = Initialize-Tier0 -ArpLimit 5000 -DisplayName $T0GatewayName
        $createdT0 = Invoke-CreateOrReplaceTier0 -Server $n -Tier0Id $T0GatewayName -Tier0 $t0
        Write-Host "Created T0 Gateway $T0GatewayName ..."
    }
}

function createT1($T1GatewayName, $T0GatewayName, $EdgeClusterName) {
    $t1s = Invoke-ListTier1 -Server $n
    $t1 = $t1s.Results | where {$_.DisplayName -eq $T1GatewayName}
    if ($t1) {
        Write-Host "T1 Gateway $T1GatewayName already exists."
    } else {
        $t0s = Invoke-ListTier0s -Server $n
        $t0 = $t0s.Results | where {$_.DisplayName -eq $T0GatewayName}
        if ($t0) {
            $t1 = Initialize-Tier1 -ArpLimit 5000 -DisplayName $T1GatewayName -Tier0Path $t0.Path
            $createdT1 = Invoke-CreateOrReplaceTier1 -Server $n -Tier1Id $T1GatewayName -Tier1 $t1
            $edgeClusters = Invoke-ListEdgeClustersForEnforcementPoint -Server $n -SiteId default -EnforcementPointId default 
            $edgeCluster = $edgeClusters.Results | where {$_.DisplayName -eq $EdgeClusterName} 
            $localeService = Initialize-LocaleServices -EdgeClusterPath $edgeCluster.Path -DisplayName default -Id default
            # Create the 'default' LocaleService to the Tier-1
            # Need to delete the LocaleService before removing the Tier-1
            Invoke-PatchTier1LocaleServices -Server $n -Tier1Id $createdT1.Id -LocaleServices $localeService -LocaleServicesId default

            Write-Host "Created T1 Gateway $T1GatewayName ..."
        } else {
            Write-Host "Unable to find Tier0 Gateway $T0GatewayName. Not creating Tier1 Gateway $T1GatewayName"
        }
    }
}

function createSegment($SegmentName, $T1GatewayName, $GatewayCIDR, $TransportZone) {

    $segments = Invoke-ListAllInfraSegments -Server $n
    $segment = $segments.Results | where {$_.DisplayName -eq $SegmentName}
    if ($segment) {
        Write-Host "Segment $SegmentName already exists."
    } else {
        if ($TransportZone) {
            $tzs = Invoke-ListTransportZonesForEnforcementPoint -Server $n -EnforcementpointId "default" -SiteId "default"
            $tz = $tzs.Results | where {$_.DisplayName -eq $TransportZone}
            if (! $tz) {
                Write-Host "Unable to find Transport Zone $TransportZone. Exiting"
                exit
            }
        }
        $subnet = Initialize-SegmentSubnet -GatewayAddress $GatewayCIDR
        $t1s = Invoke-ListTier1 -Server $n
        $t1 = $t1s.Results | where {$_.DisplayName -eq $T1GatewayName}
        if ($t1) {
            $segment = Initialize-Segment -DisplayName $SegmentName -TransportZonePath $tz.Path -Subnets $subnet -ConnectivityPath $t1.Path
            $createdSegment = Invoke-CreateOrReplaceInfraSegment -Server $n -Segment $segment -SegmentId $SegmentName
            Write-Host "Created Segment $SegmentName ..."
        } else {
            Write-Host "Unable to find Tier1 Gateway $T1Gatewayname. Not creating Segment $SegmentName"
        }
    }
}

function createGroup($GroupName, $MemberType, $Key, $Operator, $Value) {

    $allGroups = Invoke-ListGroupForDomain -Server $n -DomainId default
    $gp = $allGroups.Results | where {$_.DisplayName -eq $GroupName}
    if ($gp) {
        Write-Host "Group $GroupName already exists."
    } else {
        $cond = Initialize-Condition -ResourceType Condition -Id $GroupName -MemberType $MemberType -Value $Value -Key $Key -Operator $Operator
        $group = Initialize-Group -DisplayName $GroupName -Expression @($cond)
        $createdGroup = Invoke-PatchGroupForDomain -Server $n -DomainId default -Group $group -GroupId $GroupName
        Write-Host "Created Group $GroupName ..."
    }
}

function createDFWSecurityPolicy($PolicyName, $Category, $RuleName, $SourceGroups, $DestinationGroups, $ServiceList, $Action) {

    $alls = Invoke-ListServicesForTenant -Server $n
    $AllGroups = Invoke-ListGroupForDomain -DomainId default -Server $n

    $ServicePathList = @()
    foreach ($serv in $ServiceList) {
        $s = $alls.Results | where {$_.DisplayName -eq $serv}
        $ServicePathList += $s.Path
    }

    $SourceGroupList = @()
    foreach ($gp in $SourceGroups) {
        if ($gp -eq "ANY") {
            $SourceGroupList += "ANY"
        } else {
            $g = $AllGroups.Results | where {$_.DisplayName -eq $gp}
            $SourceGroupList += $g.Path
        }
    }

    $DestinationGroupList = @()
    foreach ($gp in $DestinationGroups) {
        if ($gp -eq "ANY") {
            $DestinationGroupList += "ANY"
        } else {
            $g = $AllGroups.Results | where {$_.DisplayName -eq $gp}
            $DestinationGroupList += $g.Path
        }
    }
    
    $r = Initialize-Rule -DisplayName $RuleName -Id $RuleName -SourceGroups $SourceGroupList -DestinationGroups $DestinationGroupList -Services $ServicePathList -Action $Action
    $sp = Initialize-SecurityPolicy -DisplayName $PolicyName -Id $PolicyName -Rules @($r) -Category $Category
    $createdSP = Invoke-PatchSecurityPolicyForDomain -Server $n -DomainId default -SecurityPolicyId $PolicyName -SecurityPolicy $sp
    Write-Host "Created DFW Policy $PolicyName with Rule $RuleName ..."
}


if ($args[0] -eq "delete") {

    $PCLIPolicies = @("PCLI-Allow-SQL", "PCLI-Allow-HTTP", "PCLI-Ops")
    $PCLIGroups = @("PCLI-all-vms", "PCLI-web-vms", "PCLI-app-vms", "PCLI-db-vms")
    $PCLISegments = @("PCLI-3Tier", "PCLI-Client")
    $PCLIT1s = @("PCLI-VMW-T1", "PCLI-Client-T1")
    $PCLIT0s = @("PCLI-3Tier-T0")

    foreach ($item in $PCLIPolicies) {

        Invoke-DeleteSecurityPolicyForDomain -Server $n -Domain default -SecurityPolicyId $item
        Write-Host "Deleted Policy $item ..."
    }
    Start-Sleep -s 5

    foreach ($item in $PCLIGroups) {

        Invoke-DeleteGroup -Server $n -Domain default -GroupID $item
        Write-Host "Deleted Group $item ..."
    }
    Start-Sleep -s 5

    foreach ($item in $PCLISegments) {

        Invoke-DeleteInfraSegment -Server $n -SegmentId $item
        Write-Host "Deleted Segment $item ..."
    }
    Start-Sleep -s 5

    foreach ($item in $PCLIT1s) {
        Invoke-DeleteTier1LocaleServices -Server $n -Tier1Id $item -LocaleServicesId default
        Invoke-DeleteTier1 -Server $n -Tier1Id $item
        Write-Host "Deleted Tier1 Gateway $item ..."
    }
    Start-Sleep -s 5

    foreach ($item in $PCLIT0s) {
        Invoke-DeleteTier0 -Server $n -Tier0Id $item
        Write-Host "Deleted Tier0 Gateway $item ..."
    }

} else {

    createT0 "PCLI-3Tier-T0"

    createT1 "PCLI-VMW-T1" "PCLI-3Tier-T0" "edge-cluster-01"
    createT1 "PCLI-Client-T1" "PCLI-3Tier-T0" "edge-cluster-01"

    createSegment "PCLI-3Tier" "PCLI-VMW-T1" "192.20.10.1/24" "nsx-overlay-transportzone"
    createSegment "PCLI-Client" "PCLI-Client-T1" "192.20.50.1/24" "nsx-overlay-transportzone"

    createGroup "PCLI-all-vms" "VirtualMachine" "Tag" "EQUALS" "nsx"
    createGroup "PCLI-web-vms" "VirtualMachine" "Tag" "EQUALS" "web"
    createGroup "PCLI-app-vms" "VirtualMachine" "Tag" "EQUALS" "app"
    createGroup "PCLI-db-vms" "VirtualMachine" "Tag" "EQUALS" "db"

    createDFWSecurityPolicy "PCLI-Allow-SQL" "Application" "allow-mysql" @("ANY") @("PCLI-db-vms") @("MySQL") "ALLOW"
    createDFWSecurityPolicy "PCLI-Allow-HTTP" "Application" "allow-browsing" @("ANY") @("PCLI-web-vms") @("HTTP", "HTTPS") "ALLOW"
    createDFWSecurityPolicy "PCLI-Ops" "Infrastructure" "allow-SSH" @("ANY") @("ANY") @("SSH") "REJECT"
    createDFWSecurityPolicy "PCLI-Ops" "Infrastructure" "allow-ICMP" @("ANY") @("ANY") @("ICMP ALL") "ALLOW"

}