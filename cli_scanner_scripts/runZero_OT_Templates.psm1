
<#
        .SYNOPSIS
        Conducts a network scan using the runZero CLI scanner and the recommended settings from the OT limited scan template.

        .DESCRIPTION
        Conducts a network scan using the runZero CLI scanner and the recommended settings from the OT limited scan template.
        Details for the scan template can be found at:
        https://help.runzero.com/docs/playbooks/scanning-ot-networks/#step-3a-create-an-ot-limited-scan-template 

        .PARAMETER Input_List
        [Required] Path to a text file containing a list of subnets, IPs, ASNs, and/or Domains to define the scan scope.

        .PARAMETER Scanner_Path
        [Optional] Path to the runZero CLI scanner executable. If this parameter is not set the location of the scanner
        executable is assumed to be in the same directory as this module and is named "runzero-scanner.exe"

        .PARAMETER Communities
        [Optional] Additional SNMP v2 community strings to use during the scan provided as comma-separated strings with no spaces.
        'public' and 'private' community strings are specified by default.
        
        .PARAMETER Output_Path
        [Optional] Path to the runZero CLI scanner output directory. If this parameter is not set the output directory
        set to the present working directory
        
        .EXAMPLE
        PS> Invoke-LimitedOTScan -Input_List \path\to\my\targets.txt -Scanner_Path \path\to\runzero-scanner.exe -Communities foo,bar   
    #>
function Invoke-LimitedOTScan {
    param (
        [Parameter(Mandatory=$true)][string]$Input_List,
        [Parameter(mandatory=$false)][string]$Scanner_Path,
        [Parameter(mandatory=$false)][string]$Communities,
        [Parameter(mandatory=$false)][string]$Output_Path)

    $Comms = "public,private"
    $Ports = "21,22,23,69,80,123,135,137,161,179,443,445,3389,5040,5900,7547,8080,8443,62078,65535"
    $Probes = "connect,layer2,syn,netbios,ntp,snmp,tftp"
    
    # test that input target list exists
    $Exists = Test-Path $Input_List
    If (! ($Exists)) {
        Write-Host "`nProvided path to CLI scanner .exe does not exist."
        Exit
    }

    # Set path to runzero CLI scanner executable to current working directory if not otherwise specified
    If ( ! $Scanner_Path ) {
        $Scanner_Path = "$PWD\runzero-scanner.exe"
    }

    # Set path to runzero CLI scanner output folder to current working directory if not otherwise specified
    If ( ! $Output_Path ) {
        $Output_Path = "$PWD"
    }

    # test that the path to the scanner binary exists
    $Exists = Test-Path $Scanner_Path
    If (! ($Exists)) {
        Write-Host "`nProvided path to CLI scanner .exe does not exist."
        Exit
    }

    # test that the path to the output folder exists
    $Exists = Test-Path $Output_Path
    If (! ($Exists)) {
        Write-Host "`nProvided path to CLI scanner output does not exist."
        Exit
    }

    #Concatenate provided community strings with default public, private
    If ( $Communities) {
        $Comms = "$Comms,$Communities" 
    }
    
    Write-Host "`nPreparing OT Limited scan..."

    & $Scanner_Path -i $Input_List --host-ping -r 300 --max-host-rate 20 --max-ttl 64 --max-group-size 2048 --tcp-ports $Ports --probes $Probes --snmp-comms $Comms -o $Output_Path

    Write-Host "`nScan complete!"
}

