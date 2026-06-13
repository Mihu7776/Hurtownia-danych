from __future__ import annotations

from typing import Any

from .database import one, rows


BASE_FROM = """
FROM factDrug f
LEFT JOIN dimCity dc ON dc.id = f.dimCity_id
LEFT JOIN dimConTh ct ON ct.id = f.dimConTh_id
LEFT JOIN dimDrug dr ON dr.id = f.dimDrug_id
LEFT JOIN dimDrugType dt ON dt.id = f.dimDrugType_id
LEFT JOIN dimMan dm ON dm.id = f.dimMan_id
LEFT JOIN dimTime tt ON tt.id = f.dimTime_id
"""

FILTER_COLUMNS = {
    "city": "dc.dimName",
    "condition": "ct.dimName",
    "drug": "dr.dimName",
    "type": "dt.dimName",
    "manufacturer": "dm.dimName",
    "year": "tt.timeYear",
    "refunded": "f.is_refunded",
}


def build_where(params: dict[str, list[str]]) -> tuple[str, list[object]]:
    clauses: list[str] = []
    args: list[object] = []
    for key, column in FILTER_COLUMNS.items():
        value = params.get(key, [""])[0].strip()
        if not value:
            continue
        clauses.append(f"{column} = ?")
        args.append(int(value) if key in {"year", "refunded"} else value)
    return (" WHERE " + " AND ".join(clauses), args) if clauses else ("", args)


def api_filters(conn: Any, params: dict[str, list[str]]) -> dict:
    return {
        "cities": [row["dimName"] for row in rows(conn, "SELECT dimName FROM dimCity ORDER BY dimName")],
        "conditions": [row["dimName"] for row in rows(conn, "SELECT dimName FROM dimConTh ORDER BY dimName")],
        "drugs": [row["dimName"] for row in rows(conn, "SELECT dimName FROM dimDrug ORDER BY dimName")],
        "types": [row["dimName"] for row in rows(conn, "SELECT dimName FROM dimDrugType ORDER BY dimName")],
        "manufacturers": [row["dimName"] for row in rows(conn, "SELECT dimName FROM dimMan ORDER BY dimName")],
        "years": [row["timeYear"] for row in rows(conn, "SELECT DISTINCT timeYear FROM dimTime WHERE timeYear IS NOT NULL ORDER BY timeYear")],
    }


def api_summary(conn: Any, params: dict[str, list[str]]) -> dict:
    where_sql, args = build_where(params)
    sql = f"""
    SELECT
      COUNT(*) AS fact_groups,
      COALESCE(SUM(f.cntDrug), 0) AS transactions,
      COALESCE(SUM(f.sumDrug), 0) AS total_sales,
      CASE WHEN COALESCE(SUM(f.cntDrug), 0) = 0 THEN 0 ELSE SUM(f.sumDrug) / SUM(f.cntDrug) END AS avg_price,
      CASE WHEN COALESCE(SUM(f.cntDrug), 0) = 0 THEN 0
           ELSE 100.0 * SUM(CASE WHEN f.is_refunded = 1 THEN f.cntDrug ELSE 0 END) / SUM(f.cntDrug)
      END AS refund_rate,
      COUNT(DISTINCT dr.id) AS drug_count,
      COUNT(DISTINCT dm.id) AS manufacturer_count,
      COUNT(DISTINCT dc.id) AS city_count,
      MIN(tt.timeDay) AS date_from,
      MAX(tt.timeDay) AS date_to
    {BASE_FROM}
    {where_sql}
    """
    return one(conn, sql, args)


def api_timeseries(conn: Any, params: dict[str, list[str]]) -> list[dict]:
    where_sql, args = build_where(params)
    sql = f"""
    SELECT
      tt.timeMonth AS label,
      COALESCE(SUM(f.sumDrug), 0) AS total_sales,
      COALESCE(SUM(f.cntDrug), 0) AS transactions,
      CASE WHEN COALESCE(SUM(f.cntDrug), 0) = 0 THEN 0 ELSE SUM(f.sumDrug) / SUM(f.cntDrug) END AS avg_price
    {BASE_FROM}
    {where_sql}
    GROUP BY tt.timeMonth
    ORDER BY tt.timeMonth
    """
    return rows(conn, sql, args)


def ranked(conn: Any, params: dict[str, list[str]], label_sql: str, order_key: str = "total_sales", limit: int = 10) -> list[dict]:
    where_sql, args = build_where(params)
    sql = f"""
    SELECT
      {label_sql} AS label,
      COALESCE(SUM(f.sumDrug), 0) AS total_sales,
      COALESCE(SUM(f.cntDrug), 0) AS transactions,
      CASE WHEN COALESCE(SUM(f.cntDrug), 0) = 0 THEN 0 ELSE SUM(f.sumDrug) / SUM(f.cntDrug) END AS avg_price
    {BASE_FROM}
    {where_sql}
    GROUP BY {label_sql}
    ORDER BY {order_key} DESC
    LIMIT {limit}
    """
    return rows(conn, sql, args)


def api_top_drugs(conn: Any, params: dict[str, list[str]]) -> list[dict]:
    return ranked(conn, params, "dr.dimName")


def api_manufacturers(conn: Any, params: dict[str, list[str]]) -> list[dict]:
    return ranked(conn, params, "dm.dimName")


def api_cities(conn: Any, params: dict[str, list[str]]) -> list[dict]:
    return ranked(conn, params, "dc.dimName")


def api_conditions(conn: Any, params: dict[str, list[str]]) -> list[dict]:
    return ranked(conn, params, "ct.dimName", limit=8)


