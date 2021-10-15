import argparse
import pyexasol
import subprocess

EXPORTING_CREATE_STATEMENT_EXEC_PATH = \
    "scripts/generate_create_statement_exporting_sql.sh"
TRAINING_CREATE_STATEMENT_SQL_PATH = \
    "scripts/create_statement_training.sql"
EXPORTING_CREATE_STATEMENT_SQL_PATH = \
    "target/create_statement_exporting.sql"


class DeployCreateStatements:
    def __init__(self, **kwargs):
        self._db_host = kwargs['host']
        self._db_port = kwargs['port']
        self._db_user = kwargs['user']
        self._db_pass = kwargs['pass']
        self._schema = kwargs['schema']
        self._to_print = kwargs['print']
        self.__exasol_conn = None
        self.__statements = []

    def run(self):
        self._create_exporting_statement()
        self._create_training_statement()
        if not self._to_print:
            self._connect_to_database()
            self._open_schema()
            self._execute_statements()
        else:
            print("\n".join(self.__statements))

    def _create_exporting_statement(self):
        subprocess.call(EXPORTING_CREATE_STATEMENT_EXEC_PATH, shell=True)
        with open(EXPORTING_CREATE_STATEMENT_SQL_PATH) as f:
            statement_str = f.read()
            self.__statements.append(statement_str)

    def _create_training_statement(self):
        with open(TRAINING_CREATE_STATEMENT_SQL_PATH) as f:
            statement_str = f.read()
            self.__statements.append(statement_str)

    def _connect_to_database(self):
        db_connection_str = "{host}:{port}".format(
            host=self._db_host, port=self._db_port)

        self.__exasol_conn = pyexasol.connect(
            dsn=db_connection_str, user=self._db_user,
            password=self._db_pass, compression=True)

    def _open_schema(self):
        queries = ["CREATE SCHEMA IF NOT EXISTS {schema_name}",
                   "OPEN SCHEMA {schema_name}"]
        for query in queries:
            self.__exasol_conn.execute(query.format(schema_name=self._schema))

    def _execute_statements(self):
        for stmt in self.__statements:
            self.__exasol_conn.execute(stmt)


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