import time
from datetime import datetime

import pytest
import exasol.bucketfs as bfs

from tests.fixtures.prepare_environment_fixture import CITestEnvironment
from tests.ci_tests.utils import parameters
from tests.ci_tests.utils.autopilot_deployment import AutopilotTestDeployment
from tests.ci_tests.utils.autopilot_polling import AutopilotTestPolling
from tests.ci_tests.utils.autopilot_prediction import AutopilotTestPrediction
from tests.ci_tests.utils.autopilot_training import AutopilotTestTraining
from tests.ci_tests.utils.cleanup import cleanup
from tests.ci_tests.utils.parameters import cls_model_setup_params, \
    reg_model_setup_params


def _is_training_completed(status):
    return len(status) == 1 and \
           len(status[0]) == 2 and \
           status[0][0].lower() == 'completed' and \
           status[0][1].lower() == 'completed'


@cleanup
def _make_prediction(job_name, endpoint_name, model_setup_params, ci_test_env: CITestEnvironment):
    # poll until the training is completed
    timeout_time = time.time() + parameters.TIMEOUT
    while True:
        status = AutopilotTestPolling.poll_autopilot_job(
            job_name,
            model_setup_params.schema_name,
            ci_test_env)
        print(status)

        if _is_training_completed(status):
            break
        if timeout_time <= time.time():
            raise Exception("Timeout exception is raised, because the training "
                            "takes too long to be completed.")

        time.sleep(parameters.POLLING_INTERVAL)

    # deploy an endpoint
    AutopilotTestDeployment.deploy_endpoint(
        job_name,
        endpoint_name,
        model_setup_params,
        ci_test_env
    )

    # assertion
    predictions = AutopilotTestPrediction.predict(
        endpoint_name, model_setup_params.schema_name, ci_test_env)
    assert predictions


@pytest.mark.skip
@pytest.mark.parametrize("db_conn,deploy_params", [
    (bfs.path.StorageBackend.onprem, bfs.path.StorageBackend.onprem),
    (bfs.path.StorageBackend.saas, bfs.path.StorageBackend.saas)
], indirect=True)
def test_predict_autopilot_regression_job(db_conn, deploy_params, prepare_ci_test_environment):
    curr_datetime = datetime.now().strftime("%y%m%d%H%M%S")
    model_name = ''.join((reg_model_setup_params.model_type, curr_datetime))
    job_name = ''.join((model_name, 'job'))
    endpoint_name = ''.join((model_name, 'ep'))

    # train
    AutopilotTestTraining.train_autopilot_regression_job(
        job_name, prepare_ci_test_environment)

    # deploy endpoint and make prediction on it
    _make_prediction(
        job_name=job_name,
        endpoint_name=endpoint_name,
        model_setup_params=reg_model_setup_params,
        db_conn=prepare_ci_test_environment)


@pytest.mark.skip
@pytest.mark.parametrize("db_conn,deploy_params", [
    (bfs.path.StorageBackend.onprem, bfs.path.StorageBackend.onprem),
    (bfs.path.StorageBackend.saas, bfs.path.StorageBackend.saas)
], indirect=True)
def test_predict_autopilot_classification_job(db_conn, deploy_params, prepare_ci_test_environment):
    curr_datetime = datetime.now().strftime("%y%m%d%H%M%S")
    model_name = ''.join((cls_model_setup_params.model_type, curr_datetime))
    job_name = ''.join((model_name, 'job'))
    endpoint_name = ''.join((model_name, 'ep'))

    # train
    AutopilotTestTraining.train_autopilot_classification_job(
        job_name, prepare_ci_test_environment)

    # deploy endpoint and make prediction on it
    _make_prediction(
        job_name=job_name,
        endpoint_name=endpoint_name,
        model_setup_params=cls_model_setup_params,
        db_conn=prepare_ci_test_environment)
