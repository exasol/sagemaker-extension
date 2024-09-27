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


def export_slc():
    export_dir = sys.argv[1]
    if not os.path.isdir(export_dir):
        os.makedirs(export_dir)
    with language_container_factory() as container_builder:
        container_builder.export(export_dir)


if __name__ == '__main__':
    export_slc()
