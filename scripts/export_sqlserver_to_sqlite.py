from __future__ import annotations

import json
import os
import sqlite3
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DB_DIR = ROOT / "data"
DB_PATH = DB_DIR / "drug_sales.db"
SERVER = os.environ.get("SQLSERVER_INSTANCE", r"(localdb)\MSSQLLocalDB")
DATABASE = os.environ.get("SQLSERVER_DATABASE", "S_Codex")


SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS factDrug;
DROP TABLE IF EXISTS dimCity;
DROP TABLE IF EXISTS dimConTh;
DROP TABLE IF EXISTS dimDrug;
DROP TABLE IF EXISTS dimDrugType;
DROP TABLE IF EXISTS dimMan;
DROP TABLE IF EXISTS dimTime;
DROP TABLE IF EXISTS import_raw;
DROP TABLE IF EXISTS tempStd;
DROP TABLE IF EXISTS source_metadata;
DROP TABLE IF EXISTS source_ndc_products;
DROP TABLE IF EXISTS source_drug_events;

CREATE TABLE dimCity (
  id INTEGER PRIMARY KEY,
  dimName TEXT NOT NULL
);

CREATE TABLE dimConTh (
  id INTEGER PRIMARY KEY,
  dimName TEXT NOT NULL
);

CREATE TABLE dimDrug (
  id INTEGER PRIMARY KEY,
  dimName TEXT NOT NULL
);

CREATE TABLE dimDrugType (
  id INTEGER PRIMARY KEY,
  dimName TEXT NOT NULL
);

CREATE TABLE dimMan (
  id INTEGER PRIMARY KEY,
  dimName TEXT NOT NULL
);

CREATE TABLE dimTime (
  id INTEGER PRIMARY KEY,
  timeDay TEXT NOT NULL,
  timeWeekDay INTEGER NOT NULL,
  timeWeekNum INTEGER NOT NULL,
  timeMonth TEXT,
  timeYear INTEGER
);

CREATE TABLE factDrug (
  id INTEGER PRIMARY KEY,
  dimCity_id INTEGER,
  dimConTh_id INTEGER,
  dimDrug_id INTEGER,
  dimDrugType_id INTEGER,
  dimMan_id INTEGER,
  dimTime_id INTEGER,
  is_refunded INTEGER NOT NULL,
  cntDrug INTEGER NOT NULL,
  sumDrug REAL NOT NULL,
  avgDrug REAL NOT NULL,
  minDrug REAL NOT NULL,
  maxDrug REAL NOT NULL,
  FOREIGN KEY (dimCity_id) REFERENCES dimCity(id),
  FOREIGN KEY (dimConTh_id) REFERENCES dimConTh(id),
  FOREIGN KEY (dimDrug_id) REFERENCES dimDrug(id),
  FOREIGN KEY (dimDrugType_id) REFERENCES dimDrugType(id),
  FOREIGN KEY (dimMan_id) REFERENCES dimMan(id),
  FOREIGN KEY (dimTime_id) REFERENCES dimTime(id)
);

CREATE TABLE import_raw (
  Transaction_ID TEXT,
  Sale_Timestamp TEXT,
  Manufacturer TEXT,
  Drug_Name TEXT,
  Price TEXT,
  Drug_Type TEXT,
  Is_Refunded TEXT,
  Condition_Treated TEXT,
  City TEXT
);

CREATE TABLE tempStd (
  Sale_Timestamp TEXT,
  Manufacturer TEXT,
  Drug_Name TEXT,
  Price REAL,
  Drug_Type TEXT,
  Is_Refunded INTEGER,
  Condition_Treated TEXT,
  City TEXT
);

CREATE TABLE source_metadata (
  source_key TEXT PRIMARY KEY,
  source_name TEXT NOT NULL,
  source_url TEXT NOT NULL,
  records_loaded INTEGER NOT NULL DEFAULT 0,
  total_available INTEGER,
  fetched_at TEXT
);

CREATE TABLE source_ndc_products (
  product_ndc TEXT PRIMARY KEY,
  product_type_name TEXT,
  proprietary_name TEXT,
  nonproprietary_name TEXT,
  labeler_name TEXT,
  dosage_form TEXT,
  route TEXT,
  marketing_category TEXT,
  start_marketing_date TEXT,
  listing_expiration_date TEXT
);

CREATE TABLE source_drug_events (
  safetyreportid TEXT PRIMARY KEY,
  receivedate TEXT,
  serious INTEGER,
  patientsex TEXT,
  reaction TEXT,
  medicinalproduct TEXT,
  brand_name TEXT,
  manufacturer_name TEXT
);

