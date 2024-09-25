import pytest
from exasol_integration_test_docker_environment.lib.docker import (  # type: ignore
    ContextDockerClient,
)


@pytest.fixture(scope='session')
def run_localstack(backend_aware_onprem_database):
    if backend_aware_onprem_database is not None:
        db_info = backend_aware_onprem_database.database_info
        container_info = db_info.container_info
        network_name = container_info.network_info.network_name
        with ContextDockerClient() as docker_client:
            docker_client.containers.run(
                image="localstack/localstack",
                ports={4566: 4566, 4571: 4571},
                environment={'SERVICES': 's3'},
                network=network_name,
                detach=True)
