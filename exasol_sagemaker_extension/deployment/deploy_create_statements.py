import argparse
import pyexasol
import os.path
from typing import Dict
import importlib_resources
from exasol_sagemaker_extension.deployment import constants
from exasol_sagemaker_extension.deployment.constants import logger
from exasol_sagemaker_extension.deployment.\
    generate_create_statement_exporting_sql \
    import ExportingCreateStatementGenerator


class DeployCreateStatements:
    """
    This class executes or prints out CREATE SCRIPT sql statements
    that generate scripts deploying the sagemaker-extension project.
    """

    def __init__(self, **kwargs):
        self._db_host = kwargs['host']
        self._db_port = kwargs['port']
        self._db_user = kwargs['user']
        self._db_pass = kwargs['pass']
        self._schema = kwargs['schema']
        self._to_print = kwargs['print']
        self.__exasol_conn = pyexasol.connect(
            dsn="{host}:{port}".format(host=self._db_host, port=self._db_port),
            user=self._db_user,
            password=self._db_pass,
            compression=True)

    def run(self):
        """
        Run the deployment by retrieving the CREATE SCRIPTS sql statements
        """
        exportig_create_stmt = self._create_exporting_statement()
        training_create_stmt = self._create_training_statement()
        logger.debug(f"Create statements are obtained")

        statement_maps= {
                "exporting create statement": exportig_create_stmt,
                "training create statement": training_create_stmt}
        
        if not self._to_print:
            self._open_schema()
            self._execute_statements(statement_maps)
        else:
            print("\n".join(statement_maps.values()))

    def _create_exporting_statement(self):
        """
        Generate and return exporting CREATE SCRIPT sql statement.

        :return str: exporting CREATE SCRIPT sql statement
        """
        statement_generator = ExportingCreateStatementGenerator()
        statement_str = statement_generator.get_statement()
        return statement_str

    def _create_training_statement(self):
        """
        Read and return training CREATE SCRIPT udf script statement

        :return str: training CREATE SCRIPT udf script statement
        """
        statement_str = constants.\
            TRAINING_CREATE_STATEMENT_SQL_PATH_OBJ.read_text()
        return statement_str

    def _open_schema(self):
        """
        Open and use the  schema  for where deployment is performed
        """
        queries = ["CREATE SCHEMA IF NOT EXISTS {schema_name}",
                   "OPEN SCHEMA {schema_name}"]
        for query in queries:
            self.__exasol_conn.execute(query.format(schema_name=self._schema))
        logger.debug(f"Scheme -{schema_name}- is opened")

    def _execute_statements(self, statement_list: Dict[str, str]):
        """
        Executes CREATE SCRIPT sql statements on Exasol db
        """
        for desc, stmt in statement_list.items():
            self.__exasol_conn.execute(stmt)
            logger.debug(f"Statement -{desc}- is executed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="deploy the Sagemaker Extension")
    parser.add_argument("--host", help="db host address", required=True)
    parser.add_argument("--port", help="db host port", required=True)
    parser.add_argument("--user", help="db user name", required=True)
    parser.add_argument("--pass", help="db user password", required=True)
    parser.add_argument("--schema", help="schema name", required=True)
    parser.add_argument("--print", help="print out statements",
                        required=False, action="store_true")

    args = vars(parser.parse_args())
    deployment = DeployCreateStatements(**args)
    deployment.run()