CREATE OR REPLACE LUA SCRIPT "SME_DELETE_SAGEMAKER_AUTOPILOT_ENDPOINT" (endpoint_name, aws_s3_connection, aws_region)  AS
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

main(exa, endpoint_name, aws_s3_connection, aws_region)
/






