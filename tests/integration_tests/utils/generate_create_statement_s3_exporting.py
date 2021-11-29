import os.path
from pathlib import PosixPath
from exasol_sagemaker_extension.deployment import constants
from exasol_sagemaker_extension.deployment.generate_create_statement_base \
    import BaseCreateStatementGenerator

UTILS_PATH = PosixPath("tests/integration_tests/utils")
CREATE_STMT_PATH = os.path.join(
    UTILS_PATH, "create_statement_template_s3_exporting_lua_script.sql")


class S3ExportingLuaScriptCreateStatementGenerator(BaseCreateStatementGenerator):
    """
    This is a custom class which generates CREATE SCRIPT sql statement
    exporting a given Exasol table into AWS S3 and
    run a training on the exported data with AWS Sagemaker Autopilot
    """

    def __init__(self):
        self._lua_src_files = [
            constants.LUA_SRC_MODULE_AUTOPILOT_TRAINING_MAIN_NAME,
            constants.LUA_SRC_MODULE_VALIDATE_INPUT,
            constants.LUA_SRC_MODULE_AWS_S3_HANDLER_NAME]
        self._modules = [
            "autopilot_training_main.lua",
            "validate_input",
            "aws_s3_handler",
            "exaerror",
            "message_expander"]
        with open(CREATE_STMT_PATH, "r") as file:
            self._create_statement_template_text = file.read()

        super().__init__(
            lua_src_files=self._lua_src_files,
            modules=self._modules,
            create_statement_template_text=self._create_statement_template_text)
