from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SQLITE_DB = ROOT / "data" / "drug_sales.db"
OUTPUT_SQL = ROOT / "data" / "mysql_seed.sql"

TABLES = [
    "dimCity",
    "dimConTh",
    "dimDrug",
    "dimDrugType",
    "dimMan",
    "dimTime",
    "factDrug",
    "import_raw",
    "tempStd",
    "source_metadata",
    "source_ndc_products",
    "source_drug_events",
]


def mysql_value(value: Any) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, (int, float)):
        return str(value)
    text = str(value).replace("\\", "\\\\").replace("'", "''")
    return f"'{text}'"


def write_table(conn: sqlite3.Connection, handle, table: str) -> None:
    columns = [row["name"] for row in conn.execute(f"PRAGMA table_info({table})")]
    if not columns:
        return
    handle.write(f"\nTRUNCATE TABLE `{table}`;\n")
    column_sql = ", ".join(f"`{column}`" for column in columns)
    cursor = conn.execute(f"SELECT {', '.join(columns)} FROM {table}")
    rows = cursor.fetchall()
    if not rows:
        return
    batch_size = 200
    for start in range(0, len(rows), batch_size):
        batch = rows[start : start + batch_size]
        handle.write(f"INSERT INTO `{table}` ({column_sql}) VALUES\n")
        values = []
        for row in batch:
            values.append("(" + ", ".join(mysql_value(row[column]) for column in columns) + ")")
        handle.write(",\n".join(values))
        handle.write(";\n")


def main() -> None:
    if not SQLITE_DB.exists():
        raise SystemExit(f"SQLite database not found: {SQLITE_DB}")
    with sqlite3.connect(SQLITE_DB) as conn:
        conn.row_factory = sqlite3.Row
        with OUTPUT_SQL.open("w", encoding="utf-8", newline="\n") as handle:
            handle.write("USE drug_dashboard;\n")
            handle.write("SET FOREIGN_KEY_CHECKS = 0;\n")
            for table in TABLES:
                write_table(conn, handle, table)
            handle.write("SET FOREIGN_KEY_CHECKS = 1;\n")
    print(f"MySQL seed written to {OUTPUT_SQL}")


if __name__ == "__main__":
    main()
