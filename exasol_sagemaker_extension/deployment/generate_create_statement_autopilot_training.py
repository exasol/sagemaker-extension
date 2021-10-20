from exasol_sagemaker_extension.deployment import constants
from exasol_sagemaker_extension.deployment.generate_create_statement_base import \
    BaseCreateStatementGenerator


class AutopilotTrainingCreateStatementGenerator(BaseCreateStatementGenerator):
    """
    This is a custom class which generates CREATE SCRIPT sql statement
    exporting a given Exasol table into AWS S3 and
    training the exported data with AWS Sagemaker Autopilot
    """
    def __init__(self):
        self._lua_src_files = [
            constants.LUA_SRC_EXECUTER,
            constants.LUA_SRC_AWS_HANDLER]
        self._modules = [
            "execute_exporter.lua",
            "aws_s3_handler",
            "exaerror",
            "message_expander"]
        self._create_statement_template = \
            constants.CREATE_STATEMENT_TEMPLATE_AUTOPILOT_TRAINING_RESOURCE

        super().__init__(
            lua_src_files=self._lua_src_files,
            modules=self._modules,
            create_statement_template=self._create_statement_template)