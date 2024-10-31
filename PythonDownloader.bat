@echo off
echo Downloading Python 3.11 installer...
set "URL=https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
set "INSTALLER=python-installer.exe"

REM Download Python installer
powershell -Command "Invoke-WebRequest -Uri %URL% -OutFile %INSTALLER%"

echo Running the installer...
start /wait %INSTALLER% /quiet InstallAllUsers=1 PrependPath=1

echo Cleaning up...
del %INSTALLER%

echo Python 3.11 installation completed. Please check the installation.
pause