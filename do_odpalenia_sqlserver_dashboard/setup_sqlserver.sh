set -euo pipefail
cd "$(dirname "$0")"
export DASHBOARD_DB_ENGINE="${DASHBOARD_DB_ENGINE:-sqlserver}"
export SQLSERVER_INSTANCE="${SQLSERVER_INSTANCE:-localhost,1433}"
export SQLSERVER_DATABASE="${SQLSERVER_DATABASE:-S}"
export SQLSERVER_USER="${SQLSERVER_USER:-sa}"
export SQLSERVER_PASSWORD="${SQLSERVER_PASSWORD:-DataWarehouse!2026}"
export SQLSERVER_TRUST_CERT="${SQLSERVER_TRUST_CERT:-1}"
export SQLSERVER_BACKUP_PATH="${SQLSERVER_BACKUP_PATH:-/var/opt/mssql/backup/S (1).bak}"
export SQLSERVER_MDF_PATH="${SQLSERVER_MDF_PATH:-/var/opt/mssql/data/S.mdf}"
export SQLSERVER_LDF_PATH="${SQLSERVER_LDF_PATH:-/var/opt/mssql/data/S_log.ldf}"
python3 scripts/setup_sqlserver.py
