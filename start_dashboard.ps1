Set-Location -LiteralPath $PSScriptRoot
$env:DASHBOARD_DB_ENGINE = "sqlserver"
$env:SQLSERVER_INSTANCE = "(localdb)\MSSQLLocalDB"
$env:SQLSERVER_DATABASE = "S_Codex"
SqlLocalDB start MSSQLLocalDB | Out-Null
python app.py
