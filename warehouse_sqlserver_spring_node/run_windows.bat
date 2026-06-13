@echo off
cd /d "%~dp0"
set SQLSERVER_INSTANCE=(localdb)\MSSQLLocalDB
set SQLSERVER_DATABASE=S
start "Java Spring API" cmd /k "cd /d ""%~dp0java-api"" && mvn spring-boot:run"
timeout /t 8 >nul
start "Node Frontend" cmd /k "cd /d ""%~dp0node-frontend"" && npm start"
start http://127.0.0.1:3000