CREATE INDEX idx_fact_city ON factDrug(dimCity_id);
CREATE INDEX idx_fact_drug ON factDrug(dimDrug_id);
CREATE INDEX idx_fact_manufacturer ON factDrug(dimMan_id);
CREATE INDEX idx_fact_time ON factDrug(dimTime_id);
CREATE INDEX idx_fact_refunded ON factDrug(is_refunded);
"""


TABLES: dict[str, list[str]] = {
    "dbo.dimCity": ["id", "dimName"],
    "dbo.dimConTh": ["id", "dimName"],
    "dbo.dimDrug": ["id", "dimName"],
    "dbo.dimDrugType": ["id", "dimName"],
    "dbo.dimMan": ["id", "dimName"],
    "dbo.dimTime": ["id", "timeDay", "timeWeekDay", "timeWeekNum", "timeMonth", "timeYear"],
    "dbo.factDrug": [
        "id",
        "dimCity_id",
        "dimConTh_id",
        "dimDrug_id",
        "dimDrugType_id",
        "dimMan_id",
        "dimTime_id",
        "is_refunded",
        "cntDrug",
        "sumDrug",
        "avgDrug",
        "minDrug",
        "maxDrug",
    ],
    "dbo.import": [
        "Transaction_ID",
        "Sale_Timestamp",
        "Manufacturer",
        "Drug_Name",
        "Price",
        "Drug_Type",
        "Is_Refunded",
        "Condition_Treated",
        "City",
    ],
    "dbo.tempStd": [
        "Sale_Timestamp",
        "Manufacturer",
        "Drug_Name",
        "Price",
        "Drug_Type",
        "Is_Refunded",
        "Condition_Treated",
        "City",
    ],
}

SQLITE_TABLE_NAMES = {
    "dbo.import": "import_raw",
}


def sql_identifier(name: str) -> str:
    parts = name.split(".")
    return ".".join(f"[{part}]" for part in parts)


def fetch_table(table: str, columns: list[str]) -> list[dict]:
    projection = ", ".join(f"[{column}]" for column in columns)
    order_by = "id" if "id" in columns else columns[0]
    query = f"SET NOCOUNT ON; SELECT {projection} FROM {sql_identifier(table)} ORDER BY [{order_by}] FOR JSON PATH, INCLUDE_NULL_VALUES;"
    command = [
        "sqlcmd",
        "-S",
        SERVER,
        "-d",
        DATABASE,
        "-f",
        "65001",
        "-w",
        "65535",
        "-y",
        "0",
        "-Q",
        query,
    ]
    result = subprocess.run(command, check=True, capture_output=True)
    output = result.stdout.decode("utf-8-sig", errors="replace").strip()
    if not output:
        return []
    compact = "".join(output.splitlines())
    start = compact.find("[")
    end = compact.rfind("]")
    if start == -1 or end == -1:
        raise RuntimeError(f"Could not find JSON payload in sqlcmd output for {table}: {output[:500]}")
    return json.loads(compact[start : end + 1])


def insert_rows(conn: sqlite3.Connection, table: str, columns: list[str], data: list[dict]) -> None:
    if not data:
        return
    sqlite_table = SQLITE_TABLE_NAMES.get(table, table.split(".")[-1])
    placeholders = ", ".join("?" for _ in columns)
    column_sql = ", ".join(columns)
    sql = f"INSERT INTO {sqlite_table} ({column_sql}) VALUES ({placeholders})"
    values = [[row.get(column) for column in columns] for row in data]
    conn.executemany(sql, values)


def main() -> None:
    DB_DIR.mkdir(exist_ok=True)
    temp_path = DB_PATH.with_suffix(".tmp")
    if temp_path.exists():
        temp_path.unlink()

    conn = sqlite3.connect(temp_path)
    try:
        conn.executescript(SCHEMA_SQL)
        for table, columns in TABLES.items():
            data = fetch_table(table, columns)
            insert_rows(conn, table, columns, data)
            print(f"{table}: {len(data)} rows")
        conn.execute(
            """
            INSERT INTO source_metadata(source_key, source_name, source_url, records_loaded, total_available, fetched_at)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
            """,
            (
                "sqlserver_backup",
                "SQL Server backup S (1).bak",
                "C:\\Users\\Michal Swislocki\\Downloads\\S (1).bak",
                conn.execute("SELECT COUNT(*) FROM factDrug").fetchone()[0],
                None,
            ),
        )
        conn.commit()
    finally:
        conn.close()

    temp_path.replace(DB_PATH)
    print(f"SQLite database written to {DB_PATH}")


if __name__ == "__main__":
    main()
