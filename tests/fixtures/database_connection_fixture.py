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

from tests.ci_tests.utils.build_language_container import (
    upload_language_container_saas, upload_language_container_onprem)
from tests.integration_tests.utils.parameters import db_params


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


@pytest.fixture(scope='session', params=[bfs.path.StorageBackend.onprem, bfs.path.StorageBackend.saas])
def backend(request) -> bfs.path.StorageBackend:
    # Here we are going to add
    # pytest.skip()
    # if there is an instruction to skip a particular backed in the command line.
    return request.param


@pytest.fixture(scope="session")
def db_conn_onprem(backend) -> pyexasol.ExaConnection | None:
    if backend == bfs.path.StorageBackend.onprem:
        conn = _open_pyexasol_connection(dsn=f"{db_params.host}:{db_params.port}",
                                         user=db_params.user,
                                         password=db_params.password)
        upload_language_container_onprem(db_conn=conn)
        return conn
    return None


@pytest.fixture(scope="session")
def saas_url() -> str:
    return _env("SAAS_HOST")


@pytest.fixture(scope="session")
def saas_account_id() -> str:
    return _env("SAAS_ACCOUNT_ID")


@pytest.fixture(scope="session")
def saas_token() -> str:
    return _env("SAAS_PAT")


@pytest.fixture(scope="session")
def saas_database_id(backend, saas_url, saas_account_id, saas_token) -> str:

    if backend == bfs.path.StorageBackend.saas:
        with ExitStack() as stack:
            # Create and configure the SaaS client.
            client = create_saas_client(host=saas_url, pat=saas_token)
            api_access = OpenApiAccess(client=client, account_id=saas_account_id)
            stack.enter_context(api_access.allowed_ip())

            # Create a temporary database and waite till it becomes operational
            db = stack.enter_context(api_access.database(
                name=timestamp_name('SME_CI'),
                idle_time=timedelta(hours=12)))
            api_access.wait_until_running(db.id, timeout=timedelta(minutes=45))
            yield db.id
    else:
        yield ''


@pytest.fixture(scope="session")
def db_conn_saas(backend, saas_url, saas_account_id, saas_database_id, saas_token) -> pyexasol.ExaConnection | None:

    if backend == bfs.path.StorageBackend.saas:
        # Create a connection to the database.
        conn_params = get_connection_params(host=saas_url,
                                            account_id=saas_account_id,
                                            database_id=saas_database_id,
                                            pat=saas_token)
        conn = _open_pyexasol_connection(**conn_params)

        # Build, upload and activate the language container
        upload_language_container_saas(db_conn=conn,
                                       saas_url=saas_url,
                                       saas_account_id=saas_account_id,
                                       saas_database_id=saas_database_id,
                                       saas_token=saas_token)
        yield conn
    else:
        yield None


@pytest.fixture(scope="session")
def db_conn(backend,
            db_conn_onprem,
            db_conn_saas) -> pyexasol.ExaConnection:
    if backend == bfs.path.StorageBackend.saas:
        assert db_conn_saas is not None
        yield db_conn_saas
    else:
        assert db_conn_onprem is not None
        yield db_conn_onprem
