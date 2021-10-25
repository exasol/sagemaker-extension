CREATE OR REPLACE LUA SCRIPT EXPORT_TO_S3 (json_str)  AS
    table.insert(_G.package.searchers,
        function (module_name)
            local loader = package.preload[module_name]
            if not loader then
                error("Module " .. module_name .. " not found in package.preload.")
            else
                return loader
            end
        end
    )

{BUNDLED_SCRIPT}

local args = parse_arguments(json_str)
local aws_s3_handler = require("aws_s3_handler")
aws_s3_handler.export_to_s3(
			args['input_schema_name'],
			args['input_table_or_view_name'],
			args['aws_credentials_connection_name'],
			args['s3_output_path'])
/






