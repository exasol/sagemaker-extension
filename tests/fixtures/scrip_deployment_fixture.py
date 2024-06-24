from __future__ import annotations
from typing import Any

import pytest
import exasol.bucketfs as bfs

from tests.integration_tests.utils.parameters import db_params


@pytest.fixture(scope="session")
def deploy_params_onprem() -> dict[str, Any]:
    return {
        'dsn': f"{db_params.host}:{db_params.port}",
        'db_user': db_params.user,
        'db_password': db_params.password
    }


@pytest.fixture(scope="session")
def deploy_params_saas(saas_url, saas_account_id, saas_database_id, saas_token) -> dict[str, Any]:
    yield {
        'saas_url': saas_url,
        'saas_account_id': saas_account_id,
        'saas_database_id': saas_database_id,
        'saas_token': saas_token
    }


@pytest.fixture(scope="session")
def deploy_params(request,
                  deploy_params_onprem,
                  deploy_params_saas) -> dict[str, Any]:
    if (hasattr(request, 'param') and
            (request.param == bfs.path.StorageBackend.saas)):
        yield deploy_params_saas
    else:
        yield deploy_params_onprem
