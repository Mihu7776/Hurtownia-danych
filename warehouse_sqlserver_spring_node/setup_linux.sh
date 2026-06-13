set -euo pipefail
cd "$(dirname "$0")"
export SQLSERVER_PASSWORD="${SQLSERVER_PASSWORD:-DataWarehouse!2026}"
export SQLSERVER_INSTANCE="${SQLSERVER_INSTANCE:-localhost,1433}"
export SQLSERVER_DATABASE="${SQLSERVER_DATABASE:-S}"
export SQLSERVER_USER="${SQLSERVER_USER:-sa}"
export SQLSERVER_TRUST_CERT="${SQLSERVER_TRUST_CERT:-1}"
docker inspect warehouse-sqlserver >/dev/null 2>&1 || docker run -e "ACCEPT_EULA=Y" -e "MSSQL_SA_PASSWORD=$SQLSERVER_PASSWORD" -p 1433:1433 -v "$PWD/data:/var/opt/mssql/backup" --name warehouse-sqlserver -d mcr.microsoft.com/mssql/server:2022-latest
docker start warehouse-sqlserver >/dev/null 2>&1 || true
sleep 25
sqlcmd -S "$SQLSERVER_INSTANCE" -U "$SQLSERVER_USER" -P "$SQLSERVER_PASSWORD" -C -i database/01_restore_database.sql -v DatabaseName="S" BackupFile="/var/opt/mssql/backup/S (1).bak" DataFile="/var/opt/mssql/data/S.mdf" LogFile="/var/opt/mssql/data/S_log.ldf" -b
sqlcmd -S "$SQLSERVER_INSTANCE" -U "$SQLSERVER_USER" -P "$SQLSERVER_PASSWORD" -C -d "$SQLSERVER_DATABASE" -i data/sqlserver_runtime_tables.sql -b
sqlcmd -S "$SQLSERVER_INSTANCE" -U "$SQLSERVER_USER" -P "$SQLSERVER_PASSWORD" -C -d "$SQLSERVER_DATABASE" -i database/02_dashboard_views.sql -b
echo "Gotowe. Teraz uruchom bash run_linux.sh"
