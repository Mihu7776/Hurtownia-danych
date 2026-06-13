# Drug Sales Intelligence

Dashboard analityczny hurtowni danych lekow. Projekt jest zrobiony w Pythonie i HTML/CSS/JS, a dane produkcyjne sa odtwarzane do SQL Servera z backupu `S (1).bak`.

## Co jest w projekcie

- `backend/` - backend HTTP w Pythonie, routing API i wykonywanie zapytan agregujacych.
- `frontend/` - statyczny frontend HTML, CSS i JavaScript.
- `sql/` - schemat gwiazdy, ETL, agregaty dashboardu i opis zrodel.
- `docs/` - ERD oraz opis procesu ETL.
- `scripts/` - restore SQL Servera i dogranie tabel openFDA.
- `data/S (1).bak` - backup bazy SQL Server.
- `data/sqlserver_runtime_tables.sql` - dane openFDA gotowe do dogrania do SQL Servera.

## Jak to dziala

Backend startuje lokalny serwer HTTP na `127.0.0.1:8000`. Frontend pobiera dane przez endpointy `/api/...` i tylko renderuje wynik w przegladarce. Logika analityczna jest po stronie backendu oraz SQL Servera.

Baza runtime nazywa sie `S`. Backup `S (1).bak` jest odtwarzany do SQL Servera, a potem skrypt dogrywa tabele open source:

- `source_metadata`
- `source_ndc_products`
- `source_drug_events`

Glowne agregaty sa liczone z tabeli faktow `factDrug` oraz wymiarow:

- `dimCity`
- `dimConTh`
- `dimDrug`
- `dimDrugType`
- `dimMan`
- `dimTime`

Ziarnem faktu jest kombinacja: miasto, choroba/condition, lek, typ leku, producent, dzien i status refundacji.

## Zrodla danych

1. Backup SQL Server: `data/S (1).bak`
2. FDA National Drug Code Directory: `https://api.fda.gov/drug/ndc.json`
3. openFDA Drug Adverse Event Reports: `https://api.fda.gov/drug/event.json`

## ETL

ETL jest opisany w `docs/ETL.md`, a SQL jest w `sql/02_etl_sqlserver.sql`.

Proces:

1. Odtworzenie backupu SQL Server do bazy `S`.
2. Standaryzacja danych wejsciowych.
3. Zaladowanie wymiarow.
4. Zbudowanie tabeli faktow `factDrug`.
5. Dogranie danych openFDA do tabel zrodlowych.
6. Uruchomienie dashboardu, ktory pobiera agregaty z SQL Servera.

Agregaty dashboardu sa w `sql/03_aggregates_dashboard_sqlserver.sql`.

## ERD

Schemat ERD jest w `docs/ERD.md`. Dashboard pokazuje rowniez relacje schematu gwiazdy w panelu dokumentacji.

## Uruchomienie na Windows

Wymagania:

- Python 3.11 lub nowszy
- SQL Server LocalDB
- `sqlcmd`

Wejdz do folderu projektu:

```powershell
cd "C:\sciezka\do\Data-warehouse"
```

Pierwsze uruchomienie bazy:

```powershell
.\setup_sqlserver.bat
```

Start dashboardu:

```powershell
.\start_dashboard.bat
```

Albo bez batcha:

```powershell
python app.py
```

Adres dashboardu:

```text
http://127.0.0.1:8000
```

W PowerShell skrypty `.bat` uruchamia sie z `.\`, np. `.\start_dashboard.bat`.

## Uruchomienie na Linux EndeavourOS

Na Linuxie LocalDB nie dziala, dlatego najprostszy wariant to SQL Server w Dockerze.

Wymagania:

- Python 3.11 lub nowszy
- Docker
- `sqlcmd`

Instalacja podstaw:

```bash
sudo pacman -Syu python docker
sudo systemctl enable --now docker
sudo usermod -aG docker "$USER"
```

Po dodaniu uzytkownika do grupy `docker` wyloguj sie i zaloguj ponownie.

Instalacja `sqlcmd` na EndeavourOS najczesciej idzie przez AUR:

```bash
yay -S mssql-tools
```

Jezeli po instalacji komenda `sqlcmd` nie jest widoczna, ustaw sciezke do narzedzia:

```bash
export SQLCMD_EXE="/opt/mssql-tools18/bin/sqlcmd"
```

Uruchom kontener SQL Server:

```bash
cd /sciezka/do/Data-warehouse
docker run -e "ACCEPT_EULA=Y" -e "MSSQL_SA_PASSWORD=DataWarehouse!2026" -p 1433:1433 -v "$PWD/data:/var/opt/mssql/backup" --name data-warehouse-sql -d mcr.microsoft.com/mssql/server:2022-latest
```

Poczekaj kilkadziesiat sekund, az SQL Server wystartuje, potem odtworz baze:

```bash
bash setup_sqlserver.sh
```

Start dashboardu:

```bash
bash start_dashboard.sh
```

Adres dashboardu:

```text
http://127.0.0.1:8000
```

Jezeli kontener juz istnieje, ale jest zatrzymany:

```bash
docker start data-warehouse-sql
```

Jezeli zmienisz haslo SA, ustaw je tez dla skryptow:

```bash
export SQLSERVER_PASSWORD="TwojeHaslo"
bash setup_sqlserver.sh
bash start_dashboard.sh
```

## Przydatne endpointy

- `/api/summary`
- `/api/timeseries`
- `/api/top-drugs`
- `/api/manufacturers`
- `/api/project-info`

## Struktura SQL

- `sql/01_schema_star_sqlserver.sql` - schemat gwiazdy.
- `sql/02_etl_sqlserver.sql` - ETL.
- `sql/03_aggregates_dashboard_sqlserver.sql` - agregaty.
- `sql/04_sources_sqlserver.sql` - zrodla open source.
