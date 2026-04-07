# SageMaker Extension 0.11.8, released 2026-04-07

Code name: Dependency update on top of 0.11.7.
## Security

Moved to sagemaker 3.

Replaced sagemaker SDK calls with boto3 in all `autopilot_utils` modules, as the sagemaker v3 package no longer provides the `Predictor` class and reorganised the `AutoML` API:

- `enpoint_deletion.py`: replaced `Predictor.delete_model()` / `delete_endpoint()` with explicit boto3 calls that describe the endpoint config to find associated models, then delete the endpoint, endpoint config, and each model.
- `enpoint_deployment.py`: replaced `AutoML.attach()` / `automl.deploy()` with `describe_auto_ml_job` to retrieve the best candidate and role, followed by explicit `create_model`, `create_endpoint_config`, `create_endpoint`, and an `endpoint_in_service` waiter.
- `status_polling.py`: replaced `AutoML.attach()` / `describe_auto_ml_job()` with a direct `sm_client.describe_auto_ml_job()` call.
- `model_prediction.py`: replaced `Predictor` with `CSVSerializer`/`CSVDeserializer` by using the `sagemaker-runtime` client's `invoke_endpoint` with `text/csv` content type and manual response parsing.
- `model_training.py`: replaced `AutoML(...).fit()` with `sm_client.create_auto_ml_job()`, mapping all optional parameters to the boto3 `AutoMLJobConfig.CompletionCriteria` structure.

Re-locked poetry.
