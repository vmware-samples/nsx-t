#
# PowerCLI Config to create the following:
#     Tier1, 2 Segments, Groups and DFW rules
#

Set-PowerCLIConfiguration -Scope User -ParticipateInCEIP $true -Confirm:$false | Out-Null
Set-PowerCLIConfiguration -Scope User -InvalidCertificateAction:Ignore -Confirm:$false | Out-Null

$nsx_ip = "nsxapp-01a.corp.local"
$nsx_user = "admin"
$nsx_password = "VMware1!VMware1!"

$edge_cluster_name = "EdgeCluster"
$tier0_name = "T0-Paris"

function Log($msg) {
    Write-Host -ForegroundColor Cyan "$msg"
}

function createT1($n, $T1GatewayName, $T0GatewayName, $EdgeClusterName) {
    $t1GatewayPolicyService = Get-NsxtPolicyService -Server $n -Name "com.vmware.nsx_policy.infra.tier1s"
    $edgeClusterService = Get-NsxtPolicyService -Server $n -Name "com.vmware.nsx_policy.infra.sites.enforcement_points.edge_clusters"
    # List has site-id and enforcementpoint-id
    $edgeCluster = ($edgeClusterService.list('default', 'default').results | where {$_.display_name -eq $EdgeClusterName})
    $edgeClusterPath = $edgeCluster.path

    $t0s = Get-NsxtPolicyService -Server $n -Name "com.vmware.nsx_policy.infra.tier0s"
    $t0 = ($t0s.list().results | where {$_.display_name -eq $T0Gatewayname})
    $t0Path = $t0.path

    $t1Spec = $t1GatewayPolicyService.help.patch.tier1.Create()
    $t1Spec.id = $T1GatewayName
    $t1Spec.display_name = $T1GatewayName
    $t1Spec.tier0_path = $t0Path
    $t1Spec.route_advertisement_types = @("TIER1_NAT", "TIER1_LB_VIP", "TIER1_LB_SNAT", "TIER1_DNS_FORWARDER_IP", "TIER1_CONNECTED", "TIER1_STATIC_ROUTES", "TIER1_IPSEC_LOCAL_ENDPOINT") 
    $t1Gateway = $t1GatewayPolicyService.patch($T1GatewayName, $t1Spec)

    $t1LocaleServices = Get-NsxtPolicyService -Server $n -Name "com.vmware.nsx_policy.infra.tier_1s.locale_services"
    $t1lsSpec = $t1LocaleServices.Help.patch.locale_services.Create()
    $t1lsSpec.display_name = "default"
    $t1lsSpec.edge_cluster_path = $edgeClusterPath
    $t1ls = $t1LocaleServices.patch($T1GatewayName, "default", $t1lsSpec)
    Log ("Created T1 Gateway $T1GatewayName ...")
}

function createT1NATRule($n, $T1GatewayName, $natDisplayName, $action, $destination_networks, $translated_networks, $ruleID) {
    $t1GatewayNatService = Get-NsxtPolicyService -Server $n -Name "com.vmware.nsx_policy.infra.tier_1s.nat.nat_rules"
    $t1s = Get-NsxtPolicyService -Server $n -Name "com.vmware.nsx_policy.infra.tier1s"

    $t1 = ($t1s.list().results | where {$_.display_name -eq $T1GatewayName})
    $t1Path = $t1.path

    $natSpec = $t1GatewayNatService.help.patch.policy_nat_rule.Create()
    $natSpec.id = $natDisplayName
    $natSpec.display_name = $natDisplayName
    $natSpec.action = $action
    $natSpec.destination_network = $destination_networks
    $natSpec.translated_network = $translated_networks
    $natRule = $t1GatewayNatService.patch($T1GatewayName, 'USER', $ruleID, $natSpec)
    Log ("Created Tier-1 Gateway NAT Rule ...")
}

function createSegment($n, $SegmentName, $T1GatewayName, $GatewayCIDR, $TransportZone) {
    $segments = Get-NsxtPolicyService -Server $n -Name "com.vmware.nsx_policy.infra.segments"
    $t1s = Get-NsxtPolicyService -Server $n -Name "com.vmware.nsx_policy.infra.tier1s"
    $tzs = Get-NsxtPolicyService -Server $n -name "com.vmware.nsx_policy.infra.sites.enforcement_points.transport_zones" 

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
    Log "Created Segment $SegmentName ..."
}

