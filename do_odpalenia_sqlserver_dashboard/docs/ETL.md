# ETL and Architecture

## Architecture

- `backend/` - Python HTTP server, DB connection, aggregate SQL API.
- `frontend/` - Tailwind HTML/CSS/JS. It only renders JSON returned by backend.
- `sql/` - SQL Server schema, ETL, aggregate queries, and source notes.
- SQL Server LocalDB `S` - runtime database restored from `S (1).bak`.

## Data Sources

1. SQL Server backup: `C:\Users\Michal Swislocki\Downloads\S (1).bak`
   - Restored into SQL Server LocalDB as `S`.
   - Provides the original sales star schema and seed data.

2. FDA National Drug Code Directory
   - API: `https://api.fda.gov/drug/ndc.json`
   - Loaded into `source_ndc_products`.
   - Used for open-data drug product context.

3. openFDA Drug Adverse Event Reports
   - API: `https://api.fda.gov/drug/event.json`
   - Loaded into `source_drug_events`.
   - Used for open-data safety/adverse-event context.

## ETL Flow

1. Extract raw sales rows from SQL Server backup into `dbo.import`.
2. Standardize raw rows into `tempStd`.
3. Load dimensions:
   - `dimCity`
   - `dimConTh`
   - `dimDrug`
   - `dimDrugType`
   - `dimMan`
   - `dimTime`
4. Build aggregate fact table `factDrug`.
   - Grain: city + condition + drug + drug type + manufacturer + day + refund status.
   - Measures: `cntDrug`, `sumDrug`, `avgDrug`, `minDrug`, `maxDrug`.
5. Load open data into:
   - `source_ndc_products`
   - `source_drug_events`
   - `source_metadata`
6. Backend executes aggregate SQL and returns JSON.
7. Frontend renders charts/tables only.

## Key SQL Files

- `docs/ERD.md` - ERD with PK/FK relationships and cardinalities.
- `sql/01_schema_star_sqlserver.sql` - SQL Server star schema and source table DDL.
- `sql/02_etl_sqlserver.sql` - staging, dimension load, fact load.
- `sql/03_aggregates_dashboard_sqlserver.sql` - dashboard aggregate queries.
- `sql/04_sources_sqlserver.sql` - source metadata and API notes.
