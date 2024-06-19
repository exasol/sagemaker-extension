from collections import namedtuple
import exasol.bucketfs as bfs


POLLING_INTERVAL = 5 * 60  # seconds
TIMEOUT = 90 * 60  # seconds

ModelSetupParams = namedtuple("ModelSetupParams", [
    "model_type", "schema_name", "table_name", "target_col",
    "data", "aws_output_path", "batch_size"])

reg_model_setup_params = ModelSetupParams(
    model_type='reg',
    schema_name="reg_schema",
    table_name="reg_table",
    target_col="output_col",
    data=[f"({i * 1.1}, {i * 1.2}, {i * 10})" for i in range(1, 1000)],
    aws_output_path="reg_path",
    batch_size=10
)

cls_model_setup_params = ModelSetupParams(
    model_type='cls',
    schema_name="cls_schema",
    table_name="cls_table",
    target_col="output_col",
    data=[f"({i * 1.1}, {i * 1.2}, {i % 2})" for i in range(1, 1000)],
    aws_output_path="cls_path",
    batch_size=10
)


def get_db_params():
    DBParams = namedtuple("DBParams", [
        "host", "port", "user", "password"])

    return DBParams(
        host="127.0.0.1",
        port="9563",
        user="sys",
        password="exasol"
    )


db_params = get_db_params()


def get_bfs_root_path() -> bfs.path.PathLike:
    root_path = bfs.path.build_path(
        backend="onprem",
        url=f"http://{db_params.host}:{db_params.port}",
        username="w",
        password="write",
        bucket_name="bfsdefault",
        verify=False,
    )

    return root_path