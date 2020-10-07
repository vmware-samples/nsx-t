# Copyright 2017-2020 VMware, Inc.  All rights reserved
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

$NSX_IP = "10.114.200.41"
$NSX_User = "admin"
$NSX_Password = "myPassword1!myPassword1!"

Write-Host "Connecting to NSX Manager ..."
Connect-NsxtServer -Server $NSX_IP -User $NSX_User -Password $NSX_Password

function createT0($T0GatewayName, $EdgeClusterName) {

    $t0s = Get-NsxtPolicyService -Name "com.vmware.nsx_policy.infra.tier0s"
    $t0LocaleServices = Get-NsxtPolicyService -Name "com.vmware.nsx_policy.infra.tier_0s.locale_services"
    $edges = Get-NsxtPolicyService -Name "com.vmware.nsx_policy.infra.sites.enforcement_points.edge_clusters"

    $edgeClusters = ($edges.list("default","default").results | where {$_.display_name -eq $EdgeClusterName})

    $t0Spec = $t0s.help.patch.tier0.Create()
    $t0Spec.id = $T0GatewayName
    $t0Spec.display_name = $T0GatewayName
    $t0Spec.ha_mode = "ACTIVE_STANDBY"
    $t0Spec.failover_mode = "NON_PREEMPTIVE"
    $t0Gateway = $t0s.patch($T0GatewayName, $t0Spec)

    $localeServiceSpec = $t0LocaleServices.help.patch.locale_services.create()
    $localeServiceSpec.display_name = "default"
    $localeServiceSpec.edge_cluster_path = $edgeClusters.path
    $localeService = $t0LocaleServices.patch($T0GatewayName, "default", $localeServiceSpec)
    Write-Host "Created T0 Gateway $T0GatewayName ..."

}

function createT1($T1GatewayName, $T0GatewayName, $EdgeClusterName) {
    $t1GatewayPolicyService = Get-NsxtPolicyService -Name "com.vmware.nsx_policy.infra.tier1s"
    $t0s = Get-NsxtPolicyService -Name "com.vmware.nsx_policy.infra.tier0s"

    $t0 = ($t0s.list().results | where {$_.display_name -eq $T0Gatewayname})
    $t0Path = $t0.path

    $t1Spec = $t1GatewayPolicyService.help.patch.tier1.Create()
    $t1Spec.id = $T1GatewayName
    $t1Spec.display_name = $T1GatewayName
    $t1Spec.tier0_path = $t0Path
    $t1Spec.route_advertisement_types = @("TIER1_NAT", "TIER1_LB_VIP", "TIER1_LB_SNAT", "TIER1_DNS_FORWARDER_IP", "TIER1_CONNECTED", "TIER1_STATIC_ROUTES", "TIER1_IPSEC_LOCAL_ENDPOINT") 
    $t1Gateway = $t1GatewayPolicyService.patch($T1GatewayName, $t1Spec)
    Write-Host "Created T1 Gateway $T1GatewayName ..."
}

function createSegment($SegmentName, $T1GatewayName, $GatewayCIDR, $TransportZone) {
    $segments = Get-NsxtPolicyService -Name "com.vmware.nsx_policy.infra.segments"
    $t1s = Get-NsxtPolicyService -Name "com.vmware.nsx_policy.infra.tier1s"
    $tzs = Get-NsxtPolicyService -name "com.vmware.nsx_policy.infra.sites.enforcement_points.transport_zones" 

    $t1 = $t1s.get($T1GatewayName)
    $tz = ($tzs.list('default', 'default').results | where { $_.display_name -eq $TransportZone})

    $segmentSpec = $segments.help.patch.segment.Create()
    $segmentSpec.id = $SegmentName
    $segmentSpec.display_name = $SegmentName
    $segmentSpec.transport_zone_path = $tz.path
    $segmentSpec.connectivity_path = $t1.path
    $segmentSpec.advanced_config.connectivity = "ON"

    $subnetSpec = $segments.help.patch.segment.subnets.Element.Create()
    $subnetSpec.gateway_address = $GatewayCIDR
    $segmentSpec.subnets.Add($subnetSpec) | Out-Null
    $segments.patch($SegmentName, $segmentSpec)
    Write-Host "Created Segment $SegmentName ..."
}

function createGroup($GroupName, $MemberType, $Key, $Operator, $Value) {
    $groups = Get-NsxtPolicyService -Name "com.vmware.nsx_policy.infra.domains.groups"

    $groupSpec = $groups.help.patch.group.Create()
    $groupSpec.id = $GroupName
    $groupSpec.display_name = $GroupName

    $expressionSpec = $groups.help.patch.group.expression.Element.condition.Create()
    $expressionSpec.member_type = $MemberType
    $expressionSpec.key = $Key
    $expressionSpec.operator = $Operator
    $expressionSpec.value = $value
    $groupSpec.expression.Add($expressionSpec) | Out-Null
    $groups.patch('default', $GroupName, $groupSpec)
    Write-Host "Created Group $GroupName ..."
}

