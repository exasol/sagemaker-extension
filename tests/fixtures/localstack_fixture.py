import pytest
from exasol_integration_test_docker_environment.lib.docker import (  # type: ignore
    ContextDockerClient,
)


@pytest.fixture(scope='session')
def run_localstack(backend_aware_onprem_database) -> tuple[str, str] | None:
    if backend_aware_onprem_database is not None:
        container_info = backend_aware_onprem_database.database_info.container_info
        network_name = container_info.network_info.network_name
        assert network_name
        with ContextDockerClient() as docker_client:
            s3_port = 4566
            container = docker_client.containers.run(
                image="localstack/localstack",
                # ports={s3_port: s3_port},
                environment={'SERVICES': 's3'},
                network=f'container:{container_info.container_name}',
                detach=True)
            network_settings = container.attrs['NetworkSettings']
            ip_address = network_settings['IPAddress']
            assert ip_address, f"Unable to get the IP address from the network settings {network_settings}"
            s3_uri = f"https://{ip_address}:{s3_port}"
            return ip_address, s3_uri
    return None