function createGroupCondition($n, $GroupName, $MemberType, $Key, $Operator, $Value, $CriteriaType) {
    $groups = Get-NsxtPolicyService -Server $n -Name "com.vmware.nsx_policy.infra.domains.groups"

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
    Log "Created Group $GroupName ..."
}

function createGroupIPExpression($n, $GroupName, $ip_addresses) {
    $groups = Get-NsxtPolicyService -Server $n -Name "com.vmware.nsx_policy.infra.domains.groups"

    $groupSpec = $groups.help.patch.group.Create()
    $groupSpec.id = $GroupName
    $groupSpec.display_name = $GroupName
	
    $expressionSpec = $groups.help.patch.group.expression.Element.IP_address_expression.Create()
    $expressionSpec.ip_addresses = $ip_addresses
    $groupSpec.expression.Add($expressionSpec) | Out-Null
	
    $groups.patch('default', $GroupName, $groupSpec)
    Log "Created Group $GroupName ..."	
}

function createDFWSecurityPolicy($n, $PolicyName, $Category, $RuleName, $SourceGroups, $DestinationGroups, $ServiceList, $Scope, $Action) {
    $policies = Get-NsxtPolicyService -Server $n -Name "com.vmware.nsx_policy.infra.domains.security_policies"
    $groups = Get-NsxtPolicyService -Server $n -Name "com.vmware.nsx_policy.infra.domains.groups"
    $services = Get-NsxtPolicyService -Server $n -Name "com.vmware.nsx_policy.infra.services"

    $sourcePath = @()
    foreach ($name in $SourceGroups) {
        if ($name -eq "ANY") {
            $sourcePath = @("ANY")
        } else {
            $g = ($groups.list('default').results | where {$_.display_name -eq $name})
            $sourcePath = $sourcePath + $g.path
        }
    }

    $destPath = @()
    foreach ($name in $DestinationGroups) {
        if ($name -eq "ANY") {
            $destPath = @("ANY")
        } else {
            $g = ($groups.list('default').results | where {$_.display_name -eq $name})
            $destPath = $destPath + $g.path
        }
    }

    $servicePath = @()
    $full_list = $services.list().results
    foreach ($name in $ServiceList) {
        if ($name -eq "ANY") {
            $servicePath = @("ANY")
        } else {
            $s = ($full_list | where {$_.display_name -eq $name})
            $servicePath = $servicePath + $s.path
        }
    }
	
    $scopePath = @()
    foreach ($name in $Scope) {
        if ($name -eq "ANY") {
            $scopePath = @("ANY")
        } else {
            $g = ($groups.list('default').results | where {$_.display_name -eq $name})
            $scopePath = $scopePath + $g.path
        }
    }

    $policySpec = $policies.help.patch.security_policy.Create()
    $policySpec.display_name = $PolicyName
    $policySpec.id = $PolicyName -replace '\s',''
    $policySpec.category = $Category

    $ruleSpec = $policies.help.patch.security_policy.rules.Element.create()
    $ruleSpec.display_name = $RuleName
    $ruleSpec.id = $RuleName -replace '\s',''
    $ruleSpec.source_groups = $sourcePath
    $ruleSpec.destination_groups = $destPath
    $ruleSpec.services = $servicePath
    $ruleSpec.action = $Action
    $ruleSpec.scope = $scopePath
    $policySpec.rules.Add($ruleSpec) | Out-Null
    Log "Created DFW Policy $PolicyName with Rule $RuleName ..."
    $policies.patch('default', $PolicyName, $policySpec)
}

Log ("Connecting to NSX Manager... Please Wait")
$n = Connect-NsxtServer -Server $nsx_ip -User $nsx_user -Password $nsx_password
Log ("Connected to NSX Manager")

