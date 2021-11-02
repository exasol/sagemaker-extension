# User Guide

Exasol Sagemaker Extension provides a Python library and Exasol Scripts and UDFs that trains data stored in Exasol using AWS SageMaker Autopilot service.

The extension basically exports a given Exasol table into AWS S3, and then triggers Machine Learning training using the AWS Autopilot service with the specified parameters. In addition, the training status can be polled using the auxiliary scripts provided within the scope of the project.

## Table of Contents

- [Getting Started](#getting-started)
- [Installation](#installation)
- [Deployment](#deployment)
- [Execution of Training](#execution-of-training)
- [Polling Training Status](#polling-training-status)


## Getting Started
- Exasol DB
  - The Exasol cluster must already be running with version 7.1 or later.
- AWS connection from Exasol 
  - An Exasol connection object must be created with AWS credentials that has AWS Sagemaker Execution permission. An example connection object is created as follows. For more information please check [Create Connection in Exasol](https://docs.exasol.com/sql/create_connection.htm?Highlight=connection):  
  ```buildoutcfg
  CREATE OR REPLACE  CONNECTION <CONNECTION_NAME>
      TO '<S3_BUCKET_ADDRESS>'
      USER '<AWS_KEY_ID>'
      IDENTIFIED BY '<AWS_ACCESS_KEY>'
  ```  


## Installation
- Install the packaged sagemaker-extension project as follows:
```buildoutcfg
pip install exasol_sagemaker_extension-0.1.0.whl
```


## Deployment
- Deploy all necessary scripts installed in the previous step to the specified  ```SCHEMA``` in Exasol using the following python cli command: 
```buildoutcfg
python -m exasol_sagemaker_extension.deployment.deploy_cli \
    --host <DB_HOST> \ 
    --port <DB_PORT> \
    --user <DB_USER> \
    --pass <PASS> \
    --schema <SCHEMA>
```



## Execution of Training
### Execute Autopilot Training
- Example usage of AWS Sagemaker Autopilot service in Exasol is as follows. `SME_TRAIN_WITH_SAGEMAKER_AUTOPILOT` UDF script takes the necessary parameters as json string and triggers the Autopilot training on the selected table with the specified parameters:
```buildoutcfg
EXECUTE SCRIPT SME_TRAIN_WITH_SAGEMAKER_AUTOPILOT('{
    "model_name"                                : "<model_name>",
    "aws_credentials_connection_name"           : "<aws_credentials_connection_name>",
    "aws_region"                                : "<aws_region>",
    "iam_sagemaker_role"                        : "<iam_sagemaker_role>", 
    "s3_bucket_uri"                             : "<s3_bucket_uri>",
    "s3_output_path"                            : "<s3_output_path>",
    "input_schema_name"                         : "<input_schema_name>",
    "input_table_or_view_name"                  : "<input_table_or_view_name>",
    "target_attribute_name"                     : "<target_attribute_name>",
    "problem_type"                              : "<problem_type>",
    "objective"                                 : "<objective>",
    "max_runtime_for_automl_job_in_seconds"     : <max_runtime_for_automl_job_in_seconds>,
    "max_candidates"                            : <max_candidates>,
    "max_runtime_per_training_job_in_seconds"   : <max_runtime_per_training_job_in_seconds>
}')
```

- Parameters:
  - ```model_name```: A unique model name that will be internally concantaned with the execution date time.
  - ```aws_credentials_connection_name```: The name of an Exasol connection object with AWS credentials. 
  - ```aws_region```: AWS region credential.
  - ```iam_sagemaker_role```: The ARN of AWS IAM identity having  the Sagemaker execution privileges.
  - ```s3_bucket_uri```: The URI to an AWS S3 Bucket to which the table gets exported for training. 
  - ```s3_output_path``` : The path in the AWS S3 Bucket to which the table gets exported for training. 
  - ```input_schema_name```: The schema name including the exported table for training.
  - ```input_table_or_view_name```: The name of exported table or view for training.
  - ```target_attribute_name```: The name of the column to which the Autopilot training will fit.
  - ```objective (optional)```: The evaluation metric measuring prediction quality of an Autopilot training model. For more information please check [Autopilot API reference guide](https://docs.aws.amazon.com/sagemaker/latest/dg/autopilot-reference.html).
  - ```max_runtime_for_automl_job_in_seconds (optional)```: The maximum runtime in seconds required to complete an Autopilot job. If a  job exceeds the maximum runtime, the job is stopped automatically. For more information please check [Autopilot API reference guide](https://docs.aws.amazon.com/sagemaker/latest/dg/autopilot-reference.html).
  - ```max_candidates (optional)```: The maximum number of model candidates that a job is allowed to create. For more information please check [Autopilot API reference guide](https://docs.aws.amazon.com/sagemaker/latest/dg/autopilot-reference.html).
  - ```max_runtime_per_training_job_in_seconds (optional)```:  The maximum runtime in seconds that each job is allowed to run. For more information please check [Autopilot API reference guide](https://docs.aws.amazon.com/sagemaker/latest/dg/autopilot-reference.html).


### Metadata of Autopitlot Job
- The following metadata information of each executed Autopilot job is inserted into `SME_METADATA_AUTOPILOT_JOBS` table in Exasol:
  - DATETIME
  - JOB_NAME
  - AWS_CREDENTIALS_CONNECTION_NAME
  - IAM_SAGEMAKER_ROLE
  - S3_BUCKET_URI
  - S3_OUTPUT_PATH
  - TARGET_ATTRIBUTE_NAME
  - PROBLEM_TYPE
  - OBJECTIVE
  - MAX_RUNTIME_FOR_AUTOML_JOB_IN_SECONDS
  - MAX_CANDIDATES
  - MAX_RUNTIME_PER_TRAINING_JOB_IN_SECONDS
  - SESSION_ID         
  - SCRIPT_USER


## Polling Training Status
- You can poll the status of a training Autopilot job with the `SME_POLL_SAGEMAKER_AUTOPILOT_JOB_STATUS` UDF script. Example usage is given below:
```buildoutcfg
EXECUTE SCRIPT SME_POLL_SAGEMAKER_AUTOPILOT_JOB_STATUS(
    job_name, 
    aws_credentials_connection_name, 
    aws_region
)
```

- Parameters:
  - ```job_name```: A unique Autopilot job name.
  - ```aws_credentials_connection_name```:   The name of an Exasol connection object with AWS credentials with AWS credentials having Sagemaker execution permission.
  - ```aws_region```: AWS region credential.


- The polling script specifies the job statuses in two columns. These columns and their status information provided by AWS Sagemaker are given below (For more information see the [description of training job](https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_DescribeTrainingJob.html)): 
  - Job status: It provides the status of the training job. Provided training job statuses: 
    - ```InProgress | Completed | Failed | Stopping | Stopped```
  - seconday job statuses : It provides detailed information about the state of the training job. Provided the states of training job: 
    - ```Starting | AnalyzingData | FeatureEngineering | ModelTuning | MaxCandidatesReached | Failed | Stopped | MaxAutoMLJobRuntimeReached | Stopping | CandidateDefinitionsGenerated | GeneratingExplainabilityReport | Completed | ExplainabilityError | DeployingModel | ModelDeploymentError.```

