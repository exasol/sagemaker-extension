import pyexasol
import pytest
from exasol_sagemaker_extension.deployment.deploy_create_statements import \
    DeployCreateStatements

DB_CONNECTION_HOST = "127.0.0.1"
DB_CONNECTION_PORT = "9563"
DB_CONNECTION_USER = "sys"
DB_CONNECTION_PASS = "exasol"
DB_SCHEMA = "TESTSCHEMA"
AUTOPILOT_TRAINING_LUA_SCRIPT_NAME = "TRAIN_WITH_SAGEMAKER_AUTOPILOT"
AUTOPILOT_TRAINING_UDF_NAME = "AutopilotTrainingUDF"


@pytest.fixture(scope="session")
def db_conn():
    conn = pyexasol.connect(
        dsn=f"{DB_CONNECTION_HOST}:{DB_CONNECTION_PORT}",
        user=DB_CONNECTION_USER,
        password=DB_CONNECTION_PASS)

    return conn


def get_all_schemas(db_conn, ):
    query_all_schemas = """SELECT SCHEMA_NAME FROM EXA_ALL_SCHEMAS"""
    all_schemas = db_conn.execute(query_all_schemas).fetchall()
    return list(map(lambda x: x[0], all_schemas))


def get_all_scripts(db_conn):
    query_all_scripts = """SELECT SCRIPT_NAME FROM EXA_ALL_SCRIPTS"""
    all_scripts = db_conn.execute(query_all_scripts).fetchall()

    return list(map(lambda x: x[0], all_scripts))


def test_deploy_create_statements(db_conn):
    deployer = DeployCreateStatements(
        db_host=DB_CONNECTION_HOST,
        db_port=DB_CONNECTION_PORT,
        db_user=DB_CONNECTION_USER,
        db_pass=DB_CONNECTION_PASS,
        schema=DB_SCHEMA,
        to_print=False
    )

    deployer.run()

    all_schemas = get_all_schemas(db_conn)
    all_scripts = get_all_scripts(db_conn)

    assert DB_SCHEMA.upper() in all_schemas
    assert AUTOPILOT_TRAINING_LUA_SCRIPT_NAME.upper() in all_scripts
    assert AUTOPILOT_TRAINING_UDF_NAME.upper() in all_scripts