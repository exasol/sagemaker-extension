from __future__ import annotations
import logging

import pyexasol
from exasol.python_extension_common.connections.pyexasol_connection import open_pyexasol_connection

from exasol_sagemaker_extension.deployment import constants
from exasol_sagemaker_extension.deployment. \
    generate_create_statement_autopilot_endpoint_deletion \
    import AutopilotEndpointDeletionLuaScriptCreateStatementGenerator
from exasol_sagemaker_extension.deployment. \
    generate_create_statement_autopilot_job_status_polling import \
    AutopilotJobStatusPollingLuaScriptCreateStatementGenerator
from exasol_sagemaker_extension.deployment. \
    generate_create_statement_autopilot_training \
    import AutopilotTrainingLuaScriptCreateStatementGenerator
from exasol_sagemaker_extension.deployment. \
    generate_create_statement_autopilot_endpoint_deployment \
    import AutopilotEndpointDeploymentLuaScriptCreateStatementGenerator

logger = logging.getLogger(__name__)


class DeployCreateStatements:
    """
    This class executes or prints out CREATE SCRIPT sql statements
    that generate scripts deploying the sagemaker-extension project.
    """

    def __init__(self, exasol_conn: pyexasol.ExaConnection,
                 schema: str, to_print: bool, develop: bool):
        self._schema = schema
        self._to_print = to_print
        self._develop = develop
        self.__exasol_conn = exasol_conn

    @property
    def statement_maps(self):
        stmt_udf_texts = {
            "Create statement of autopilot training udf":
                constants.CREATE_STATEMENT_AUTOPILOT_TRAINING_UDF_RESOURCE_TEXT,
            "Create statement of autopilot job status polling udf":
                constants.CREATE_STATEMENT_AUTOPILOT_JOB_STATUS_POLLING_UDF_RESOURCE_TEXT,
            "Create statement of autopilot endpoint deployment udf":
                constants.CREATE_STATEMENT_AUTOPILOT_ENDPOINT_DEPLOYMENT_UDF_RESOURCE_TEXT,
            "Create statement of autopilot endpoint deletion udf":
                constants.CREATE_STATEMENT_AUTOPILOT_ENDPOINT_DELETION_UDF_RESOURCE_TEXT,
        }

        stmt_lua_texts = {
            "Create statement of autopilot training lua script":
                constants.CREATE_STATEMENT_AUTOPILOT_TRAINING_LUA_SCRIPT_PATH.
                read_text(),
            "Create statement of autopilot job status polling lua script":
                constants.CREATE_STATEMENT_AUTOPILOT_JOB_STATUS_POLLING_LUA_SCRIPT_PATH.
                read_text(),
            "Create statement of autopilot endpoint deployment lua script":
                constants.CREATE_STATEMENT_AUTOPILOT_ENDPOINT_DEPLOYMENT_LUA_SCRIPT_PATH.
                read_text(),
            "Create statement of autopilot endpoint deletion lua script":
                constants.CREATE_STATEMENT_AUTOPILOT_ENDPOINT_DELETION_LUA_SCRIPT_PATH.
                read_text(),
        }

        stmt_create_table_texts = {
            "Create statement of autopilot jobs metadata table":
                constants.CREATE_STATEMENT_AUTOPILOT_JOBS_METADATA_TABLE_RESOURCE_TEXT,
        }
        logger.debug(f"Create statements are obtained")

        return {**stmt_udf_texts, **stmt_lua_texts, **stmt_create_table_texts}

    def run(self):
        """
        Run the deployment by retrieving the CREATE SCRIPTS sql statements
        """
        # generate scripts from scratch
        if self._develop:
            self.create_statements()

        # print or execute scripts
        if not self._to_print:
            self._open_schema()
            self._execute_statements()
        else:
            print("\n".join(self.statement_maps.values()))

    def _open_schema(self):
        """
        Open and use the  schema  for where deployment is performed
        """
        queries = ["CREATE SCHEMA IF NOT EXISTS {schema_name}",
                   "OPEN SCHEMA {schema_name}"]
        for query in queries:
            self.__exasol_conn.execute(query.format(schema_name=self._schema))
        logger.debug(f"Schema {self._schema} is opened")

    def _execute_statements(self):
        """
        Executes CREATE SCRIPT sql statements on Exasol db
        """
        for desc, stmt in self.statement_maps.items():
            self.__exasol_conn.execute(stmt)
            logger.debug(f"{desc} is executed")

    @staticmethod
    def create_statements():
        """
        Creates and saves CREATE SCRIPT sql statements
        """
        generators = [
            AutopilotTrainingLuaScriptCreateStatementGenerator,
            AutopilotJobStatusPollingLuaScriptCreateStatementGenerator,
            AutopilotEndpointDeploymentLuaScriptCreateStatementGenerator,
            AutopilotEndpointDeletionLuaScriptCreateStatementGenerator
        ]
        for generator in generators:
            stmt_generator = generator()
            stmt_generator.save_statement()
            logger.debug(f"{stmt_generator.__class__.__name__} "
                         "is created and saved.")

    @classmethod
    def create_and_run(cls,
                       schema: str,
                       to_print: bool = False,
                       develop: bool = False,
                       **kwargs):

        exasol_conn = open_pyexasol_connection(**kwargs)
        deployer = cls(exasol_conn, schema, to_print, develop)
        deployer.run()