def api_drug_types(conn: Any, params: dict[str, list[str]]) -> list[dict]:
    return ranked(conn, params, "dt.dimName", limit=4)


def api_refunds(conn: Any, params: dict[str, list[str]]) -> list[dict]:
    where_sql, args = build_where(params)
    sql = f"""
    SELECT
      CASE WHEN f.is_refunded = 1 THEN 'Refundowane' ELSE 'Bez refundacji' END AS label,
      COALESCE(SUM(f.sumDrug), 0) AS total_sales,
      COALESCE(SUM(f.cntDrug), 0) AS transactions
    {BASE_FROM}
    {where_sql}
    GROUP BY f.is_refunded
    ORDER BY f.is_refunded DESC
    """
    return rows(conn, sql, args)


def api_records(conn: Any, params: dict[str, list[str]]) -> list[dict]:
    where_sql, args = build_where(params)
    sql = f"""
    SELECT
      f.id,
      tt.timeDay AS sale_date,
      dc.dimName AS city,
      ct.dimName AS condition,
      dr.dimName AS drug,
      dt.dimName AS drug_type,
      dm.dimName AS manufacturer,
      f.is_refunded,
      f.cntDrug,
      ROUND(f.sumDrug, 2) AS total_sales,
      ROUND(f.avgDrug, 2) AS avg_price
    {BASE_FROM}
    {where_sql}
    ORDER BY tt.timeDay DESC, f.id DESC
    LIMIT 100
    """
    return rows(conn, sql, args)


def api_source_summary(conn: Any, params: dict[str, list[str]]) -> dict:
    metadata = rows(conn, "SELECT source_key, source_name, source_url, records_loaded, total_available, fetched_at FROM source_metadata ORDER BY source_key")
    ndc_count = one(conn, "SELECT COUNT(*) AS value FROM source_ndc_products")["value"]
    event_count = one(conn, "SELECT COUNT(*) AS value FROM source_drug_events")["value"]
    return {"ndc_count": ndc_count, "event_count": event_count, "metadata": metadata}


def api_source_labelers(conn: Any, params: dict[str, list[str]]) -> list[dict]:
    return rows(
        conn,
        """
        SELECT COALESCE(NULLIF(labeler_name, ''), 'Unknown') AS label, COUNT(*) AS products
        FROM source_ndc_products
        GROUP BY COALESCE(NULLIF(labeler_name, ''), 'Unknown')
        ORDER BY products DESC, label
        LIMIT 10
        """,
    )


def api_source_reactions(conn: Any, params: dict[str, list[str]]) -> list[dict]:
    return rows(
        conn,
        """
        SELECT COALESCE(NULLIF(reaction, ''), 'Unknown') AS label, COUNT(*) AS reports
        FROM source_drug_events
        GROUP BY COALESCE(NULLIF(reaction, ''), 'Unknown')
        ORDER BY reports DESC, label
        LIMIT 10
        """,
    )


def api_project_info(conn: Any, params: dict[str, list[str]]) -> dict:
    return {
        "architecture": [
            "backend/server.py serves HTML assets and JSON API",
            "backend/queries.py contains dashboard aggregate SQL",
            "frontend/assets/app.js renders charts and tables only",
            "SQL Server LocalDB S is the default runtime database",
            "sql/ contains schema, ETL, and aggregate queries for SQL Server",
        ],
        "etl": [
            "Extract: SQL Server backup and two public openFDA endpoints",
            "Stage: dbo.import, tempStd, source_ndc_products, source_drug_events",
            "Dimensions: city, condition, drug, drug type, manufacturer, time",
            "Fact load: grouped insert into factDrug with count/sum/avg/min/max",
            "Dashboard: backend executes aggregate SQL and returns JSON",
        ],
        "sql_files": [
            {"name": "ERD documentation", "url": "/docs/ERD.md"},
            {"name": "Star schema SQL Server DDL", "url": "/sql/01_schema_star_sqlserver.sql"},
            {"name": "ETL SQL Server SQL", "url": "/sql/02_etl_sqlserver.sql"},
            {"name": "Dashboard aggregate SQL Server SQL", "url": "/sql/03_aggregates_dashboard_sqlserver.sql"},
            {"name": "Data sources SQL Server notes", "url": "/sql/04_sources_sqlserver.sql"},
        ],
        "sources": [
            {
                "name": "SQL Server backup",
                "url": "C:\\Users\\Michal Swislocki\\Downloads\\S (1).bak",
                "role": "original sales warehouse schema and seed data",
            },
            {
                "name": "FDA National Drug Code Directory",
                "url": "https://api.fda.gov/drug/ndc.json",
                "role": "open source drug product reference data",
            },
            {
                "name": "openFDA Drug Adverse Event Reports",
                "url": "https://api.fda.gov/drug/event.json",
                "role": "open source safety/adverse-event context data",
            },
        ],
    }


API_ROUTES = {
    "/api/filters": api_filters,
    "/api/summary": api_summary,
    "/api/timeseries": api_timeseries,
    "/api/top-drugs": api_top_drugs,
    "/api/manufacturers": api_manufacturers,
    "/api/cities": api_cities,
    "/api/conditions": api_conditions,
    "/api/refunds": api_refunds,
    "/api/drug-types": api_drug_types,
    "/api/records": api_records,
    "/api/source-summary": api_source_summary,
    "/api/source-labelers": api_source_labelers,
    "/api/source-reactions": api_source_reactions,
    "/api/project-info": api_project_info,
}
