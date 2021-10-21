import pyexasol
import pytest
import importlib_resources
from exasol_sagemaker_extension.deployment import constants


SCHEMA_NAME = "TEST_SCHEMA"
CREATE_SCRIPT_NAME = "AutopilotTrainingUDF".upper()


def open_schema(conn):
    queries = ["CREATE SCHEMA IF NOT EXISTS {schema_name}",
               "OPEN SCHEMA {schema_name}"]
    for query in queries:
        conn.execute(query.format(schema_name=SCHEMA_NAME))


@pytest.fixture(scope="session")
def setup_database(db_conn):
    open_schema(db_conn)
    return db_conn


def get_created_scripts(conn):
    exa_all_scripts_list = conn.export_to_list(
        "Select SCRIPT_NAME FROM EXA_ALL_SCRIPTS")
    return sum(exa_all_scripts_list, [])


def test_export_table(setup_database):
    db_conn = setup_database

    statement_str = constants.\
        CREATE_STATEMENT_AUTOPILOT_TRAINING_UDF_RESOURCE.read_text()
    db_conn.execute(statement_str)

    exa_all_created_scripts = get_created_scripts(db_conn)
    assert CREATE_SCRIPT_NAME in exa_all_created_scripts

