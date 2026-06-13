from __future__ import annotations

import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DATABASE = os.environ.get("SQLSERVER_DATABASE", "S")
SERVER = os.environ.get("SQLSERVER_INSTANCE", r"(localdb)\MSSQLLocalDB")
SQLCMD = os.environ.get("SQLCMD_EXE", "sqlcmd")
SQLSERVER_USER = os.environ.get("SQLSERVER_USER", "")
SQLSERVER_PASSWORD = os.environ.get("SQLSERVER_PASSWORD", "")
SQLSERVER_TRUST_CERT = os.environ.get("SQLSERVER_TRUST_CERT", "0").lower() in {"1", "true", "yes"}
RUNTIME_SQL = DATA_DIR / "sqlserver_runtime_tables.sql"


def find_backup() -> Path:
    candidates = [
        ROOT / "S (1).bak",
        DATA_DIR / "S (1).bak",
        Path.home() / "Downloads" / "S (1).bak",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    raise SystemExit("Nie znaleziono pliku S (1).bak. Wrzuc go do folderu projektu albo do folderu data.")


def sql_text(value: object) -> str:
    return str(value).replace("'", "''")


def run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def sqlcmd_args(database: str | None = None) -> list[str]:
    command = [SQLCMD, "-S", SERVER]
    if database:
        command.extend(["-d", database])
    if SQLSERVER_USER:
        command.extend(["-U", SQLSERVER_USER, "-P", SQLSERVER_PASSWORD])
    if SQLSERVER_TRUST_CERT:
        command.append("-C")
    return command


def is_localdb() -> bool:
    return "localdb" in SERVER.lower()


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    backup = find_backup()
    backup_path = os.environ.get("SQLSERVER_BACKUP_PATH", str(backup))
    mdf = os.environ.get("SQLSERVER_MDF_PATH", str(DATA_DIR / "S.mdf"))
    ldf = os.environ.get("SQLSERVER_LDF_PATH", str(DATA_DIR / "S_log.ldf"))

    if is_localdb():
        print("Startuje SQL Server LocalDB...")
        subprocess.run(["SqlLocalDB", "start", "MSSQLLocalDB"], capture_output=True)

    print(f"Odtwarzam backup: {backup}")
    restore_sql = f"""
    IF DB_ID(N'{DATABASE}') IS NOT NULL
    BEGIN
      ALTER DATABASE {DATABASE} SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
      DROP DATABASE {DATABASE};
    END;
    RESTORE DATABASE {DATABASE}
    FROM DISK = N'{sql_text(backup_path)}'
    WITH
      MOVE N'S' TO N'{sql_text(mdf)}',
      MOVE N'S_log' TO N'{sql_text(ldf)}',
      REPLACE;
    """
    run(sqlcmd_args() + ["-Q", restore_sql, "-b"])

    if RUNTIME_SQL.exists():
        print("Dogrywam tabele openFDA do SQL Server...")
        run(sqlcmd_args(DATABASE) + ["-i", str(RUNTIME_SQL), "-b"])
    else:
        print("Brak data/sqlserver_runtime_tables.sql - pomijam dogranie openFDA.")

    print("Gotowe. Teraz uruchom start_dashboard.bat")


if __name__ == "__main__":
    main()
