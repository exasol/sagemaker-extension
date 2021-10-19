import os.path
import logging
import tempfile
import importlib_resources

# set logger
logging.basicConfig(
    format='%(asctime)s - %(module)s  - %(message)s',
    level=logging.DEBUG)
logger = logging.getLogger(__name__)

# create tmp folder
TMP_DIR_OBJ = tempfile.TemporaryDirectory()
TMP_DIR = TMP_DIR_OBJ.name

# set deployment paths
BASE_DIR = importlib_resources.files("exasol_sagemaker_extension")
LUA_SRC_DIR = (BASE_DIR / "lua" / "src")

LUA_SRC_EXECUTER = "execute_exporter.lua"
LUA_SRC_AWS_HANDLER = "aws_s3_handler.lua"

LUA_BUNDLED_SOURCES_PATH = os.path.join(TMP_DIR, "bundle_sources.lua")
LUA_BUNDLED_EXAERROR_PATH = os.path.join(TMP_DIR, "bundle_exaerror.lua")
LUA_BUNDLED_FINAL_PATH = os.path.join(TMP_DIR, "bundle_final.lua")

EXPORTING_CREATE_STATEMENT_TEMPLATE_SQL_PATH_OBJ = BASE_DIR.joinpath(
    "resources").joinpath("create_statement_exporting_template.sql")
TRAINING_CREATE_STATEMENT_SQL_PATH_OBJ = BASE_DIR.joinpath(
    "resources").joinpath("create_statement_training.sql")
