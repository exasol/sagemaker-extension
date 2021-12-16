local luaunit = require("luaunit")
local validate_input = require("validate_input")


test_validate_input= {
    sample_job_name_inputs = {
        ["jobname"] = true,
        ["JobName"] = true,
        ["123JobName"] = true,
        ["JobName123"] = true,
        ["Job Name"] = false,
        ["Job_Name"] = false,
        ["Job-Name"] = false,
        ["Job123-Name"] = false,
        ["JobName123456789123456789123456789"] = false,
    },

    sample_endpoint_name_inputs = {
        ["endpointname"] = true,
        ["EndpointName"] = true,
        ["EndpointName123"] = true,
        ["123EndpointName"] = true,
        ["Endpoint Name"] = false,
        ["Endpoint_Name"] = false,
        ["Endpoint-Name"] = false,
        ["Endpoint123-Name"] = false
    }
}

function test_validate_input.test_autopilot_job_name()
    for job_name, expected  in pairs(
            test_validate_input.sample_job_name_inputs) do
        luaunit.assertEquals(
                validate_input.is_autopilot_job_name_valid(job_name), expected)
    end
end

function test_validate_input.test_autopilot_endpoint_name()
    for endpoint_name, expected  in pairs(
            test_validate_input.sample_endpoint_name_inputs) do
        luaunit.assertEquals(
                validate_input.is_autopilot_endpoint_name_valid(endpoint_name), expected)
    end
end




os.exit(luaunit.LuaUnit.run())