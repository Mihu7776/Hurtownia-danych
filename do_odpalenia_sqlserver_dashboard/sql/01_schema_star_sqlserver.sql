
USE S;
GO



IF OBJECT_ID(N'dbo.source_drug_events', N'U') IS NOT NULL DROP TABLE dbo.source_drug_events;
IF OBJECT_ID(N'dbo.source_ndc_products', N'U') IS NOT NULL DROP TABLE dbo.source_ndc_products;
IF OBJECT_ID(N'dbo.source_metadata', N'U') IS NOT NULL DROP TABLE dbo.source_metadata;
GO

CREATE TABLE dbo.source_metadata (
  source_key NVARCHAR(80) NOT NULL PRIMARY KEY,
  source_name NVARCHAR(255) NOT NULL,
  source_url NVARCHAR(MAX) NOT NULL,
  records_loaded INT NOT NULL DEFAULT 0,
  total_available INT NULL,
  fetched_at NVARCHAR(40) NULL
);

CREATE TABLE dbo.source_ndc_products (
  product_ndc NVARCHAR(80) NOT NULL PRIMARY KEY,
  product_type_name NVARCHAR(MAX) NULL,
  proprietary_name NVARCHAR(MAX) NULL,
  nonproprietary_name NVARCHAR(MAX) NULL,
  labeler_name NVARCHAR(255) NULL,
  dosage_form NVARCHAR(MAX) NULL,
  route NVARCHAR(MAX) NULL,
  marketing_category NVARCHAR(MAX) NULL,
  start_marketing_date NVARCHAR(20) NULL,
  listing_expiration_date NVARCHAR(20) NULL
);

CREATE INDEX IX_source_ndc_labeler ON dbo.source_ndc_products(labeler_name);

CREATE TABLE dbo.source_drug_events (
  safetyreportid NVARCHAR(80) NOT NULL PRIMARY KEY,
  receivedate NVARCHAR(20) NULL,
  serious BIT NULL,
  patientsex NVARCHAR(20) NULL,
  reaction NVARCHAR(MAX) NULL,
  medicinalproduct NVARCHAR(MAX) NULL,
  brand_name NVARCHAR(MAX) NULL,
  manufacturer_name NVARCHAR(MAX) NULL
);

GO
