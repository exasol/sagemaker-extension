import sys
import os
import re
from contextlib import contextmanager

from exasol.python_extension_common.deployment.language_container_builder import (
    LanguageContainerBuilder, find_path_backwards, exclude_cuda)

CONTAINER_NAME = "exasol_sagemaker_extension_container"


def add_pytorch_to_requirements(container_builder: LanguageContainerBuilder) -> None:
    """Modifies the default dependencies/Dockerfile"""
    dockerfile_file = "flavor_base/dependencies/Dockerfile"
    dockerfile = container_builder.read_file(dockerfile_file)
    install_pattern = (
        r"^\s*(?i:run)\s+python\d.\d+\s+-m\s+pip\s+install"
        r"\s+-r\s+/project/requirements.txt"
    )
    install_extra = "--extra-index-url https://download.pytorch.org/whl/cpu"
    dockerfile = re.sub(
        install_pattern, rf"\g<0> {install_extra}", dockerfile, flags=re.MULTILINE
    )
    container_builder.write_file(dockerfile_file, dockerfile)


@contextmanager
def language_container_factory():
    with LanguageContainerBuilder(CONTAINER_NAME) as container_builder:
        add_pytorch_to_requirements(container_builder)
        project_directory = find_path_backwards("pyproject.toml", __file__).parent
        container_builder.prepare_flavor(project_directory, requirement_filter=exclude_cuda)
        yield container_builder


@contextmanager
def export_slc(export_dir: str | None = None):
    if export_dir and (not os.path.isdir(export_dir)):
        os.makedirs(export_dir)
    with language_container_factory() as container_builder:
        export_result = container_builder.export(export_dir)
        export_info = export_result.export_infos[str(container_builder.flavor_path)]["release"]
        yield export_info.cache_file


if __name__ == '__main__':
    with export_slc(sys.argv[1]):
        pass
