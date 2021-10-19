import pytest
import pyexasol
import json
import os.path
import localstack_client.session
import importlib_resources

TMP_DIR = "/tmp"
EXPORTING_CREATE_SCRIPT_PATH = os.path.join(
    TMP_DIR, "create_statement_exporting.sql")

DB_CONNECTION_ADDR = "127.0.0.1:9563"
DB_CONNECTION_USER = "sys"
DB_CONNECTION_PASS = "exasol"
AWS_IP_ADDR = "192.168.0.2"
AWS_KEY_ID = ""
AWS_ACCESS_KEY = ""
AWS_S3_URI = f"https://{AWS_IP_ADDR}:4566"


INPUT_DICT = {
    "model_name": "todo_model",
    "input_schema_name": "INTEGRATION_TEST_SCHEMA",
    "input_table_or_view_name": "TEST_TABLE",
    "aws_credentials_connection_name": "S3_CONNECTION",
    "s3_bucket_uri": "https://exasol-sagemaker-extension.s3.amazonaws.com",
    "s3_output_path": "integrationtestbucket",
    "iam_sagemaker_role": "todo_ExecuteSageMakerRole",
    "target_attribute_name": "todo_target",
    "problem_type": "todo_regression",
    "max_runtime_for_automl_job_in_seconds": 3000,
    "max_runtime_per_training_job_in_seconds": 300,
    "max_candidates": 100,
    "model_info_schema_name": "todo_INFO_SCHEMA",
    "model_info_table_name": "todo_INFO_TABLE",
    "objective": "todo_mean absolute error",
    "aws_tags": "todo"
}


def open_schema(conn):
    queries = ["CREATE SCHEMA IF NOT EXISTS {schema_name}",
               "OPEN SCHEMA {schema_name}"]
    for query in queries:
        conn.execute(query.format(schema_name=INPUT_DICT["input_schema_name"]))


def create_aws_connection(conn):
    query = "CREATE OR REPLACE  CONNECTION {aws_conn_name} TO '{aws_s3_uri}' " \
            "USER '{aws_key_id}' IDENTIFIED BY '{aws_access_key}'"\
        .format(aws_conn_name=INPUT_DICT["aws_credentials_connection_name"],
                aws_s3_uri=AWS_S3_URI,
                aws_key_id=AWS_KEY_ID,
                aws_access_key=AWS_ACCESS_KEY)
    print(query)
    conn.execute(query)


def create_scripts(conn):
    with open(EXPORTING_CREATE_SCRIPT_PATH, "r") as file:
        statement_str = file.read()
    conn.execute(statement_str)
    print("create statement script is executed!")


def create_table(conn, table_name):
    query = "CREATE OR REPLACE TABLE {table_name} " \
            "(col1 INTEGER, col2 INTEGER)".\
        format(table_name=table_name)
    conn.execute(query)


def insert_into_table(conn, table_name):
    values = ",".join([f"({i}, {i * 10})" for i in range(1, 11)])
    query = "INSERT INTO {table_name} VALUES {values}".\
        format(table_name=table_name, values=values)
    print(query)
    conn.execute(query)


def create_s3_bucket():
    session = localstack_client.session.Session(
        localstack_host='{ip_addr}'.format(ip_addr=AWS_IP_ADDR))
    s3_client = session.client('s3')
    s3_client.create_bucket(Bucket=INPUT_DICT["s3_output_path"])


@pytest.fixture(scope="session")
def setup_database():
    conn = pyexasol.connect(
        dsn=DB_CONNECTION_ADDR,
        user=DB_CONNECTION_USER,
        password=DB_CONNECTION_PASS)

    open_schema(conn)
    create_aws_connection(conn)
    create_scripts(conn)
    create_table(conn, table_name=INPUT_DICT["input_table_or_view_name"])
    insert_into_table(conn, table_name=INPUT_DICT["input_table_or_view_name"])
    create_s3_bucket()
    return conn


def get_export_to_s3_query():
    return "EXECUTE SCRIPT INTEGRATION_TEST_SCHEMA.{script_name}" \
           "('{json_str}')".\
        format(script_name="TRAIN_WITH_SAGEMAKER_AUTOPILOT",
               json_str=json.dumps(INPUT_DICT))


def get_import_from_s3_query(import_table_name):
    s3_file_path = os.path.join(
        INPUT_DICT["s3_output_path"],
        "".join((INPUT_DICT["input_table_or_view_name"], "1.csv")))

    query = "IMPORT INTO {table_name} FROM CSV AT {s3_connection_name} " \
            "FILE '{s3_file_path}'".\
        format(table_name=import_table_name,
               s3_connection_name=INPUT_DICT["aws_credentials_connection_name"],
               s3_file_path=s3_file_path)
    return query


def get_comparison_query(import_table_name):
    return "SELECT * FROM {export_table_name} " \
           "UNION SELECT * FROM {import_table_name} " \
           "EXCEPT " \
           "SELECT * FROM {export_table_name} " \
           "INTERSECT SELECT * FROM {import_table_name}".\
        format(export_table_name=INPUT_DICT["input_table_or_view_name"],
               import_table_name=import_table_name)


def test_export_table(setup_database):
    db_conn = setup_database

    # execute the created script and export table to s3
    query_export_to_s3 = get_export_to_s3_query()
    db_conn.execute(query_export_to_s3)

    # import the data from s3 to the specified table
    import_table_name = "_".join(
        (INPUT_DICT["input_table_or_view_name"], "IMPORTED"))
    create_table(db_conn, import_table_name)
    query_import_from_s3 = get_import_from_s3_query(import_table_name)
    db_conn.execute(query_import_from_s3)

    # compare exported and imported tables
    query_comparison = get_comparison_query(import_table_name)
    n_different_rows = db_conn.execute(query_comparison).rowcount()
    assert n_different_rows == 0
