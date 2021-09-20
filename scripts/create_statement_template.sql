CREATE OR REPLACE LUA SCRIPT "BUNDLE" () RETURNS TABLE AS
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

BUNDLED_SCRIPT

/

--/
CREATE OR REPLACE LUA SCRIPT TRAIN_WITH_SAGEMAKER_AUTOPILOT (json_str) AS
    import('BUNDLE', 'bundle')
    bundle.main(json_str)
/




