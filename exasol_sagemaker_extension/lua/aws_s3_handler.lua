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

function M.export_to_s3(table_name, aws_credentials_connection_name, s3_output_path)
	local query_export = [[EXPORT ::t INTO CSV AT ::c FILE :f]]
	local success, res = M.pquery_func(query_export, {
							t=table_name,
							c=aws_credentials_connection_name,
							f=s3_output_path
						})
	if not success then
		exit()
	end

	return success
end

return M;