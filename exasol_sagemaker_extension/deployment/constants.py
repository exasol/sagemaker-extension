import importlib_resources

# set deployment paths
BASE_DIR = importlib_resources.files("exasol_sagemaker_extension")
RESOURCE_UDF_DIR = (BASE_DIR / "resources" / "udf")
RESOURCE_LUA_DIR = (BASE_DIR / "resources" / "lua")
RESOURCE_SQL_DIR = (BASE_DIR / "resources" / "sql")
LUA_SRC_DIR = (BASE_DIR / "lua" / "src")

LUA_SRC_MODULE_AUTOPILOT_TRAINING_MAIN_NAME = "autopilot_training_main.lua"
LUA_SRC_MODULE_AWS_S3_HANDLER_NAME = "aws_s3_handler.lua"
LUA_SRC_MODULE_DB_METADATA_WRITER_NAME = "db_metadata_writer.lua"
LUA_SRC_MODULE_AWS_SAGEMAKER_HANDLER_NAME = "aws_sagemaker_handler.lua"
LUA_SRC_MODULE_AUTOPILOT_JOB_STATUS_POLLING_NAME = "autopilot_job_status_polling.lua"
LUA_SRC_MODULE_SAGEMAKER_ENDPOINT_DEPLOYMENT_NAME = "autopilot_endpoint_deployment.lua"
LUA_SRC_MODULE_SAGEMAKER_ENDPOINT_DELETION_NAME = "autopilot_endpoint_deletion.lua"
LUA_SRC_MODULE_ENDPOINT_CONNECTION_HANDLER_NAME = "endpoint_connection_handler.lua"
LUA_SRC_MODULE_INSTALL_AUTOPILOT_PREDICTION_UDF_NAME = "install_autopilot_prediction_udf.lua"
LUA_SRC_MODULE_DB_METADATA_READER_NAME = "db_metadata_reader.lua"
LUA_SRC_MODULE_VALIDATE_INPUT = "validate_input.lua"

LUA_BUNDLED = "bundle_final.lua"

# training Lua & UDF scripts paths & texts
CREATE_STATEMENT_AUTOPILOT_TRAINING_LUA_SCRIPT_PATH = \
    RESOURCE_LUA_DIR.joinpath("outputs").joinpath(
        "create_statement_autopilot_training_lua_script.sql")
CREATE_STATEMENT_TEMPLATE_AUTOPILOT_TRAINING_LUA_SCRIPT_PATH = \
    RESOURCE_LUA_DIR.joinpath("templates").joinpath(
        "create_statement_template_autopilot_training_lua_script.sql")
CREATE_STATEMENT_AUTOPILOT_TRAINING_UDF_RESOURCE_PATH = \
    RESOURCE_UDF_DIR.joinpath(
        "create_statement_autopilot_training_udf.sql")
CREATE_STATEMENT_TEMPLATE_AUTOPILOT_TRAINING_LUA_SCRIPT_TEXT = \
    CREATE_STATEMENT_TEMPLATE_AUTOPILOT_TRAINING_LUA_SCRIPT_PATH. \
        read_text()
CREATE_STATEMENT_AUTOPILOT_TRAINING_UDF_RESOURCE_TEXT = \
    CREATE_STATEMENT_AUTOPILOT_TRAINING_UDF_RESOURCE_PATH. \
        read_text()

# polling Lua & UDF scripts paths & texts
CREATE_STATEMENT_AUTOPILOT_JOB_STATUS_POLLING_LUA_SCRIPT_PATH = \
    RESOURCE_LUA_DIR.joinpath("outputs").joinpath(
        "create_statement_autopilot_job_status_polling_lua_script.sql")
CREATE_STATEMENT_TEMPLATE_AUTOPILOT_JOB_STATUS_POLLING_LUA_SCRIPT_PATH = \
    RESOURCE_LUA_DIR.joinpath("templates").joinpath(
        "create_statement_template_autopilot_job_status_polling_lua_script.sql")
