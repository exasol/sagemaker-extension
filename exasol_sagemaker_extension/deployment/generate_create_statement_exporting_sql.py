import os.path
import subprocess
from pathlib import Path
import importlib_resources

# This script packages Lua modules into a single file and generates
# the CREATE SCRIPT statement sql by inserting the packaged module
# inside the sql script.


BASE_DIR = importlib_resources.files("exasol_sagemaker_extension")
LUA_SRC_DIR = (BASE_DIR / "lua" / "src")
TMP_DIR = "/tmp"


LUA_SRC_EXECUTER = "execute_exporter.lua"
LUA_SRC_AWS_HANDLER = "aws_s3_handler.lua"
LUA_BUNDLED_SOURCES_PATH = os.path.join(TMP_DIR, "bundle_sources.lua")
LUA_BUNDLED_EXAERROR_PATH = os.path.join(TMP_DIR, "bundle_exaerror.lua")
LUA_BUNDLED_FINAL_PATH = os.path.join(TMP_DIR, "bundle_final.lua")

lua_copy_source_list = [
    LUA_SRC_EXECUTER,
    LUA_SRC_AWS_HANDLER]
lua_remove_artifact_list = [
    LUA_BUNDLED_SOURCES_PATH,
    LUA_BUNDLED_EXAERROR_PATH]

EXPORTING_CREATE_SCRIPT_PATH = os.path.join(
    TMP_DIR, "create_statement_exporting.sql")
exporting_create_statement_template_sql_path_obj = BASE_DIR.joinpath(
    "resources").joinpath("create_statement_exporting_template.sql")


def copy_lua_source_files():
    for lua_src_file in lua_copy_source_list:
        src_data = (LUA_SRC_DIR / lua_src_file).read_text()
        with open(os.path.join(TMP_DIR, lua_src_file), "w") as file:
            file.write(src_data)
            print(f"Copy {lua_src_file} to {TMP_DIR}")


def bundle_lua_scripts():
    bash_command = \
        "cd {tmp_dir} " \
        "&& amalg.lua -o {src_path} -s execute_exporter.lua aws_s3_handler " \
        "&& amalg.lua -o {err_path} -s {src_path} exaerror " \
        "&& amalg.lua -o {fin_path} -s {err_path} message_expander".format(
            tmp_dir=TMP_DIR,
            src_path=LUA_BUNDLED_SOURCES_PATH,
            err_path=LUA_BUNDLED_EXAERROR_PATH,
            fin_path=LUA_BUNDLED_FINAL_PATH)

    subprocess.check_call(bash_command, shell=True)
    print(f"Lua scripts are bundled into {LUA_BUNDLED_FINAL_PATH}")


def clean_lua_artifacts():
    for file_path in lua_remove_artifact_list:
        os.remove(file_path)
    print("Lua bundle artifacts are removed")


def insert_bundle_into_sql_script():
    sql_template = exporting_create_statement_template_sql_path_obj.read_text()

    with open(LUA_BUNDLED_FINAL_PATH, "r") as file:
        lua_bundled_data = file.read()

    with open(EXPORTING_CREATE_SCRIPT_PATH, "w") as file:
        file.write(sql_template.format(BUNDLED_SCRIPT=lua_bundled_data))

    print(f"Create statement is saved as {EXPORTING_CREATE_SCRIPT_PATH}")


def run():
    copy_lua_source_files()
    bundle_lua_scripts()
    clean_lua_artifacts()
    insert_bundle_into_sql_script()


if __name__ == "__main__":
    run()

