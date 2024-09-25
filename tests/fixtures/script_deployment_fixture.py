"""
This is rather ugly workaround for the problem with incompatible names of the DB and
BucketFS parameters, that are used in different scenarios.

In the ideal world, the parameters returned by the backend_aware_database_params and
backend_aware_bucketfs_params fixtures would be suitable for both creating respectively
a DB or BFS connection and using them in a command line (or more precisely, simulating
the command line in the context of tests). Unfortunately, the names and even the meanings
of some of the parameters in those two scenarios do not match.

At some point, we will standardise the names and replace the deploy_params and upload_params
fixtures with backend_aware_database_params and backend_aware_bucketfs_params.
"""
from __future__ import annotations
from typing import Any
import pytest


_deploy_param_map = {
    'dsn': 'dsn',
    'user': 'db_user',
    'password': 'db_pass'
}


def _translate_params(source: dict[str, Any], param_map: dict[str, str]) -> dict[str, Any]:
    return {param_map[k]: v for k, v in source.items() if k in param_map}


@pytest.fixture(scope="session")
def deploy_params(backend_aware_database_params, deployed_slc) -> dict[str, Any]:
    return _translate_params(backend_aware_database_params, _deploy_param_map)
