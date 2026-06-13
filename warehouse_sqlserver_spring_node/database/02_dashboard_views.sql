USE S;
GO

CREATE OR ALTER VIEW dbo.v_dashboard_summary AS
SELECT
  COUNT_BIG(*) AS fact_rows,
  SUM(f.cntDrug) AS sold_count,
  ROUND(SUM(f.sumDrug), 2) AS sales_value,
  ROUND(AVG(f.avgDrug), 2) AS average_price,
  COUNT(DISTINCT f.dimDrug_id) AS drug_count,
  COUNT(DISTINCT f.dimMan_id) AS manufacturer_count
FROM dbo.factDrug f;
GO

CREATE OR ALTER VIEW dbo.v_sales_by_month AS
SELECT
  t.timeYear AS year_number,
  t.timeMonth AS month_name,
  SUM(f.cntDrug) AS sold_count,
  ROUND(SUM(f.sumDrug), 2) AS sales_value
FROM dbo.factDrug f
INNER JOIN dbo.dimTime t ON t.id = f.dimTime_id
GROUP BY t.timeYear, t.timeMonth;
GO

CREATE OR ALTER VIEW dbo.v_top_drugs AS
SELECT TOP 10
  d.dimName AS drug_name,
  SUM(f.cntDrug) AS sold_count,
  ROUND(SUM(f.sumDrug), 2) AS sales_value
FROM dbo.factDrug f
INNER JOIN dbo.dimDrug d ON d.id = f.dimDrug_id
GROUP BY d.dimName
ORDER BY SUM(f.cntDrug) DESC;
GO

CREATE OR ALTER VIEW dbo.v_top_manufacturers AS
SELECT TOP 10
  m.dimName AS manufacturer_name,
  SUM(f.cntDrug) AS sold_count,
  ROUND(SUM(f.sumDrug), 2) AS sales_value
FROM dbo.factDrug f
INNER JOIN dbo.dimMan m ON m.id = f.dimMan_id
GROUP BY m.dimName
ORDER BY SUM(f.sumDrug) DESC;
GO

CREATE OR ALTER VIEW dbo.v_city_sales AS
SELECT TOP 10
  c.dimName AS city_name,
  SUM(f.cntDrug) AS sold_count,
  ROUND(SUM(f.sumDrug), 2) AS sales_value
FROM dbo.factDrug f
INNER JOIN dbo.dimCity c ON c.id = f.dimCity_id
GROUP BY c.dimName
ORDER BY SUM(f.sumDrug) DESC;
GO

CREATE OR ALTER VIEW dbo.v_open_source_summary AS
SELECT
  source_key,
  source_name,
  records_loaded,
  total_available,
  fetched_at
FROM dbo.source_metadata;
GO