CREATE_STATEMENT_AUTOPILOT_JOB_STATUS_POLLING_UDF_RESOURCE_PATH = \
    RESOURCE_UDF_DIR.joinpath(
        "create_statement_autopilot_job_status_polling_udf.sql")
CREATE_STATEMENT_TEMPLATE_AUTOPILOT_JOB_STATUS_POLLING_LUA_SCRIPT_TEXT = \
    CREATE_STATEMENT_TEMPLATE_AUTOPILOT_JOB_STATUS_POLLING_LUA_SCRIPT_PATH. \
        read_text()
CREATE_STATEMENT_AUTOPILOT_JOB_STATUS_POLLING_UDF_RESOURCE_TEXT = \
    CREATE_STATEMENT_AUTOPILOT_JOB_STATUS_POLLING_UDF_RESOURCE_PATH. \
        read_text()

# deployment Lua & UDF scripts paths & texts
CREATE_STATEMENT_AUTOPILOT_ENDPOINT_DEPLOYMENT_LUA_SCRIPT_PATH = \
    RESOURCE_LUA_DIR.joinpath("outputs").joinpath(
        "create_statement_autopilot_endpoint_deployment_lua_script.sql")
CREATE_STATEMENT_TEMPLATE_AUTOPILOT_ENDPOINT_DEPLOYMENT_LUA_SCRIPT_PATH = \
    RESOURCE_LUA_DIR.joinpath("templates").joinpath(
        "create_statement_template_autopilot_endpoint_deployment_lua_script.sql")
CREATE_STATEMENT_AUTOPILOT_ENDPOINT_DEPLOYMENT_UDF_RESOURCE_PATH = \
    RESOURCE_UDF_DIR.joinpath(
        "create_statement_autopilot_endpoint_deployment_udf.sql")
CREATE_STATEMENT_TEMPLATE_AUTOPILOT_ENDPOINT_DEPLOYMENT_LUA_SCRIPT_TEXT = \
    CREATE_STATEMENT_TEMPLATE_AUTOPILOT_ENDPOINT_DEPLOYMENT_LUA_SCRIPT_PATH. \
        read_text()
CREATE_STATEMENT_AUTOPILOT_ENDPOINT_DEPLOYMENT_UDF_RESOURCE_TEXT = \
    CREATE_STATEMENT_AUTOPILOT_ENDPOINT_DEPLOYMENT_UDF_RESOURCE_PATH.\
        read_text()

# deletion Lua & UDF scripts paths & texts
CREATE_STATEMENT_AUTOPILOT_ENDPOINT_DELETION_LUA_SCRIPT_PATH = \
    RESOURCE_LUA_DIR.joinpath("outputs").joinpath(
        "create_statement_autopilot_endpoint_deletion_lua_script.sql")
CREATE_STATEMENT_TEMPLATE_AUTOPILOT_ENDPOINT_DELETION_LUA_SCRIPT_PATH = \
    RESOURCE_LUA_DIR.joinpath("templates").joinpath(
        "create_statement_template_autopilot_endpoint_deletion_lua_script.sql")
CREATE_STATEMENT_AUTOPILOT_ENDPOINT_DELETION_UDF_RESOURCE_PATH = \
    RESOURCE_UDF_DIR.joinpath(
        "create_statement_autopilot_endpoint_deletion_udf.sql")
CREATE_STATEMENT_TEMPLATE_AUTOPILOT_ENDPOINT_DELETION_LUA_SCRIPT_TEXT = \
    CREATE_STATEMENT_TEMPLATE_AUTOPILOT_ENDPOINT_DELETION_LUA_SCRIPT_PATH.\
        read_text()
CREATE_STATEMENT_AUTOPILOT_ENDPOINT_DELETION_UDF_RESOURCE_TEXT = \
    CREATE_STATEMENT_AUTOPILOT_ENDPOINT_DELETION_UDF_RESOURCE_PATH.\
        read_text()

CREATE_STATEMENT_AUTOPILOT_JOBS_METADATA_TABLE_RESOURCE_TEXT = \
    RESOURCE_SQL_DIR.joinpath(
        "create_statement_autopilot_jobs_metadata_table.sql").read_text()
