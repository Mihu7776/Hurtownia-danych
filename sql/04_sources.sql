-- Data sources used by the project.
-- The source metadata is also stored in source_metadata.

USE drug_dashboard;

INSERT INTO source_metadata (
  source_key,
  source_name,
  source_url,
  records_loaded,
  total_available,
  fetched_at
)
VALUES
  (
    'sqlserver_backup',
    'SQL Server backup S (1).bak',
    'C:\\Users\\Michal Swislocki\\Downloads\\S (1).bak',
    999,
    NULL,
    NOW()
  ),
  (
    'openfda_ndc',
    'FDA National Drug Code Directory',
    'https://api.fda.gov/drug/ndc.json',
    1000,
    135430,
    NOW()
  ),
  (
    'openfda_event',
    'openFDA Drug Adverse Event Reports',
    'https://api.fda.gov/drug/event.json',
    1000,
    2936534,
    NOW()
  )
ON DUPLICATE KEY UPDATE
  source_name = VALUES(source_name),
  source_url = VALUES(source_url),
  records_loaded = VALUES(records_loaded),
  total_available = VALUES(total_available),
  fetched_at = VALUES(fetched_at);

-- Public open-data extraction used by scripts/load_open_sources.py:
-- 1. NDC products:
--    https://api.fda.gov/drug/ndc.json?limit=1000
--
-- 2. Adverse event reports:
--    https://api.fda.gov/drug/event.json?search=receivedate:[20240101 TO 20261231]&limit=100&skip=...
--
-- The adverse-event endpoint is paged by 100 rows because larger single
-- requests can be rejected. The script loops with skip until the requested
-- event limit is loaded.
