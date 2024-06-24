import pytest

from tests.fixtures.prepare_environment_fixture import CITestEnvironment


@pytest.fixture(scope="session")
def setup_ci_test_environment(prepare_ci_test_environment) -> CITestEnvironment:
    return prepare_ci_test_environment
