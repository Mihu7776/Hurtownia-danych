from __future__ import annotations

import argparse
import json
import sqlite3
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "drug_sales.db"
OPENFDA_NDC_URL = "https://api.fda.gov/drug/ndc.json"
OPENFDA_EVENT_URL = "https://api.fda.gov/drug/event.json"


SOURCE_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS source_metadata (
  source_key TEXT PRIMARY KEY,
  source_name TEXT NOT NULL,
  source_url TEXT NOT NULL,
  records_loaded INTEGER NOT NULL DEFAULT 0,
  total_available INTEGER,
  fetched_at TEXT
);

CREATE TABLE IF NOT EXISTS source_ndc_products (
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

CREATE TABLE IF NOT EXISTS source_drug_events (
  safetyreportid TEXT PRIMARY KEY,
  receivedate TEXT,
  serious INTEGER,
  patientsex TEXT,
  reaction TEXT,
  medicinalproduct TEXT,
  brand_name TEXT,
  manufacturer_name TEXT
);
"""


def fetch_json(url: str, params: dict[str, Any]) -> dict:
    full_url = f"{url}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(full_url, headers={"User-Agent": "drug-sales-dashboard/1.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_pages(url: str, base_params: dict[str, Any], limit: int, page_size: int) -> tuple[list[dict], int | None]:
    records: list[dict] = []
    total_available: int | None = None
    for skip in range(0, max(limit, 0), page_size):
        params = dict(base_params)
        params["limit"] = min(page_size, limit - skip)
        if skip:
            params["skip"] = skip
        payload = fetch_json(url, params)
        total_available = payload.get("meta", {}).get("results", {}).get("total")
        batch = payload.get("results", [])
        records.extend(batch)
        if len(batch) < params["limit"]:
            break
    return records, total_available


def first(value: Any) -> str | None:
    if isinstance(value, list) and value:
        return str(value[0])
    if value is None:
        return None
    return str(value)


def text(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    return str(value)


def upsert_metadata(
    conn: sqlite3.Connection,
    source_key: str,
    source_name: str,
    source_url: str,
    records_loaded: int,
    total_available: int | None,
) -> None:
    conn.execute(
        """
        INSERT INTO source_metadata(source_key, source_name, source_url, records_loaded, total_available, fetched_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(source_key) DO UPDATE SET
          source_name = excluded.source_name,
          source_url = excluded.source_url,
          records_loaded = excluded.records_loaded,
          total_available = excluded.total_available,
          fetched_at = excluded.fetched_at
        """,
        (
            source_key,
            source_name,
            source_url,
            records_loaded,
            total_available,
            datetime.now(timezone.utc).isoformat(timespec="seconds"),
        ),
    )


def load_ndc(conn: sqlite3.Connection, limit: int) -> None:
    payload = fetch_json(OPENFDA_NDC_URL, {"limit": min(limit, 1000)})
    records = payload.get("results", [])
    conn.execute("DELETE FROM source_ndc_products")
    for item in records:
        conn.execute(
            """
            INSERT OR REPLACE INTO source_ndc_products(
              product_ndc, product_type_name, proprietary_name, nonproprietary_name,
              labeler_name, dosage_form, route, marketing_category,
              start_marketing_date, listing_expiration_date
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                item.get("product_ndc"),
                item.get("product_type_name"),
                item.get("brand_name") or item.get("proprietary_name"),
                item.get("generic_name") or item.get("nonproprietary_name"),
                item.get("labeler_name"),
                item.get("dosage_form"),
                text(item.get("route")),
                item.get("marketing_category"),
                item.get("marketing_start_date") or item.get("start_marketing_date"),
                item.get("listing_expiration_date"),
            ),
        )
    total = payload.get("meta", {}).get("results", {}).get("total")
    upsert_metadata(conn, "openfda_ndc", "FDA National Drug Code Directory", OPENFDA_NDC_URL, len(records), total)
    print(f"openFDA NDC: {len(records)} rows")


def load_events(conn: sqlite3.Connection, limit: int, search: str) -> None:
    records, total = fetch_pages(OPENFDA_EVENT_URL, {"search": search}, limit, 100)
    conn.execute("DELETE FROM source_drug_events")
    for item in records:
        patient = item.get("patient", {}) or {}
        drug = first(patient.get("drug")) if isinstance(patient.get("drug"), list) else None
        if isinstance(patient.get("drug"), list) and patient.get("drug"):
            drug_data = patient["drug"][0]
        else:
            drug_data = {}
        if isinstance(patient.get("reaction"), list) and patient.get("reaction"):
            reaction = patient["reaction"][0].get("reactionmeddrapt")
        else:
            reaction = None
        openfda = drug_data.get("openfda", {}) if isinstance(drug_data, dict) else {}
        conn.execute(
            """
            INSERT OR REPLACE INTO source_drug_events(
              safetyreportid, receivedate, serious, patientsex, reaction,
              medicinalproduct, brand_name, manufacturer_name
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                item.get("safetyreportid"),
                item.get("receivedate"),
                int(item.get("serious") or 0),
                patient.get("patientsex"),
                reaction,
                drug_data.get("medicinalproduct") if isinstance(drug_data, dict) else drug,
                first(openfda.get("brand_name")),
                first(openfda.get("manufacturer_name")),
            ),
        )
    upsert_metadata(conn, "openfda_event", "openFDA Drug Adverse Event Reports", OPENFDA_EVENT_URL, len(records), total)
    print(f"openFDA events: {len(records)} rows")


def main() -> None:
    parser = argparse.ArgumentParser(description="Load two public FDA/openFDA datasets into SQLite.")
    parser.add_argument("--ndc-limit", type=int, default=1000)
    parser.add_argument("--event-limit", type=int, default=1000)
    parser.add_argument("--event-search", default="receivedate:[20240101 TO 20261231]")
    args = parser.parse_args()

    if not DB_PATH.exists():
        raise SystemExit(f"Database not found: {DB_PATH}. Run export_sqlserver_to_sqlite.py first.")

    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(SOURCE_SCHEMA_SQL)
        load_ndc(conn, args.ndc_limit)
        load_events(conn, args.event_limit, args.event_search)
        conn.commit()


if __name__ == "__main__":
    main()
