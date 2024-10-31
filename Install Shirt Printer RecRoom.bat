@echo off
setlocal

REM Define variables
set "PYTHON_URL=https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
set "PYTHON_INSTALLER=python-installer.exe"
set "SHIRT_PRINTER_REPO=https://github.com/RenePotocnik/RecRoom-Shirt-Printer.git"
set "SHIRT_PRINTER_DIR=RecRoom-Shirt-Printer"
set "REQUIREMENTS_FILE=D:\CustomizationAndCreationPrograms\Applicaitons\RecRoom-Shirt-Printer-main\RecRoom-Shirt-Printer-main\requirements.txt"

REM Step 1: Download Python 3.11 installer
echo Downloading Python 3.11 installer...
powershell -Command "Invoke-WebRequest -Uri %PYTHON_URL% -OutFile %PYTHON_INSTALLER%"

REM Step 2: Install Python 3.11 without a restart
echo Installing Python 3.11...
start /wait %PYTHON_INSTALLER% /quiet InstallAllUsers=1 PrependPath=1 Include_test=0 Include_pip=1

REM Step 3: Clean up installer
echo Cleaning up...
del %PYTHON_INSTALLER%

REM Step 4: Clone RecRoom Shirt Printer repository
echo Cloning RecRoom Shirt Printer repository...
git clone %SHIRT_PRINTER_REPO%

REM Step 5: Install required packages
echo Installing required packages...
pip install -r "%REQUIREMENTS_FILE%"

REM Step 6: Run the Python script to import requirements
echo Running the Python script to import requirements...
python "D:\CustomizationAndCreationPrograms\Applicaitons\RecRoom-Shirt-Printer-main\RecRoom-Shirt-Printer-main\import requirements.py"

echo Setup completed successfully.
pause
endlocal