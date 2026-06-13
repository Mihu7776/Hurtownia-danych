
USE S;
GO

EXEC dbo.ETL;
GO


TRUNCATE TABLE dbo.factDrug;

INSERT INTO dbo.factDrug (
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
  SUM(CONVERT(float, t.Price)) AS sumDrug,
  AVG(CONVERT(float, t.Price)) AS avgDrug,
  MIN(CONVERT(float, t.Price)) AS minDrug,
  MAX(CONVERT(float, t.Price)) AS maxDrug
FROM dbo.tempStd t
INNER JOIN dbo.dimCity dc ON dc.dimName = t.City
INNER JOIN dbo.dimConTh ct ON ct.dimName = t.Condition_Treated
INNER JOIN dbo.dimDrug dr ON dr.dimName = t.Drug_Name
INNER JOIN dbo.dimDrugType dt ON dt.dimName = t.Drug_Type
INNER JOIN dbo.dimMan dm ON dm.dimName = t.Manufacturer
INNER JOIN dbo.dimTime tt ON tt.timeDay = CAST(t.Sale_Timestamp AS date)
GROUP BY
  dc.id,
  ct.id,
  dr.id,
  dt.id,
  dm.id,
  tt.id,
  t.Is_Refunded;
GO
