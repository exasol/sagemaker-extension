import pytest
from tests.integration_tests.utils.parameters import reg_setup_params, \
    aws_params, cls_setup_params


@pytest.fixture(scope="session")
def setup_database(db_conn):
    create_aws_connection(db_conn)
    for setup_params in [reg_setup_params, cls_setup_params]:
        create_table(db_conn, setup_params)
        insert_into_table(db_conn, setup_params)
    return db_conn


def create_aws_connection(conn):
    query = "CREATE OR REPLACE  CONNECTION {aws_conn_name} " \
            "TO '{aws_s3_uri}' " \
            "USER '{aws_key_id}' IDENTIFIED BY '{aws_access_key}'"\
        .format(aws_conn_name=aws_params.aws_conn_name,
                aws_s3_uri=aws_params.aws_s3_uri,
                aws_key_id=aws_params.aws_access_key_id,
                aws_access_key=aws_params.aws_secret_access_key)
    conn.execute(query)


def create_table(conn, setup_params):
    query = "CREATE OR REPLACE TABLE {schema_name}.{table_name} " \
            "(col1 FLOAT, col2 FLOAT, output_col INTEGER)".\
        format(schema_name=setup_params.schema_name,
               table_name=setup_params.table_name)
    conn.execute(query)


def insert_into_table(conn, setup_params):
    values = ",".join(setup_params.data)
    query = "INSERT INTO {schema_name}.{table_name} VALUES {values}".\
        format(schema_name=setup_params.schema_name,
               table_name=setup_params.table_name,
               values=values)
    conn.execute(query)
