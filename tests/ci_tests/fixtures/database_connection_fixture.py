import pyexasol
import pytest
from tests.ci_tests.utils.parameters import db_params


@pytest.fixture(scope="session")
def db_conn():
    conn = pyexasol.connect(
        dsn="{host}:{port}".format(
            host=db_params.host,
            port=db_params.port),
        user=db_params.user,
        password=db_params.password)

    return conn
