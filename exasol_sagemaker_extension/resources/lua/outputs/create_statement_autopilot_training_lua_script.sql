CREATE OR REPLACE LUA SCRIPT "SME_TRAIN_WITH_SAGEMAKER_AUTOPILOT" (json_str)  AS
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

do
local _ENV = _ENV
package.preload[ "aws_s3_handler" ] = function( ... ) local arg = _G.arg;
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
end
end

do
local _ENV = _ENV
package.preload[ "aws_sagemaker_handler" ] = function( ... ) local arg = _G.arg;
---
-- @module aws_sagemaker_handler
--
-- This module handles AWS Sagemaker service operations
--

local M = {}

local exaerror = require("exaerror")

_G.global_env = {
	pquery = pquery,
	error = error
}

---
-- Invoke AWS Sagemaker Autopilot training
--
-- @return result   The name of the Autopilot run job
--
function M.train_autopilot(
        schema_name,
        job_name,
        aws_s3_connection,
        aws_region,
        role,
        s3_bucket_uri,
        s3_output_path,
        target_attribute_name,
        problem_type,
        objective,
        total_job_runtime_in_seconds,
        max_candidates,
        max_runtime_per_training_job_in_seconds)

    local query_training = [[SELECT ::schema."SME_AUTOPILOT_TRAINING_UDF"(
        :job_name ,
        :aws_s3_connection ,
        :aws_region ,
        :role ,
        :s3_bucket_uri,
        :s3_output_path,
        :target_attribute_name ,
        :problem_type ,
        :objective ,
        :total_job_runtime_in_seconds ,
        :max_candidates ,
        :max_runtime_per_training_job_in_seconds
        )]]
    local params = {
        schema = schema_name,
        job_name = job_name,
        aws_s3_connection = aws_s3_connection,
        aws_region = aws_region,
        role = role,
        s3_bucket_uri = s3_bucket_uri,
        s3_output_path = s3_output_path,
        target_attribute_name = target_attribute_name,
        problem_type = problem_type,
        objective = objective,
        total_job_runtime_in_seconds = total_job_runtime_in_seconds,
        max_candidates = max_candidates,
        max_runtime_per_training_job_in_seconds = max_runtime_per_training_job_in_seconds
    }

    local success, result = _G.global_env.pquery(query_training, params)
	if not success then
		local error_obj = exaerror.create("E-SME-7",
				'Error occurred in training with Sagemaker Autopilot: ' .. result.error_message)
		_G.global_env.error(tostring(error_obj))
	end

    return  result[1][1]
end

return M;
end
end

do
local _ENV = _ENV
package.preload[ "db_metadata_writer" ] = function( ... ) local arg = _G.arg;
---
-- @module db_metadata_writer
--
-- This module inserts the metadata of an Autopilot job
--

local M = {}

local exaerror = require("exaerror")

_G.global_env = {
	pquery = pquery,
	error = error
}

---
-- Insert the metadata of an Autopilot job
--
function M.insert_metadata_into_db(
			schema_name,
			job_name,
			aws_credentials_connection_name,
			iam_sagemaker_role,
			s3_bucket_uri,
			s3_output_path,
			target_attribute_name,
			problem_type,
			objective,
			max_runtime_for_automl_job_in_seconds,
			max_candidates,
			max_runtime_per_training_job_in_seconds,
			session_id,
			script_user,
			col_names,
			col_types
)
	local query_inserting = [[INSERT INTO ::schema."SME_METADATA_AUTOPILOT_JOBS" VALUES(
			CURRENT_TIMESTAMP,
			:job_name,
			:aws_credentials_connection_name,
			:iam_sagemaker_role,
			:s3_bucket_uri,
			:s3_output_path,
			:target_attribute_name,
			:problem_type,
			:objective,
			:max_runtime_for_automl_job_in_seconds,
			:max_candidates,
			:max_runtime_per_training_job_in_seconds,
			:session_id,
			:script_user,
			:col_names,
			:col_types
        )]]
    local params = {
        schema = schema_name,
		job_name=job_name,
		aws_credentials_connection_name=aws_credentials_connection_name,
		iam_sagemaker_role=iam_sagemaker_role,
		s3_bucket_uri=s3_bucket_uri,
		s3_output_path=s3_output_path,
		target_attribute_name=target_attribute_name,
		problem_type=problem_type,
		objective=objective,
		max_runtime_for_automl_job_in_seconds=max_runtime_for_automl_job_in_seconds,
		max_candidates=max_candidates,
		max_runtime_per_training_job_in_seconds=max_runtime_per_training_job_in_seconds,
		session_id=session_id,
		script_user=script_user,
		col_names=col_names,
		col_types=col_types
    }

	local success, result = _G.global_env.pquery(query_inserting, params)
	if not success then
		local error_obj = exaerror.create("E-SME-8",
				'Error occurred in inserting metadata into database: ' .. result.error_message)
		_G.global_env.error(tostring(error_obj))
	end
