--
-- TODO: Create trigger that prevents source from being empty (because we are naughty when it comes to docs)
--

CREATE TEMPORARY TABLE template (
  sample VARCHAR(144) NOT NULL,
  cross_section DOUBLE UNSIGNED NOT NULL,
  last_updated DATETIME NOT NULL,
  source VARCHAR(512) NOT NULL,
  comments VARCHAR(2048),
  PRIMARY KEY (sample)
);

--
-- TODO: Rename existing tables into backups instead of dropping them, just in case.
--       Though you only should use this file for fresh install and tests.
--

DROP TABLE IF EXISTS xs_7TeV;
DROP TABLE IF EXISTS xs_8TeV;
DROP TABLE IF EXISTS xs_13TeV;
DROP TABLE IF EXISTS xs_14TeV;

CREATE TABLE xs_7TeV LIKE template;
CREATE TABLE xs_8TeV LIKE template;
CREATE TABLE xs_13TeV LIKE template;
CREATE TABLE xs_14TeV LIKE template;

ALTER TABLE template DROP PRIMARY KEY;
ALTER TABLE template ADD PRIMARY KEY (sample, last_updated);

DROP TABLE IF EXISTS xs_7TeV_history;
DROP TABLE IF EXISTS xs_8TeV_history;
DROP TABLE IF EXISTS xs_13TeV_history;
DROP TABLE IF EXISTS xs_14TeV_history;

CREATE TABLE xs_7TeV_history LIKE template;
CREATE TABLE xs_8TeV_history LIKE template;
CREATE TABLE xs_13TeV_history LIKE template;
CREATE TABLE xs_14TeV_history LIKE template;
