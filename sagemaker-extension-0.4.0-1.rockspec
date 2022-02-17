package = "sagemaker-extension"
version = "0.4.0-1"
source = {
   url = "git://github.com/exasol/sagemaker-extension"
}
description = {
   detailed = "This project provides a Python library that trains data stored in Exasol using AWS SageMaker.",
   homepage = "https://github.com/exasol/sagemaker-extension",
   license = "MIT"
}
dependencies = {
    "lua >= 5.1",
    "amalg >= 0.8-1",
    "lua-cjson >= 2.1.0.6-1",
    "luaunit >= 3.4.-1",
    "mockagne >= 1.0-2",
    "exaerror >= 1.1.0-1",
    "luacheck >= 0.25.0-1",
    "luacov >= 0.15.0-1",
    "luacov-coveralls >= 0.2.3-1",
    "luaunit >= 3.4",
}
build = {
   type = "builtin",
   modules = {
      ["exasol_sagemaker_extension.lua.src.autopilot_endpoint_deletion"] = "exasol_sagemaker_extension/lua/src/autopilot_endpoint_deletion.lua",
      ["exasol_sagemaker_extension.lua.src.autopilot_endpoint_deployment"] = "exasol_sagemaker_extension/lua/src/autopilot_endpoint_deployment.lua",
      ["exasol_sagemaker_extension.lua.src.autopilot_job_status_polling"] = "exasol_sagemaker_extension/lua/src/autopilot_job_status_polling.lua",
      ["exasol_sagemaker_extension.lua.src.autopilot_training_main"] = "exasol_sagemaker_extension/lua/src/autopilot_training_main.lua",
      ["exasol_sagemaker_extension.lua.src.aws_s3_handler"] = "exasol_sagemaker_extension/lua/src/aws_s3_handler.lua",
      ["exasol_sagemaker_extension.lua.src.aws_sagemaker_handler"] = "exasol_sagemaker_extension/lua/src/aws_sagemaker_handler.lua",
      ["exasol_sagemaker_extension.lua.src.db_metadata_reader"] = "exasol_sagemaker_extension/lua/src/db_metadata_reader.lua",
      ["exasol_sagemaker_extension.lua.src.db_metadata_writer"] = "exasol_sagemaker_extension/lua/src/db_metadata_writer.lua",
      ["exasol_sagemaker_extension.lua.src.endpoint_connection_handler"] = "exasol_sagemaker_extension/lua/src/endpoint_connection_handler.lua",
      ["exasol_sagemaker_extension.lua.src.install_autopilot_prediction_udf"] = "exasol_sagemaker_extension/lua/src/install_autopilot_prediction_udf.lua",
      ["exasol_sagemaker_extension.lua.src.validate_input"] = "exasol_sagemaker_extension/lua/src/validate_input.lua",
      ["exasol_sagemaker_extension.lua.test.test_autopilot_endpoint_deletion"] = "exasol_sagemaker_extension/lua/test/test_autopilot_endpoint_deletion.lua",
      ["exasol_sagemaker_extension.lua.test.test_autopilot_endpoint_deployment"] = "exasol_sagemaker_extension/lua/test/test_autopilot_endpoint_deployment.lua",
      ["exasol_sagemaker_extension.lua.test.test_autopilot_job_status_polling"] = "exasol_sagemaker_extension/lua/test/test_autopilot_job_status_polling.lua",
      ["exasol_sagemaker_extension.lua.test.test_autopilot_training_main"] = "exasol_sagemaker_extension/lua/test/test_autopilot_training_main.lua",
      ["exasol_sagemaker_extension.lua.test.test_aws_s3_handler"] = "exasol_sagemaker_extension/lua/test/test_aws_s3_handler.lua",
      ["exasol_sagemaker_extension.lua.test.test_aws_sagemaker_handler"] = "exasol_sagemaker_extension/lua/test/test_aws_sagemaker_handler.lua",
      ["exasol_sagemaker_extension.lua.test.test_db_metadata_reader"] = "exasol_sagemaker_extension/lua/test/test_db_metadata_reader.lua",
      ["exasol_sagemaker_extension.lua.test.test_db_metadata_writer"] = "exasol_sagemaker_extension/lua/test/test_db_metadata_writer.lua",
      ["exasol_sagemaker_extension.lua.test.test_endpoint_connection_handler"] = "exasol_sagemaker_extension/lua/test/test_endpoint_connection_handler.lua",
      ["exasol_sagemaker_extension.lua.test.test_install_autopilot_prediction_udf"] = "exasol_sagemaker_extension/lua/test/test_install_autopilot_prediction_udf.lua",
      ["exasol_sagemaker_extension.lua.test.test_validate_input"] = "exasol_sagemaker_extension/lua/test/test_validate_input.lua"
   },
   copy_directories = {
      "doc",
      "tests"
   }
}