<#
        .SYNOPSIS
        Conducts a network scan using the runZero CLI scanner and the recommended settings from the OT limited scan template.

        .DESCRIPTION
        Conducts a network scan using the runZero CLI scanner and the recommended settings from the OT full scan template.
        Details for the scan template can be found at:
        https://help.runzero.com/docs/playbooks/scanning-ot-networks/#step-3b-create-an-ot-full-scan-template

        .PARAMETER Input_List
        [Required] Path to a text file containing a list of subnets, IPs, ASNs, and/or Domains to define the scan scope.

        .PARAMETER Scanner_Path
        [Optional] Path to the runZero CLI scanner executable. If this parameter is not set the location of the scanner
        executable is assumed to be in the same directory as this module and is named "runzero-scanner.exe"

        .PARAMETER Output_Path
        [Optional] Path to the runZero CLI scanner output directory. If this parameter is not set the output directory
        set to the present working directory

        .PARAMETER Communities
        [Optional] Additional SNMP v2 community strings to use during the scan.
        'public' and 'private' community strings are specified by default.   
        
        .PARAMETER Modbus
        [Optional] Specify Modbus identification level.
        Options are basic, regular, or extended.
        Defaults to regular if left unspecified 

        .PARAMETER S7comm
        [Optional]  Request s7comm extended information.
        Options are true or false.
        Defaults to false if left unspecified.

        .PARAMETER Dnp3
        [Optional] Specify dnp3 banner address discovery.
        Options are require, prefer, or ignore.
        Defaults to ignore if left unspecified. 

        .EXAMPLE
        PS> Invoke-LimitedOTScan -Input_List \path\to\my\targets.txt -Scanner_Path \path\to\runzero-scanner.exe -Communities foo,bar -Modbus extended -S7comm true -Dnp3 prefer
    #>
function Invoke-FullOTScan {
    param (
        [Parameter(Mandatory=$true)][string]$Input_List,
        [Parameter(mandatory=$false)][string]$Scanner_Path,
        [Parameter(mandatory=$false)][string]$Communities,
        [Parameter(mandatory=$false)][string]$Output_Path,
        [Parameter(mandatory=$false)][ValidateSet('basic', 'regular', 'default')][string]$Modbus,
        [Parameter(mandatory=$false)][ValidateSet('true', 'false')][string]$S7comm,
        [Parameter(mandatory=$false)][ValidateSet('require', 'prefer', 'ignore')][string]$Dnp3)
    
    # Set default parameters if not otherwise specified
    If ( ! $Modbus ) {
        $Modbus = "regular"
    }
    If ( ! $S7comm ) {
        $S7comm = "false"
    }
    If ( ! $Dnp3 ) {
        $Dnp3 = "ignore"
    }

    $Comms = "public,private"
    $Probes = "connect,layer2,syn,bacnet,dahua-dhip,dns,dtls,ike,ipmi,kerberos,knxnet,l2t,l2tp,lantronix,ldap,mssql,netbios,ntp,openvpn,pca,sip,ssdp,snmp,ssh,tftp,ubnt,vmware,webmin,modbus,ethernetip,s7comm,fins,dnp3"

    # test that input target list exists
    $Exists = Test-Path $Input_List
    If ( ! ($Exists)) {
        Write-Host "`nProvided input list of targets does not exist."
        Exit
    }

    # Set path to runzero CLI scanner executable to current working directory if not otherwise specified
    If ( ! $Scanner_Path ) {
        $Scanner_Path = "$PWD\runzero-scanner.exe"
    }

    # Set path to runzero CLI scanner output folder to current working directory if not otherwise specified
    If ( ! $Output_Path ) {
        $Output_Path = "$PWD"
    }

    # test that the path to the scanner binary exists
    $Exists = Test-Path $Scanner_Path
    If (! ($Exists)) {
        Write-Host "`nProvided path to CLI scanner .exe does not exist."
        Exit
    }

    # test that the path to the output folder exists
    $Exists = Test-Path $Output_Path
    If (! ($Exists)) {
        Write-Host "`nProvided path to CLI scanner output does not exist."
        Exit
    }

    #Concatenate provided community strings with default public, private
    If ( $Communities) {
        $Comms = "$Comms,$Communities" 
    }

    Write-Host "`nPreparing OT Full scan..."

    & $Scanner_Path -i $Input_List --host-ping -r 500 --max-host-rate 20 --max-ttl 64 --max-group-size 2048 --modbus-identification-level $Modbus --s7comm-request-extended-information $S7comm --dnp3-banner-address-discovery $Dnp3 --probes $Probes --snmp-comms $Comms -o $Output_Path

    Write-Host "`nScan complete!"
}