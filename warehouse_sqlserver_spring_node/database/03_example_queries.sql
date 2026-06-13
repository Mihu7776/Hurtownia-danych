USE S;
GO

SELECT * FROM dbo.v_dashboard_summary;
SELECT * FROM dbo.v_sales_by_month ORDER BY year_number, month_name;
SELECT * FROM dbo.v_top_drugs;
SELECT * FROM dbo.v_top_manufacturers;
SELECT * FROM dbo.v_city_sales;
SELECT * FROM dbo.v_open_source_summary;
GO
