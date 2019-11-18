Set-Location $(Split-Path $PSScriptRoot -Parent)
Remove-Item -Path 'dist' -Recurse -Force
pyinstaller TekkenBotPrime.spec

if ($MyInvocation.CommandOrigin -eq 'Runspace')
{
    Copy-Item -Path 'data' -Destination 'dist\data' -Recurse -Force -Exclude 'settings.ini'
}