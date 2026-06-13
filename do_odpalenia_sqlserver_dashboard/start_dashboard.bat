@echo off
cd /d "%~dp0"
set DASHBOARD_DB_ENGINE=sqlserver
set SQLSERVER_INSTANCE=(localdb)\MSSQLLocalDB
set SQLSERVER_DATABASE=S
SqlLocalDB start MSSQLLocalDB >nul 2>nul
python app.py
pause
