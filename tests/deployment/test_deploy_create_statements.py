import pytest
import exasol.bucketfs as bfs

from exasol_sagemaker_extension.deployment.deploy_create_statements import \
    DeployCreateStatements

DB_SCHEMA = "TEST_DEPLOY_SCHEMA"
AUTOPILOT_TRAINING_LUA_SCRIPT_NAME = \
    "SME_TRAIN_WITH_SAGEMAKER_AUTOPILOT"
AUTOPILOT_TRAINING_UDF_NAME = \
    "SME_AUTOPILOT_TRAINING_UDF"
AUTOPILOT_JOB_STATUS_POLLING_LUA_SCRIPT_NAME = \
    "SME_POLL_SAGEMAKER_AUTOPILOT_JOB_STATUS"
AUTOPILOT_JOB_STATUS_POLLING_UDF_NAME = \
    "SME_AUTOPILOT_JOB_STATUS_POLLING_UDF"


def get_all_schemas(db_conn, ):
    query_all_schemas = """SELECT SCHEMA_NAME FROM EXA_ALL_SCHEMAS"""
    all_schemas = db_conn.execute(query_all_schemas).fetchall()
    return list(map(lambda x: x[0], all_schemas))


def get_all_scripts(db_conn):
    query_all_scripts = """SELECT SCRIPT_NAME FROM EXA_ALL_SCRIPTS"""
    all_scripts = db_conn.execute(query_all_scripts).fetchall()

    return list(map(lambda x: x[0], all_scripts))


@pytest.mark.slow
def test_deploy_create_statements(backend, db_conn, deploy_params):

    # We validate the server certificate in SaaS, but not in the Docker DB
    cert_validation = backend == bfs.path.StorageBackend.saas
    DeployCreateStatements.create_and_run(**deploy_params, schema=DB_SCHEMA,
                                          use_ssl_cert_validation=cert_validation)

    all_schemas = get_all_schemas(db_conn)
    all_scripts = get_all_scripts(db_conn)

    assert DB_SCHEMA.upper() in all_schemas
    assert AUTOPILOT_TRAINING_LUA_SCRIPT_NAME.upper() in all_scripts
    assert AUTOPILOT_TRAINING_UDF_NAME.upper() in all_scripts
    assert AUTOPILOT_JOB_STATUS_POLLING_LUA_SCRIPT_NAME.upper() in all_scripts
    assert AUTOPILOT_JOB_STATUS_POLLING_UDF_NAME.upper() in all_scripts
