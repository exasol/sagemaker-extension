# User Guide

Exasol Sagemaker Extension provides a Python library together with Exasol Scripts 
and UDFs that train Machine Learning Models on data stored in Exasol using AWS SageMaker 
Autopilot service.

The extension exports a given Exasol table into AWS S3, and then triggers Machine Learning training
using the AWS Autopilot service with the specified parameters. The training status can be polled using
the auxiliary scripts provided within the scope of the project.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Deployment](#deployment)
- [Execution of Training](#execution-of-training)
- [Polling Training Status](#polling-training-status)
- [Prediction on AWS Sagemaker Endpoint](#prediction-on-aws-sageamker-endpoint)


## Prerequisites
- Exasol DB
  - The Exasol cluster must already be running with version 7.1 or later.


## Installation

### Install the Python Package
The Sagemaker Extension package can be installed using pip:
```shell
pip install exasol-sagemaker-extension
```

### Deploy the Extension to the Database
The Sagemaker Extension must be deployed to the database using the following command:
```shell
python -m exasol_sagemaker_extension.deploy <options>
```

The deployment includes the installation of the Script Language Container (SLC) and several
scripts. The SLC is a way to install the required programming language and necessary dependencies
in the Exasol Database so that UDF scripts can be executed. The version of the installed SLC must
match the version of the Sagemaker Extension Package. See [the latest release](https://github.com/exasol/sagemaker-extension/releases) on Github.

For information about the available options common to all Exasol extensions please refer to the
[documentation](https://github.com/exasol/python-extension-common/blob/0.8.0/doc/user_guide/user-guide.md) 
in the Exasol Python Extension Common package. 
In addition, this extension provides the following installation options:

| Option name         | Default | Comment                                        |
|:--------------------|:-------:|:-----------------------------------------------|
| [no-]deploy-slc     |  True   | Install SLC as part of the deployment          |
| [no-]deploy-scripts |  True   | Install scripts as part of the deployment      |
| [no-]to-print       |  False  | Print SQL statements instead of executing them |

### Create AWS Connection Object
Create an Exasol connection object with AWS credentials that have AWS Sagemaker Execution permission.
The connection will encapsulate the address of the AWS S3 bucket where the exported data will be stored. 
For more information please check the [Create Connection in Exasol](https://docs.exasol.com/sql/create_connection.htm?Highlight=connection) document.
Below is a template of the query that will create the required connection object. 
  ```buildoutcfg
  CREATE OR REPLACE  CONNECTION <CONNECTION_NAME>
      TO 'https://<S3_BUCKET_NAME>.s3.<AWS_REGION>.amazonaws.com'
      USER '<AWS_ACCESS_KEY_ID>'
      IDENTIFIED BY '<AWS_SECRET_ACCESS_KEY>'
  ```  

## Execution of Training
### Execute Autopilot Training
- Example usage of the AWS Sagemaker Autopilot service in Exasol is as follows. 
The `SME_TRAIN_WITH_SAGEMAKER_AUTOPILOT` UDF script takes the necessary parameters 
as json string and triggers the Autopilot training on the selected table with 
the specified parameters:
```buildoutcfg
EXECUTE SCRIPT SME_TRAIN_WITH_SAGEMAKER_AUTOPILOT('{
    "job_name"                                  : "<job_name>",
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
  - ```job_name```: A unique job name. It can also be treated as model_name since only one job is created for each model.
  - ```aws_credentials_connection_name```: The name of an [Exasol connection object](#aws-connection-object) with AWS credentials. 
  - ```aws_region```: The AWS region where the training should run.
  - ```iam_sagemaker_role```: The ARN of AWS IAM identity having  the Sagemaker execution privileges.
  - ```s3_bucket_uri```: The URI to an AWS S3 Bucket to which the table gets exported for training. This should have the form 's3://<S3_BUCKET_NAME>'.
  - ```s3_output_path``` : The path in the AWS S3 Bucket to which the table gets exported for training. 
  - ```input_schema_name```: The schema name including the exported table for training.
  - ```input_table_or_view_name```: The name of exported table or view for training.
  - ```target_attribute_name```: The name of the column to which the Autopilot training will fit.
  - ```objective (optional)```: The evaluation metric measuring prediction quality of an Autopilot training model. For more information please check [Autopilot API reference guide](https://docs.aws.amazon.com/sagemaker/latest/dg/autopilot-reference.html).
  - ```max_runtime_for_automl_job_in_seconds (optional)```: The maximum runtime in seconds required to complete an Autopilot job. If a  job exceeds the maximum runtime, the job is stopped automatically. For more information please check [Autopilot API reference guide](https://docs.aws.amazon.com/sagemaker/latest/dg/autopilot-reference.html).
  - ```max_candidates (optional)```: The maximum number of model candidates that a job is allowed to create. For more information please check [Autopilot API reference guide](https://docs.aws.amazon.com/sagemaker/latest/dg/autopilot-reference.html).
  - ```max_runtime_per_training_job_in_seconds (optional)```:  The maximum runtime in seconds that each job is allowed to run. For more information please check [Autopilot API reference guide](https://docs.aws.amazon.com/sagemaker/latest/dg/autopilot-reference.html).


### Metadata of Autopilot Job
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
- You can poll the status of a training Autopilot job with the 
`SME_POLL_SAGEMAKER_AUTOPILOT_JOB_STATUS` UDF script. Example usage is given below:
```buildoutcfg
EXECUTE SCRIPT SME_POLL_SAGEMAKER_AUTOPILOT_JOB_STATUS(
    job_name, 
    aws_credentials_connection_name, 
    aws_region
)
```

- Parameters:
  - ```job_name```: A unique Autopilot job name.
  - ```aws_credentials_connection_name```:   The name of an [Exasol connection object](#aws-connection-object) with AWS credentials.
  - ```aws_region```: The AWS region where the training should run.


- The polling script specifies the job statuses in two columns. These columns and their status information provided by AWS Sagemaker are given below (For more information see the [description of training job](https://docs.aws.amazon.com/sagemaker/latest/APIReference/API_DescribeTrainingJob.html)): 
  - Job status: It provides the status of the training job. Provided training job statuses: 
    - ```InProgress | Completed | Failed | Stopping | Stopped```
  - seconday job statuses : It provides detailed information about the state of the training job. Provided the states of training job: 
    - ```Starting | AnalyzingData | FeatureEngineering | ModelTuning | MaxCandidatesReached | Failed | Stopped | MaxAutoMLJobRuntimeReached | Stopping | CandidateDefinitionsGenerated | GeneratingExplainabilityReport | Completed | ExplainabilityError | DeployingModel | ModelDeploymentError.```


## Prediction on AWS Sagemaker Endpoint

In order to perform prediction on a trained Autopilot model, one of the methods 
is  to deploy the model to the real-time AWS endpoint. This extension provides 
Lua scripts for creating/deleting real-time endpoint and creates a model-specific 
UDF script for making real-time predictions.

### Creating Real-Time Endpoint
- Use `SME_DEPLOY_SAGEMAKER_AUTOPILOT_ENDPOINT` lua script to create an endpoint 
and deploy the best candidate model.  Example usage is given below:
```buildoutcfg
EXECUTE SCRIPT SME_DEPLOY_SAGEMAKER_AUTOPILOT_ENDPOINT(
    job_name, 
    endpoint_name,
    schema_name,
    instance_type,
    instance_count,
    aws_credentials_connection_name,
    aws_region
)
```

- Parameters
  - ```job_name```: A unique Autopilot job name.
  - ```endpoint_name```: A unique Endpoint name and the name of the prediction UDF.
  - ```schema_name```: The name of schema where the prediction UDF gets created.
  - ``` instance_type```: The EC2 instance type of the endpoint to deploy the Autopilot model to e.g., 'ml.m5.large'. For more information please check [Autopilot API reference guide](https://docs.aws.amazon.com/sagemaker/latest/dg/autopilot-reference.html).
  - ```instance_count```: The initial number of instances to run the endpoint on. For more information please check [Autopilot API reference guide](https://docs.aws.amazon.com/sagemaker/latest/dg/autopilot-reference.html).
  - ```aws_credentials_connection_name```:   The name of an [Exasol connection object](#aws-connection-object) with AWS credentials.
  - ```aws_region```: The AWS region where the deployment should run.


### Including Prediction into your Queries
- The Exasol SageMaker Extension  provides a prediction UDF script for each model, 
enabling you to perform prediction on the created endpoint.

- The name of the prediction script is the same as the name of the endpoint 
(`endpoint_name` ) specified when creating the endpoint. You can see how it works in an example scenario below:
  - Assume that the Autopilot model, which fits 2 columns (_COL1_, _COL2_) of 
  a table called _TEST_TABLE_, is deployed to a real-time endpoint called _PREDICT_VIA_ENDPOINT_.
  - Assume that the schema name is stated as _PRED_SCHEMA_ for which the prediction UDF 
  script will be installed while creating the endpoint.
    ```buildoutcfg
    SELECT PRED_SCHEMA.PREDICT_VIA_ENDPOINT(
      t.COL1, 
      t.COL2
    ) from TEST_TABLE as t
    ```
  - The prediction results are presented as a _PREDICTIONS_ column, by being 
  combined with the columns (_COL1_, _COL2_) used in model training. For example:

    | COL1       | COL2       | PREDICTIONS |
    | ---------- | ---------- | ----------- |
    | val1       | val2       | pred1       |
    | ...        | ...        | ...         |
  

### Deleting the Deployed Endpoint
- It is important to delete the endpoint created, when you are finished with 
the endpoint Otherwise, the endpoint will continue to be charged. You  can use 
the following Lua script to delete the endpoint and associated resources.

```buildoutcfg
EXECUTE SCRIPT SME_DELETE_SAGEMAKER_AUTOPILOT_ENDPOINT(
    endpoint_name, 
    aws_credentials_connection_name,
    aws_region
```

- Parameters
  - ```endpoint_name```: The name of endpoint to be deleted.
  - ```aws_credentials_connection_name```:   The name of an [Exasol connection object](#aws-connection-object) with AWS credentials.
  - ```aws_region```: The AWS region where the deletion should run.

