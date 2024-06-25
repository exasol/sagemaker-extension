from __future__ import annotations
import logging

import pyexasol
from exasol.python_extension_common.deployment.language_container_deployer import get_websocket_sslopt
from exasol.saas.client.api_access import get_connection_params

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
                       dsn: str | None = None,
                       db_user: str | None = None,
                       db_pass: str | None = None,
                       saas_url: str | None = None,
                       saas_account_id: str | None = None,
                       saas_database_id: str | None = None,
                       saas_database_name: str | None = None,
                       saas_token: str | None = None,
                       use_ssl_cert_validation: bool = True,
                       ssl_trusted_ca: str | None = None,
                       ssl_client_certificate: str | None = None,
                       ssl_private_key: str | None = None,
                       to_print: bool = False,
                       develop: bool = False):
        """
        Creates a database connection object, either in an On-Prem or SaaS database,
        based on the provided credentials. Creates an instance of the DeployCreateStatements
        passing the connection object to it and calls its run method.

        Parameters:
            schema              - Schema where the scripts should be created
            dsn                 - On-Prem database host address, including the port
            db_user             - On-Prem database username
            db_pass             - On-Prem database user password
            saas_url            - SaaS service url
            saas_account_id     - SaaS account id
            saas_database_id    - SaaS database id
            saas_database_name  - SaaS database name, to be used in case the id is unknown
            saas_token          - SaaS Personal Access Token (PAT)
            use_ssl_cert_validation - Use SSL server certificate validation
            ssl_trusted_ca          - Path to a file or directory with a trusted CA bundle
            ssl_client_certificate  - Path to a file with the client SSL certificate
            ssl_private_key         - Path to a file with the client private key
            to_print            - If True the script creation SQL commands will be
                                  printed rather than executed
            develop             - If True the scripts will be generated from scratch
        """

        # Infer where the database is - on-prem or SaaS.
        if all((dsn, db_user, db_pass)):
            connection_params = {'dsn': dsn, 'user': db_user, 'password': db_pass}
        elif all((saas_url, saas_account_id, saas_token,
                  any((saas_database_id, saas_database_name)))):
            connection_params = get_connection_params(host=saas_url,
                                                      account_id=saas_account_id,
                                                      database_id=saas_database_id,
                                                      database_name=saas_database_name,
                                                      pat=saas_token)
        else:
            raise ValueError('Incomplete parameter list. '
                             'Please either provide the parameters [dns, db_user, db_pass] '
                             'for an On-Prem database or [saas_url, saas_account_id, '
                             'saas_database_id, saas_token] for a SaaS database.')

        websocket_sslopt = get_websocket_sslopt(use_ssl_cert_validation, ssl_trusted_ca,
                                                ssl_client_certificate, ssl_private_key)

        exasol_conn = pyexasol.connect(**connection_params,
                                       encryption=True,
                                       websocket_sslopt=websocket_sslopt,
                                       compression=True)

        deployer = cls(exasol_conn, schema, to_print, develop)
        deployer.run()
