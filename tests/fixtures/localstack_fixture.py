import pytest
from exasol_integration_test_docker_environment.lib.docker import (  # type: ignore
    ContextDockerClient,
)


@pytest.fixture(scope='session')
def localstack_s3_uri(backend_aware_onprem_database) -> str | None:
    if backend_aware_onprem_database is not None:
        container_info = backend_aware_onprem_database.database_info.container_info
        with ContextDockerClient() as docker_client:
            # Create a user-defined network.
            network_name = 'it-network'
            networks = docker_client.networks.list(names=[network_name])
            if networks:
                network = networks[0]
            else:
                network = docker_client.networks.create(network_name, driver='bridge')

            # Connect the ITDE container to this network.
            network.connect(container_info.container_name)

            # Run the localstack container and connect it to the created network.
            # Also map the s3 port, to make it accessible from the host.
            ls_container = docker_client.containers.run(
                image="localstack/localstack",
                ports={4566: 4566, 4571: 4571},
                environment={'SERVICES': 's3'},
                network=network_name,
                detach=True)
            network.reload()
            assert ls_container in network.containers

            # Get the IP address of the localstack container.
            ls_container.reload()
            network_settings = ls_container.attrs['NetworkSettings']
            assert network_name in network_settings['Networks']
            ip_address = network_settings['Networks'][network_name]['IPAddress']
            assert ip_address

            return f"https://{ip_address}:4566"
    return None
