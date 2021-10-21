import pyexasol
import pytest


@pytest.fixture(scope="session")
def get_params():
    return {
        "DB_CONNECTION_HOST": "127.0.0.1",
        "DB_CONNECTION_PORT": "9563",
        "DB_CONNECTION_USER": "sys",
        "DB_CONNECTION_PASS": "exasol"}


@pytest.fixture(scope="session")
def db_conn(get_params):
    conn = pyexasol.connect(
        dsn="{host}:{port}".format(
            host=get_params["DB_CONNECTION_HOST"],
            port=get_params["DB_CONNECTION_PORT"]),
        user=get_params["DB_CONNECTION_USER"],
        password=get_params["DB_CONNECTION_PASS"])

    return conn