import os.path
import tempfile
import subprocess
from typing import List
from exasol_sagemaker_extension.deployment import constants
import logging
logger = logging.getLogger(__name__)


class BaseCreateStatementGenerator:
    """
    This class packages Lua modules into a single file and generates
    the CREATE SCRIPT statement sql by inserting the packaged module
    inside the sql script.

    :param lua_src_files: List of Lua source file names
    :param modules: List of Lua module names
    :param create_statement_output_path: Path of the generated CREATE statement
    :param create_statement_template_text: Template of the CREATE statement to
    which the bundled scripts will be inserted.
    """
    def __init__(
            self,
            lua_src_files: List[str],
            modules: List[str],
            create_statement_output_path: str,
            create_statement_template_text: str):
        self._lua_copy_source_list = lua_src_files
        self._lua_modules = modules
        self._lua_modules_str = " ".join(modules)
        self._create_statement_output_path = create_statement_output_path
        self._create_statement_template_text = create_statement_template_text

    def _copy_lua_source_files(self, tmp_dir: str):
        """
        Copy Lua source files into the temporary directory where amalg script
        is executed and the bundle script is generated

        :param tmp_dir: Temporary directory path
        """
        for lua_src_file in self._lua_copy_source_list:
            src_data = (constants.LUA_SRC_DIR / lua_src_file).read_text()
            with open(os.path.join(tmp_dir, lua_src_file), "w") as file:
                file.write(src_data)
                logger.debug(f"Copy {lua_src_file} to {tmp_dir}")

    def _bundle_lua_scripts(self, tmp_dir: str):
        """
        Executes amalg.lua script to bundle given Lua modules.

        :param tmp_dir: Temporary directory path
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

        :param tmp_dir: Temporary directory path

        :return: The generated CREATE SCRIPT sql statement
        """
        with open(os.path.join(tmp_dir, constants.LUA_BUNDLED), "r") as file:
            lua_bundled_data = file.read()

        logger.debug("Bundled script is inserted into create statement")
        return self._create_statement_template_text.format(
            BUNDLED_SCRIPT=lua_bundled_data)

    def get_statement(self):
        """
        Executes helper functions sequentially
        to generate CREATE SCRIPT sql statement

        :return: The generated CREATE SCRIPT sql statement
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            self._copy_lua_source_files(tmp_dir)
            self._bundle_lua_scripts(tmp_dir)
            stmt = self._insert_bundle_into_sql_script(tmp_dir)

        return stmt

    def save_statement(self):
        stmt = self.get_statement()
        with open(self._create_statement_output_path, "w") as file:
            file.write(stmt)
            logger.debug(f"The create statement saved.")
