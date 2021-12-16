---
-- @module db_metadata_reader
--
-- This module reads the metadata of an Autopilot job
--

local M = {}

local exaerror = require("exaerror")

_G.global_env = {
	pquery = pquery,
	error = error
}

---
-- Read the metadata of an Autopilot job
--
-- @param schema_name       The name of schema in which metadata table is stored
-- @param job_name          The name of the job, is used to find out the metadata
-- @param columns			The metadata columns to be read, by default read all columns
--
-- @return 		A table including desired columns
--
function M.read_metadata(schema, job_name, columns)
	local params = {
		schema=schema,
		job_name=job_name
	}

	local columns_ids = {}
	if columns == nil or columns == '' then
		columns_ids[#columns_ids+1] = '*'
	else
		for i=1, #columns do
			local key_ = 'c' .. tostring(i)
			columns_ids[#columns_ids+1] = '::' .. key_
			params[key_] = columns[i]
		end
	end

	local query_reading = [[SELECT ]] .. table.concat(columns_ids, ",")
			.. [[ FROM ::schema."SME_METADATA_AUTOPILOT_JOBS" WHERE JOB_NAME = :job_name]]
	local success, result = _G.global_env.pquery(query_reading, params)
	if not success then
		local error_obj = exaerror.create("F-SME-3",
				'Error occurred in reading metadata: ' .. result.error_message)
		_G.global_env.error(tostring(error_obj))
	end

	return result
end

return M;

