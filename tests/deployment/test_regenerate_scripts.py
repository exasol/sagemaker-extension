import importlib_resources
from pathlib import Path
from exasol_sagemaker_extension.deployment import regenerate_scripts, constants

BASE_DIR = importlib_resources.files("exasol_sagemaker_extension")
RESOURCE_LUA_DIR = (BASE_DIR / "resources" / "lua")


def test_regenerate_scripts():
    regenerate_scripts.generate_scripts()

    script_list = [
        constants.CREATE_STATEMENT_AUTOPILOT_TRAINING_LUA_SCRIPT_PATH,
        constants.CREATE_STATEMENT_AUTOPILOT_JOB_STATUS_POLLING_LUA_SCRIPT_PATH,
        constants.CREATE_STATEMENT_AUTOPILOT_ENDPOINT_DELETION_LUA_SCRIPT_PATH,
        constants.CREATE_STATEMENT_AUTOPILOT_ENDPOINT_DEPLOYMENT_LUA_SCRIPT_PATH
    ]

    for script in script_list:
        assert Path(script).is_file()



