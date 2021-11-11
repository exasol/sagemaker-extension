import json
import pytest
import os.path
import localstack_client.session
from tests.integration_tests.utils.generate_create_statement_s3_exporting \
    import  S3ExportingLuaScriptCreateStatementGenerator

DB_CONNECTION_ADDR = "127.0.0.1:9563"
DB_CONNECTION_USER = "sys"
DB_CONNECTION_PASS = "exasol"
AWS_IP_ADDR = "192.168.0.2"
AWS_KEY_ID = ""
AWS_ACCESS_KEY = ""
AWS_S3_URI = f"https://{AWS_IP_ADDR}:4566"


INPUT_DICT = {
    "job_name": "todo_model",
    "input_schema_name": "INTEGRATION_TEST_SCHEMA",
    "input_table_or_view_name": "TEST_TABLE",
    "aws_credentials_connection_name": "S3_CONNECTION",
    "s3_bucket_uri": "s3://exasol-sagemaker-extension",
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

    conn.execute(query)


def create_scripts(conn):
    statement_generator = S3ExportingLuaScriptCreateStatementGenerator()
    statement_str = statement_generator.get_statement()
    conn.execute(statement_str)


def create_table(conn, table_name):
    query = "CREATE OR REPLACE TABLE {table_name} " \
            "(col1 INTEGER, col2 INTEGER)".\
        format(table_name=table_name)
    conn.execute(query)


def insert_into_table(conn, table_name):
    values = ",".join([f"({i}, {i * 10})" for i in range(1, 11)])
    query = "INSERT INTO {table_name} VALUES {values}".\
        format(table_name=table_name, values=values)
    conn.execute(query)


def create_s3_bucket(s3_client):
    s3_client.create_bucket(Bucket=INPUT_DICT["s3_output_path"])


def get_s3_bucket_files(s3_client):
    files = []
    for key in s3_client.list_objects(
            Bucket=INPUT_DICT["s3_output_path"])['Contents']:
        files.append(os.path.join(INPUT_DICT["s3_output_path"], key['Key']))
    return files


@pytest.fixture(scope="session")
def s3_client():
    session = localstack_client.session.Session(
        localstack_host='{ip_addr}'.format(ip_addr=AWS_IP_ADDR))
    s3_client = session.client('s3')
    return s3_client


@pytest.fixture(scope="session")
def setup_database(db_conn, s3_client):
    open_schema(db_conn)
    create_aws_connection(db_conn)
    create_scripts(db_conn)
    create_table(db_conn, table_name=INPUT_DICT["input_table_or_view_name"])
    insert_into_table(db_conn, table_name=INPUT_DICT["input_table_or_view_name"])
    create_s3_bucket(s3_client)
    return db_conn


def get_export_to_s3_query():
    return "EXECUTE SCRIPT INTEGRATION_TEST_SCHEMA.{script_name}" \
           "('{json_str}')".\
        format(script_name="EXPORT_TO_S3",
               json_str=json.dumps(INPUT_DICT))


def get_import_from_s3_query(import_table_name, s3_client):
    s3_bucket_files = get_s3_bucket_files(s3_client)
    s3_bucket_files_str = []
    for s3_file_path in s3_bucket_files:
        s3_bucket_files_str.append(f"FILE '{s3_file_path}'")

    query = "IMPORT INTO {table_name} FROM CSV AT {s3_connection_name} " \
            "{s3_bucket_files_str} SKIP=1".\
        format(table_name=import_table_name,
               s3_connection_name=INPUT_DICT["aws_credentials_connection_name"],
               s3_bucket_files_str=" ".join(s3_bucket_files_str))

    return query


def get_comparison_query(import_table_name):
    return "(SELECT * FROM {export_table_name} " \
           "UNION SELECT * FROM {import_table_name})" \
           "EXCEPT " \
           "(SELECT * FROM {export_table_name} " \
           "INTERSECT SELECT * FROM {import_table_name})".\
        format(export_table_name=INPUT_DICT["input_table_or_view_name"],
               import_table_name=import_table_name)


def test_export_table(setup_database, s3_client):
    db_conn = setup_database

    # execute the created script and export table to s3
    query_export_to_s3 = get_export_to_s3_query()
    db_conn.execute(query_export_to_s3)

    # import the data from s3 to the specified table
    import_table_name = "_".join(
        (INPUT_DICT["input_table_or_view_name"], "IMPORTED"))
    create_table(db_conn, import_table_name)
    query_import_from_s3 = get_import_from_s3_query(
        import_table_name, s3_client)
    db_conn.execute(query_import_from_s3)

    # compare exported and imported tables
    query_comparison = get_comparison_query(import_table_name)
    n_different_rows = db_conn.execute(query_comparison).rowcount()
    assert n_different_rows == 0
