# Asset Queries:

## Assets where both OS support and extended support are expired
```
os_eol:<now AND os_eol_extended:<now
```

## Assets where OS support is EOL but still covered by extended support
```
os_eol:<now AND os_eol_extended:>now
```
## EOL Linux operating systems
```
os:linux AND os_eol:<now
```
## EOL Windows operating systems
```
os:windows AND os_eol:<now
```

## Assets discovered within the past two weeks
```
first_seen:"<2weeks"
```

## Windows assets offering SMB services
```
os:windows AND protocol:smb1 OR protocol:smb2
```

## Assets created as a result of arbitrary responses (e.g. Firewall)
```
has_mac:f AND has_name:f AND os:= AND hardware:= AND detected_by:icmp AND service_count:<2
```
## Assets with Microsoft FTP server
```
alive:t AND protocol:"ftp" AND banner:"=%Microsoft FTP%”
```

## Assets with public IPs and remote access protocols
```
has_public:t OR has_public:t AND alive:t AND (protocol:rdp OR protocol:vnc OR protocol:teamviewer)
```

## Assets offering remote access protocols
```
protocol:rdp OR protocol:vnc OR protocol:teamviewer OR protocol:ssh OR protocol:telnet
```

## Assets with open ports associated with clear text protocols
```
port:21 OR port:23 OR port:80 OR port:139 OR port:445 OR port:3306 OR port:1433 OR port:161 OR port:8080 OR port:3389 OR port:5900
```

## Multi-homed assets connected only to private networks
```
multi_home:t AND has_public:f
```

## Multi-homed assets connected to private and public networks
```
alive:t AND has_public:t AND has_private:t
```
## Assets with serial numbers from SNMP
```
protocol:snmp has:snmp.serialNumbers
```

