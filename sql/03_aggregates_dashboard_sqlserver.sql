-- SQL Server aggregate queries used by backend/queries.py.
-- Optional filters are injected in the backend.

USE S_Codex;
GO

-- KPI summary.
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
FROM dbo.factDrug f
LEFT JOIN dbo.dimCity dc ON dc.id = f.dimCity_id
LEFT JOIN dbo.dimConTh ct ON ct.id = f.dimConTh_id
LEFT JOIN dbo.dimDrug dr ON dr.id = f.dimDrug_id
LEFT JOIN dbo.dimDrugType dt ON dt.id = f.dimDrugType_id
LEFT JOIN dbo.dimMan dm ON dm.id = f.dimMan_id
LEFT JOIN dbo.dimTime tt ON tt.id = f.dimTime_id;

-- Monthly trend.
SELECT
  tt.timeMonth AS label,
  COALESCE(SUM(f.sumDrug), 0) AS total_sales,
  COALESCE(SUM(f.cntDrug), 0) AS transactions,
  CASE WHEN COALESCE(SUM(f.cntDrug), 0) = 0 THEN 0 ELSE SUM(f.sumDrug) / SUM(f.cntDrug) END AS avg_price
FROM dbo.factDrug f
LEFT JOIN dbo.dimTime tt ON tt.id = f.dimTime_id
GROUP BY tt.timeMonth
ORDER BY tt.timeMonth;

-- Top drugs.
SELECT TOP (10)
  dr.dimName AS label,
  COALESCE(SUM(f.sumDrug), 0) AS total_sales,
  COALESCE(SUM(f.cntDrug), 0) AS transactions
FROM dbo.factDrug f
LEFT JOIN dbo.dimDrug dr ON dr.id = f.dimDrug_id
GROUP BY dr.dimName
ORDER BY total_sales DESC;

-- Refund split.
SELECT
  CASE WHEN f.is_refunded = 1 THEN N'Refundowane' ELSE N'Bez refundacji' END AS label,
  COALESCE(SUM(f.sumDrug), 0) AS total_sales,
  COALESCE(SUM(f.cntDrug), 0) AS transactions
FROM dbo.factDrug f
GROUP BY f.is_refunded
ORDER BY f.is_refunded DESC;
GO
