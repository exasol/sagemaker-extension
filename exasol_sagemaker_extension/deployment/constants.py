import os.path
import logging
import importlib_resources

# set logger
logging.basicConfig(
    format='%(asctime)s - %(module)s  - %(message)s',
    level=logging.DEBUG)
logger = logging.getLogger(__name__)

# set deployment paths
BASE_DIR = importlib_resources.files("exasol_sagemaker_extension")
LUA_SRC_DIR = (BASE_DIR / "lua" / "src")

LUA_SRC_EXECUTER = "execute_exporter.lua"
LUA_SRC_AWS_HANDLER = "aws_s3_handler.lua"
LUA_BUNDLED = "bundle_final.lua"

EXPORTING_CREATE_STATEMENT_TEMPLATE_SQL_PATH_OBJ = BASE_DIR.joinpath(
    "resources").joinpath("create_statement_exporting_template.sql")
TRAINING_CREATE_STATEMENT_SQL_PATH_OBJ = BASE_DIR.joinpath(
    "resources").joinpath("create_statement_training.sql")
