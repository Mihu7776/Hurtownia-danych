from __future__ import annotations

import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FRONTEND_DIR = ROOT / "frontend"
SQL_DIR = ROOT / "sql"
DOCS_DIR = ROOT / "docs"
DB_PATH = ROOT / "data" / "drug_sales.db"

HOST = os.environ.get("DASHBOARD_HOST", "127.0.0.1")
PORT = int(os.environ.get("DASHBOARD_PORT", "8000"))

DB_ENGINE = os.environ.get("DASHBOARD_DB_ENGINE", "sqlserver").lower()
SQLSERVER_CONFIG = {
    "server": os.environ.get("SQLSERVER_INSTANCE", r"(localdb)\MSSQLLocalDB"),
    "database": os.environ.get("SQLSERVER_DATABASE", "S"),
    "sqlcmd": os.environ.get("SQLCMD_EXE", "sqlcmd"),
    "user": os.environ.get("SQLSERVER_USER", ""),
    "password": os.environ.get("SQLSERVER_PASSWORD", ""),
    "trust_cert": os.environ.get("SQLSERVER_TRUST_CERT", "0").lower() in {"1", "true", "yes"},
}
MYSQL_CONFIG = {
    "host": os.environ.get("MYSQL_HOST", "127.0.0.1"),
    "port": int(os.environ.get("MYSQL_PORT", "3306")),
    "user": os.environ.get("MYSQL_USER", "root"),
    "password": os.environ.get("MYSQL_PASSWORD", ""),
    "database": os.environ.get("MYSQL_DATABASE", "drug_dashboard"),
}
