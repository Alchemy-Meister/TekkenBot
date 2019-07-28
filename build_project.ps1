<# get pyinstaller if you haven't already! #>
<# pip install pyinstaller #>
pyinstaller TekkenBotPrime.spec
xcopy /s /Y /i data dist\data
Compress-Archive -Force -Path dist\data,dist\TekkenBotPrime.exe -DestinationPath dist\TekkenBotPrime_vX.X.X.zip
pause