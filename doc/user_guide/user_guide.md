# User Guide

Exasol Sagemaker Extension provides a Python library that trains data stored in Exasol using AWS SageMaker Autopilot service.

The extension basically imports a given Exasol table into AWS S3, and then triggers Machine Learning training using the AWS Autopilot service with the specified parameters. In addition, the training status can be polled using the auxiliary scripts provided within the scope of the project.

## Table of Contents

- [1.Getting Started](#getting-started)
- [2.Installation](#installation)
- [3.Deployment](#deployment)
- [4.Execution of Training](#execution_of_training)
- [5.Polling Training Status](#preparing-exasol-table)


## 1.Getting Started
- Exasol 7.1 or newer running ...
  - ...
- Existence of an Exasol Connection created with AWS credentials that has AWS Sagemaker Execution permission
  - ...

## 2.Installation
### Clone Project
- clone project :
```buildoutcfg
git clone git@ ...
```

### Build language container
- run ./build_script...
- upload ./exaslct ..

### Build project
- run poetry build ...
- pip install dist/sagme..whl


## 3.Deployment
- All necessary scripts are deployed in specified Exasol DB 
```buildoutcfg
    python -m exasol_sagemaker_extension.deployment.deploy_cli \
        --host HOST \ 
        --port PORT \
        -- ...
```

Arguments:
- ```HOST``` Exasol DB host address
- ...

## 4.Execution of Training
### Execute Autopilot Trainig
```buildoutcfg
    EXECUTE SCRIPT SME_TRAIN_WITH_SAGEMAKER_AUTOPILOT('{
        "model_name"                                : "end2end",
        "aws_credentials_connection_name"           : "S3_CONNECTION",
        ...
    }')
```

Parameters:
- ```model_name``` the unique model name will be internally concantaned with the run datetime
- ```aws_credentials_connection_name``` Exasol connection name
- ...

### Metadata of Autopitlot Job
- The following metadata information of a running Autopilot job is inserted into _SME_METADATA_AUTOPILOT_JOBS_ table

    - datetime 
    - job name
    - aws_connection_name 
    - ....


## 5.Polling Training Status
- Poll status of Autopilot job ..
- job status and secondary job status provided by Sagemaker
  - job statuses: 
    - ```Completed, InProgress , Failed ...```
  - seconday job statuses : 
    - ```Starting, AnalyzingData, Modeltuning ...```
    
- Call pooling script as follows:
```buildoutcfg
    EXECUTE SCRIPT SME_POLL_SAGEMAKER_AUTOPILOT_JOB_STATUS(
        job_name, 
        aws_credentials_connection_name, 
        aws_region
    ) 
```

Parameters:
- ```job_name``` autopilot job name
- ```aws_credentials_connection_name``` Exasol connection name
- ...

