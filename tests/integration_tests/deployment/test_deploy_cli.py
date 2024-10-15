from click.testing import CliRunner
from exasol.python_extension_common.cli.std_options import StdParams, get_cli_arg

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


def test_deploy_cli(pyexasol_connection, cli_args):

    pyexasol_connection.execute(f'CREATE SCHEMA IF NOT EXISTS "{DB_SCHEMA}"')

    with export_slc() as container_file:
        args_string = ' '.join([cli_args, get_cli_arg(StdParams.schema, DB_SCHEMA),
                                get_cli_arg(StdParams.container_file, container_file)])
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
