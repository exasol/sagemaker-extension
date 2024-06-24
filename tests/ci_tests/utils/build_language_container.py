import pyexasol
import subprocess
from pathlib import Path
import exasol.bucketfs as bfs
from exasol.python_extension_common.deployment.language_container_deployer import LanguageContainerDeployer

from tests.integration_tests.utils.parameters import db_params

LANGUAGE_ALIAS = "PYTHON3_SME"
CONTAINER_FILE_NAME = "exasol_sagemaker_extension_container.tar.gz"


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


def build_language_container() -> Path:
    """
    Returns the path of the built container
    """
    script_dir = find_script("build_language_container.sh")
    completed_process = subprocess.run(
        [script_dir], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = completed_process.stdout.decode("UTF-8")
    print(output)
    completed_process.check_returncode()

    lines = output.splitlines()
    container_path_selector = "Cached container under "
    container_path = \
        next(line for line in lines if line.startswith(container_path_selector))
    container_path = container_path[len(container_path_selector):]
    return Path(container_path)


def upload_language_container(db_conn: pyexasol.ExaConnection,
                              bucketfs_location: bfs.path.PathLike) -> None:

    container_path = build_language_container()

    deployer = LanguageContainerDeployer(pyexasol_connection=db_conn,
                                         language_alias=LANGUAGE_ALIAS,
                                         bucketfs_path=bucketfs_location)

    deployer.run(container_file=container_path,
                 bucket_file_path=CONTAINER_FILE_NAME,
                 wait_for_completion=True)


def upload_language_container_onprem(db_conn: pyexasol.ExaConnection) -> None:

    bucketfs_location = bfs.path.build_path(backend=bfs.path.StorageBackend.onprem,
                                            url=f'http://{db_params.host}:{db_params.bfs_port}',
                                            username=db_params.bfs_user,
                                            password=db_params.bfs_password,
                                            verify=False,
                                            bucket_name='default',
                                            service_name='bfsdefault',
                                            path='container')

    upload_language_container(db_conn, bucketfs_location)


def upload_language_container_saas(db_conn: pyexasol.ExaConnection,
                                   saas_url: str,
                                   saas_account_id: str,
                                   saas_database_id: str,
                                   saas_token: str) -> None:

    bucketfs_location = bfs.path.build_path(backend=bfs.path.StorageBackend.saas,
                                            url=saas_url,
                                            account_id=saas_account_id,
                                            database_id=saas_database_id,
                                            pat=saas_token)

    upload_language_container(db_conn, bucketfs_location)
