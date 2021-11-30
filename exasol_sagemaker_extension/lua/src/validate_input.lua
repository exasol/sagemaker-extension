
---
-- @module validate_input
--
-- This module validates user inputs
--

local M = {
    max_length_job_name = 32
}


---
-- Checks whether a given job_name is valid for AWS autopilot
--
-- @param job_name     The name of the Autopilot job
--
function M.is_autopilot_job_name_valid(job_name)
    if string.len(job_name) <= M.max_length_job_name and
            string.match(job_name, "^(%w+)$") then
        return true
    end
    return false
end


---
-- Checks whether a given endpoint_name is valid for both AWS autopilot and SQL
--
-- @param endpoint_name     The name of the Autopilot endpoint
--
function M.is_autopilot_endpoint_name_valid(endpoint_name)
    if string.match(endpoint_name, "^(%w+)$") then
        return true
    end
    return false
end



return M;