import pyexasol
import pytest

SQL_CREATE_STATEMENT_FILE_PATH = "./scripts/create_statement_training.sql"
DB_CONNECTION_ADDR = "127.0.0.1:9563"
DB_CONNECTION_USER = "sys"
DB_CONNECTION_PASS = "exasol"
SCHEMA_NAME = "TEST_SCHEMA"
CREATE_SCRIPT_NAME = "AutopilotTrainingUDF".upper()


def open_schema(conn):
    queries = ["CREATE SCHEMA IF NOT EXISTS {schema_name}",
               "OPEN SCHEMA {schema_name}"]
    for query in queries:
        conn.execute(query.format(schema_name=SCHEMA_NAME))


def get_schema_name(conn):
    query_create_script = "CREATE OR REPLACE SCRIPT get_schema_name () " \
                          "AS output(exa.meta.script_schema)"
    conn.execute(query_create_script)

    query_run_script = "EXECUTE SCRIPT get_schema_name () WITH OUTPUT"
    return conn.execute(query_run_script).fetchval()


@pytest.fixture(scope="session")
def setup_database():
    conn = pyexasol.connect(
        dsn=DB_CONNECTION_ADDR,
        user=DB_CONNECTION_USER,
        password=DB_CONNECTION_PASS)

    global schema_name

    open_schema(conn)
    schema_name = get_schema_name(conn)
    return conn


def get_created_scripts(conn):
    exa_all_scripts_list = conn.export_to_list(
        "Select SCRIPT_NAME FROM EXA_ALL_SCRIPTS")
    return sum(exa_all_scripts_list, [])


def test_export_table(setup_database):
    db_conn = setup_database

    with open(SQL_CREATE_STATEMENT_FILE_PATH) as f:
        statement_str = f.read()
    statement_str = statement_str.format(SCHEMA_NAME=schema_name)
    db_conn.execute(statement_str)

    exa_all_created_scripts = get_created_scripts(db_conn)
    assert CREATE_SCRIPT_NAME in exa_all_created_scripts



