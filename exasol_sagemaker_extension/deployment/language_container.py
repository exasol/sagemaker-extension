import sys
import os
from contextlib import contextmanager

from exasol.python_extension_common.deployment.language_container_builder import (
    LanguageContainerBuilder, find_path_backwards)

CONTAINER_NAME = "exasol_sagemaker_extension_container"


@contextmanager
def language_container_factory():
    with LanguageContainerBuilder(CONTAINER_NAME) as container_builder:
        project_directory = find_path_backwards("pyproject.toml", __file__).parent
        container_builder.prepare_flavor(project_directory)
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
