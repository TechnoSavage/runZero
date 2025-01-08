[Active Directory](https://github.com/TechnoSavage/runZero/blob/main/attributes_by_integration.md#active-directory)

[AWS](https://github.com/TechnoSavage/runZero/blob/main/attributes_by_integration.md#aws)

[Azure](https://github.com/TechnoSavage/runZero/blob/main/attributes_by_integration.md#azure)

[Censys](https://github.com/TechnoSavage/runZero/blob/main/attributes_by_integration.md#censys)

[Crowdstrike](https://github.com/TechnoSavage/runZero/blob/main/attributes_by_integration.md#crowdstrike)

[Defender](https://github.com/TechnoSavage/runZero/blob/main/attributes_by_integration.md#defender)

[Google Cloud](https://github.com/TechnoSavage/runZero/blob/main/attributes_by_integration.md#google-cloud)

[Google Workspace](https://github.com/TechnoSavage/runZero/blob/main/attributes_by_integration.md#google-workspace)

[Miradore](https://github.com/TechnoSavage/runZero/blob/main/attributes_by_integration.md#miradore)

[Nessus](https://github.com/TechnoSavage/runZero/blob/main/attributes_by_integration.md#nessus)

[Rapid7](https://github.com/TechnoSavage/runZero/blob/main/attributes_by_integration.md#rapid7)

[SCCM/MECM](https://github.com/TechnoSavage/runZero/blob/main/attributes_by_integration.md#sccm-mecm)

[SentinelOne](https://github.com/TechnoSavage/runZero/blob/main/attributes_by_integration.md#sentinelone)

[Shodan](https://github.com/TechnoSavage/runZero/blob/main/attributes_by_integration.md#shodan)

[Tanium](https://github.com/TechnoSavage/runZero/blob/main/attributes_by_integration.md#tanium)

[Tenable](https://github.com/TechnoSavage/runZero/blob/main/attributes_by_integration.md#tenable)

[Qualys](https://github.com/TechnoSavage/runZero/blob/main/attributes_by_integration.md#qualys)

[Wiz](https://github.com/TechnoSavage/runZero/blob/main/attributes_by_integration.md#wiz)

[ServiceNow](https://github.com/TechnoSavage/runZero/blob/main/attributes_by_integration.md#servicenow)

# Inbound

## Active Directory

### (@ldap.computer)

```
badPwdCount
cn
codePage
countryCode
dNSHostName
description
distinguishedName
id
instanceType
isCriticalSystemObject
lastLogonTS
lastLogonTimestampTS
localPolicyFlags
logonCount
memberOf
name
objectCategory
objectClass
objectGUID
objectSid
operatingSystem
operatingSystemVersion
primaryGroupID
pwdLastSetTS
sAMAccountName
sAMAccountType
ts
userAccountControl
userCertificate
whenChangedTS
whenCreatedTS
```

## AWS

### ec2 (@aws.ec2)

```
accountID
architecture
availabilityZone
hypervisor
id
imageID
instanceID
instanceLifecycle
instanceType
ipv4
ipv6
keyName
launchTimeTS
macs
privateDNS
privateIP
publicDNS
publicIP
region
rootDeviceName
rootDeviceType
spotInstanceRequestID
subnetID
tags
tenancy
ts
type
virtualizationType
vpcID
```

## Azure

### VMs (@azure.vmss)

```
clientID
hardwareProfile.vmSize
id
ipConfigurations.names
ipv4
keyNames
loadBalancers.names
location
macs
name
networkInterfaceConfigurations.0.ipConfigurations.0.name
networkInterfaceConfigurations.0.name
networkInterfaceConfigurations.names
osProfile.adminUsername
osProfile.computerName
privateIP
resourceGroup
scaleSet
state
storageProfile.imageReference.exactVersion
storageProfile.imageReference.offer
storageProfile.imageReference.publisher
storageProfile.imageReference.sku
storageProfile.imageReference.version
storageProfile.osDisk.caching
storageProfile.osDisk.createOption
storageProfile.osDisk.diskSizeGB
storageProfile.osDisk.managedDisk.id
storageProfile.osDisk.managedDisk.storageAccountType
storageProfile.osDisk.name
storageProfile.osDisk.osType
subnetID
subscriptionID
tenantID
ts
type
vmID
```

### LBs (@azure.lb)

```
backendAddressPools.0.loadBalancerBackendAddress.0.name
backendAddressPools.0.loadBalancerBackendAddress.1.name
backendAddressPools.0.name
backendAddressPools.names
clientID
frontendIPConfigurations.0.name
frontendIPConfigurations.0.privateIPAllocationMethod
frontendIPConfigurations.names
id
inboundNATPools.0.backendPort
inboundNATPools.0.frontendPortRangeEnd
inboundNATPools.0.frontendPortRangeStart
inboundNATPools.0.name
inboundNATPools.0.protocol
inboundNATPools.names
inboundNATRules.0.backendPort
inboundNATRules.0.frontendPort
inboundNATRules.0.name
inboundNATRules.0.protocol
inboundNATRules.1.backendPort
inboundNATRules.1.frontendPort
inboundNATRules.1.name
inboundNATRules.1.protocol
inboundNatRules.names
ipv4
loadBalancingRules.0.backendPort
loadBalancingRules.0.frontendPort
loadBalancingRules.0.loadDistribution
loadBalancingRules.0.name
loadBalancingRules.0.protocol
loadBalancingRules.names
location
macs
name
probes.0.name
probes.0.port
probes.0.protocol
probes.names
provisioningState
publicIP
resourceGUID
resourceGroup
sku.name
sku.tier
subscriptionID
tenantID
ts
type
```

## Azure AD

### ()

## Censys

### (@censys.host)

```
address
addresses
asUpdatedAtTS
asn.bgpPrefix
asn.countryCode
asn.description
asn.name
asn.number
dns.names
id
lastUpdatedAtTS
location.city
location.continent
location.coordinates.latitude
location.coordinates.longitude
location.country
location.countryCode
location.postalCode
location.province
location.registeredCountry
location.registeredCountryCode
location.timezone
locationUpdatedAtTS
match.criteria
os.part
os.product
os.source
os.uniformResourceIdentifier
ts
```

## Crowdstrike

### (@crowdstrike.dev)

```
agentLoadFlags
agentLocalTime
agentVersion
biosManufacturer
biosVersion
buildNumber
cid
configIDBase
configIDBuild
configIDPlatform
deviceID
externalIP
firstLoginTS
firstLoginUser
firstSeen
groupHash
hostname
id
instanceID
lastInteractiveTS
lastInteractiveUser
lastLoginTS
lastLoginUser
lastLogins
lastSeen
localIP
macAddress
majorVersion
match.criteria
meta.version
minorVersion
modifiedTS
osVersion
platformID
platformName
pointerSize
productType
productTypeDesc
provisionStatus
reducedFunctionalityMode
serialNumber
servicePackMajor
servicePackMinor
serviceProvider
serviceProviderAccountID
status
systemManufacturer
systemProductName
ts
```

## Defender

### (@ms365defender.dev)

```
agentVersion
computerDNSName
defenderAVStatus
deviceValue
exposureLevel
firstSeen
healthStatus
id
ip
ips
isAADJoined
lastSeen
machineTags
macs
managedBy
managedByStatus
onboardingStatus
osArchitecture
osBuild
osPlatform
osProcessor
publicIP
riskScore
version
```

## Google Cloud

### VMs (@gcp.vm)

```
canIPForward
clientID
confidentialInstanceConfig.enableConfidentialCompute
cpuPlatform
creationTimestamp
deletionProtection
disks.0.autoDelete
disks.0.boot
disks.0.deviceName
disks.0.diskSizeGb
disks.0.guestOsFeatures.types
disks.0.index
disks.0.interface
disks.0.kind
disks.0.licenses
disks.0.mode
disks.0.source
disks.0.type
displayDevice.enableDisplay
id
ipv4
kind
lastStartTimestamp
machineType
match.criteria
metadata.kind
name
projectID
reservationAffinity.consumeReservationType
scheduling.automaticRestart
scheduling.onHostMaintenance
scheduling.preemptible
selfLink
serviceAccounts.0.email
serviceAccounts.0.scopes
shieldedInstanceConfig.enableIntegrityMonitoring
shieldedInstanceConfig.enableSecureBoot
shieldedInstanceConfig.enableVtpm
shieldedInstanceIntegrityPolicy.updateAutoLearnPolicy
startRestricted
status
ts
type
zone
```

### LBs (@gcp.lb)

```
clientID
creationTimestamp
defaultBackendService
defaultBackendService.backends.0.balancingMode
defaultBackendService.backends.0.capacityScaler
defaultBackendService.backends.0.maxUtilization
defaultBackendService.connectionDraining.drainingTimeoutSec
defaultBackendService.creationTimestamp
defaultBackendService.enableCDN
defaultBackendService.fingerprint
defaultBackendService.id
defaultBackendService.kind
defaultBackendService.loadBalancingScheme
defaultBackendService.logConfig.enable
defaultBackendService.name
defaultBackendService.port
defaultBackendService.portName
defaultBackendService.protocol
defaultBackendService.selfLink
defaultBackendService.sessionAffinity
defaultBackendService.timeoutSec
defaultService
fingerprint
forwardingRule.creationTimestamp
forwardingRule.fingerprint
forwardingRule.id
forwardingRule.ipprotocol
forwardingRule.ipversion
forwardingRule.kind
forwardingRule.labelFingerprint
forwardingRule.loadBalancingScheme
forwardingRule.name
forwardingRule.networkTier
forwardingRule.portRange
forwardingRule.selfLink
forwardingRule.target
httpProxy.creationTimestamp
httpProxy.fingerprint
httpProxy.id
httpProxy.kind
httpProxy.name
httpProxy.selfLink
httpProxy.urlmap
id
ipv4
kind
match.criteria
name
projectID
selfLink
ts
```

### DBs (@gcp.cloudsql)

```
addresses
backendType
clientID
connectionName
createTime
currentDiskSize
databaseInstalledVersion
databaseVersion
etag
gceZone
id
instanceType
ipAddress.0.ipAddress
ipAddress.0.type
kind
maintenanceVersion
match.criteria
maxDiskSize
name
project
projectID
region
satisfiesPzs
selfLink
serverCaCert.certSerialNumber
serverCaCert.commonName
serverCaCert.createTime
serverCaCert.expirationTime
serverCaCert.instance
serverCaCert.kind
serverCaCert.sha1Fingerprint
serviceAccountEmailAddress
settings.activationPolicy
settings.availabilityType
settings.backupConfiguration.backupRetentionSettings.retainedBackups
settings.backupConfiguration.backupRetentionSettings.retentionUnit
settings.backupConfiguration.binaryLogEnabled
settings.backupConfiguration.enabled
settings.backupConfiguration.kind
settings.backupConfiguration.pointInTimeRecoveryEnabled
settings.backupConfiguration.replicationLogArchivingEnabled
settings.backupConfiguration.startTime
settings.backupConfiguration.transactionLogRetentionDays
settings.crashSafeReplicationEnabled
settings.dataDiskSizeGb
settings.dataDiskType
settings.databaseReplicationEnabled
settings.ipConfiguration.ipv4Enabled
settings.ipConfiguration.privateNetwork
settings.ipConfiguration.requireSsl
settings.kind
settings.locationPreference.kind
settings.locationPreference.zone
settings.maintenanceWindow.day
settings.maintenanceWindow.hour
settings.maintenanceWindow.kind
settings.pricingPlan
settings.replicationType
settings.storageAutoResize
settings.storageAutoResizeLimit
settings.tier
state
ts
```

## Google Workspace

### Endpoints (@googleworkspace.endpoint)

```
android.enabledUnknownSources
android.ownerProfileAccount
android.supportsWorkProfile
clientTypes
createdTS
deviceType
email
email.names
email.uid
enabledDeveloperOptions
enabledUsbDebugging
encryptionState
hostname
id
lastSyncTS
model
osVersion
ownerType
releaseVersion
resourceName
securityPatchTS
serialNumber
ts
```

### Mobile (@googleworkspace.mobile)

```
adbStatus
developerOptionsStatus
deviceCompromisedStatus
devicePasswordStatus
email
email.names
email.uid
encryptionStatus
etag
firstSyncTS
id
kind
lastSyncTS
managedAccountIsOnOwnerProfile
model
os
owner
privilege
releaseVersion
resourceId
securityPatchLevel
status
supportsWorkProfile
ts
type
unknownSourcesStatus
```

## Intune

### (@intune.dev)

```
azureADDeviceID
azureADRegistered
complianceGracePeriodExpirationDateTimeTS
complianceState
deviceCategoryDisplayName
deviceEnrollmentType
deviceName
deviceRegistrationState
easActivated
easActivationDateTimeTS
easDeviceID
enrolledDateTimeTS
exchangeAccessState
exchangeAccessStateReason
exchangeLastSuccessfulSyncDateTimeTS
freeStorageSpaceInBytes
id
isEncrypted
isSupervised
jailBroken
lastSyncDateTimeTS
managedDeviceName
managedDeviceOwnerType
managementAgent
manufacturer
model
operatingSystem
osVersion
partnerReportedThreatState
physicalMemoryInBytes
serialNumber
totalStorageSpaceInBytes
ts
userDisplayName
userID
userPrincipalName
wiFiMacAddress
```

## Miradore

### (@miradore.dev)

```
createdAt
device.bluetoothMAC
device.deviceName
device.deviceType
device.manufacturer
device.model
device.productName
device.serialNumber
device.softwareVersion
device.storeAccountActive
device.udid
device.wifiMAC
id
ip
lastReportedAt
mac
os.language
os.platform
os.version
osVersionName
platform
status
ts
user.email
user.name
```

## Nessus

### (@nessus.dev)

```
firstSeenTS
fqdns
id
ipv4s
lastScanTimeTS
lastSeenTS
macAddresses
match.criteria
operatingSystems
policyUsed
scannedIPv4s
systemTypes
traceroute
ts
```

## Rapid7

### (@rapid7.dev)

```
id
node.address
node.deviceID
node.hardwareAddress
node.macPairs
node.names
node.riskScore
node.scanTemplate
node.siteImportance
node.siteName
node.status
os.arch
os.certainty
os.deviceClass
os.family
os.product
os.vendor
os.version
report.endTimeTS
report.startTimeTS
report.version
ts
```

## SCCM-MECM

```
adLastLogonTime
adSiteName
architectureKey
atpOnboardingState
boundaryGroups
clientActiveStatus
clientCertType
clientCheckPass
clientEdition
clientState
clientType
clientVersion
cnAccessMP
cnIsOnInternet
cnIsOnline
cnLastOfflineTime
cnLastOnlineTime
coManaged
deviceOS
deviceOSBuild
deviceOwner
domain
epDeploymentState
id
ipAddress
isAOACCapable
isActive
isAlwaysInternet
isApproved
isBlocked
isClient
isInternetEnabled
isObsolete
isVirtualMachine
lastActiveTime
lastClientCheckTime
lastDDR
lastHardwareScan
lastMPServerName
lastPolicyRequest
lastStatusMessage
macAddress
machineID
managementAuthority
match.criteria
name
serialNumber
siteCode
smbiosGUID
smsID
ts
```

## SentinelOne

### (@sentinelone.dev)

```
accountID
accountName
activeThreats
agentVersion
allowRemoteShell
appsVulnerabilityStatus
cloudProviders
computerName
consoleMigrationStatus
coreCount
cpuCount
cpuID
createdAtTS
domain
encryptedApplications
externalIP
firewallEnabled
firstFullModeTimeTS
gateways
groupID
groupIP
groupName
groupUpdatedAtTS
id
inRemoteShellSession
infected
installerType
ips
isActive
isDecommissioned
isPendingUninstall
isUninstalled
isUpToDate
lastActiveDateTS
lastIPToMgmt
lastLoggedInUserName
licenseKey
location.ids
location.names
locationEnabled
locationType
machineType
macs
mitigationMode
mitigationModeSuspicious
modelName
networkQuarantineEnabled
networkStatus
operationalState
operationalStateExpirationTS
osArch
osName
osRevision
osStartTimeTS
osType
osUsername
policyUpdatedAtTS
rangerStatus
rangerVersion
registeredAtTS
remoteProfilingState
remoteProfilingStateExpiration
scanAbortedAtTS
scanFinishedAtTS
scanStartedAtTS
scanStatus
siteID
siteName
threatRebootRequired
totalMemory
ts
updatedAtTS
userActionsNeeded
uuid
```

## Shodan

### (@shodan.dev)

```
host.asn
host.city
host.countryCode
host.countryName
host.domains
host.hostnames
host.ip
host.ipStr
host.isp
host.lastUpdateTS
host.latitude
host.longitude
host.org
host.os
host.ports
host.regionCode
host.tags
host.vulns
id
service.firstFoundTS
service.lastFoundTS
ts
```

## Tanium

```
chassisType
computerID
disks.free
disks.name
disks.total
disks.usedPercentage
disks.usedSpace
domainName
eidFirstSeen
eidLastSeen
id
ipAddress
ipAddresses
isEncrypted
isVirtual
lastLoggedInUser
macAddresses
manufacturer
match.criteria
memory.ram
memory.total
model
name
networking.adapters.connectionID
networking.adapters.macAddress
networking.adapters.manufacturer
networking.adapters.name
networking.adapters.speed
networking.adapters.type
networking.dnsServers
networking.wirelessAdapters.state
os.generation
os.language
os.name
os.platform
os.windows.majorVersion
os.windows.releaseID
os.windows.type
processor.architecture
processor.cacheSize
processor.consumption
processor.cpu
processor.family
processor.logicalProcessors
processor.manufacturer
processor.revision
processor.speed
serialNumber
systemUUID
ts
```

## Tenable

### (@tenable.dev)

```
biosUUID
createdAtTS
firstScanTimeTS
firstSeenTS
fqdns
hasAgent
hasPluginResults
hostnames
id
installedSoftware
ipv4s
ipv6s
lastAuthenticatedScanDateTS
lastLicensedScanDateTS
lastScanID
lastScanTimeTS
lastScheduleID
lastSeenTS
macAddresses
netBIOSNames
networkID
networkName
operatingSystems
policyUsed
scannedIPv4s
sshFingerprints
systemTypes
traceroute
ts
updatedAtTS
```

## Qualys

### (@qualys.dev)

```
detection.firstFoundTS
detection.lastFoundTS
host.dns
host.domain
host.fqdn
host.hostname
host.id
host.ip
host.lastScannedDateTimeTS
host.lastVMAuthScannedDateTS
host.lastVMScannedDateTS
host.netbios
host.networkID
host.os
host.trackingMethod
id
match.criteria
qg.hostID
ts
```

## Wiz

### (@wiz.dev)

```
accessibleFromInternet
atRestEncryption
awsLambdaCodeSHA256
awsLambdaURLConfigs
cloudPlatform
cloudProviderURL
creationDateTS
dns
externalID
hasBackups
hasHighPrivileges
hasSensitiveData
id
ipv4
ipv6
isEphemeral
isManaged
isPaaS
kind
match.criteria
memoryGB
name
nativeType
numAddressesOpenForHTTP
numAddressesOpenForHTTPS
numAddressesOpenForNonStandardPorts
numAddressesOpenToInternet
numPortsOpenToInternet
openToAllInternet
operatingSystem
operatingSystemVersion
providerUniqueID
region
regionLocation
replicaCount
runtime
sizeGB
status
subscriptionExternalID
tags
totalDisks
ts
type
updatedAtTS
validatedOpenPorts
vcpus
version
wafEnabled
```

# Outbound

## ServiceNow 

### From runZero SNOW API to ServiceGraph Connector

```
addresses_extra
addresses_scope
alive
asset_id
comments
detected_by
domains
first_discovered
has_public
hw_version
ip_address
last_discovered
last_updated
lowest_rtt
lowest_ttl
mac_address
mac_manufacturer
mac_vendors
macs
manufacturer
model
name
names
newest_mac_age
organization
os
os_vendor
os_version
serial_numbers
service_count
service_count_arp
service_count_icmp
service_count_tcp
service_count_udp
site
site_id
site_name
snmp_mac_vendor
snmp_sysDesc
snmp_sysName
tags
type
virtual
virtual_type
```

## Splunk

### From runZero Splunk API to Splunk store connector

```
addresses
addresses_extra
agent_name
alive
attributes
comments
created_at
credentials
criticality_rank
custom_integration_ids
detected_by
domains
eol_os
eol_os_ext
first_seen
foreign_attributes
hw
hw_product
hw_vendor
hw_version
id
last_agent_id
last_seen
last_task_id
lowest_rtt
lowest_ttl
mac_vendors
macs
modified_risk_rank
names
newest_mac
newest_mac_age
newest_mac_vendor
org_name
organization_id
os
os_product
os_vendor
os_version
outlier_raw
outlier_score
owners
ownership
risk_rank
scanned
service_count
service_count_arp
service_count_icmp
service_count_tcp
service_count_udp
service_ports_tcp
service_ports_udp
service_products
service_protocols
site_id
site_name
software_count
source_ids
surface_types
tags
type
updated_at
vulnerability_count
```