if ($args[0] -eq "delete") {
    $policies = Get-NsxtPolicyService -Server $n -Name "com.vmware.nsx_policy.infra.domains.security_policies"
    $groups = Get-NsxtPolicyService -Server $n -Name "com.vmware.nsx_policy.infra.domains.groups"
    $segments = Get-NsxtPolicyService -Server $n -Name "com.vmware.nsx_policy.infra.segments"
	$nats = Get-NsxtPolicyService -Server $n -Name "com.vmware.nsx_policy.infra.tier_1s.nat.nat_rules"
    $ls = Get-NsxtPolicyService -Server $n -Name "com.vmware.nsx_policy.infra.tier_1s.locale_services"
    $t1s = Get-NsxtPolicyService -Server $n -Name "com.vmware.nsx_policy.infra.tier1s"

    $PCLIPolicies = @("Management Access", "2Tier App")
    $PCLIGroups = @("DB-VM-Group", "Web-VM-Group", "Mgmt-IP-ipset")
	$PCLINats = @("NAT-WEB01")
    $PCLILS = @("default")
    $PCLISegments = @("db-seg", "web-seg")
    $PCLIT1s = @("T1-Paris")

    foreach ($item in $PCLIPolicies) {
        $p = ($policies.list('default').results | where {$_.display_name -eq $item})
        if ($p) {
            $policies.delete('default', $p.id)
            Log "Deleted SecurityPolicy $item ..."
        }
    }
    start-sleep -s 10

    foreach ($item in $PCLIGroups) {
        $g = ($groups.list('default').results | where {$_.display_name -eq $item})
        if ($g) {
            $groups.delete('default', $g.id)
            Log "Deleted Group $item ..."
        }
    }
    start-sleep -s 10

    foreach ($item in $PCLISegments) {
        $s = ($segments.list().results | where {$_.display_name -eq $item})
        if ($s) {
            $segments.delete($s.id)
            Log "Deleted Segment $item ..."
        }
    }
    start-sleep -s 10

    foreach ($item in $PCLINats) {
        $n = ($nats.list('T1-Paris', 'USER').results | where {$_.display_name -eq $item})
		if ($n) {
            $nats.delete('T1-Paris', 'USER', $n.id)
            Log "Deleted NAT $item ..."
        }	
    }
    start-sleep -s 10

    foreach ($item in $PCLILS) {
        $l = ($ls.list('T1-Paris').results | where {$_.display_name -eq $item})
        if ($l) {
            $ls.delete('T1-Paris',$l.id)
        }
    }
    start-sleep -s 10

    foreach ($item in $PCLIT1s) {
        $t1 = ($t1s.list().results | where {$_.display_name -eq $item})
        if ($t1) {
            $t1s.delete($t1.id)
            Log "Deleted Tier1 Gateway $item ..."
        }
    }
    start-sleep -s 10
} else {

    createT1 $n "T1-Paris" $tier0_name $edge_cluster_name
    createT1NATRule $n "T1-Paris" "NAT-WEB01" "DNAT" "88.88.88.88" "172.16.10.11" "nat-rule"

    createSegment $n "web-seg" "T1-Paris" "172.16.10.1/24" "nsx-overlay-transportzone"
    createSegment $n "db-seg" "T1-Paris" "172.16.20.1/24" "nsx-overlay-transportzone"

    createGroupCondition $n "DB-VM-Group" "VirtualMachine" "Name" "STARTSWITH" "DB"
    createGroupCondition $n "Web-VM-Group" "VirtualMachine" "Name" "STARTSWITH" "Web"
    createGroupIPExpression $n "Mgmt-IP-ipset" @("192.168.110.10")

    createDFWSecurityPolicy $n "Management Access" "Infrastructure" "Management SSH + ICMP" @("Mgmt-IP-ipset") @("DB-VM-Group", "Web-VM-Group") @("SSH", "ICMP ALL") @("DB-VM-Group", "Web-VM-Group") "ALLOW"
    createDFWSecurityPolicy $n "2Tier App" "Application" "Any to Web" @("ANY") @("Web-VM-Group") @("ICMP ALL", "HTTPS") @("DB-VM-Group", "Web-VM-Group") "ALLOW"
    createDFWSecurityPolicy $n "2Tier App" "Application" "Web to DB" @("Web-VM-Group") @("DB-VM-Group") @("MYSQL") @("DB-VM-Group", "Web-VM-Group") "ALLOW"
    createDFWSecurityPolicy $n "2Tier App" "Application" "Deny All" @("ANY") @("ANY") @("ANY") @("Web-VM-Group", "DB-VM-Group") "REJECT"
}

