import time
from datetime import datetime

from tests.fixtures.prepare_environment_fixture import CITestEnvironment
from tests.ci_tests.utils import parameters
from tests.ci_tests.utils.autopilot_deployment import AutopilotTestDeployment
from tests.ci_tests.utils.autopilot_polling import AutopilotTestPolling
from tests.ci_tests.utils.autopilot_training import AutopilotTestTraining
from tests.ci_tests.utils.cleanup import cleanup
from tests.ci_tests.utils.parameters import cls_model_setup_params
from tests.ci_tests.utils.queries import DatabaseQueries


def _is_training_completed(status):
    return len(status) == 1 and \
           len(status[0]) == 2 and \
           status[0][0].lower() == 'completed' and \
           status[0][1].lower() == 'completed'


@cleanup
def _deploy_endpoint(job_name, endpoint_name, model_setup_params, ci_test_env: CITestEnvironment, ):
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
    all_scripts = DatabaseQueries.get_all_scripts(
        model_setup_params, ci_test_env.db_conn)
    assert endpoint_name in list(map(lambda x: x[0], all_scripts))


def test_deploy_autopilot_endpoint(prepare_ci_test_environment):
    curr_datetime = datetime.now().strftime("%y%m%d%H%M%S")
    model_name = ''.join((cls_model_setup_params.model_type, curr_datetime))
    job_name = ''.join((model_name, 'job'))
    endpoint_name = ''.join((model_name, 'ep'))

    # train
    AutopilotTestTraining.train_autopilot_classification_job(
        job_name, prepare_ci_test_environment)

    # deploy
    _deploy_endpoint(
        job_name=job_name,
        endpoint_name=endpoint_name,
        model_setup_params=cls_model_setup_params,
        db_conn=prepare_ci_test_environment)
