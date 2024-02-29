@echo off
curl -o python-3.10.11-amd64.exe https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe
start /wait python-3.10.11-amd64.exe /quiet InstallAllUsers=1 PrependPath=1
del python-3.10.11-amd64.exe
start /wait cmd /c "pip install requests PyQt5 selenium"
pause
