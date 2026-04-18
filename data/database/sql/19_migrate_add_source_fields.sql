-- Migration: add ISOGEN metadata and source tracking to skeys and spindles
-- Run once on existing databases

-- skeys: PCF identification string (e.g. 'FLANGE', 'VALVE', 'TEE')
ALTER TABLE skeys ADD COLUMN pcf_identification TEXT;

-- skeys: IDF record number(s) as text (e.g. '105', '65/0', '70/0/71/72')
ALTER TABLE skeys ADD COLUMN idf_record TEXT;

-- skeys: whether symbol geometry can be user-redefined (1=YES, 0=NO)
ALTER TABLE skeys ADD COLUMN user_definable INTEGER NOT NULL DEFAULT 1;

-- skeys: symbol follows flow direction dependency (1=Y, 0=N)
ALTER TABLE skeys ADD COLUMN flow_dependency INTEGER NOT NULL DEFAULT 0;

-- skeys: foreign key to symbol_sources (NULL = source unknown / built-in)
ALTER TABLE skeys ADD COLUMN source_id INTEGER REFERENCES symbol_sources(id) ON DELETE SET NULL;

-- skeys: 1 = defined by the ISOGEN standard, 0 = user/custom addition
ALTER TABLE skeys ADD COLUMN isogen_standard INTEGER NOT NULL DEFAULT 0;

-- spindles: same source tracking
ALTER TABLE spindles ADD COLUMN source_id INTEGER REFERENCES symbol_sources(id) ON DELETE SET NULL;
ALTER TABLE spindles ADD COLUMN isogen_standard INTEGER NOT NULL DEFAULT 0;
