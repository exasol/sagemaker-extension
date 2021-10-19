import os.path
import subprocess
import importlib_resources
from exasol_sagemaker_extension.deployment import constants

# This script packages Lua modules into a single file and generates
# the CREATE SCRIPT statement sql by inserting the packaged module
# inside the sql script.


lua_copy_source_list = [
    constants.LUA_SRC_EXECUTER,
    constants.LUA_SRC_AWS_HANDLER]

lua_remove_artifact_list = [
    constants.LUA_BUNDLED_SOURCES_PATH,
    constants.LUA_BUNDLED_EXAERROR_PATH]


def copy_lua_source_files():
    for lua_src_file in lua_copy_source_list:
        src_data = (constants.LUA_SRC_DIR / lua_src_file).read_text()
        with open(os.path.join(constants.TMP_DIR, lua_src_file), "w") as file:
            file.write(src_data)
            print(f"Copy {lua_src_file} to {constants.TMP_DIR}")


def bundle_lua_scripts():
    bash_command = \
        "cd {tmp_dir} " \
        "&& amalg.lua -o {src_path} -s execute_exporter.lua aws_s3_handler " \
        "&& amalg.lua -o {err_path} -s {src_path} exaerror " \
        "&& amalg.lua -o {fin_path} -s {err_path} message_expander".format(
            tmp_dir=constants.TMP_DIR,
            src_path=constants.LUA_BUNDLED_SOURCES_PATH,
            err_path=constants.LUA_BUNDLED_EXAERROR_PATH,
            fin_path=constants.LUA_BUNDLED_FINAL_PATH)

    subprocess.check_call(bash_command, shell=True)
    print(f"Lua scripts are bundled into {constants.LUA_BUNDLED_FINAL_PATH}")


def clean_lua_artifacts():
    for file_path in lua_remove_artifact_list:
        os.remove(file_path)
    print("Lua bundle artifacts are removed")


def insert_bundle_into_sql_script():
    sql_template = constants.\
        EXPORTING_CREATE_STATEMENT_TEMPLATE_SQL_PATH_OBJ.read_text()

    with open(constants.LUA_BUNDLED_FINAL_PATH, "r") as file:
        lua_bundled_data = file.read()

    with open(constants.EXPORTING_CREATE_SCRIPT_PATH, "w") as file:
        file.write(sql_template.format(BUNDLED_SCRIPT=lua_bundled_data))

    print(f"Create statement is saved as "
          f"{constants.EXPORTING_CREATE_SCRIPT_PATH}")


def run():
    copy_lua_source_files()
    bundle_lua_scripts()
    clean_lua_artifacts()
    insert_bundle_into_sql_script()


if __name__ == "__main__":
    run()

