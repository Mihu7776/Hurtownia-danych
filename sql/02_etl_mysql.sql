-- ETL for MySQL 8.
-- Goal: load raw sales data into a clean staging table, dimensions, and factDrug.

USE drug_dashboard;

-- 1. Standardize raw imported sales rows.
TRUNCATE TABLE tempStd;

INSERT INTO tempStd (
  Sale_Timestamp,
  Manufacturer,
  Drug_Name,
  Price,
  Drug_Type,
  Is_Refunded,
  Condition_Treated,
  City
)
SELECT
  CASE
    WHEN Sale_Timestamp REGEXP '^[0-9]{4}-[0-9]{2}-[0-9]{2}'
      THEN CAST(Sale_Timestamp AS DATETIME)
    ELSE STR_TO_DATE(Sale_Timestamp, '%Y-%m-%d %H:%i:%s')
  END AS Sale_Timestamp,
  TRIM(Manufacturer) AS Manufacturer,
  TRIM(Drug_Name) AS Drug_Name,
  CAST(REPLACE(Price, ',', '.') AS DECIMAL(10, 2)) AS Price,
  TRIM(Drug_Type) AS Drug_Type,
  CASE
    WHEN LOWER(TRIM(Is_Refunded)) IN ('1', 'true', 'yes', 'y', 't') THEN 1
    ELSE 0
  END AS Is_Refunded,
  TRIM(Condition_Treated) AS Condition_Treated,
  TRIM(City) AS City
FROM import_raw
WHERE Drug_Name IS NOT NULL
  AND Manufacturer IS NOT NULL
  AND City IS NOT NULL
  AND Price IS NOT NULL;

-- 2. Load dimensions. Unique keys protect dimensions from duplicates.
INSERT INTO dimCity (dimName)
SELECT DISTINCT City
FROM tempStd
WHERE City IS NOT NULL
ON DUPLICATE KEY UPDATE dimName = VALUES(dimName);

INSERT INTO dimConTh (dimName)
SELECT DISTINCT Condition_Treated
FROM tempStd
WHERE Condition_Treated IS NOT NULL
ON DUPLICATE KEY UPDATE dimName = VALUES(dimName);

INSERT INTO dimDrug (dimName)
SELECT DISTINCT Drug_Name
FROM tempStd
WHERE Drug_Name IS NOT NULL
ON DUPLICATE KEY UPDATE dimName = VALUES(dimName);

INSERT INTO dimDrugType (dimName)
SELECT DISTINCT Drug_Type
FROM tempStd
WHERE Drug_Type IS NOT NULL
ON DUPLICATE KEY UPDATE dimName = VALUES(dimName);

INSERT INTO dimMan (dimName)
SELECT DISTINCT Manufacturer
FROM tempStd
WHERE Manufacturer IS NOT NULL
ON DUPLICATE KEY UPDATE dimName = VALUES(dimName);

INSERT INTO dimTime (timeDay, timeWeekDay, timeWeekNum, timeMonth, timeYear)
SELECT DISTINCT
  DATE(Sale_Timestamp) AS timeDay,
  DAYOFWEEK(Sale_Timestamp) AS timeWeekDay,
  WEEK(Sale_Timestamp, 3) AS timeWeekNum,
  DATE_FORMAT(Sale_Timestamp, '%Y-%m') AS timeMonth,
  YEAR(Sale_Timestamp) AS timeYear
FROM tempStd
WHERE Sale_Timestamp IS NOT NULL
ON DUPLICATE KEY UPDATE
  timeWeekDay = VALUES(timeWeekDay),
  timeWeekNum = VALUES(timeWeekNum),
  timeMonth = VALUES(timeMonth),
  timeYear = VALUES(timeYear);

-- 3. Load aggregate fact table.
-- This is the key star-schema ETL step: one grouped fact row per
-- city + condition + drug + type + manufacturer + day + refund status.
TRUNCATE TABLE factDrug;

INSERT INTO factDrug (
  dimCity_id,
  dimConTh_id,
  dimDrug_id,
  dimDrugType_id,
  dimMan_id,
  dimTime_id,
  is_refunded,
  cntDrug,
  sumDrug,
  avgDrug,
  minDrug,
  maxDrug
)
SELECT
  dc.id AS dimCity_id,
  ct.id AS dimConTh_id,
  dr.id AS dimDrug_id,
  dt.id AS dimDrugType_id,
  dm.id AS dimMan_id,
  tt.id AS dimTime_id,
  t.Is_Refunded AS is_refunded,
  COUNT(*) AS cntDrug,
  SUM(t.Price) AS sumDrug,
  AVG(t.Price) AS avgDrug,
  MIN(t.Price) AS minDrug,
  MAX(t.Price) AS maxDrug
FROM tempStd t
INNER JOIN dimCity dc ON dc.dimName = t.City
INNER JOIN dimConTh ct ON ct.dimName = t.Condition_Treated
INNER JOIN dimDrug dr ON dr.dimName = t.Drug_Name
INNER JOIN dimDrugType dt ON dt.dimName = t.Drug_Type
INNER JOIN dimMan dm ON dm.dimName = t.Manufacturer
INNER JOIN dimTime tt ON tt.timeDay = DATE(t.Sale_Timestamp)
GROUP BY
  dc.id,
  ct.id,
  dr.id,
  dt.id,
  dm.id,
  tt.id,
  t.Is_Refunded;
