-- Dashboard aggregate SQL.
-- The backend executes these patterns and injects optional filters:
-- city, condition, drug, type, manufacturer, year, refunded.

USE drug_dashboard;

-- Shared star-schema join.
-- factDrug is already aggregated by ETL, so dashboard queries are fast.

-- KPI summary.
SELECT
  COUNT(*) AS fact_groups,
  COALESCE(SUM(f.cntDrug), 0) AS transactions,
  COALESCE(SUM(f.sumDrug), 0) AS total_sales,
  CASE
    WHEN COALESCE(SUM(f.cntDrug), 0) = 0 THEN 0
    ELSE SUM(f.sumDrug) / SUM(f.cntDrug)
  END AS avg_price,
  CASE
    WHEN COALESCE(SUM(f.cntDrug), 0) = 0 THEN 0
    ELSE 100.0 * SUM(CASE WHEN f.is_refunded = 1 THEN f.cntDrug ELSE 0 END) / SUM(f.cntDrug)
  END AS refund_rate,
  COUNT(DISTINCT dr.id) AS drug_count,
  COUNT(DISTINCT dm.id) AS manufacturer_count,
  COUNT(DISTINCT dc.id) AS city_count,
  MIN(tt.timeDay) AS date_from,
  MAX(tt.timeDay) AS date_to
FROM factDrug f
LEFT JOIN dimCity dc ON dc.id = f.dimCity_id
LEFT JOIN dimConTh ct ON ct.id = f.dimConTh_id
LEFT JOIN dimDrug dr ON dr.id = f.dimDrug_id
LEFT JOIN dimDrugType dt ON dt.id = f.dimDrugType_id
LEFT JOIN dimMan dm ON dm.id = f.dimMan_id
LEFT JOIN dimTime tt ON tt.id = f.dimTime_id;

-- Monthly trend.
SELECT
  tt.timeMonth AS label,
  COALESCE(SUM(f.sumDrug), 0) AS total_sales,
  COALESCE(SUM(f.cntDrug), 0) AS transactions,
  CASE
    WHEN COALESCE(SUM(f.cntDrug), 0) = 0 THEN 0
    ELSE SUM(f.sumDrug) / SUM(f.cntDrug)
  END AS avg_price
FROM factDrug f
LEFT JOIN dimTime tt ON tt.id = f.dimTime_id
GROUP BY tt.timeMonth
ORDER BY tt.timeMonth;

-- Top drugs by sales.
SELECT
  dr.dimName AS label,
  COALESCE(SUM(f.sumDrug), 0) AS total_sales,
  COALESCE(SUM(f.cntDrug), 0) AS transactions
FROM factDrug f
LEFT JOIN dimDrug dr ON dr.id = f.dimDrug_id
GROUP BY dr.dimName
ORDER BY total_sales DESC
LIMIT 10;

-- Top manufacturers by sales.
SELECT
  dm.dimName AS label,
  COALESCE(SUM(f.sumDrug), 0) AS total_sales,
  COALESCE(SUM(f.cntDrug), 0) AS transactions
FROM factDrug f
LEFT JOIN dimMan dm ON dm.id = f.dimMan_id
GROUP BY dm.dimName
ORDER BY total_sales DESC
LIMIT 10;

-- City ranking.
SELECT
  dc.dimName AS label,
  COALESCE(SUM(f.sumDrug), 0) AS total_sales,
  COALESCE(SUM(f.cntDrug), 0) AS transactions
FROM factDrug f
LEFT JOIN dimCity dc ON dc.id = f.dimCity_id
GROUP BY dc.dimName
ORDER BY total_sales DESC
LIMIT 10;

-- Treatment-condition ranking.
SELECT
  ct.dimName AS label,
  COALESCE(SUM(f.sumDrug), 0) AS total_sales,
  COALESCE(SUM(f.cntDrug), 0) AS transactions
FROM factDrug f
LEFT JOIN dimConTh ct ON ct.id = f.dimConTh_id
GROUP BY ct.dimName
ORDER BY total_sales DESC
LIMIT 8;

-- Refund split.
SELECT
  CASE WHEN f.is_refunded = 1 THEN 'Refundowane' ELSE 'Bez refundacji' END AS label,
  COALESCE(SUM(f.sumDrug), 0) AS total_sales,
  COALESCE(SUM(f.cntDrug), 0) AS transactions
FROM factDrug f
GROUP BY f.is_refunded
ORDER BY f.is_refunded DESC;

-- Drug type split.
SELECT
  dt.dimName AS label,
  COALESCE(SUM(f.sumDrug), 0) AS total_sales,
  COALESCE(SUM(f.cntDrug), 0) AS transactions,
  CASE
    WHEN COALESCE(SUM(f.cntDrug), 0) = 0 THEN 0
    ELSE SUM(f.sumDrug) / SUM(f.cntDrug)
  END AS avg_price
FROM factDrug f
LEFT JOIN dimDrugType dt ON dt.id = f.dimDrugType_id
GROUP BY dt.dimName
ORDER BY total_sales DESC;

-- Open data aggregate: FDA NDC top labelers.
SELECT
  COALESCE(NULLIF(labeler_name, ''), 'Unknown') AS label,
  COUNT(*) AS products
FROM source_ndc_products
GROUP BY COALESCE(NULLIF(labeler_name, ''), 'Unknown')
ORDER BY products DESC, label
LIMIT 10;

-- Open data aggregate: openFDA adverse event top reactions.
SELECT
  COALESCE(NULLIF(reaction, ''), 'Unknown') AS label,
  COUNT(*) AS reports
FROM source_drug_events
GROUP BY COALESCE(NULLIF(reaction, ''), 'Unknown')
ORDER BY reports DESC, label
LIMIT 10;