function createDFWSecurityPolicy($PolicyName, $Category, $RuleName, $SourceGroups, $DestinationGroups, $ServiceList, $Action) {
    $policies = Get-NsxtPolicyService -Name com.vmware.nsx_policy.infra.domains.security_policies
    $groups = Get-NsxtPolicyService -Name "com.vmware.nsx_policy.infra.domains.groups"
    $services = Get-NsxtPolicyService -Name "com.vmware.nsx_policy.infra.services"

    $sourcePath = @()
    foreach ($name in $SourceGroups) {
        if ($name -eq "ANY") {
            $sourcePath += "ANY"
        } else {
            $g = ($groups.list('default').results | where {$_.display_name -eq $name})
            $sourcePath += $g.path
        }
    }

    $destPath = @()
    foreach ($name in $DestinationGroups) {
        if ($name -eq "ANY") {
            $destPath += "ANY"
        } else {
            $g = ($groups.list('default').results | where {$_.display_name -eq $name})
            $destPath += $g.path
        }
    }

    $servicePath = @()
    $full_list = $services.list().results
    foreach ($name in $ServiceList) {
        if ($name -eq "ANY") {
            $servicePath += "ANY"
        } else {
            $s = ($full_list | where {$_.display_name -eq $name})
            $servicePath += $s.path
        }
    }

    $policySpec = $policies.help.patch.security_policy.Create()
    $policySpec.id = $PolicyName
    $policySpec.display_name = $PolicyName
    $policySpec.category = $Category

    $ruleSpec = $policies.help.patch.security_policy.rules.Element.create()
    $ruleSpec.display_name = $RuleName
    $ruleSpec.source_groups = $sourcePath
    $ruleSpec.destination_groups = $destPath
    $ruleSpec.services = $servicePath
    $ruleSpec.action = $Action
    $policySpec.rules.Add($ruleSpec) | Out-Null
    $policies.patch('default', $PolicyName, $policySpec)
    Write-Host "Created DFW Policy $PolicyName with Rule $RuleName ..."
}


if ($args[0] -eq "delete") {
    $policies = Get-NsxtPolicyService -Name com.vmware.nsx_policy.infra.domains.security_policies
    $groups = Get-NsxtPolicyService -Name "com.vmware.nsx_policy.infra.domains.groups"
    $segments = Get-NsxtPolicyService -Name "com.vmware.nsx_policy.infra.segments"
    $t1s = Get-NsxtPolicyService -Name "com.vmware.nsx_policy.infra.tier1s"
    $t0LocaleServices = Get-NsxtPolicyService -Name "com.vmware.nsx_policy.infra.tier_0s.locale_services"
    $t0s = Get-NsxtPolicyService -Name "com.vmware.nsx_policy.infra.tier0s"

    $PCLIPolicies = @("PCLI-Allow-SQL", "PCLI-Allow-HTTP", "PCLI-Ops")
    $PCLIGroups = @("PCLI-all-vms", "PCLI-web-vms", "PCLI-app-vms", "PCLI-db-vms")
    $PCLISegments = @("PCLI-3Tier", "PCLI-Client")
    $PCLIT1s = @("PCLI-VMW-T1", "PCLI-Client-T1")
    $PCLIT0s = @("PCLI-3Tier-T0")

    foreach ($item in $PCLIPolicies) {
        $p = ($policies.list('default').results | where {$_.display_name -eq $item})
        $policies.delete('default', $p.id)
        Write-Host "Deleted Policy $item ..."
    }

    foreach ($item in $PCLIGroups) {
        $g = ($groups.list('default').results | where {$_.display_name -eq $item})
        $groups.delete('default', $g.id)
        Write-Host "Deleted Group $item ..."
    }

    foreach ($item in $PCLISegments) {
        $s = ($segments.list().results | where {$_.display_name -eq $item})
        $segments.delete($s.id)
        Write-Host "Deleted Segment $item ..."
    }

    foreach ($item in $PCLIT1s) {
        $t1 = ($t1s.list().results | where {$_.display_name -eq $item})
        $t1s.delete($t1.id)
        Write-Host "Deleted Tier1 Gateway $item ..."
    }

    foreach ($item in $PCLIT0s) {
        $t0 = ($t0s.list().results | where {$_.display_name -eq $item})
        $t0ls = ($t0LocaleServices.list($t0.id).results | where {$_.display_name -eq 'default'})
        $t0LocaleServices.delete($t0.id, $t0ls.id)
        $t0s.delete($t0.id)
        Write-Host "Deleted Tier0 Gateway $item ..."
    }

} else {

    createT0 "PCLI-3Tier-T0" "Edge-Cluster-01"

    createT1 "PCLI-VMW-T1" "PCLI-3Tier-T0" "Edge-Cluster-01"
    createT1 "PCLI-Client-T1" "PCLI-3Tier-T0" "Edge-Cluster-01"

    createSegment "PCLI-3Tier" "PCLI-VMW-T1" "192.20.10.1/24" "Overlay-TZ"
    createSegment "PCLI-Client" "PCLI-Client-T1" "192.20.50.1/24" "Overlay-TZ"

    createGroup "PCLI-all-vms" "VirtualMachine" "Tag" "EQUALS" "nsx"
    createGroup "PCLI-web-vms" "VirtualMachine" "Tag" "EQUALS" "web"
    createGroup "PCLI-app-vms" "VirtualMachine" "Tag" "EQUALS" "app"
    createGroup "PCLI-db-vms" "VirtualMachine" "Tag" "EQUALS" "db"

    createDFWSecurityPolicy "PCLI-Allow-SQL" "Application" "allow-mysql" @("ANY") @("PCLI-db-vms") @("MySQL") "ALLOW"
    createDFWSecurityPolicy "PCLI-Allow-HTTP" "Application" "allow-browsing" @("ANY") @("PCLI-web-vms") @("HTTP", "HTTPS") "ALLOW"
    createDFWSecurityPolicy "PCLI-Ops" "Infrastructure" "allow-SSH" @("ANY") @("ANY") @("SSH") "REJECT"
    createDFWSecurityPolicy "PCLI-Ops" "Infrastructure" "allow-ICMP" @("ANY") @("ANY") @("ICMP ALL") "ALLOW"

}
