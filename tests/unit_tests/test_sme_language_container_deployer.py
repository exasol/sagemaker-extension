import pytest
from pathlib import Path
from unittest.mock import create_autospec, MagicMock, call
from pyexasol import ExaConnection
import exasol.bucketfs as bfs

from exasol_sagemaker_extension.deployment.sme_language_container_deployer import SmeLanguageContainerDeployer
from exasol.python_extension_common.deployment.language_container_deployer import LanguageActivationLevel

@pytest.fixture
def sme_container_deployer() -> SmeLanguageContainerDeployer:
    deployer = SmeLanguageContainerDeployer(pyexasol_connection=create_autospec(ExaConnection),
                                            language_alias='PYTHON3_TEST',
                                            bucketfs_path=create_autospec(bfs.path.PathLike))
    deployer.upload_container = MagicMock()
    deployer.activate_container = MagicMock()
    return deployer


def test_sme_language_container_deployer(sme_container_deployer):
    file_name = "sme_container.tar.gz"
    file_path = Path(file_name)
    sme_container_deployer.run(container_file=file_path,
                               bucket_file_path=file_name,
                               alter_system=True,
                               allow_override=True,
                               wait_for_completion=False)
    sme_container_deployer.upload_container.assert_called_once_with(file_path, file_name)
    expected_calls = [
        call(file_name, LanguageActivationLevel.Session, True),
        call(file_name, LanguageActivationLevel.System, True)
    ]
    sme_container_deployer.activate_container.assert_has_calls(expected_calls, any_order=True)
