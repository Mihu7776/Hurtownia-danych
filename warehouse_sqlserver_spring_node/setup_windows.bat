@echo off
cd /d "%~dp0"
set SQLSERVER_INSTANCE=(localdb)\MSSQLLocalDB
set SQLSERVER_DATABASE=S
SqlLocalDB start MSSQLLocalDB >nul 2>nul
sqlcmd -S "%SQLSERVER_INSTANCE%" -i database\01_restore_database.sql -v DatabaseName="S" BackupFile="%CD%\data\S (1).bak" DataFile="%CD%\data\S.mdf" LogFile="%CD%\data\S_log.ldf" -b
sqlcmd -S "%SQLSERVER_INSTANCE%" -d "%SQLSERVER_DATABASE%" -i data\sqlserver_runtime_tables.sql -b
sqlcmd -S "%SQLSERVER_INSTANCE%" -d "%SQLSERVER_DATABASE%" -i database\02_dashboard_views.sql -b
echo Gotowe. Teraz uruchom run_windows.bat
pause
