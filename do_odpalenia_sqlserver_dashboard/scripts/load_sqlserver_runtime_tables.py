from __future__ import annotations

import os
import sqlite3
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SQLITE_DB = ROOT / "data" / "drug_sales.db"
OUTPUT_SQL = ROOT / "data" / "sqlserver_runtime_tables.sql"
SERVER = os.environ.get("SQLSERVER_INSTANCE", r"(localdb)\MSSQLLocalDB")
DATABASE = os.environ.get("SQLSERVER_DATABASE", "S")
SQLCMD = os.environ.get("SQLCMD_EXE", "sqlcmd")
SQLSERVER_USER = os.environ.get("SQLSERVER_USER", "")
SQLSERVER_PASSWORD = os.environ.get("SQLSERVER_PASSWORD", "")
SQLSERVER_TRUST_CERT = os.environ.get("SQLSERVER_TRUST_CERT", "0").lower() in {"1", "true", "yes"}

TABLES = [
    "source_metadata",
    "source_ndc_products",
    "source_drug_events",
]


DDL = """
IF OBJECT_ID(N'dbo.source_drug_events', N'U') IS NOT NULL DROP TABLE dbo.source_drug_events;
IF OBJECT_ID(N'dbo.source_ndc_products', N'U') IS NOT NULL DROP TABLE dbo.source_ndc_products;
IF OBJECT_ID(N'dbo.source_metadata', N'U') IS NOT NULL DROP TABLE dbo.source_metadata;

CREATE TABLE dbo.source_metadata (
  source_key NVARCHAR(80) NOT NULL PRIMARY KEY,
  source_name NVARCHAR(255) NOT NULL,
  source_url NVARCHAR(MAX) NOT NULL,
  records_loaded INT NOT NULL DEFAULT 0,
  total_available INT NULL,
  fetched_at NVARCHAR(40) NULL
);

CREATE TABLE dbo.source_ndc_products (
  product_ndc NVARCHAR(80) NOT NULL PRIMARY KEY,
  product_type_name NVARCHAR(MAX) NULL,
  proprietary_name NVARCHAR(MAX) NULL,
  nonproprietary_name NVARCHAR(MAX) NULL,
  labeler_name NVARCHAR(255) NULL,
  dosage_form NVARCHAR(MAX) NULL,
  route NVARCHAR(MAX) NULL,
  marketing_category NVARCHAR(MAX) NULL,
  start_marketing_date NVARCHAR(20) NULL,
  listing_expiration_date NVARCHAR(20) NULL
);

CREATE INDEX IX_source_ndc_labeler ON dbo.source_ndc_products(labeler_name);

CREATE TABLE dbo.source_drug_events (
  safetyreportid NVARCHAR(80) NOT NULL PRIMARY KEY,
  receivedate NVARCHAR(20) NULL,
  serious BIT NULL,
  patientsex NVARCHAR(20) NULL,
  reaction NVARCHAR(MAX) NULL,
  medicinalproduct NVARCHAR(MAX) NULL,
  brand_name NVARCHAR(MAX) NULL,
  manufacturer_name NVARCHAR(MAX) NULL
);
"""


def sqlcmd_args() -> list[str]:
    command = [SQLCMD, "-S", SERVER, "-d", DATABASE]
    if SQLSERVER_USER:
        command.extend(["-U", SQLSERVER_USER, "-P", SQLSERVER_PASSWORD])
    if SQLSERVER_TRUST_CERT:
        command.append("-C")
    return command


def sql_value(value: Any) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, (int, float)):
        return str(value)
    text = str(value).replace("'", "''")
    return f"N'{text}'"


def write_table(conn: sqlite3.Connection, handle, table: str) -> None:
    columns = [row["name"] for row in conn.execute(f"PRAGMA table_info({table})")]
    rows = conn.execute(f"SELECT {', '.join(columns)} FROM {table}").fetchall()
    if not rows:
        return
    column_sql = ", ".join(f"[{column}]" for column in columns)
    batch_size = 100
    for start in range(0, len(rows), batch_size):
        batch = rows[start : start + batch_size]
        handle.write(f"\nINSERT INTO dbo.{table} ({column_sql}) VALUES\n")
        values = []
        for row in batch:
            values.append("(" + ", ".join(sql_value(row[column]) for column in columns) + ")")
        handle.write(",\n".join(values))
        handle.write(";\n")


def main() -> None:
    if not SQLITE_DB.exists():
        raise SystemExit(f"SQLite database not found: {SQLITE_DB}")
    with sqlite3.connect(SQLITE_DB) as conn:
        conn.row_factory = sqlite3.Row
        with OUTPUT_SQL.open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(DDL)
            for table in TABLES:
                write_table(conn, handle, table)
    subprocess.run(sqlcmd_args() + ["-i", str(OUTPUT_SQL), "-b"], check=True)
    print(f"SQL Server runtime tables loaded into {DATABASE}. Script: {OUTPUT_SQL}")


if __name__ == "__main__":
    main()
