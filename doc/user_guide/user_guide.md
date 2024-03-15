# User Guide

Exasol Sagemaker Extension provides a Python library together with Exasol Scripts 
and UDFs that train Machine Learning Models on data stored in Exasol using AWS SageMaker 
Autopilot service.

The extension basically exports a given Exasol table into AWS S3, and then triggers 
Machine Learning training using the AWS Autopilot service with the specified parameters. 
In addition, the training status can be polled using the auxiliary scripts provided 
within the scope of the project.

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
### Install The Built Archive
- Install the packaged sagemaker-extension project as follows (Please check [the latest release](https://github.com/exasol/sagemaker-extension/releases/latest)):
```buildoutcfg
pip install exasol_sagemaker_extension.whl
```
### The Pre-built Language Container

This extension requires the installation of the language container for this 
extension to run. It can be installed in two ways: Quick and Customized 
installations

#### Quick Installation
The language container is downloaded and installed by executing the 
deployment script below with the desired version. Make sure the version matches with your installed version of the 
Sagemaker Extension Package. See [the latest release](https://github.com/exasol/sagemaker-extension/releases) on Github.

  ```buildoutcfg
  python -m exasol_sagemaker_extension.deploy language-container \
      --dsn <DB_HOST:DB_PORT> \
      --db-user <DB_USER> \
      --db-pass <DB_PASSWORD> \
      --bucketfs-name <BUCKETFS_NAME> \
      --bucketfs-host <BUCKETFS_HOST> \
      --bucketfs-port <BUCKETFS_PORT> \
      --bucketfs-user <BUCKETFS_USER> \
      --bucketfs-password <BUCKETFS_PASSWORD> \
      --bucketfs-use-https <USE_HTTPS_BOOL> \
      --bucket <BUCKETFS_NAME> \
      --path-in-bucket <PATH_IN_BUCKET> \
      --version <RELEASE_VERSION> \
      --ssl-cert-path <ssl-cert-path> \
      --use-ssl-cert-validation
  ```
The `--ssl-cert-path` is optional if your certificate is not in the OS truststore. 
The option `--use-ssl-cert-validation`is the default, you can disable it with `--no-use-ssl-cert-validation`.
Use caution if you want to turn certificate validation off as it potentially lowers the security of your 
Database connection.

By default, the above command will upload and activate the language container at the System level.
The latter requires you to have the System Privileges, as it will attempt to change DB system settings.
If such privileges cannot be granted the activation can be skipped by using the `--no-alter-system` option.
The command will then print two possible language activation SQL queries, which look like the following:
```sql
ALTER SESSION SET SCRIPT_LANGUAGES=...
ALTER SYSTEM SET SCRIPT_LANGUAGES=...
```
These queries represent two alternative ways of activating a language container. The first one activates the
container at the [Session level](https://docs.exasol.com/db/latest/sql/alter_session.htm). It doesn't require 
System Privileges. However, it must be run every time a new session starts. The second one activates the container
at the [System level](https://docs.exasol.com/db/latest/sql/alter_system.htm). It  needs to be run just once,
but it does require System Privileges. It may be executed by a database administrator. Please note, that changes 
made at the system level only become effective in new sessions, as described
[here](https://docs.exasol.com/db/latest/sql/alter_system.htm#microcontent1).

It is also possible to activate the language without repeatedly uploading the container. If the container
has already been uploaded one can use the `--no-upload-container` option to skip this step.

By default, overriding language activation is not permitted. If a language with the same alias has already 
been activated the command will result in an error. To override the activation, you can use the
`--allow-override` option.

#### Customized Installation
In this installation, you can install the desired or customized language 
container. In the following steps,  it is explained how to install the 
language container file released in GitHub Releases section.


##### Download Language Container
   - Please download the language container archive (*.tar.gz) from the Releases section. 
(see [the latest release](https://github.com/exasol/sagemaker-extension/releases/latest)).

##### Install Language Container
There are two ways to install the language container: (1) using a python script and (2) manual installation. See the next paragraphs for details.

  1. *Installation with Python Script*

     To install the language container, it is necessary to load the container 
     into the BucketFS and activate it in the database. The following command 
     performs this setup using the python script provided with this library:

      ```buildoutcfg
      python -m exasol_sagemaker_extension.deploy language-container
          --dsn <DB_HOST:DB_PORT> \
          --db-user <DB_USER> \
          --db-pass <DB_PASSWORD> \
          --bucketfs-name <BUCKETFS_NAME> \
          --bucketfs-host <BUCKETFS_HOST> \
          --bucketfs-port <BUCKETFS_PORT> \
          --bucketfs-user <BUCKETFS_USER> \
          --bucketfs-password <BUCKETFS_PASSWORD> \
          --bucket <BUCKETFS_NAME> \
          --path-in-bucket <PATH_IN_BUCKET> \
          --container-file <path/to/language_container_name.tar.gz>       
      ```
     Please note, that all considerations described in the Quick Installation 
     section are still applicable.


  2. *Manual Installation*

     In the manual installation, the pre-built container should be firstly 
     uploaded into BucketFS. In order to do that, you can use 
     either a [http(s) client](https://docs.exasol.com/database_concepts/bucketfs/file_access.htm) 
     or the [bucketfs-client](https://github.com/exasol/bucketfs-client). 
     The following command uploads a given container into BucketFS through curl 
     command, an http(s) client: 
      ```shell
      curl -vX PUT -T \ 
          "<CONTAINER_FILE>" 
          "http://w:<BUCKETFS_WRITE_PASSWORD>@<BUCKETFS_HOST>:<BUCKETFS_PORT>/<BUCKETFS_NAME>/<PATH_IN_BUCKET><CONTAINER_FILE>"
      ```

      Please note that specifying the password on command line will make your shell record the password in the history. To avoid leaking your password please consider to set an environment variable. The following examples sets environment variable `BUCKETFS_WRITE_PASSWORD`:
      ```shell 
        read -sp "password: " BUCKETFS_WRITE_PASSWORD
      ```

      Secondly, the uploaded container should be activated through adjusting 
      the session parameter `SCRIPT_LANGUAGES`. As it was mentioned before, the activation can be scoped
      either session-wide (`ALTER SESSION`) or system-wide (`ALTER SYSTEM`). 
      The following example query activates the container session-wide:

      ```sql
      ALTER SESSION SET SCRIPT_LANGUAGES=\
      PYTHON3_SME=localzmq+protobuf:///<BUCKETFS_NAME>/<BUCKET_NAME>/<PATH_IN_BUCKET><CONTAINER_NAME>/?\
              lang=python#buckets/<BUCKETFS_NAME>/<BUCKET_NAME>/<PATH_IN_BUCKET><CONTAINER_NAME>/\
              exaudf/exaudfclient_py3
      ```
     

### Scripts Deployment
- Deploy all necessary scripts installed in the previous step to the specified  ```SCHEMA``` in Exasol using the following python cli command: 
```buildoutcfg
python -m exasol_sagemaker_extension.deployment.deploy_cli \
    --host <DB_HOST> \ 
    --port <DB_PORT> \
    --user <DB_USER> \
    --pass <PASS> \
    --schema <SCHEMA>
```


### AWS Connection Object
  - Create an Exasol connection object with AWS credentials that has 
AWS Sagemaker Execution permission. The connection will encapsulate the address of the AWS S3 bucket where the exported data will be stored. 
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

