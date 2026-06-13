from __future__ import annotations

import argparse
import json
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "openfda_generated.sql"


def fetch_json(url: str) -> dict[str, Any]:
    with urllib.request.urlopen(url, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def text(value: Any) -> str:
    if value is None:
        return "NULL"
    return "N'" + str(value).replace("'", "''")[:1000] + "'"


def metadata(name: str, url: str, count: int, total: int | None) -> str:
    now = datetime.now(timezone.utc).isoformat()
    return (
        "INSERT INTO dbo.source_metadata "
        "(source_key, source_name, source_url, records_loaded, total_available, fetched_at) VALUES "
        f"({text(name)}, {text(name)}, {text(url)}, {count}, {total if total is not None else 'NULL'}, {text(now)});"
    )


def product_insert(item: dict[str, Any]) -> str:
    return (
        "INSERT INTO dbo.source_ndc_products "
        "(product_ndc, product_type_name, proprietary_name, nonproprietary_name, labeler_name, dosage_form, route, marketing_category, start_marketing_date, listing_expiration_date) VALUES "
        f"({text(item.get('product_ndc'))}, {text(item.get('product_type'))}, {text(item.get('brand_name'))}, "
        f"{text(item.get('generic_name'))}, {text(item.get('labeler_name'))}, {text(item.get('dosage_form'))}, "
        f"{text(', '.join(item.get('route', [])) if isinstance(item.get('route'), list) else item.get('route'))}, "
        f"{text(item.get('marketing_category'))}, {text(item.get('marketing_start_date'))}, {text(item.get('listing_expiration_date'))});"
    )


def event_insert(item: dict[str, Any]) -> str:
    patient = item.get("patient", {})
    drugs = patient.get("drug", [])
    reactions = patient.get("reaction", [])
    first_drug = drugs[0] if drugs else {}
    first_reaction = reactions[0] if reactions else {}
    return (
        "INSERT INTO dbo.source_drug_events "
        "(safetyreportid, receivedate, serious, patientsex, reaction, medicinalproduct, brand_name, manufacturer_name) VALUES "
        f"({text(item.get('safetyreportid'))}, {text(item.get('receivedate'))}, "
        f"{1 if str(item.get('serious', '0')) == '1' else 0}, {text(patient.get('patientsex'))}, "
        f"{text(first_reaction.get('reactionmeddrapt'))}, {text(first_drug.get('medicinalproduct'))}, "
        f"{text(first_drug.get('openfda', {}).get('brand_name', [''])[0] if first_drug.get('openfda', {}).get('brand_name') else '')}, "
        f"{text(first_drug.get('openfda', {}).get('manufacturer_name', [''])[0] if first_drug.get('openfda', {}).get('manufacturer_name') else '')});"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=100)
    args = parser.parse_args()

    ndc_url = f"https://api.fda.gov/drug/ndc.json?limit={args.limit}"
    event_query = urllib.parse.quote("receivedate:[20240101 TO 20261231]")
    event_url = f"https://api.fda.gov/drug/event.json?search={event_query}&limit={min(args.limit, 100)}"

    ndc = fetch_json(ndc_url)
    events = fetch_json(event_url)
    ndc_rows = ndc.get("results", [])
    event_rows = events.get("results", [])

    lines = [
        "USE S;",
        "DELETE FROM dbo.source_drug_events;",
        "DELETE FROM dbo.source_ndc_products;",
        "DELETE FROM dbo.source_metadata;",
        metadata("openFDA NDC products", ndc_url, len(ndc_rows), ndc.get("meta", {}).get("results", {}).get("total")),
        metadata("openFDA drug events", event_url, len(event_rows), events.get("meta", {}).get("results", {}).get("total")),
    ]
    lines.extend(product_insert(item) for item in ndc_rows)
    lines.extend(event_insert(item) for item in event_rows)

    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Zapisano {OUTPUT}")


if __name__ == "__main__":
    main()
