import pytest
from datetime import datetime
from tests.ci_tests.utils.autopilot_training import AutopilotTestTraining
from tests.ci_tests.utils.autopilot_utils import AutopilotTestUtils
from tests.ci_tests.utils.checkers import is_aws_credentials_not_set
from tests.ci_tests.utils.parameters import reg_model_setup_params, \
    cls_model_setup_params


# generate unique model name
curr_datetime = datetime.now().strftime("%y%m%d%H%M%S")


@pytest.mark.skipif("is_aws_credentials_not_set() == True",
                    reason="AWS credentials are not set")
def test_train_autopilot_regression_job(setup_ci_test_environment):
    model_name = ''.join((reg_model_setup_params.model_type, curr_datetime))
    job_name = ''.join((model_name, 'job'))

    AutopilotTestTraining.train_autopilot_regression_job(
        job_name, setup_ci_test_environment)

    _assert_method(job_name, reg_model_setup_params, setup_ci_test_environment)


@pytest.mark.skipif("is_aws_credentials_not_set() == True",
                    reason="AWS credentials are not set")
def test_train_autopilot_classification_job(setup_ci_test_environment):
    model_name = ''.join((cls_model_setup_params.model_type, curr_datetime))
    job_name = ''.join((model_name, 'job'))

    # train
    AutopilotTestTraining.train_autopilot_classification_job(
        job_name, setup_ci_test_environment)

    _assert_method(job_name, cls_model_setup_params, setup_ci_test_environment)


def _assert_method(job_name, model_setup_params, db_con):
    all_jobs = AutopilotTestUtils.get_all_jobs(
        reg_model_setup_params, model_setup_params)
    assert job_name in list(map(lambda x: x[0], all_jobs))
