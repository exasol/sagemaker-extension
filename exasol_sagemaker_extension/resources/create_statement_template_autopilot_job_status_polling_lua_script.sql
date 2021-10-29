CREATE OR REPLACE LUA SCRIPT "SME_POLL_SAGEMAKER_AUTOPILOT_JOB_STATUS" (job_name, aws_s3_connection, aws_region)  RETURNS TABLE AS
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

local result, cols = main(exa, job_name, aws_s3_connection, aws_region)
return result, cols
/