## Switch assets accepting Username and Password authentication over HTTP
```
type:switch AND (_asset.protocol:http AND NOT _asset.protocol:tls) AND ( html.inputs:"password:" OR last.html.inputs:"password:" OR has:http.head.wwwAuthenticate OR has:last.http.head.wwwAuthenticate )`
```

## All available serial number sources
```
protocol:snmp has:snmp.serialNumbers OR hw.serialNumber:t OR ilo.serialNumber:t
```

## Assets that are virtual machines
```
attribute:virtual
```

## Assets that are Azure, AWS EC2, or GCP, virtual machines
```
virtual:azure OR virtual:ec2 OR virtual:gcp
```

## Assets that are VMware, or Hyper-V, or Xen virtual machines
```
virtual:vmware OR virtual:"Hyper-V" OR virtual:xen
```

## Assets not managed by a Microsoft product
```
source:runzero AND NOT (source:ms365defender OR source:intune OR source:azuread)
```

## Assets more than 8 hops away:
```
attribute:"ip.ttl.hops" AND ip.ttl.hops:>"8"
```

## Assets first seen within the past two weeks:
```
first_seen:<"2weeks"
```

## Assets created in the inventory within the last two weeks:
```
created_at:<"2weeks"
```

## Assets last seen over two weeks ago:
```
last_seen:>"2weeks" 
```

## Assets last updated over two weeks ago:
```
updated_at:>"2weeks"
```

## Assets that (likely) have Tanium Client installed and running
```
alive:t AND port:17472 AND (type:server OR type:desktop OR type:laptop)
```

## Assets missing either Crowdstrike or SentinelOne EDR agents
```
NOT edr.name:Crowdstrike AND (type:server OR type:desktop OR type:laptop) OR NOT edr.name:Sentinelone AND (type:server OR type:desktop OR type:laptop)
```

## Assets that could be managed by Miradore MDM but are not currently
```
NOT miradore.name:"%" AND (type:desktop OR type:laptop OR type:mobile)
```

## Assets with Crowdstrike Agent status "Not Provisioned"
```
@crowdstrike.dev.provisionStatus:"NotProvisioned"
```

## Assets with Crowdstrike Agent mode "Reduced Functionality"
```
@crowdstrike.dev.reducedFunctionalityMode:"yes"
```

## Assets with Crowdstrike Agent status "Normal"
```
@crowdstrike.dev.status:"normal"
```

## Assets with SentinelOne Agent requiring patch
```
(alive:t OR scanned:f) AND has:"@sentinelone.dev.appsVulnerabilityStatus" AND @sentinelone.dev.appsVulnerabilityStatus:"=patch_required"
```

## Assets that have the Tenable agent installed
```
@tenable.dev.hasAgent:="true"
```

## Assets that have been scanned by Tenable over 2 weeks ago
```
@tenable.dev.lastScanTimeTS:>"2weeks"
```

## Assets scanned by Tenable over an 8 ACR (asset cirticality rating) score:
```
(alive:t OR scanned:f) AND has:"@tenable.dev.acrScore" AND @tenable.dev.acrScore:"=8"
```

## Assets where last Rapid7 scan concluded over 2 weeks ago
```
@rapid7.dev.report.endTimeTS:">2weeks"
```

## Assets that have been scanned by Qualys over 2 weeks ago
```
@qualys.dev.host.lastScannedDateTimeTS:">2weeks"
```

## Assets where Google Workspace reports developer options are enabled
```
@googleworkspace.endpoint.enabledDeveloperOptions:="true"
```

## Assets where Google Workspace reports USB debugging is enabled
```
@googleworkspace.endpoint.enabledUsbDebugging:="true"
```

## Linux VMs
```
os:Linux AND (source:VMware or attribute:virtual)
```

## Windows VMs
```
os:Windows AND (source:VMware or attribute:virtual)
```

## VMs not syncing time with host
```
@vmware.vm.config.tools.syncTimeWithHost:"=false"
```

## VMs where VMware tools are not installed
```
@vmware.vm.config.extra.guestinfo.vmtools.versionString:”_”
```

## VMs with less than 16GB of memory
```
@vmware.vm.runtime.maxMemoryUsage:"16384"
```

## VMs set to floppy0 autodetect
```
@vmware.vm.config.extra.floppy0.autodetect:"true”
```

## BACnet devices
```
type:bacnet
```

## Hikvision DVRs
```
type:dvr AND os:hikvision
```

## IoT Devices
```
type:"IP Camera" OR type:"thermostat" OR type:"Amazon Device" OR hw:"Google Chromecast" OR type:"Game Console" OR type:"Robotic Cleaner" OR type:"Nest Device" OR type:"Network Audio" OR type:"Smart TV" OR type:"VR Headset" OR type:"Voice Assistant""
```

## Video related assets
```
type:"IP Camera" OR type:"DVR" OR type:"Video Encoder"
```

## IP Cameras with possible publicly exposed video streams or login pages:
```
type:"ip camera" AND has_public:t AND (protocol:rtsp OR protocol:http)
```

# Service Queries:

## Online assets with SSH accepting password authentication
```
alive:t AND has:"ssh.authMethods" AND protocol:"ssh" AND (ssh.authMethods:"=password" OR ssh.authMethods:"=password%publickey")
```

## Telnet running on non-standard port
```
protocol:telnet AND NOT port:23
```

## SSH version predating 2.0
```
protocol:ssh AND (banner:"%1.0%" OR banner:"%1.5-" OR banner:"1.99")
```

## Detect OpenSSL version 3.0
```
_service.product:="OpenSSL:OpenSSL:3.0"
```

## PHP websites
```
product:php OR banner:"%php%" OR cookie:phpsessid OR html.forms:"%.php" OR http.body:"%php%" OR http.head.location:"%.php" OR http.head.setCookie:"%phpsessid%" OR last.http.uri:"%.php" OR last.http.body:"%php%" OR last.html.forms:"%.php"
```

## RDP Authentication detected on external or v6 IP:
```
protocol:rdp and (rdp.auth.rdp:supported or rdp.auth.ssl:supported or rdp.auth.sspeua:supported or rdp.auth.tls:supported) and (has_public:t or has_ipv6:t)
```

## Cisco devices with loopback interface configured:
```
snmp.arpcache.ports:"lo"
```

## Cisco device with specific IP assigned to loopback interface:
```
snmp.arpcache.ports:"lo" and snmp.interfaceAddrs:"<loopback IP>"
```
e.g.
```
snmp.arpcache.ports:"lo" and snmp.interfaceAddrs:"192.168.100.1"
```
```
snmp.arpcache.ports:"lo" and snmp.interfaceAddrs:"192.168.100.1/255.255.255.0"
```

# Software Queries:

## Detect OpenSSL version 3.0
```
product:openssl AND version:3.0
```

## Assets with SQL databases
```
product:sql OR product:mariadb OR product:oracledb
```

# Vulnerability Queries:

## Rapid7 - fails PCI compliance
```
test.pciComplianceStatus:"fail"
```

## Tenable - High and Critical severity vulnerabilities that are on CISA's Known Exploited list
```
plugin.xrefs.type:"CISA-KNOWN-EXPLOITED" AND (severity:high OR severity:critical)
```

## Tenable - Critical severity vulnerabilities where exploits are avaialable
```
plugin.exploitabilityEase:"Exploits are available" AND severity:critical
```

## Tenable - High and Critical severity vulnerabilities where exploits are not required
```
plugin.exploitabilityEase:"No exploit is required" AND (severity:critical OR severity:high)
```

## Tenable - Query on VPR score (equal to, greater than, or less than)
```
plugin.vpr.score:"6.0" 
```
```
plugin.vpr.score:>"6.0"
```
```
plugin.vpr.score:<"6.0"
```

## Tenable - Vulnerability has an available patch 
```
plugin.hasPatch:"true"
```

## Qualys - Easy to exploit vulnerabilities
```
vulnerability.threatIntel:"%Easy_Exploit%"
```

## Qualys - vulnerabilities with publicly available exploits
```
vulnerability.threatIntel:"%Exploit_Public%"	
```

## Qualys - vulnerabilities enabling lateral movement
```
vulnerability.threatIntel:"%High_Lateral_Movement%"
```

## Qualys - high data loss vulnerabilities 
```
vulnerability.threatIntel:"%High_Data_Loss%"
```

## Qualys - vulnerabilities that enable DoS
```
vulnerability.threatIntel:"%Denial_of_Service%"
```

## Qualys - high risk vulnerabilities 
```
vulnerability.threatIntel:"%Predicted_High_Risk%"
```

## Qualys - vulnerabilities that allow for unauthenticated exploit
```
vulnerability.threatIntel:"%unauthenticated_Exploitation%"
```

## Qualys - vulnerabilities that allow RCE
```
vulnerability.threatIntel:"%Remote_Code_Execution%"
```

## Qualys - vulnerabilities that are wormable
```
vulnerability.threatIntel:"%Wormable%"
```

## Qualys - Ransomware
```
vulnerability.threatIntel:"%Ransomware%"
```

## Qualys - High and Critical severity vulnerabilities that are on CISA's Known Exploited list
```
vulnerability.threatIntel:"%Cisa_Known_Exploited_Vulns%"
```

## Qualys - assets with Qualys endpoint agent installed:
```
@qualys.dev.host.trackingMethod:="AGENT"
```

## Qualys - Reported by Qualys but do not have the endpoint agent installed
```
source:qualys and not @qualys.dev.host.trackingMethod:="AGENT"
```

## Qualys - Reported by qualys and found via vuln scan
```
@qualys.dev.host.trackingMethod:="IP"
```

## Qualys - Endpoints that could host a Qualys endpoint agent but do not have one installed
```
not @qualys.dev.host.trackingMethod:="AGENT" and (type:server or type:laptop or type:desktop)
```

# Wireless Queries:

## Search ESSID for authentication exceptions:
```
essid:<ssid name> AND NOT authentication:<wifi security standard>
```
e.g.
```
essid:"Corporate_network" AND NOT authentication:"wpa2-enterprise"
```

## Find unknown BSSIDs broadcasting known ESSID (exclude known BSSIDs in query for gap analysis)
```
essid:="2WIRE640" AND NOT (bssid:"14:ed:bb:e0:99:1d" OR bssid:"15:ea:cd:e4:78:2f")
```
