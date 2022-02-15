import pytest
from datetime import datetime
from tests.ci_tests.utils.autopilot_training import AutopilotTestTraining
from tests.ci_tests.utils.queries import DatabaseQueries
from tests.ci_tests.utils.checkers import is_aws_credentials_not_set
from tests.ci_tests.utils.parameters import reg_model_setup_params, \
    cls_model_setup_params


@pytest.mark.skipif("is_aws_credentials_not_set() == True",
                    reason="AWS credentials are not set")
def test_train_autopilot_regression_job(setup_ci_test_environment):
    curr_datetime = datetime.now().strftime("%y%m%d%H%M%S")
    model_name = ''.join((reg_model_setup_params.model_type, curr_datetime))
    job_name = ''.join((model_name, 'job'))

    # train
    AutopilotTestTraining.train_autopilot_regression_job(
        job_name, setup_ci_test_environment)

    _assert_training_job(
        job_name, reg_model_setup_params, setup_ci_test_environment)


@pytest.mark.skipif("is_aws_credentials_not_set() == True",
                    reason="AWS credentials are not set")
def test_train_autopilot_classification_job(setup_ci_test_environment):
    curr_datetime = datetime.now().strftime("%y%m%d%H%M%S")
    model_name = ''.join((cls_model_setup_params.model_type, curr_datetime))
    job_name = ''.join((model_name, 'job'))

    # train
    AutopilotTestTraining.train_autopilot_classification_job(
        job_name, setup_ci_test_environment)

    _assert_training_job(
        job_name, cls_model_setup_params, setup_ci_test_environment)


def _assert_training_job(job_name, model_setup_params, db_conn):
    all_jobs = DatabaseQueries.get_all_jobs(
        model_setup_params, db_conn)
    assert job_name in list(map(lambda x: x[0], all_jobs))
