import pytest

from tests.ci_tests.fixtures.prepare_environment_fixture import CITestEnvironment


@pytest.fixture(scope="session")
def setup_ci_test_environment(register_language_container,
                              prepare_ci_test_environment) -> CITestEnvironment:
    return prepare_ci_test_environment
