import argparse
import pyexasol
import importlib_resources
from exasol_sagemaker_extension.resources import \
    generate_create_statement_exporting_sql


package = importlib_resources.files("exasol_sagemaker_extension")
TRAINING_CREATE_STATEMENT_SQL_PATH = package.joinpath(
    "resources").joinpath("create_statement_training.sql")
EXPORTING_CREATE_STATEMENT_SQL_PATH = package.joinpath(
    "target").joinpath("create_statement_exporting.sql")


class DeployCreateStatements:
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
        exportig_create_stmt = self._create_exporting_statement()
        training_create_stmt = self._create_training_statement()
        statement_maps= {
                "exporting create statement": exportig_create_stmt,
                "training create statement": training_create_stmt
        }
        if not self._to_print:
            self._open_schema()
            self._execute_statements(statement_maps)
        else:
            print("\n".join(statement_maps.values()))

    def _create_exporting_statement(self):
        generate_create_statement_exporting_sql.run()
        with open(EXPORTING_CREATE_STATEMENT_SQL_PATH) as f:
            statement_str = f.read()
        return statement_str

    def _create_training_statement(self):
        with open(TRAINING_CREATE_STATEMENT_SQL_PATH) as f:
            statement_str = f.read()
        return statement_str

    def _open_schema(self):
        queries = ["CREATE SCHEMA IF NOT EXISTS {schema_name}",
                   "OPEN SCHEMA {schema_name}"]
        for query in queries:
            self.__exasol_conn.execute(query.format(schema_name=self._schema))

    def _execute_statements(self, statement_list: dict):
        for desc, stmt in statement_list.items():
            self.__exasol_conn.execute(stmt)
            print(f"Executed {desc}")


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