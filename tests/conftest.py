pytest_plugins = [
    "tests.unit_tests.fixtures.aws_connection_fixture",
    "tests.integration_tests.fixtures.database_connection_fixture",
    "tests.integration_tests.fixtures.build_language_container_fixture",
    "tests.integration_tests.fixtures.setup_database_fixture",
    "tests.integration_tests.fixtures.deploy_scripts_fixture",
]
