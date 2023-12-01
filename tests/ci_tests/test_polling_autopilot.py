from datetime import datetime

from tests.ci_tests.utils.autopilot_polling import AutopilotTestPolling
from tests.ci_tests.utils.autopilot_training import AutopilotTestTraining
from tests.ci_tests.utils.checkers import skip_if_aws_credentials_not_set
from tests.ci_tests.utils.parameters import cls_model_setup_params


@skip_if_aws_credentials_not_set
def test_poll_autopilot_job(setup_ci_test_environment):
    curr_datetime = datetime.now().strftime("%y%m%d%H%M%S")
    model_name = ''.join((cls_model_setup_params.model_type, curr_datetime))
    job_name = ''.join((model_name, 'job'))

    # train
    AutopilotTestTraining.train_autopilot_classification_job(
        job_name, setup_ci_test_environment)

    # poll
    status = AutopilotTestPolling.poll_autopilot_job(
        job_name,
        cls_model_setup_params.schema_name,
        setup_ci_test_environment)

    assert len(status) == 1
    assert len(status[0]) == 2
