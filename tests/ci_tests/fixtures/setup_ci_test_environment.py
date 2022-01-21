import pytest


@pytest.fixture(scope="session")
def setup_ci_test_environment(register_language_container,
                              prepare_ci_test_environment):
    conn = prepare_ci_test_environment
    return conn
