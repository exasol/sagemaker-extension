from datetime import datetime

import pytest
import exasol.bucketfs as bfs

from tests.ci_tests.utils.autopilot_polling import AutopilotTestPolling
from tests.ci_tests.utils.autopilot_training import AutopilotTestTraining
from tests.ci_tests.utils.parameters import cls_model_setup_params


@pytest.mark.parametrize("db_conn,deploy_params", [
    (bfs.path.StorageBackend.onprem, bfs.path.StorageBackend.onprem),
    (bfs.path.StorageBackend.saas, bfs.path.StorageBackend.saas)
], indirect=True)
def test_poll_autopilot_job(db_conn, deploy_params, prepare_ci_test_environment):
    curr_datetime = datetime.now().strftime("%y%m%d%H%M%S")
    model_name = ''.join((cls_model_setup_params.model_type, curr_datetime))
    job_name = ''.join((model_name, 'job'))

    # train
    AutopilotTestTraining.train_autopilot_classification_job(
        job_name, prepare_ci_test_environment)

    # poll
    status = AutopilotTestPolling.poll_autopilot_job(
        job_name,
        cls_model_setup_params.schema_name,
        prepare_ci_test_environment)

    assert len(status) == 1
    assert len(status[0]) == 2
