import os.path
import tempfile
import subprocess
from typing import List
from pathlib import Path
import importlib_resources
from exasol_sagemaker_extension.deployment import constants
from exasol_sagemaker_extension.deployment.constants import logger

# This script packages Lua modules into a single file and generates
# the CREATE SCRIPT statement sql by inserting the packaged module
# inside the sql script.


class BaseCreateStatementGenerator:
    """
    This class packages Lua modules into a single file and generates
    the CREATE SCRIPT statement sql by inserting the packaged module
    inside the sql script.

    :param List[str] lua_src_files: list of lua source file names
    :param List[str] modules: list of module names
    """
    def __init__(self, lua_src_files: List[str], modules: List[str]):
        self._lua_copy_source_list = lua_src_files
        self._lua_modules = modules
        self._lua_modules_str = " ".join(modules)

    def _copy_lua_source_files(self, tmp_dir: str):
        """
        Copy Lua source files into the temporary directory where amalg script
        is executed and the bundle script is generated

        :param str tmp_dir: temporary directory  path
        """
        for lua_src_file in self._lua_copy_source_list:
            src_data = (constants.LUA_SRC_DIR / lua_src_file).read_text()
            with open(os.path.join(tmp_dir, lua_src_file), "w") as file:
                file.write(src_data)
                logger.debug(f"Copy {lua_src_file} to {tmp_dir}")

    def _bundle_lua_scripts(self, tmp_dir: str):
        """
        Executes amalg.lua script to bundle given Lua modules.

        :param str tmp_dir: temporary directory  path
        """
        lua_bundle_path = os.path.join(tmp_dir, constants.LUA_BUNDLED)
        bash_command = \
            "cd {tmp_dir} && amalg.lua -o {fin_path} -s {modules}".format(
                tmp_dir=tmp_dir,
                fin_path=lua_bundle_path,
                modules=self._lua_modules_str)

        subprocess.check_call(bash_command, shell=True)
        logger.debug(f"Lua scripts are bundled into {lua_bundle_path}")

    def _insert_bundle_into_sql_script(self, tmp_dir: str):
        """
        Insert the bundled Lua script read in  temporary directory to
        the CREATE SCRIPT sql statement read from Resources.

        :param str tmp_dir: temporary directory  path

        :return str: completed CREATE SCRIPT sql statement
        """
        sql_tmplate = constants.\
            EXPORTING_CREATE_STATEMENT_TEMPLATE_SQL_PATH_OBJ.read_text()

        with open(os.path.join(tmp_dir, constants.LUA_BUNDLED), "r") as file:
            lua_bundled_data = file.read()

        logger.debug("Bundled script is inserted into create statement")
        return sql_tmplate.format(BUNDLED_SCRIPT=lua_bundled_data)

    def get_statement(self):
        """
        Executes helper functions sequentially
        to generate CREATE SCRIPT sql statement

        :return str: completed CREATE SCRIPT sql statement
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            self._copy_lua_source_files(tmp_dir)
            self._bundle_lua_scripts(tmp_dir)
            stmt = self._insert_bundle_into_sql_script(tmp_dir)

        return stmt


class ExportingCreateStatementGenerator(BaseCreateStatementGenerator):
    """
    This is a custom class which generates CREATE SCRIPT sql statement
    exporting a given Exasol table into AWS S3.
    """
    def __init__(self):
        self._lua_src_files = [
            constants.LUA_SRC_EXECUTER,
            constants.LUA_SRC_AWS_HANDLER]
        self._modules = [
            "execute_exporter.lua",
            "aws_s3_handler",  
            "exaerror",  
            "message_expander"]
        super().__init__(self._lua_src_files, self._modules)
