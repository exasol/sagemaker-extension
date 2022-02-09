from exasol_sagemaker_extension.deployment import constants
from exasol_sagemaker_extension.deployment.generate_create_statement_base \
    import BaseCreateStatementGenerator


class AutopilotTrainingLuaScriptCreateStatementGenerator(BaseCreateStatementGenerator):
    """
    This is a custom class which generates CREATE SCRIPT sql statement
    exporting a given Exasol table into AWS S3 and
    run a training on the exported data with AWS Sagemaker Autopilot
    """
    def __init__(self):
        self._lua_src_files = [
            constants.LUA_SRC_MODULE_AUTOPILOT_TRAINING_MAIN_NAME,
            constants.LUA_SRC_MODULE_VALIDATE_INPUT,
            constants.LUA_SRC_MODULE_AWS_S3_HANDLER_NAME,
            constants.LUA_SRC_MODULE_DB_METADATA_WRITER_NAME,
            constants.LUA_SRC_MODULE_AWS_SAGEMAKER_HANDLER_NAME]
        self._modules = [
            "autopilot_training_main.lua",
            "validate_input",
            "aws_s3_handler",
            "db_metadata_writer",
            "aws_sagemaker_handler",
            "exaerror",
            "message_expander"]
        self._create_statement_output_path = constants.\
            CREATE_STATEMENT_AUTOPILOT_TRAINING_LUA_SCRIPT_PATH
        self._create_statement_template_text = constants.\
            CREATE_STATEMENT_TEMPLATE_AUTOPILOT_TRAINING_LUA_SCRIPT_TEXT

        super().__init__(
            lua_src_files=self._lua_src_files,
            modules=self._modules,
            create_statement_output_path=self._create_statement_output_path,
            create_statement_template_text=self._create_statement_template_text)

