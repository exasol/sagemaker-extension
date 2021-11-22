CREATE TABLE IF NOT EXISTS "SME_METADATA_AUTOPILOT_JOBS" (
	datetime TIMESTAMP NOT NULL,
	job_name VARCHAR(32) PRIMARY KEY,
	aws_credentials_connection_name VARCHAR(200) NOT NULL,
	iam_sagemaker_role VARCHAR(200) NOT NULL,
	s3_bucket_uri VARCHAR(200) NOT NULL,
	s3_output_path VARCHAR(100) NOT NULL,
	target_attribute_name VARCHAR(100) NOT NULL,
	problem_type VARCHAR(100),
	objective VARCHAR(100),
	max_runtime_for_automl_job_in_seconds INT,
	max_candidates INT,
	max_runtime_per_training_job_in_seconds INT,
	session_id DECIMAL(20,0) NOT NULL,
	script_user VARCHAR(100) NOT NULL,
	column_names VARCHAR(2000000) NOT NULL,
	column_types VARCHAR(2000000) NOT NULL
)