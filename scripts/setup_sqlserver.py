from __future__ import annotations

import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DATABASE = "S_Codex"
SERVER = r"(localdb)\MSSQLLocalDB"
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


def sql_text(value: Path) -> str:
    return str(value).replace("'", "''")


def run(command: list[str]) -> None:
    subprocess.run(command, check=True)


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    backup = find_backup()
    mdf = DATA_DIR / "S_Codex.mdf"
    ldf = DATA_DIR / "S_Codex_log.ldf"

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
    FROM DISK = N'{sql_text(backup)}'
    WITH
      MOVE N'S' TO N'{sql_text(mdf)}',
      MOVE N'S_log' TO N'{sql_text(ldf)}',
      REPLACE;
    """
    run(["sqlcmd", "-S", SERVER, "-Q", restore_sql, "-b"])

    if RUNTIME_SQL.exists():
        print("Dogrywam tabele openFDA do SQL Server...")
        run(["sqlcmd", "-S", SERVER, "-d", DATABASE, "-i", str(RUNTIME_SQL), "-b"])
    else:
        print("Brak data/sqlserver_runtime_tables.sql - pomijam dogranie openFDA.")

    print("Gotowe. Teraz uruchom start_dashboard.bat")


if __name__ == "__main__":
    main()
