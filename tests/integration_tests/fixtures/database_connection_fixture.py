import ssl

import pyexasol
import pytest
from tests.integration_tests.utils.parameters import db_params


@pytest.fixture(scope="session")
def db_conn():
    conn = pyexasol.connect(
        dsn="{host}:{port}".format(
            host=db_params.host,
            port=db_params.port),
        user=db_params.user,
        password=db_params.password,
        encryption=True,
        websocket_sslopt={
            "cert_reqs": ssl.CERT_NONE,
        }
    )

    return conn
