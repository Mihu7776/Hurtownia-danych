set -euo pipefail
cd "$(dirname "$0")"
export SQLSERVER_INSTANCE="${SQLSERVER_INSTANCE:-localhost,1433}"
export SQLSERVER_DATABASE="${SQLSERVER_DATABASE:-S}"
export SQLSERVER_USER="${SQLSERVER_USER:-sa}"
export SQLSERVER_PASSWORD="${SQLSERVER_PASSWORD:-DataWarehouse!2026}"
export SQLSERVER_TRUST_CERT="${SQLSERVER_TRUST_CERT:-1}"
(cd java-api && mvn spring-boot:run) &
sleep 8
(cd node-frontend && npm start)
