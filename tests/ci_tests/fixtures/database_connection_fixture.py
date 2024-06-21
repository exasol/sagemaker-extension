import os
from datetime import timedelta
from contextlib import ExitStack

import ssl
import pytest
import pyexasol
import exasol.bucketfs as bfs
from exasol.saas.client.api_access import (
    OpenApiAccess,
    create_saas_client,
    timestamp_name,
    get_connection_params
)

from tests.ci_tests.utils.parameters import db_params


def _env(var: str) -> str:
    result = os.environ.get(var)
    if result:
        return result
    raise RuntimeError(f"Environment variable {var} is empty.")


def _open_pyexasol_connection(**kwargs) -> pyexasol.ExaConnection:

    return pyexasol.connect(**kwargs,
                            encryption=True,
                            websocket_sslopt={"cert_reqs": ssl.CERT_NONE},
                            compression=True)


@pytest.fixture(scope="session")
def db_conn_onprem() -> pyexasol.ExaConnection:
    return _open_pyexasol_connection(dsn=f"{db_params.host}:{db_params.port}",
                                     user=db_params.user,
                                     password=db_params.password)


@pytest.fixture(scope="session")
def db_conn_saas() -> pyexasol.ExaConnection:

    host = _env("SAAS_HOST")
    account_id = _env("SAAS_ACCOUNT_ID")
    pat = _env("SAAS_PAT")

    with ExitStack() as stack:
        # Create and configure the SaaS client.
        client = create_saas_client(host=host, pat=pat)
        api_access = OpenApiAccess( client=client, account_id=account_id)
        stack.enter_context(api_access.allowed_ip())

        # Create a temporary database and waite till it becomes operational
        db = stack.enter_context(api_access.database(
            name=timestamp_name('SME_CI'),
            idle_time=timedelta(hours=12)))
        api_access.wait_until_running(db.id)

        # Create and return a connection to the database.
        conn_params = get_connection_params(host=host, account_id=account_id,
                                            pat=pat, database_id=db.id)
        yield _open_pyexasol_connection(**conn_params)


@pytest.fixture(scope="session")
def db_conn(request,
            db_conn_onprem,
            db_conn_saas) -> pyexasol.ExaConnection:
    if request.param == bfs.path.StorageBackend.onprem:
        yield db_conn_onprem
    elif request.param == bfs.path.StorageBackend.saas:
        yield db_conn_saas
    else:
        raise ValueError(('Unrecognised testing backend in the prepare_ci_test_environment. '
                          'Should be either "onprem" or "saas"'))
