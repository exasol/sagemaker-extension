---
-- @module aws_s3_handler
--
-- This module handles AWS S3 service operations.
--

local M = {pquery_func = nil}

function M.init(pquery_func)
	M.pquery_func = pquery_func
	return M
end




---
-- Export the specified Exasol table to AWS S3
--
-- @param table_name						the name of the Exasol table to be exported
-- @param aws_credentials_connection_name	the name of the connection object with the AWS credentials
-- @param s3_output_path					the s3 bucket path to be placed
--
-- @return	boolean indicating whether it is exported successfully
--

function M.export_to_s3(schema_name, table_name, aws_credentials_connection_name, s3_output_path)
	-- get number of nodes for parallelism
	local success, res = pquery([[SELECT NPROC()]])
	if not success or #res < 1  then
		exit()
	end

	-- init
	local n_nodes = res[1][1]
	local parallelism_factor = 2
	local n_exporter = n_nodes * parallelism_factor
	local query_export = [[EXPORT ::t INTO CSV AT ::c]]
	local params = {
			t=schema_name..'.'..table_name,
			c=aws_credentials_connection_name}

	-- prepare the query
	for i=1, n_exporter do
		key_ = 'f' .. tostring(i)
		val_ =  s3_output_path .. table_name .. tostring(i) .. '.csv'
		query_export = query_export .. ' FILE :' .. key_
		params[key_] = val_
	end

	-- execute
	success, res = pquery(query_export, params)

	if not success then
		exit()
	end

	return success
end

return M;