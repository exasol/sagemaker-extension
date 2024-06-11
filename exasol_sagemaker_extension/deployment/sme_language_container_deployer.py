from typing import Optional
from pathlib import Path
from exasol.python_extension_common.deployment.language_container_deployer import LanguageContainerDeployer


class SmeLanguageContainerDeployer(LanguageContainerDeployer):

    SLC_NAME = "exasol_sagemaker_extension_container.tar.gz"
    SLC_URL_FORMATTER = "https://github.com/exasol/sagemaker-extension/releases/download/{version}/" + SLC_NAME

    def download_from_github_and_run(self, version: str,
                                     alter_system: bool = True,
                                     allow_override: bool = False,
                                     wait_for_completion: bool = True) -> None:

        self.download_and_run(self.SLC_URL_FORMATTER.format(version=version), self.SLC_NAME,
                              alter_system=alter_system, allow_override=allow_override,
                              wait_for_completion=wait_for_completion)

    def run(self, container_file: Optional[Path] = None,
            bucket_file_path: Optional[str] = None,
            alter_system: bool = True,
            allow_override: bool = False,
            wait_for_completion: bool = True) -> None:

        if not bucket_file_path:
            bucket_file_path = self.SLC_NAME
        super().run(container_file, bucket_file_path, alter_system, allow_override, wait_for_completion)
