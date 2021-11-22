import pytest
from exasol_sagemaker_extension.deployment import deploy_cli
from tests.integration_tests.utils.parameters import db_params, setup_params


@pytest.fixture(scope="session")
def deploy_scripts():
    args_list = [
        "--host", db_params.host,
        "--port", db_params.port,
        "--user", db_params.user,
        "--pass", db_params.password,
        "--schema", setup_params.schema_name
    ]
    deploy_cli.main(args_list)
