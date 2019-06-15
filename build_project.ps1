<# get pyinstaller if you haven't already! #>
<# pip install pyinstaller #>
pyinstaller --windowed --clean -F --icon=data/tekken_bot_close.ico --name TekkenBotPrime tekken_bot_prime.py
xcopy /s /Y data dist\data
Compress-Archive -Force -Path dist\data,dist\TekkenBotPrime.exe -DestinationPath dist\TekkenBotPrime_vX.X.X.zip
pause