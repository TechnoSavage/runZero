[AWS](https://github.com/TechnoSavage/runZero/blob/main/attributes_by_integration.md#AWS)

[Crowdstrike](https://github.com/TechnoSavage/runZero/blob/main/attributes_by_integration.md#Crowdstrike)

[Defender](https://github.com/TechnoSavage/runZero/blob/main/attributes_by_integration.md#Defender)

[Rapid7](https://github.com/TechnoSavage/runZero/blob/main/attributes_by_integration.md#Rapid7)

[SCCM/MECM](https://github.com/TechnoSavage/runZero/blob/main/attributes_by_integration.md#SCCM-MECM)

[Tanium](https://github.com/TechnoSavage/runZero/blob/main/attributes_by_integration.md#Tanium)

[Tenable](https://github.com/TechnoSavage/runZero/blob/main/attributes_by_integration.md#Tenable)

[Qualys](https://github.com/TechnoSavage/runZero/blob/main/attributes_by_integration.md#Qualys)

[ServiceNow](https://github.com/TechnoSavage/runZero/blob/main/attributes_by_integration.md#ServiceNow)

# Inbound

## AWS

### ec2

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

## Crowdstrike

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

## Rapid7

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

# Outbound

## ServiceNow 

### From runZero SNOW API to ServiceGraph Connector

```
addresses_extra
addresses_scope
alive
asset_id
comments
detected_by_domains
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