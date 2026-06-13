from __future__ import annotations

import json
import re
import sqlite3
import subprocess
from typing import Any

from .config import DB_ENGINE, DB_PATH, MYSQL_CONFIG, SQLSERVER_CONFIG


class SqlCmdConnection:
    def __init__(self) -> None:
        self.server = SQLSERVER_CONFIG["server"]
        self.database = SQLSERVER_CONFIG["database"]
        self.sqlcmd = SQLSERVER_CONFIG["sqlcmd"]
        self.user = SQLSERVER_CONFIG["user"]
        self.password = SQLSERVER_CONFIG["password"]
        self.trust_cert = SQLSERVER_CONFIG["trust_cert"]

    def close(self) -> None:
        return


def connect() -> Any:
    if DB_ENGINE == "sqlite":
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    if DB_ENGINE == "mysql":
        try:
            import mysql.connector
        except ModuleNotFoundError as exc:
            raise RuntimeError("Install mysql-connector-python or keep DASHBOARD_DB_ENGINE=sqlite.") from exc
        return mysql.connector.connect(**MYSQL_CONFIG)
    if DB_ENGINE == "sqlserver":
        return SqlCmdConnection()
    raise RuntimeError(f"Unsupported DASHBOARD_DB_ENGINE: {DB_ENGINE}")


def _sql(sql: str) -> str:
    if DB_ENGINE == "mysql":
        return sql.replace("?", "%s")
    if DB_ENGINE == "sqlserver":
        sql = re.sub(r"\s+LIMIT\s+(\d+)\s*$", r" OFFSET 0 ROWS FETCH NEXT \1 ROWS ONLY", sql.strip(), flags=re.IGNORECASE)
        return sql
    return sql


def _literal(value: object) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, (int, float)):
        return str(value)
    return "N'" + str(value).replace("'", "''") + "'"


def _substitute_params(sql: str, args: list[object]) -> str:
    parts = sql.split("?")
    if len(parts) - 1 != len(args):
        raise RuntimeError("SQL placeholder count does not match argument count.")
    result = parts[0]
    for value, tail in zip(args, parts[1:]):
        result += _literal(value) + tail
    return result


def _sqlcmd_args(conn: SqlCmdConnection) -> list[str]:
    command = [
        conn.sqlcmd,
        "-S",
        conn.server,
        "-d",
        conn.database,
    ]
    if conn.user:
        command.extend(["-U", conn.user, "-P", conn.password])
    if conn.trust_cert:
        command.append("-C")
    return command


def _rows_sqlserver(conn: SqlCmdConnection, sql: str, args: list[object]) -> list[dict]:
    query = _substitute_params(_sql(sql).rstrip(";"), args)
    command = _sqlcmd_args(conn) + [
        "-f",
        "65001",
        "-w",
        "65535",
        "-y",
        "0",
        "-Q",
        f"SET NOCOUNT ON; {query} FOR JSON PATH, INCLUDE_NULL_VALUES;",
    ]
    result = subprocess.run(command, capture_output=True, check=True)
    output = result.stdout.decode("utf-8-sig", errors="replace")
    start = output.find("[")
    end = output.rfind("]")
    if start == -1 or end == -1:
        return []
    return json.loads("".join(output[start : end + 1].splitlines()))


def rows(conn: Any, sql: str, args: list[object] | None = None) -> list[dict]:
    args = args or []
    if DB_ENGINE == "mysql":
        cursor = conn.cursor(dictionary=True)
        cursor.execute(_sql(sql), args)
        result = list(cursor.fetchall())
        cursor.close()
        return result
    if DB_ENGINE == "sqlserver":
        return _rows_sqlserver(conn, sql, args)
    return [dict(row) for row in conn.execute(sql, args)]


def one(conn: Any, sql: str, args: list[object] | None = None) -> dict:
    result = rows(conn, sql, args)
    return result[0] if result else {}
