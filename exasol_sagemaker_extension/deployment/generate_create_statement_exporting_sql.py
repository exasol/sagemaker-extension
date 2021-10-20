import shutil
import os.path
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

    def _copy_lua_source_files(self):
        """
        Copy Lua source files into the temporary directory where amalg script
        is executed and the bundle script is generated
        """
        for lua_src_file in self._lua_copy_source_list:
            src_data = (constants.LUA_SRC_DIR / lua_src_file).read_text()
            with open(os.path.join(
                    constants.TMP_DIR, lua_src_file), "w") as file:
                file.write(src_data)
                logger.debug(f"Copy {lua_src_file} to {constants.TMP_DIR}")

    def _bundle_lua_scripts(self):
        """
        Executes amalg.lua script to bundle given Lua modules.
        """
        bash_command = \
            "cd {tmp_dir} && amalg.lua -o {fin_path} -s {modules}".format(
                tmp_dir=constants.TMP_DIR,
                fin_path=constants.LUA_BUNDLED_FINAL_PATH,
                modules=self._lua_modules_str)

        subprocess.check_call(bash_command, shell=True)
        logger.debug(f"Lua scripts are bundled into "
                     f"{constants.LUA_BUNDLED_FINAL_PATH}")

    def _remove_tmp_dir(self):
        """
        Remove the temporary directory when bundle operation is completed.
        """
        if os.path.exists(constants.TMP_DIR):
            constants.TMP_DIR_OBJ.cleanup()
            logger.debug("Temporary directory is removed")

    def _insert_bundle_into_sql_script(self):
        """
        Insert the bundled Lua script read in  temporary directory to
        the CREATE SCRIPT sql statement read from Resources.

        :return str: completed CREATE SCRIPT sql statement
        """
        sql_tmplate = constants.\
            EXPORTING_CREATE_STATEMENT_TEMPLATE_SQL_PATH_OBJ.read_text()

        with open(constants.LUA_BUNDLED_FINAL_PATH, "r") as file:
            lua_bundled_data = file.read()

        logger.debug("Bundled script is inserted into create statement")
        return sql_tmplate.format(BUNDLED_SCRIPT=lua_bundled_data)

    def get_statement(self):
        """
        Executes helper functions sequentially
        to generate CREATE SCRIPT sql statement

        :return str: completed CREATE SCRIPT sql statement
        """

        self._copy_lua_source_files()
        self._bundle_lua_scripts()
        stmt = self._insert_bundle_into_sql_script()
        self._remove_tmp_dir()
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
