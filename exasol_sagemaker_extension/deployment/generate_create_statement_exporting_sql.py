import os.path
import subprocess
from pathlib import Path
import importlib_resources

# This script packages Lua modules into a single file and generates
# the CREATE SCRIPT statement sql by inserting the packaged module
# inside the sql script.


BASE_DIR = importlib_resources.files("exasol_sagemaker_extension")

LUA_SRC_DIR = (BASE_DIR / "lua" / "src")
TARGET_DIR = (BASE_DIR / "target")

LUA_BUNDLED_SOURCES_PATH = TARGET_DIR.joinpath("bundle_sources.lua")
LUA_BUNDLED_EXAERROR_PATH = TARGET_DIR.joinpath("bundle_exaerror.lua")
LUA_BUNDLED_FINAL_PATH = TARGET_DIR.joinpath("bundle_final.lua")
lua_remove_artifact_list = [
    LUA_BUNDLED_SOURCES_PATH,
    LUA_BUNDLED_EXAERROR_PATH]

EXPORTING_CREATE_SCRIPT_TEMPLATE_PATH =  BASE_DIR.joinpath(
    "resources").joinpath("create_statement_exporting_template.sql")
EXPORTING_CREATE_SCRIPT_PATH = TARGET_DIR.joinpath(
    "create_statement_exporting.sql")


def create_target_dir():
    Path(TARGET_DIR).mkdir(parents=True, exist_ok=True)
    print(f"{TARGET_DIR} is created if not exist")


def bundle_lua_scripts():
    bash_command = \
        "cd {lua_dir} " \
        "&& amalg.lua -o {src_path} -s execute_exporter.lua aws_s3_handler " \
        "&& amalg.lua -o {err_path} -s {src_path} exaerror " \
        "&& amalg.lua -o {fin_path} -s {err_path} message_expander".format(
            lua_dir=LUA_SRC_DIR,
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
    with open(EXPORTING_CREATE_SCRIPT_TEMPLATE_PATH, "r") as file:
        sql_template = file.read()

    with open(LUA_BUNDLED_FINAL_PATH, "r") as file:
        lua_bundled_data = file.read()

    with open(EXPORTING_CREATE_SCRIPT_PATH, "w") as file:
        file.write(sql_template.format(BUNDLED_SCRIPT=lua_bundled_data))

    print(f"Create statement is saved as {EXPORTING_CREATE_SCRIPT_PATH}")


def run():
    create_target_dir()
    bundle_lua_scripts()
    clean_lua_artifacts()
    insert_bundle_into_sql_script()


if __name__ == "__main__":
    run()

