
USE S;
GO

MERGE dbo.source_metadata AS target
USING (
  VALUES
    (
      N'sqlserver_backup',
      N'SQL Server backup S (1).bak',
      N'C:\Users\Michal Swislocki\Downloads\S (1).bak',
      999,
      NULL,
      CONVERT(NVARCHAR(40), SYSDATETIMEOFFSET())
    ),
    (
      N'openfda_ndc',
      N'FDA National Drug Code Directory',
      N'https://api.fda.gov/drug/ndc.json',
      1000,
      135430,
      CONVERT(NVARCHAR(40), SYSDATETIMEOFFSET())
    ),
    (
      N'openfda_event',
      N'openFDA Drug Adverse Event Reports',
      N'https://api.fda.gov/drug/event.json',
      1000,
      2936534,
      CONVERT(NVARCHAR(40), SYSDATETIMEOFFSET())
    )
) AS source(source_key, source_name, source_url, records_loaded, total_available, fetched_at)
ON target.source_key = source.source_key
WHEN MATCHED THEN UPDATE SET
  source_name = source.source_name,
  source_url = source.source_url,
  records_loaded = source.records_loaded,
  total_available = source.total_available,
  fetched_at = source.fetched_at
WHEN NOT MATCHED THEN INSERT (
  source_key,
  source_name,
  source_url,
  records_loaded,
  total_available,
  fetched_at
) VALUES (
  source.source_key,
  source.source_name,
  source.source_url,
  source.records_loaded,
  source.total_available,
  source.fetched_at
);
GO

