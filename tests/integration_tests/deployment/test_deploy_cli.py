from click.testing import CliRunner
from exasol.python_extension_common.cli.std_options import StdParams

from exasol_sagemaker_extension.deploy import deploy_command
from exasol_sagemaker_extension.deployment.language_container import export_slc

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


def _cli_params_to_args(cli_params) -> str:
    from typing import Any

    def arg_string(k: str, v: Any):
        k = k.replace("_", "-")
        if isinstance(v, bool):
            return f'--{k}' if v else f'--no-{k}'
        return f'--{k} "{v}"'

    return ' '.join(arg_string(k, v) for k, v in cli_params.items())


def test_deploy_cli_main(pyexasol_connection, database_std_params, bucketfs_std_params, tmp_path):

    # Bug in pytest-extension
    std_params = dict(database_std_params)
    std_params.update(bucketfs_std_params)
    cli_args = _cli_params_to_args(std_params)

    pyexasol_connection.execute(f'CREATE SCHEMA IF NOT EXISTS "{DB_SCHEMA}"')

    def std_param_to_opt(std_param: StdParams) -> str:
        # This method should be implemented in the StdParams
        return f'--{std_param.name.replace("_", "-")}'

    container_file = export_slc(str(tmp_path))

    args_string = (f'{cli_args} '
                   f'{std_param_to_opt(StdParams.schema)} "{DB_SCHEMA}" '
                   f'{std_param_to_opt(StdParams.container_file)} "{container_file}"')

    runner = CliRunner()
    result = runner.invoke(deploy_command, args=args_string, catch_exceptions=False)
    assert result.exit_code == 0

    all_schemas = get_all_schemas(pyexasol_connection)
    all_scripts = get_all_scripts(pyexasol_connection)

    assert DB_SCHEMA.upper() in all_schemas
    assert AUTOPILOT_TRAINING_LUA_SCRIPT_NAME.upper() in all_scripts
    assert AUTOPILOT_TRAINING_UDF_NAME.upper() in all_scripts
    assert AUTOPILOT_JOB_STATUS_POLLING_LUA_SCRIPT_NAME.upper() in all_scripts
    assert AUTOPILOT_JOB_STATUS_POLLING_UDF_NAME.upper() in all_scripts
    assert AUTOPILOT_ENDPOINT_DEPLOYMENT_LUA_SCRIPT_NAME.upper() in all_scripts
    assert AUTOPILOT_ENDPOINT_DEPLOYMENT_UDF_NAME.upper() in all_scripts
    assert AUTOPILOT_ENDPOINT_DELETION_LUA_SCRIPT_NAME in all_scripts
    assert AUTOPILOT_ENDPOINT_DELETION_UDF_NAME in all_scripts
