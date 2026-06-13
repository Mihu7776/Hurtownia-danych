-- MySQL 8 star schema for the drug sales dashboard.
-- Target database: drug_dashboard

CREATE DATABASE IF NOT EXISTS drug_dashboard
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE drug_dashboard;

SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS factDrug;
DROP TABLE IF EXISTS dimCity;
DROP TABLE IF EXISTS dimConTh;
DROP TABLE IF EXISTS dimDrug;
DROP TABLE IF EXISTS dimDrugType;
DROP TABLE IF EXISTS dimMan;
DROP TABLE IF EXISTS dimTime;
DROP TABLE IF EXISTS import_raw;
DROP TABLE IF EXISTS tempStd;
DROP TABLE IF EXISTS source_metadata;
DROP TABLE IF EXISTS source_ndc_products;
DROP TABLE IF EXISTS source_drug_events;
SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE dimCity (
  id INT AUTO_INCREMENT PRIMARY KEY,
  dimName VARCHAR(1000) NOT NULL,
  UNIQUE KEY uq_dimCity_name (dimName)
);

CREATE TABLE dimConTh (
  id INT AUTO_INCREMENT PRIMARY KEY,
  dimName VARCHAR(1000) NOT NULL,
  UNIQUE KEY uq_dimConTh_name (dimName)
);

CREATE TABLE dimDrug (
  id INT AUTO_INCREMENT PRIMARY KEY,
  dimName VARCHAR(1000) NOT NULL,
  UNIQUE KEY uq_dimDrug_name (dimName)
);

CREATE TABLE dimDrugType (
  id INT AUTO_INCREMENT PRIMARY KEY,
  dimName VARCHAR(1000) NOT NULL,
  UNIQUE KEY uq_dimDrugType_name (dimName)
);

CREATE TABLE dimMan (
  id INT AUTO_INCREMENT PRIMARY KEY,
  dimName VARCHAR(1000) NOT NULL,
  UNIQUE KEY uq_dimMan_name (dimName)
);

CREATE TABLE dimTime (
  id INT AUTO_INCREMENT PRIMARY KEY,
  timeDay DATE NOT NULL,
  timeWeekDay INT NOT NULL,
  timeWeekNum INT NOT NULL,
  timeMonth VARCHAR(7),
  timeYear INT,
  UNIQUE KEY uq_dimTime_day (timeDay)
);

CREATE TABLE factDrug (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  dimCity_id INT,
  dimConTh_id INT,
  dimDrug_id INT,
  dimDrugType_id INT,
  dimMan_id INT,
  dimTime_id INT,
  is_refunded BOOLEAN NOT NULL,
  cntDrug INT NOT NULL,
  sumDrug DOUBLE NOT NULL,
  avgDrug DOUBLE NOT NULL,
  minDrug DOUBLE NOT NULL,
  maxDrug DOUBLE NOT NULL,
  CONSTRAINT fk_fact_city FOREIGN KEY (dimCity_id) REFERENCES dimCity(id),
  CONSTRAINT fk_fact_condition FOREIGN KEY (dimConTh_id) REFERENCES dimConTh(id),
  CONSTRAINT fk_fact_drug FOREIGN KEY (dimDrug_id) REFERENCES dimDrug(id),
  CONSTRAINT fk_fact_type FOREIGN KEY (dimDrugType_id) REFERENCES dimDrugType(id),
  CONSTRAINT fk_fact_manufacturer FOREIGN KEY (dimMan_id) REFERENCES dimMan(id),
  CONSTRAINT fk_fact_time FOREIGN KEY (dimTime_id) REFERENCES dimTime(id),
  KEY idx_fact_city (dimCity_id),
  KEY idx_fact_condition (dimConTh_id),
  KEY idx_fact_drug (dimDrug_id),
  KEY idx_fact_type (dimDrugType_id),
  KEY idx_fact_manufacturer (dimMan_id),
  KEY idx_fact_time (dimTime_id),
  KEY idx_fact_refunded (is_refunded)
);

CREATE TABLE import_raw (
  Transaction_ID TEXT,
  Sale_Timestamp TEXT,
  Manufacturer TEXT,
  Drug_Name TEXT,
  Price TEXT,
  Drug_Type TEXT,
  Is_Refunded TEXT,
  Condition_Treated TEXT,
  City TEXT
);

CREATE TABLE tempStd (
  Sale_Timestamp DATETIME,
  Manufacturer VARCHAR(100),
  Drug_Name VARCHAR(100),
  Price DECIMAL(10, 2),
  Drug_Type VARCHAR(50),
  Is_Refunded BOOLEAN,
  Condition_Treated VARCHAR(100),
  City VARCHAR(100)
);

CREATE TABLE source_metadata (
  source_key VARCHAR(80) PRIMARY KEY,
  source_name VARCHAR(255) NOT NULL,
  source_url TEXT NOT NULL,
  records_loaded INT NOT NULL DEFAULT 0,
  total_available INT,
  fetched_at VARCHAR(40)
);

CREATE TABLE source_ndc_products (
  product_ndc VARCHAR(80) PRIMARY KEY,
  product_type_name VARCHAR(255),
  proprietary_name VARCHAR(255),
  nonproprietary_name VARCHAR(255),
  labeler_name VARCHAR(255),
  dosage_form VARCHAR(255),
  route TEXT,
  marketing_category VARCHAR(255),
  start_marketing_date VARCHAR(20),
  listing_expiration_date VARCHAR(20),
  KEY idx_ndc_labeler (labeler_name)
);

CREATE TABLE source_drug_events (
  safetyreportid VARCHAR(80) PRIMARY KEY,
  receivedate VARCHAR(20),
  serious BOOLEAN,
  patientsex VARCHAR(20),
  reaction VARCHAR(255),
  medicinalproduct VARCHAR(255),
  brand_name VARCHAR(255),
  manufacturer_name VARCHAR(255),
  KEY idx_event_reaction (reaction),
  KEY idx_event_product (medicinalproduct)
);
