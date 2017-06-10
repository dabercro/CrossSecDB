--
-- TODO: Create trigger that prevents source from being empty (because we are naughty when it comes to docs)
--

CREATE TEMPORARY TABLE template (
  sample VARCHAR(144) PRIMARY KEY,
  cross_section DOUBLE UNSIGNED,
  last_updated DATETIME,
  source VARCHAR(512) NOT NULL,
  comments VARCHAR(2048)
);

--
-- TODO: Rename existing tables into backups instead of dropping them, just in case
--

DROP TABLE IF EXISTS xs_7TeV;
DROP TABLE IF EXISTS xs_8TeV;
DROP TABLE IF EXISTS xs_13TeV;
DROP TABLE IF EXISTS xs_14TeV;

CREATE TABLE xs_7TeV LIKE template;
CREATE TABLE xs_8TeV LIKE template;
CREATE TABLE xs_13TeV LIKE template;
CREATE TABLE xs_14TeV LIKE template;
