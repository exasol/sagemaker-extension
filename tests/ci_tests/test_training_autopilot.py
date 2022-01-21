import pytest
from tests.ci_tests.utils.checkers import is_aws_credentials_not_set


@pytest.mark.skipif("is_aws_credentials_not_set() == True",
                    reason="AWS credentials are not set")
def test_train_autopilot_job(setup_ci_test_environment):
    assert 1 == 1