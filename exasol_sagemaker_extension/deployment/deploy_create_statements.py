import logging
import pyexasol
from typing import Dict
from exasol_sagemaker_extension.deployment import constants
from exasol_sagemaker_extension.deployment.\
    generate_create_statement_autopilot_endpoint_deletion \
    import AutopilotEndpointDeletionLuaScriptCreateStatementGenerator
from exasol_sagemaker_extension.deployment.\
    generate_create_statement_autopilot_job_status_polling import \
    AutopilotJobStatusPollingLuaScriptCreateStatementGenerator
from exasol_sagemaker_extension.deployment. \
    generate_create_statement_autopilot_training \
    import AutopilotTrainingLuaScriptCreateStatementGenerator
from exasol_sagemaker_extension.deployment.\
    generate_create_statement_autopilot_endpoint_deployment \
    import AutopilotEndpointDeploymentLuaScriptCreateStatementGenerator

logger = logging.getLogger(__name__)


class DeployCreateStatements:
    """
    This class executes or prints out CREATE SCRIPT sql statements
    that generate scripts deploying the sagemaker-extension project.
    """

    def __init__(self, db_host: str, db_port: str, db_user: str,
                 db_pass: str, schema: str, to_print: bool):
        self._db_host = db_host
        self._db_port = db_port
        self._db_user = db_user
        self._db_pass = db_pass
        self._schema = schema
        self._to_print = to_print
        self.__exasol_conn = pyexasol.connect(
            dsn="{host}:{port}".format(host=self._db_host, port=self._db_port),
            user=self._db_user,
            password=self._db_pass,
            compression=True)

    def run(self):
        """
        Run the deployment by retrieving the CREATE SCRIPTS sql statements
        """
        statement_maps = {
            "Create statement of autopilot training lua script":
                self._create_autopilot_training_lua_script_statement(),
            "Create statement of autopilot training udf":
                constants.CREATE_STATEMENT_AUTOPILOT_TRAINING_UDF_RESOURCE_TEXT,
            "Create statement of autopilot jobs metadata table":
                constants.CREATE_STATEMENT_AUTOPILOT_JOBS_METADATA_TABLE_RESOURCE_TEXT,
            "Create statement of autopilot job status polling lua script":
                self._create_autopilot_job_status_polling_lua_script_statement(),
            "Create statement of autopilot job status polling udf":
                constants.CREATE_STATEMENT_AUTOPILOT_JOB_STATUS_POLLING_UDF_RESOURCE_TEXT,
            "Create statement of autopilot endpoint deployment lua script":
                self._create_autopilot_endpoint_deployment_lua_script_statement(),
            "Create statement of autopilot endpoint deployment udf":
                constants.CREATE_STATEMENT_AUTOPILOT_ENDPOINT_DEPLOYMENT_UDF_RESOURCE_TEXT,
            "Create statement of autopilot endpoint deletion lua script":
                self._create_autopilot_endpoint_deletion_lua_script_statement(),
            "Create statement of autopilot endpoint deletion udf":
                constants.CREATE_STATEMENT_AUTOPILOT_ENDPOINT_DELETION_UDF_RESOURCE_TEXT,
        }
        logger.debug(f"Create statements are obtained")

        if not self._to_print:
            self._open_schema()
            self._execute_statements(statement_maps)
        else:
            print("\n".join(statement_maps.values()))


    def _create_autopilot_endpoint_deletion_lua_script_statement(self):
        """
        Generate and return an endpoint deletion CREATE SCRIPT sql statement.

        :return: The deletion CREATE SCRIPT sql statement
        """
        statement_generator = \
            AutopilotEndpointDeletionLuaScriptCreateStatementGenerator()
        statement_str = statement_generator.get_statement()
        return statement_str

    def _create_autopilot_endpoint_deployment_lua_script_statement(self):
        """
        Generate and return an endpoint deployment CREATE SCRIPT sql statement.

        :return: The deployment CREATE SCRIPT sql statement
        """
        statement_generator = \
            AutopilotEndpointDeploymentLuaScriptCreateStatementGenerator()
        statement_str = statement_generator.get_statement()
        return statement_str

    def _create_autopilot_job_status_polling_lua_script_statement(self):
        """
        Generate and return job status polling CREATE SCRIPT sql statement.

        :return: The polling CREATE SCRIPT sql statement
        """
        statement_generator = \
            AutopilotJobStatusPollingLuaScriptCreateStatementGenerator()
        statement_str = statement_generator.get_statement()
        return statement_str

    def _create_autopilot_training_lua_script_statement(self):
        """
        Generate and return exporting CREATE SCRIPT sql statement.

        :return: The exporting CREATE SCRIPT sql statement
        """
        statement_generator = \
            AutopilotTrainingLuaScriptCreateStatementGenerator()
        statement_str = statement_generator.get_statement()
        return statement_str

    def _open_schema(self):
        """
        Open and use the  schema  for where deployment is performed
        """
        queries = ["CREATE SCHEMA IF NOT EXISTS {schema_name}",
                   "OPEN SCHEMA {schema_name}"]
        for query in queries:
            self.__exasol_conn.execute(query.format(schema_name=self._schema))
        logger.debug(f"Schema {self._schema} is opened")

    def _execute_statements(self, statement_list: Dict[str, str]):
        """
        Executes CREATE SCRIPT sql statements on Exasol db
        """
        for desc, stmt in statement_list.items():
            self.__exasol_conn.execute(stmt)
            logger.debug(f"{desc} is executed")
