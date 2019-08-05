<# get pyinstaller if you haven't already! #>
<# pip install pyinstaller #>
pyinstaller TekkenBotPrime.spec
Remove-Item -Path 'dist\data' -Recurse -Force
Copy-Item -Path 'data' -Destination 'dist\data' -Recurse -Force -Exclude 'settings.ini'
Compress-Archive -Force -Path dist\data,dist\TekkenBotPrime.exe -DestinationPath dist\TekkenBotPrime_vX.X.X.zip
pause