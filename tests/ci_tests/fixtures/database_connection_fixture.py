from __future__ import annotations
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
def db_conn_saas() -> pyexasol.ExaConnection | None:

    host = os.environ.get("SAAS_HOST")
    account_id = os.environ.get("SAAS_ACCOUNT_ID")
    pat = os.environ.get("SAAS_PAT")

    if not all([host, account_id, pat]):
        yield None
        return

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
    if (request.param == bfs.path.StorageBackend.saas) and (db_conn_saas is not None):
        yield db_conn_saas
    else:
        yield db_conn_onprem
