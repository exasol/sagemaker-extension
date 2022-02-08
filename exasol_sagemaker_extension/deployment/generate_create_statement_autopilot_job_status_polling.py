from exasol_sagemaker_extension.deployment import constants
from exasol_sagemaker_extension.deployment.generate_create_statement_base \
    import BaseCreateStatementGenerator


class AutopilotJobStatusPollingLuaScriptCreateStatementGenerator(BaseCreateStatementGenerator):
    """
    This is a custom class which generates CREATE SCRIPT sql statement
    polling status of a given Autopilot job.
    """
    def __init__(self):
        self._lua_src_files = [
            constants.LUA_SRC_MODULE_AUTOPILOT_JOB_STATUS_POLLING_NAME]
        self._modules = [
            "autopilot_job_status_polling.lua",
            "exaerror",
            "message_expander"]
        self._create_statement_output_path = constants.\
            CREATE_STATEMENT_AUTOPILOT_JOB_STATUS_POLLING_LUA_SCRIPT_PATH
        self._create_statement_template_text = constants.\
            CREATE_STATEMENT_TEMPLATE_AUTOPILOT_JOB_STATUS_POLLING_LUA_SCRIPT_TEXT

        super().__init__(
            lua_src_files=self._lua_src_files,
            modules=self._modules,
            create_statement_output_path=self._create_statement_output_path,
            create_statement_template_text=self._create_statement_template_text)