end

return M;
end
end

do
local _ENV = _ENV
package.preload[ "exaerror" ] = function( ... ) local arg = _G.arg;
---
-- This module provides a uniform way to define errors in a Lua application.
--
-- @module M
--
local M = {
    VERSION = "1.2.0",
}

local msgexpander = require("message_expander")

-- Lua 5.1 backward compatibility
_G.unpack = table.unpack or _G.unpack

local function expand(message, parameters)
    return msgexpander:new({message =message, parameters = parameters}):expand()
end

---
-- Convert error to a string representation.
-- <p>
-- Note that <code>__tostring</code> is the metamethod called by Lua's global <code>tostring</code> function.
-- This allows using the error message in places where Lua expects a string.
-- </p>
--
-- @return string representation of the error object
--
function M:__tostring()
    local lines = {}
    if self.code then
        if self.message then
            table.insert(lines, self.code .. ": " .. self:get_message())
        else
            table.insert(lines, self.code)
        end
    else
        if self.message then
            table.insert(lines, self:get_message())
        else
            table.insert(lines, "<Missing error message. This should not happen. Please contact the software maker.>")
        end
    end
    if (self.mitigations ~= nil) and (#self.mitigations > 0) then
        table.insert(lines, "\nMitigations:\n")
        for _, mitigation in ipairs(self.mitigations) do
            table.insert(lines, "* " .. expand(mitigation, self.parameters))
        end
    end
    return table.concat(lines, "\n")
end

---
-- Concatenate an error object with another object.
--
-- @return String representing the concatenation.
--
function M.__concat(left, right)
    return tostring(left) .. tostring(right)
end

---
-- Create a new instance of an error message.
--
-- @param object pre-initialized object to be used for the instance
--        (optional) a new object is created if you don't provide one
--
-- @return created object
--
function M:new(object)
    object = object or {}
    self.__index = self
    setmetatable(object, self)
    return object
end

---
-- Factory method for a new error message.
--
-- @param code error code
-- @param message message body
-- @param parameters parameters to replace the placeholders in the message (if any)
--
-- @return created object
--
function M.create(code, message, parameters)
    return M:new({code = code, message = message, parameters = parameters, mitigations = {}})
end

---
-- Add mitigations.
--
-- @param ... one or more mitigation descriptions
--
-- @return error message object
--
function M:add_mitigations(...)
    for _, mitigation in ipairs({...}) do
        table.insert(self.mitigations, mitigation)
    end
    return self
end

---
-- Add issue ticket mitigation
-- <p>
-- This is a special kind of mitigation which you should use in case of internal software errors that should not happen.
-- For example when a path in the code is reached that should be unreachable if the code is correct.
-- </p>
--
-- @return error message object
--
function M:add_ticket_mitigation()
    table.insert(self.mitigations,
        "This is an internal software error. Please report it via the project's ticket tracker.")
    return self
end


---
-- Get the error code.
--
-- @return error code
--
function M:get_code()
    return self.code
end

---
-- Get the error message.
-- <p>
-- This method supports Lua's standard string interpolation used in <code>string.format</code>.
-- Placeholders in the raw message are replaced by the parameters given when building the error message object.
-- </p>
-- <p>
-- For fault tolerance, this method returns the raw message in case the parameters are missing.
-- </p>
--
-- @return error message
--
function M:get_message()
    return expand(self.message, self.parameters)
end

function M:get_raw_message()
    return self.message or ""
end

---
-- Get parameter definitions.
--
function M:get_parameters()
    return self.parameters
end

---
-- Get the description of a parameter.
--
-- @parameter parameter_name name of the parameter
--
-- @return parameter description or the string "<code><missing parameter description></code>"
--
function M:get_parameter_description(parameter_name)
    return self.parameters[parameter_name].description or "<missing parameter description>"
end

---
-- Get the mitigations for the error.
--
-- @return list of mitigations
--
function M:get_mitigations()
    return unpack(self.mitigations)
end

---
-- Raise the error.
-- <p>
-- Like in Lua's <code>error</code> function, you can optionally specify if and from which level down the stack trace
-- is included in the error message.
-- </p>
-- <ul>
-- <li>0: no stack trace</li>
-- <li>1: stack trace starts at the point inside <code>exaerror</code> where the error is raised
-- <li>2: stack trace starts at the calling function (default)</li>
-- <li>3+: stack trace starts below the calling function</li>
-- </ul>
--
-- @parameter level (optional) level from which down the stack trace will be displayed
--
-- @raise Lua error for the given error object
--
function M:raise(level)
    level = (level == nil) and 2 or level
    error(tostring(self), level)
end

---
-- Raise an error that represents the error object's contents.
-- <p>
-- This function supports two calling styles. Either like <code>exaerror:create</code> with a flat list of parameters.
-- Or like <code>exaerror:new</code> with a table to preinitialize the error object.
-- </p>
-- <p>The first parameter decides on the calling convention. If it is a table, <code>exaerror:new</code is used.
--
-- @see M.create
-- @see M:new
--
-- @raise Lua error for the given error object
--
function M.error(arg1, ...)
    if type(arg1) == "table" then
        M:new(arg1):raise()
    else
        M.create(arg1, ...):raise()
    end
end

return M
end
end

do
local _ENV = _ENV
package.preload[ "message_expander" ] = function( ... ) local arg = _G.arg;
---
-- This module provides a parser for messages with named parameters and can expand the message using the parameter
-- values.
--
-- @module M
--
local M = {}

local FROM_STATE_INDEX = 1
local GUARD_INDEX = 2
local ACTION_INDEX = 3
local TO_STATE_INDEX = 4

---
-- Create a new instance of a message expander.
--
-- @param object pre-initialized object to be used for the instance
--        (optional) a new object is created if you don't provide one
--
-- @return created object
--
function M:new(object)
    object = object or {}
    self.__index = self
    setmetatable(object, self)
    self.tokens_ = {}
    self.last_parameter_ = {characters = {}, quote = true}
    return object
end

---
-- Create new instance of a message expander.
--
-- @parameter message to be expanded
-- @parameter ... values used to replace the placeholders
--
function M.create(message, ...)
    return M:new({
        message = message,
        parameters = {...},
    })
end

local function tokenize(text)
    return string.gmatch(text, ".")
end

---
-- Expand the message.
-- <p>
-- Note that if no parameter values are supplied, the message will be returned as is, without any replacements.
-- </p>
--
-- @return expanded message
--
function M:expand()
    if (self.parameters == nil) or (not next(self.parameters)) then
        return self.message
    else
        self:run_()
    end
    return table.concat(self.tokens_)
end

function M:run_()
    self.state = "TEXT"
    local token_iterator = tokenize(self.message)
    for token in token_iterator do
        self.state = self:transit_(token)
    end
end

function M:transit_(token)
    for _, transition in ipairs(M.transitions_) do
        local from_state = transition[FROM_STATE_INDEX]
        local guard = transition[GUARD_INDEX]
        if(from_state == self.state and guard(token)) then
            local action = transition[ACTION_INDEX]
            action(self, token)
            local to_state = transition[TO_STATE_INDEX]
            return to_state
        end
    end
end

local function is_any()
    return true
end

local function is_opening_bracket(token)
    return token == "{"
end

local function is_closing_bracket(token)
    return token == "}"
end

-- We are intentionally not using the symbol itself here for compatibility reasons.
-- See https://github.com/exasol/error-reporting-lua/issues/15 for details.
local function is_pipe(token)
    return token == string.char(124)
end

local function is_u(token)
    return token == "u"
end

local function is_not_bracket(token)
    return not is_opening_bracket(token) and not is_closing_bracket(token)
end

local function add_token(self, token)
    table.insert(self.tokens_, token)
end

local function add_open_plus_token(self, token)
    table.insert(self.tokens_, "{")
    table.insert(self.tokens_, token)
end

local function add_parameter_name(self, token)
    table.insert(self.last_parameter_.characters, token)
end

local function set_unquoted(self)
    self.last_parameter_.quote = false
end

local function unwrap_parameter_value(parameter)
    if parameter == nil then
        return "missing value"
    else
        local type = type(parameter)
        if (type == "table") then
            return parameter.value
        else
            return parameter
        end
    end
end

local function replace_parameter(self)
    local parameter_name = table.concat(self.last_parameter_.characters)
    local value = unwrap_parameter_value(self.parameters[parameter_name])
    local type = type(value)
    if (type == "string") and (self.last_parameter_.quote) then
        table.insert(self.tokens_, "'")
        table.insert(self.tokens_, value)
        table.insert(self.tokens_, "'")
    else
        table.insert(self.tokens_, value)
    end
    self.last_parameter_.characters = {}
    self.last_parameter_.quote = true
end

local function replace_and_add(self, token)
    replace_parameter(self)
    add_token(self, token)
end

local function do_nothing() end

M.transitions_ = {
    {"TEXT"     , is_not_bracket    , add_token          , "TEXT"     },
    {"TEXT"     , is_opening_bracket, do_nothing         , "OPEN_1"   },
    {"OPEN_1"   , is_opening_bracket, do_nothing         , "PARAMETER"},
    {"OPEN_1"   , is_any            , add_open_plus_token, "TEXT"     },
    {"PARAMETER", is_closing_bracket, do_nothing         , "CLOSE_1"  },
    {"PARAMETER", is_pipe           , do_nothing         , "SWITCH"   },
    {"PARAMETER", is_any            , add_parameter_name , "PARAMETER"},
    {"SWITCH"   , is_closing_bracket, do_nothing         , "CLOSE_1"  },
    {"SWITCH"   , is_u              , set_unquoted       , "SWITCH"   },
    {"SWITCH"   , is_any            , do_nothing         , "SWITCH"   },
    {"CLOSE_1"  , is_closing_bracket, replace_parameter  , "TEXT"     },
    {"CLOSE_1"  , is_any            , replace_and_add    , "TEXT"     }
}

return M
end
end

do
local _ENV = _ENV
package.preload[ "validate_input" ] = function( ... ) local arg = _G.arg;

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
end
end

---
-- @module autopilot_training_main
--
-- This module exports a given Exasol table into AWS S3.
--

local exaerror = require("exaerror")
local validate_input = require("validate_input")

_G.global_env = {
    pquery = pquery,
    error = error
}

local required_args = {
	job_name = true,
	input_schema_name = true,
	input_table_or_view_name = true,
	aws_credentials_connection_name = true,
	s3_bucket_uri = true,
	s3_output_path = true,
	iam_sagemaker_role = true,
	target_attribute_name = true,
	problem_type = nil,
	max_runtime_for_automl_job_in_seconds = nil,
	max_runtime_per_training_job_in_seconds = nil,
	max_candidates = nil,
	model_info_schema_name = nil,
	model_info_table_name = nil,
	objective = nil,
	aws_tags = nil
}

---
-- Returns concatenated string of the  required arguments
--
-- @return concatenated string
--
function concat_required_args()
    local concat_args = ''
    for arg, is_required in pairs(required_args) do
        if is_required then
            concat_args = concat_args .. "\n" .. arg
        end
    end
    return concat_args
end

---
-- Checks whether the list of required arguments is subset of the user specified argument list
--
-- @param args	a table including arguments keys and their values
--
-- @return boolean, true if the user specified arguments contain all required arguments
--
function contains_required_arguments(args)
   for arg, is_required in pairs(required_args) do
      if is_required and not args[arg] then
         return false
      end
    end
   return true
end


---
-- Parse a given arguments in json string format.
--
-- @param json_str	input parameters as json string
--
-- @return lua table including parameters
--
function parse_arguments(json_str)
	local json = require('cjson')
	local success, args =  pcall(json.decode, json_str)
	if not success then
		local error_obj = exaerror.create("E-SME-5",
				"Error while parsing input json string, it could not be converted to json object:"
		):add_mitigations("Check syntax of the input string json is correct")
		_G.global_env.error(tostring(error_obj))
	end

	if not contains_required_arguments(args) then
		local error_obj = exaerror.create("E-SME-6", "Missing required arguments"
		):add_mitigations('Following required arguments have to be specified: ' .. concat_required_args())
		_G.global_env.error(tostring(error_obj))
	end

	if not validate_input.is_autopilot_job_name_valid(args['job_name']) then
		local error_obj = exaerror.create("E-SME-11",
				"Invalid job name " .. args['job_name']
		):add_mitigations("The name of job should match the following pattern: ^[a-zA-Z0-9]{0,31}")
		_G.global_env.error(tostring(error_obj))
	end

	if not args['problem_type'] then
		args['problem_type'] = NULL
	end

	if not args['max_runtime_for_automl_job_in_seconds'] then
		args['max_runtime_for_automl_job_in_seconds'] = NULL
	end

	if not args['max_runtime_per_training_job_in_seconds'] then
		args['max_runtime_per_training_job_in_seconds'] = NULL
	end

	if not args['max_candidates'] then
		args['max_candidates'] = NULL
	end

	if not args['objective'] then
		args['objective'] = NULL
	end

	args['compression_type'] = 'gzip' -- default : 'gzip'

	-- store following params as uppercase
	args["input_schema_name"] = string.upper(args["input_schema_name"])
	args["input_table_or_view_name"] = string.upper(args["input_table_or_view_name"])
	args["target_attribute_name"] = string.upper(args["target_attribute_name"])

	return args
end


---
-- This function invokes export_to_s3 method in aws_s3_handler module
--
-- @param args		A table including input parameters
--
function export_to_s3_caller(args)
	local aws_s3_handler = require("aws_s3_handler")
	aws_s3_handler.export_to_s3(
			args['input_schema_name'],
			args['input_table_or_view_name'],
			args['aws_credentials_connection_name'],
			args['s3_output_path'])
end

---
-- This function invokes autopilot_training in aws_sagemaker_handler module
--
-- @param exa			Exa context
-- @param arg			A table including input parameters
--
-- @return job_name		Job name of the Autopilot training run
--
function train_autopilot_caller(exa, args)
	local schema_name = exa.meta.script_schema
	local aws_sagemaker_handler = require("aws_sagemaker_handler")
	local job_name = aws_sagemaker_handler.train_autopilot(
		schema_name,
		args['job_name'],
		args['aws_credentials_connection_name'],
		args['aws_region'],
		args['iam_sagemaker_role'],
		args['s3_bucket_uri'],
		args['s3_output_path'],
		args['target_attribute_name'],
		args['problem_type'],
		args['objective'],
		args['max_runtime_for_automl_job_in_seconds'],
		args['max_candidates'],
		args['max_runtime_per_training_job_in_seconds'])

	return job_name
end

---
-- This method returns names and types of columns as comma-separated strings respectively.
--
-- @param schema_name		The name of schema where the table is in.
-- @param table_name		The name of table from which column information is retrieved.
--
-- return two strings including column names and types
--
function get_table_columns(schema_name, table_name)
	local query = [[SELECT COLUMN_NAME , COLUMN_TYPE FROM SYS.EXA_ALL_COLUMNS eac
					WHERE COLUMN_SCHEMA = :schema_name AND COLUMN_TABLE = :table_name]]
	local params = {schema_name=schema_name, table_name=table_name}

	local success, res = _G.global_env.pquery(query, params)
	if not success then
		local error_obj = exaerror.create("F-SME-2",
				"Error while getting columns information from SYS.EXA_ALL_COLUMNS: " ..  res.error_message)
		_G.global_env.error(tostring(error_obj))
	end

	local col_names, col_types = {}, {}
	for i=1, #res do
		col_names[#col_names+1] = res[i][1]
		col_types[#col_types+1] = res[i][2]
	end
	return table.concat(col_names, ';'), table.concat(col_types, ';')

end

---
-- This method saves the metdata of the job running for training in Autopilot to Database
--
-- @param exa			Exa context
-- @param args			A table including input parameters
-- @param job_name		The name of the Autopilot job
--
function insert_metadata_into_db_caller(exa, args, job_name)
	local schema_name = exa.meta.script_schema
	local col_names, col_types = get_table_columns(
			args['input_schema_name'], args['input_table_or_view_name'])

	local db_metadata_writer = require("db_metadata_writer")
	db_metadata_writer.insert_metadata_into_db(
			schema_name,
			job_name,
			args['aws_credentials_connection_name'],
			args['iam_sagemaker_role'],
			args['s3_bucket_uri'],
			args['s3_output_path'],
			args['target_attribute_name'],
			args['problem_type'],
			args['objective'],
			args['max_runtime_for_automl_job_in_seconds'],
			args['max_candidates'],
			args['max_runtime_per_training_job_in_seconds'],
			exa.meta.session_id,
			exa.meta.current_user,
			col_names,
			col_types
	)
end

---
-- This is the main function of exporting to S3.
--
-- @param json_str	input parameters as json string
--
function main(json_str, exa)
	local args = parse_arguments(json_str)
	export_to_s3_caller(args)
	local job_name = train_autopilot_caller(exa, args)
	insert_metadata_into_db_caller(exa, args, job_name)

end



main(json_str, exa)
/






