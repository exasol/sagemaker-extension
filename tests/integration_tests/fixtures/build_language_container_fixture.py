import pytest
import subprocess
from pathlib import Path

import exasol_bucketfs_utils_python.upload as bfsupload
from exasol_bucketfs_utils_python.bucket_config import BucketConfig
from exasol_bucketfs_utils_python.bucketfs_config import BucketFSConfig
from exasol_bucketfs_utils_python.bucketfs_connection_config import \
    BucketFSConnectionConfig


def find_script(script_name: str):
    current_path = Path("../..").absolute()
    script_path = None
    while current_path != current_path.root:
        script_path = Path(current_path, script_name)
        if script_path.exists():
            break
        current_path = current_path.parent
    if script_path.exists():
        return script_path
    else:
        raise RuntimeError("Could not find build_language_container.sh")


@pytest.fixture(scope="session")
def language_container():
    script_dir = find_script("build_language_container.sh")
    completed_process = subprocess.run(
        [script_dir], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = completed_process.stdout.decode("UTF-8")
    completed_process.check_returncode()

    print(output)
    lines = output.splitlines()

    alter_session_selector = "ALTER SYSTEM SET SCRIPT_LANGUAGES='"
    alter_session = \
        [line for line in lines if line.startswith(alter_session_selector)][0]
    alter_session = alter_session[len(alter_session_selector):-2]

    container_path_selector = "Cached container under "
    container_path = \
        [line for line in lines if line.startswith(container_path_selector)][0]
    container_path = container_path[len(container_path_selector):]

    return {
        "container_path": container_path,
        "alter_session": alter_session
    }


@pytest.fixture(scope="session")
def upload_language_container(language_container, get_params, db_conn):
    connection_config = BucketFSConnectionConfig(
        host=get_params["DB_CONNECTION_HOST"],
        port=6666,
        user="w",
        pwd="write",
        is_https=False
    )

    bucket_config = BucketConfig(
        bucket_name="default",
        bucketfs_config=BucketFSConfig(
            bucketfs_name="bfsdefault",
            connection_config=connection_config)
    )

    path_in_bucket = "container"
    container_name = "exasol_sagemaker_extension_container.tar.gz"
    container_path = Path(language_container["container_path"])

    alter_session = Path(language_container["alter_session"])
    db_conn.execute(f"ALTER SYSTEM SET SCRIPT_LANGUAGES='{alter_session}'")

    with open(container_path, "rb") as container_file:
        bfsupload.upload_fileobj_to_bucketfs(
            bucket_config=bucket_config,
            bucket_file_path=f"{path_in_bucket}/{container_name}",
            fileobj=container_file)

