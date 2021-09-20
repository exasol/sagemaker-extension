---
-- @module aws_s3_handler
--
-- This module handles AWS S3 service operations.
--

local M = {
	pquery_func = pquery,
	exit_func = exit,
	parallelism_factor = 4
}

function M.init(pquery_func, exit_func)
	M.pquery_func = pquery_func
	M.exit_func = exit_func
	return M
end


---
-- Get the number of Exasol nodes.
--
-- @return an integer that shows the number of nodes
--
function M.get_node_count()
	local success, res = M.pquery_func([[SELECT NPROC()]])
	if not success or #res < 1  then
		M.exit_func()
	else
		return res[1][1]
	end
end


---
-- Prepare parallel export query.
--
-- @param n_nodes							the number of nodes using for parallelism
-- @param schema_name						the name of the Exasol schema containing the table to export
-- @param table_name						the name of the Exasol table to be exported
-- @param aws_credentials_connection_name	the name of the connection object with the AWS credentials
-- @param s3_output_path					the s3 bucket path to be placed
--
-- @return	boolean indicating whether it is exported successfully
--
function M.prepare_export_query(n_nodes, schema_name, table_name, aws_credentials_connection_name, s3_output_path)
	-- init
	local n_exporter = n_nodes * M.parallelism_factor
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

	return query_export, params
end


---
-- Export the specified Exasol table to AWS S3.
--
-- @param schema_name						the name of the Exasol schema containing the table to export
-- @param table_name						the name of the Exasol table to be exported
-- @param aws_credentials_connection_name	the name of the connection object with the AWS credentials
-- @param s3_output_path					the s3 bucket path to be placed
--
-- @return	a string having export query and a lua table including query parameters
--
function M.export_to_s3(schema_name, table_name, aws_credentials_connection_name, s3_output_path)
	local n_nodes = M.get_node_count()

	local query_export, params = M.prepare_export_query(
			n_nodes, schema_name, table_name, aws_credentials_connection_name, s3_output_path)

	-- execute
	local success, _ = M.pquery_func(query_export, params)

	if not success then
		M.exit_func()
	end

	return success
end

return M;