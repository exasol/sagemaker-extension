from exasol_sagemaker_extension.deployment import constants
from exasol_sagemaker_extension.deployment.generate_create_statement_base \
    import BaseCreateStatementGenerator


class AutopilotEndpointDeploymentLuaScriptCreateStatementGenerator(BaseCreateStatementGenerator):
    """
    This is a custom class which generates CREATE SCRIPT sql statement
    polling status of a given Autopilot job.
    """
    def __init__(self):
        self._lua_src_files = [
            constants.LUA_SRC_MODULE_SAGEMAKER_ENDPOINT_DEPLOYMENT_NAME,
            constants.LUA_SRC_MODULE_VALIDATE_INPUT,
            constants.LUA_SRC_MODULE_ENDPOINT_CONNECTION_HANDLER_NAME,
            constants.LUA_SRC_MODULE_INSTALL_AUTOPILOT_PREDICTION_UDF_NAME,
            constants.LUA_SRC_MODULE_DB_METADATA_READER_NAME
        ]
        self._modules = [
            "autopilot_endpoint_deployment.lua",
            "validate_input",
            "endpoint_connection_handler",
            "install_autopilot_prediction_udf",
            "db_metadata_reader",
            "exaerror",
            "message_expander"]
        self._create_statement_output_path = constants.\
            CREATE_STATEMENT_AUTOPILOT_ENDPOINT_DEPLOYMENT_LUA_SCRIPT_PATH
        self._create_statement_template_text = constants.\
            CREATE_STATEMENT_TEMPLATE_AUTOPILOT_ENDPOINT_DEPLOYMENT_LUA_SCRIPT_TEXT

        super().__init__(
            lua_src_files=self._lua_src_files,
            modules=self._modules,
            create_statement_output_path=self._create_statement_output_path,
            create_statement_template_text=self._create_statement_template_text)
