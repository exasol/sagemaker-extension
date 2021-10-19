import shutil
import os.path
import subprocess
from pathlib import Path
import importlib_resources
from exasol_sagemaker_extension.deployment import constants

# This script packages Lua modules into a single file and generates
# the CREATE SCRIPT statement sql by inserting the packaged module
# inside the sql script.


class ExportingCreateStatementGenerator:

    def __init__(self):
        self._lua_copy_source_list = [
            constants.LUA_SRC_EXECUTER,
            constants.LUA_SRC_AWS_HANDLER]
        self._tmp_dir_name = ExportingCreateStatementGenerator.__name__
        self._tmp_dir = self.__create_tmp_dir()

    def __create_tmp_dir(self):
        tmp_dir_path = os.path.join(constants.TMP_DIR, self._tmp_dir_name)
        Path(tmp_dir_path).mkdir(parents=True, exist_ok=True)

        print(f"Temporary directory {tmp_dir_path} is created")
        return tmp_dir_path

    def _copy_lua_source_files(self):
        for lua_src_file in self._lua_copy_source_list:
            src_data = (constants.LUA_SRC_DIR / lua_src_file).read_text()
            with open(os.path.join(self._tmp_dir, lua_src_file), "w") as file:
                file.write(src_data)
                print(f"Copy {lua_src_file} to {self._tmp_dir}")

    def _bundle_lua_scripts(self):
        bash_command = \
            "cd {tmp_dir} " \
            "&& amalg.lua -o {src_path} -s execute_exporter.lua aws_s3_handler " \
            "&& amalg.lua -o {err_path} -s {src_path} exaerror " \
            "&& amalg.lua -o {fin_path} -s {err_path} message_expander".format(
                tmp_dir=self._tmp_dir,
                src_path=constants.LUA_BUNDLED_SOURCES_PATH,
                err_path=constants.LUA_BUNDLED_EXAERROR_PATH,
                fin_path=constants.LUA_BUNDLED_FINAL_PATH)

        subprocess.check_call(bash_command, shell=True)
        print(f"Lua scripts are bundled into {constants.LUA_BUNDLED_FINAL_PATH}")

    def _remove_tmp_dir(self):
        if os.path.exists(self._tmp_dir):
            shutil.rmtree(self._tmp_dir, ignore_errors=True)
            print("Temporary directory is removed")

    def _insert_bundle_into_sql_script(self):
        sql_tmplate = constants.\
            EXPORTING_CREATE_STATEMENT_TEMPLATE_SQL_PATH_OBJ.read_text()

        with open(constants.LUA_BUNDLED_FINAL_PATH, "r") as file:
            lua_bundled_data = file.read()

        return sql_tmplate.format(BUNDLED_SCRIPT=lua_bundled_data)

    def get_statement(self):
        self._copy_lua_source_files()
        self._bundle_lua_scripts()
        self._remove_tmp_dir()
        stmt = self._insert_bundle_into_sql_script()
        return stmt


