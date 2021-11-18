---
-- @module aws_s3_handler
--
-- This module handles AWS S3 service operations.
--

local M = {
	default_parallelism_factor = 4
}

local exaerror = require("exaerror")

_G.global_env = {
	pquery = pquery,
	error = error
}

---
-- Get the number of Exasol nodes.
--
-- @return an integer that shows the number of nodes
--
function M.get_node_count()
	local success, result = _G.global_env.pquery([[SELECT NPROC()]])
	if not success or #result < 1  then
		local error_obj = exaerror.create("F-SME-1",
				"Error while retrieving the number of nodes from Exasol DB"
		) :add_mitigations("Please create an error report")
		_G.global_env.error(tostring(error_obj))
	else
		return result[1][1]
	end
end


---
-- Prepare parallel export query.
--
-- @param n_nodes				the number of nodes using for parallelism
-- @param schema_name				the name of the Exasol schema containing the table to export
-- @param table_name				the name of the Exasol table to be exported
-- @param aws_credentials_connection_name	the name of the connection object with the AWS credentials
-- @param s3_output_path			the s3 bucket path to be placed
--
-- @return	a string having export query and a lua table including query parameters
--
function M.prepare_export_query(
		n_nodes,
		parallelism_factor,
		schema_name, table_name,
		aws_credentials_connection_name,
		s3_output_path)
	-- init
	local n_exporter = n_nodes * parallelism_factor
	local query_export = [[EXPORT ::t INTO CSV AT ::c]]
	local params = {
			t = schema_name .. '.' .. table_name,
			c = aws_credentials_connection_name}

	-- prepare the query
	for i=1, n_exporter do
		key_ = 'f' .. tostring(i)
		val_ =  s3_output_path .. '/' .. table_name .. tostring(i) .. '.csv'
		query_export = query_export .. ' FILE :' .. key_
		params[key_] = val_
	end
	query_export = query_export .. ' WITH COLUMN NAMES'

	return query_export, params
end


---
-- Export the specified Exasol table to AWS S3.
--
-- @param schema_name				the name of the Exasol schema containing the table to export
-- @param table_name				the name of the Exasol table to be exported
-- @param aws_credentials_connection_name	the name of the connection object with the AWS credentials
-- @param s3_output_path			the s3 bucket path to be placed
--
function M.export_to_s3(schema_name, table_name, aws_credentials_connection_name, s3_output_path)
	local n_nodes = M.get_node_count()

	local query_export, params = M.prepare_export_query(
			n_nodes, M.default_parallelism_factor, schema_name, table_name,
			aws_credentials_connection_name, s3_output_path)

	-- execute
	local success, result = _G.global_env.pquery(query_export, params)
	if not success then
		local error_obj = exaerror.create("E-SME-1",
				'Error occurred in exporting Exasol table to AWS S3: ' .. result.error_message
		) :add_mitigations("Please check AWS connection")
		_G.global_env.error(tostring(error_obj))
	end

end

return M;
