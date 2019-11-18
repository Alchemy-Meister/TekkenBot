Set-Location $(Split-Path $PSScriptRoot -Parent)
& .\build_scripts\build_project.ps1
$version=$(python ./build_scripts/increase_version.py --release)
Copy-Item -Path 'data' -Destination 'dist\data' -Recurse -Force -Exclude 'settings.ini'
$destination_path='dist\TekkenBotPrime_v{0}.zip' -f $version
Compress-Archive -Force -Path dist\data,dist\TekkenBotPrime.exe -DestinationPath $destination_path