import time
import pytest
from datetime import datetime
from tests.ci_tests.utils.autopilot_deletion import AutopilotTestDeletion
from tests.ci_tests.utils.autopilot_deployment import AutopilotTestDeployment
from tests.ci_tests.utils.autopilot_polling import AutopilotTestPolling
from tests.ci_tests.utils.autopilot_training import AutopilotTestTraining
from tests.ci_tests.utils.queries import DatabaseQueries
from tests.ci_tests.utils.checkers import is_aws_credentials_not_set
from tests.ci_tests.utils.parameters import cls_model_setup_params

POLLING_INTERVAL = 120  # seconds
curr_datetime = datetime.now().strftime("%y%m%d%H%M%S")


@pytest.mark.skipif("is_aws_credentials_not_set() == True",
                    reason="AWS credentials are not set")
def test_deploy_autopilot_endpoint(setup_ci_test_environment):
    model_name = ''.join((cls_model_setup_params.model_type, curr_datetime))
    job_name = ''.join((model_name, 'job'))
    endpoint_name = ''.join((model_name, 'ep'))

    # train
    AutopilotTestTraining.train_autopilot_classification_job(
        job_name, setup_ci_test_environment)

    # poll until the training is completed
    while True:
        status = AutopilotTestPolling.poll_autopilot_job(
            job_name,
            cls_model_setup_params.schema_name,
            setup_ci_test_environment)
        print(status)
        if _is_training_completed(status):
            break

        time.sleep(POLLING_INTERVAL)

    try:
        # deploy an endpoint
        AutopilotTestDeployment.deploy_endpoint(
            job_name,
            endpoint_name,
            cls_model_setup_params,
            setup_ci_test_environment
        )

        # assert and delete the endpoint
        all_scripts = DatabaseQueries.get_all_scripts(
            cls_model_setup_params, setup_ci_test_environment)
        assert endpoint_name in list(map(lambda x: x[0], all_scripts))
    except AssertionError as err:
        print("Error occurred while asserting deployment %s" % err)
    except Exception as exc:
        print("Exception is raised while asserting deployment %s" % exc)
    finally:
        print("Delete the created endpoint")
        AutopilotTestDeletion.delete_endpoint(
            endpoint_name, cls_model_setup_params, setup_ci_test_environment)


def _is_training_completed(status):
    return len(status) == 1 and \
           len(status[0]) == 2 and \
           status[0][0].lower() == 'completed' and \
           status[0][1].lower() == 'completed'
