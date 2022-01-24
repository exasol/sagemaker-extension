import os
import json
import pytest
from datetime import datetime
from tests.ci_tests.utils.checkers import is_aws_credentials_not_set
from tests.ci_tests.utils.parameters import reg_model_setup_params, aws_params, \
    cls_model_setup_params

curr_datetime = datetime.now().strftime("%y%m%d%H%M%S")


@pytest.mark.skipif("is_aws_credentials_not_set() == True",
                    reason="AWS credentials are not set")
def test_deploy_autopilot_job(setup_ci_test_environment):
    # TODO 1: train new model
    # TODO 2: poll the trained model
    # TODO 3: when poll returns 'Completed', deploy endpoint
    # TODO 4: delete the created endpoint
    pass