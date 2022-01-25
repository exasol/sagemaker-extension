import time
import pytest
from datetime import datetime
from tests.ci_tests.utils.autopilot_deletion import AutopilotTestDeletion
from tests.ci_tests.utils.autopilot_deployment import AutopilotTestDeployment
from tests.ci_tests.utils.autopilot_polling import AutopilotTestPolling
from tests.ci_tests.utils.autopilot_prediction import AutopilotTestPrediction
from tests.ci_tests.utils.autopilot_training import AutopilotTestTraining
from tests.ci_tests.utils.checkers import is_aws_credentials_not_set
from tests.ci_tests.utils.parameters import cls_model_setup_params, \
    reg_model_setup_params

POLLING_INTERVAL = 120  # seconds
curr_datetime = datetime.now().strftime("%y%m%d%H%M%S")


@pytest.mark.skipif("is_aws_credentials_not_set() == True",
                    reason="AWS credentials are not set")
def test_predict_autopilot_regression_job(setup_ci_test_environment):
    model_name = ''.join((reg_model_setup_params.model_type, curr_datetime))
    job_name = ''.join((model_name, 'job'))
    endpoint_name = ''.join((model_name, 'ep'))

    # train
    AutopilotTestTraining.train_autopilot_regression_job(
        job_name, setup_ci_test_environment)

    _run_prediction_test(
        job_name,
        endpoint_name,
        reg_model_setup_params,
        setup_ci_test_environment)


@pytest.mark.skipif("is_aws_credentials_not_set() == True",
                    reason="AWS credentials are not set")
def test_predict_autopilot_classification_job(setup_ci_test_environment):
    model_name = ''.join((cls_model_setup_params.model_type, curr_datetime))
    job_name = ''.join((model_name, 'job'))
    endpoint_name = ''.join((model_name, 'ep'))

    # train
    AutopilotTestTraining.train_autopilot_classification_job(
        job_name, setup_ci_test_environment)

    _run_prediction_test(
        job_name,
        endpoint_name,
        cls_model_setup_params,
        setup_ci_test_environment)


def _run_prediction_test(job_name, endpoint_name, model_setup_params, db_conn):

    # poll until the training is completed
    while True:
        status = AutopilotTestPolling.poll_autopilot_job(
            job_name,
            model_setup_params.schema_name,
            db_conn)
        print(status)
        if _is_training_completed(status):
            break

        time.sleep(POLLING_INTERVAL)

    try:
        # deploy an endpoint
        AutopilotTestDeployment.deploy_endpoint(
            job_name,
            endpoint_name,
            model_setup_params,
            db_conn
        )

        # assert and delete the endpoint
        predictions = AutopilotTestPrediction.predict(
            endpoint_name, model_setup_params.schema_name, db_conn)
        assert predictions
    except AssertionError as err:
        print("Error occurred while asserting deployment %s" % err)
    except Exception as exc:
        print("Exception is raised while asserting deployment %s" % exc)
    finally:
        print("Delete the created endpoint")
        AutopilotTestDeletion.delete_endpoint(
            endpoint_name, model_setup_params, db_conn)


def _is_training_completed(status):
    return len(status) == 1 and \
           len(status[0]) == 2 and \
           status[0][0].lower() == 'completed' and \
           status[0][1].lower() == 'completed'
