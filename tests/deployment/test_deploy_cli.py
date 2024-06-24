from __future__ import annotations
from typing import Any

import pytest
from click.testing import CliRunner
import exasol.bucketfs as bfs

from exasol_sagemaker_extension.deployment import deploy_cli

DB_SCHEMA = "TEST_CLI_SCHEMA"
AUTOPILOT_TRAINING_LUA_SCRIPT_NAME = \
    "SME_TRAIN_WITH_SAGEMAKER_AUTOPILOT"
AUTOPILOT_TRAINING_UDF_NAME = \
    "SME_AUTOPILOT_TRAINING_UDF"
AUTOPILOT_JOB_STATUS_POLLING_LUA_SCRIPT_NAME = \
    "SME_POLL_SAGEMAKER_AUTOPILOT_JOB_STATUS"
AUTOPILOT_JOB_STATUS_POLLING_UDF_NAME = \
    "SME_AUTOPILOT_JOB_STATUS_POLLING_UDF"
AUTOPILOT_ENDPOINT_DEPLOYMENT_LUA_SCRIPT_NAME = \
    "SME_DEPLOY_SAGEMAKER_AUTOPILOT_ENDPOINT"
AUTOPILOT_ENDPOINT_DEPLOYMENT_UDF_NAME = \
    "SME_AUTOPILOT_ENDPOINT_DEPLOYMENT_UDF"
AUTOPILOT_ENDPOINT_DELETION_LUA_SCRIPT_NAME = \
    "SME_DELETE_SAGEMAKER_AUTOPILOT_ENDPOINT"
AUTOPILOT_ENDPOINT_DELETION_UDF_NAME = \
    "SME_AUTOPILOT_ENDPOINT_DELETION_UDF"


def get_all_schemas(db_conn):
    query_all_schemas = """SELECT SCHEMA_NAME FROM EXA_ALL_SCHEMAS"""
    all_schemas = db_conn.execute(query_all_schemas).fetchall()
    return list(map(lambda x: x[0], all_schemas))


def get_all_scripts(db_conn):
    query_all_scripts = """SELECT SCRIPT_NAME FROM EXA_ALL_SCRIPTS"""
    all_scripts = db_conn.execute(query_all_scripts).fetchall()

    return list(map(lambda x: x[0], all_scripts))


@pytest.mark.parametrize("db_conn,deploy_params", [
    (bfs.path.StorageBackend.onprem, bfs.path.StorageBackend.onprem),
    (bfs.path.StorageBackend.saas, bfs.path.StorageBackend.saas)
], indirect=True)
def test_deploy_cli_main(db_conn, deploy_params):

    args_list: list[Any] = []
    for param_name, param_value in deploy_params.items():
        args_list.append(f'--{param_name}')
        args_list.append(param_value)

    runner = CliRunner()
    result = runner.invoke(deploy_cli.main, args_list)
    assert result.exit_code == 0

    all_schemas = get_all_schemas(db_conn)
    all_scripts = get_all_scripts(db_conn)

    assert DB_SCHEMA.upper() in all_schemas
    assert AUTOPILOT_TRAINING_LUA_SCRIPT_NAME.upper() in all_scripts
    assert AUTOPILOT_TRAINING_UDF_NAME.upper() in all_scripts
    assert AUTOPILOT_JOB_STATUS_POLLING_LUA_SCRIPT_NAME.upper() in all_scripts
    assert AUTOPILOT_JOB_STATUS_POLLING_UDF_NAME.upper() in all_scripts
    assert AUTOPILOT_ENDPOINT_DEPLOYMENT_LUA_SCRIPT_NAME.upper() in all_scripts
    assert AUTOPILOT_ENDPOINT_DEPLOYMENT_UDF_NAME.upper() in all_scripts
    assert AUTOPILOT_ENDPOINT_DELETION_LUA_SCRIPT_NAME in all_scripts
    assert AUTOPILOT_ENDPOINT_DELETION_UDF_NAME in all_scripts
