-- Insert a new Skey
INSERT INTO skeys (
	name, skey_group_key, skey_subgroup_key, skey_description_key,
	spindle_skey, orientation, flow_arrow, dimensioned,
	pcf_identification, idf_record, user_definable, flow_dependency,
	source_id, isogen_standard
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
