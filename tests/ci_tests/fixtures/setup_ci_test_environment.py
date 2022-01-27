import pytest


@pytest.fixture(scope="session")
def setup_ci_test_environment(register_language_container,
                              prepare_ci_test_environment):
    db_conn = prepare_ci_test_environment
    return db_conn
