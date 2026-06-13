# Drug Sales Intelligence

Python backend + Tailwind frontend dashboard running on SQL Server LocalDB.

## Run

If this is the first launch on a new machine/folder, restore the SQL Server database first:

```text
setup_sqlserver.bat
```

Then start the dashboard.

Double-click:

```text
start_dashboard.bat
```

or run:

```powershell
python app.py
```

The app opens automatically:

```text
http://127.0.0.1:8000
```

## Runtime Database

Default database engine:

```text
SQL Server LocalDB
```

Connection:

```text
Server: (localdb)\MSSQLLocalDB
Database: S_Codex
```

The backup `S (1).bak` was restored into `S_Codex`. The dashboard now reads aggregates from SQL Server, not SQLite.

## Project Structure

```text
backend/                         Python backend, API, SQL Server access, aggregate SQL
frontend/                        Tailwind HTML/CSS/JS, only renders API JSON
sql/01_schema_star_sqlserver.sql SQL Server schema notes + openFDA tables
sql/02_etl_sqlserver.sql         SQL Server ETL / fact load
sql/03_aggregates_dashboard_sqlserver.sql
sql/04_sources_sqlserver.sql
docs/ERD.md                      ERD with PK/FK relationships
docs/ETL.md                      ETL and architecture notes
```

## Architecture

- Backend connects to SQL Server and executes aggregate SQL.
- Frontend only renders JSON returned by backend.
- ERD and star schema are visible in the dashboard.
- SQL files are linked inside the dashboard.

## Star Schema

Fact table:

```text
factDrug
```

Dimensions:

```text
dimCity
dimConTh
dimDrug
dimDrugType
dimMan
dimTime
```

Fact grain:

```text
city + condition + drug + drug type + manufacturer + day + refund status
```

Measures:

```text
cntDrug
sumDrug
avgDrug
minDrug
maxDrug
```

## ETL

Main SQL Server ETL file:

```text
sql/02_etl_sqlserver.sql
```

Flow:

1. Restore SQL Server backup into `S_Codex`.
2. Standardize sales data into `tempStd`.
3. Load dimensions.
4. Build aggregated `factDrug`.
5. Load public openFDA tables into SQL Server:
   - `source_metadata`
   - `source_ndc_products`
   - `source_drug_events`
6. Backend executes dashboard aggregate SQL against SQL Server.

## Data Sources

1. SQL Server backup:

```text
C:\Users\Michal Swislocki\Downloads\S (1).bak
```

2. FDA National Drug Code Directory:

```text
https://api.fda.gov/drug/ndc.json
```

3. openFDA Drug Adverse Event Reports:

```text
https://api.fda.gov/drug/event.json
```

## Rebuild SQL Server Runtime Tables

If needed:

```powershell
python scripts/load_sqlserver_runtime_tables.py
```
