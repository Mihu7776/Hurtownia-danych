@echo off
setlocal
cd /d "%~dp0"

set "MYSQL_EXE=C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"
if not exist "%MYSQL_EXE%" set "MYSQL_EXE=C:\Program Files\MySQL\MySQL Workbench 8.0\mysql.exe"

if not exist "%MYSQL_EXE%" (
  echo mysql.exe was not found. Add MySQL bin to PATH or edit this file.
  pause
  exit /b 1
)

set /p MYSQL_USER=MySQL user [root]: 
if "%MYSQL_USER%"=="" set "MYSQL_USER=root"

echo.
echo This will recreate the drug_dashboard schema and load seed data.
pause

"%MYSQL_EXE%" -u %MYSQL_USER% -p < "sql\01_schema_star_mysql.sql"
if errorlevel 1 goto fail

"%MYSQL_EXE%" -u %MYSQL_USER% -p drug_dashboard < "data\mysql_seed.sql"
if errorlevel 1 goto fail

echo.
echo MySQL import finished.
echo To run app against MySQL:
echo   set DASHBOARD_DB_ENGINE=mysql
echo   set MYSQL_USER=%MYSQL_USER%
echo   set MYSQL_PASSWORD=your_password
echo   python app.py
pause
exit /b 0

:fail
echo.
echo MySQL import failed.
pause
exit /b 1
