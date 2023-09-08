CREATE OR REPLACE LUA SCRIPT "SME_DEPLOY_SAGEMAKER_AUTOPILOT_ENDPOINT" (job_name, endpoint_name, schema_name, instance_type, instance_count, aws_s3_connection, aws_region)  AS
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
package.preload[ "db_metadata_reader" ] = function( ... ) local arg = _G.arg;
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
end
end

do
local _ENV = _ENV
package.preload[ "endpoint_connection_handler" ] = function( ... ) local arg = _G.arg;
---
-- @module endpoint_connection_handler
--
-- This module handles operations on EXA connection object
--

local M = {}

local exaerror = require("exaerror")

_G.global_env = {
	pquery = pquery,
	error = error
}


---
--	This function creates or updates an Exasol connection object of a given Autopilot model
--
-- @param aws_s3_connection		The name of the AWS connection object, required to call endpoint in prediction
-- @param aws_region			The name of aws region
-- @param endpoint_name			The name of the Autopilot endpoint
-- @param status				Endpoint status such as 'deployed', 'deleted'
--
function M.update_model_connection_object(aws_s3_connection, aws_region, endpoint_name, status)
	local json = require('cjson')
	local conn_data_dict = {
		aws_s3_connection=aws_s3_connection,
		aws_region = aws_region,
		endpoint_name=endpoint_name,
		status=status,
		batch_size=100
	}

	local conn_name = [[SME_SAGEMAKER_AUTOPILOT_ENDPOINT_CONNECTION_]] .. string.upper(endpoint_name)
	local conn_to = json.encode(conn_data_dict)
	local query = [[CREATE OR REPLACE CONNECTION ]] .. conn_name .. [[ TO ']] .. conn_to .. [[']]

	local success, result = _G.global_env.pquery(query)
	if not success then
		local error_obj = exaerror.create("E-SME-9",
				'Error occurred in creating model connection object: ' .. result.error_message)
		_G.global_env.error(tostring(error_obj))
	end

	return conn_name
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
package.preload[ "install_autopilot_prediction_udf" ] = function( ... ) local arg = _G.arg;
---
-- @module install_autopilot_prediction_udf
--
-- This module generates and deploys Autopilot prediction udf
--

local M = {}

local exaerror = require("exaerror")

_G.global_env = {
	pquery = pquery,
	error = error
}

---
-- Determine the sql data-type according to given endpoint problem type.
-- If It is a 'Regression' problem, type should be DOUBLE. Otherwise,
-- the type is either INT or VARCHAR depends on target column type.
--
-- @param endpoint_problem_type		The problem type of deployed endpoint model
--
function M.determine_sql_type(endpoint_problem_type, target_column_type)
	local type  = target_column_type
	if endpoint_problem_type == 'Regression' then
		type = 'DOUBLE'
	end

	return type
end


---
-- Split the given string using the specified seperator into a list of strings
--
-- @param character		The separator to use when splitting the string.
--
-- @return  a list of strings
--
function string:split(seperator)
  local splitted_result = {}
  local i = 1
  for str in string.gmatch(self, "[^"..seperator.."]+") do
    splitted_result[i] = str
    i = i + 1
  end
  return splitted_result
end

---
-- This function parses the given metadata into parameters for the prediction udf
--
-- @param metadata_row				The row of the relevant model in metadata table
-- @param endpoint_problem_type		The problem type of the deployed endpoint model
--
-- @return  input and output params of the prediction udf
--
function M.get_udf_params(metadata_row, endpoint_problem_type)
	local target_column = metadata_row[1][1]
	local col_names_list = metadata_row[1][2]:split(';')
	local col_types_list = metadata_row[1][3]:split(';')

	local input_params = {}
	local output_params = {}
	local target_param = nil
	local prediction_column_name = 'PREDICTIONS'
	local probability_column_name = 'PROBABILITY'
	for i=1, #col_names_list do
		if col_names_list[i] ~= target_column then
			input_params[#input_params+1]=col_names_list[i] .. ' ' .. col_types_list[i]
			output_params[#output_params+1]=col_names_list[i] .. ' ' .. col_types_list[i]
		else
			target_param = prediction_column_name .. ' ' .. M.determine_sql_type(
					endpoint_problem_type, col_types_list[i])
		end
	end

	-- last two output columns must be  'PROBABILITY' and  'PREDICTIONS', respectively
	if endpoint_problem_type ~= 'Regression' then
		output_params[#output_params+1] = probability_column_name .. ' ' .. 'DECIMAL(18,4)'
	end
	output_params[#output_params+1] = target_param

	return input_params, output_params
end


---
-- Generate and deploy prediction udf
--
-- @param schema		       	The name of schema where the prediction udf gets created
-- @param endpoint_name     	The name of endpoint is for which prediction UDF is created
-- @param model_conn_name   	The name of connection holds information about mode
-- @param input_params          Input parameters for the prediction udf
-- @param output_params			Output for the prediction udf
--
function M.install_udf(schema, endpoint_name, model_conn_name, input_params, output_params)
    local query_create  =
	"CREATE OR REPLACE PYTHON3_SME SET SCRIPT "
		.. schema .. ".\"" .. endpoint_name .. "\""
		.. "(" .. table.concat(input_params, ',') .. ")"
		.. "EMITS (" .. table.concat(output_params, ',') .. ") AS\n"
	.. "from exasol_sagemaker_extension.autopilot_prediction_udf import AutopilotPredictionUDF\n"
	.. "udf = AutopilotPredictionUDF(exa, '" .. model_conn_name .. "')\ndef run(ctx):\n\tudf.run(ctx)\n/"

    local success, result = _G.global_env.pquery(query_create)
	if not success then
		local error_obj = exaerror.create("E-SME-10",
				'Error occurred in installing prediction udf: ' .. result.error_message)
		_G.global_env.error(tostring(error_obj))
	end
end


---
-- This is the main function of installing Prediction UDF
--
-- @param job_name          	The name of the job, is used to find out the metadata
-- @param script_schema_name	The name of schema in which metadata table is stored
-- @param endpoint_name     	The name of endpoint is for which prediction UDF is created
-- @param schema_name       	The name of schema where PredictionUDF gets created
-- @param model_conn_name   	The name of connection holds information about model
--
function M.main(job_name, endpoint_problem_type, script_schema_name, endpoint_name, schema_name, model_conn_name)
    local db_metadata_reader = require('db_metadata_reader')
    local metadata_row = db_metadata_reader.read_metadata(
            script_schema_name, job_name,
			{'TARGET_ATTRIBUTE_NAME', 'COLUMN_NAMES', 'COLUMN_TYPES'})

    local input_params, output_params = M.get_udf_params(metadata_row, endpoint_problem_type)

	M.install_udf(schema_name, endpoint_name, model_conn_name, input_params, output_params)

end

return M;
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
-- @module autopilot_endpoint_deployment
--
-- This module creates and deploys the best candidate of a trained Autopilot job.
--

local exaerror = require("exaerror")
local validate_input = require("validate_input")

_G.global_env = {
    pquery = pquery,
    error = error
}

---
-- This function deploys an endpoint for a given Autopilot job
--
-- @schema_name					The name of schema on which the script is deployed
-- @param job_name				Job name of the Autopilot training run
-- @param endpoint_name			The name of endpoint to be created and deployed
-- @param instance_type			EC2 instance type to deploy this Model to
-- @param instance_count		The initial number of instances to run in endpoint
-- @param aws_s3_connection		The name of the connection object with the AWS credentials
-- @param aws_region			The name of aws region
--
function deploy_autopilot_endpoint(
		script_schema_name, job_name, endpoint_name,
		instance_type, instance_count, aws_s3_connection, aws_region)
	local query = [[SELECT ::schema."SME_AUTOPILOT_ENDPOINT_DEPLOYMENT_UDF"(
		:job_name,
		:endpoint_name,
		:instance_type,
		:instance_count,
		:aws_s3_connection,
		:aws_region
	)]]
	local params = {
		schema=script_schema_name,
		job_name=job_name,
		endpoint_name=endpoint_name,
		instance_type=instance_type,
		instance_count=instance_count,
		aws_s3_connection=aws_s3_connection,
		aws_region=aws_region
	}

	local success, result = _G.global_env.pquery(query, params)
	if not success then
		local error_obj = exaerror.create("E-SME-3",
				'Error occurred in deploying Sagemaker endpoint: ' .. result.error_message)
		_G.global_env.error(tostring(error_obj))
	end

	return  result[1][1]
end

---
-- This is the main function of deploying Autopilot endpoint
--
-- @param exa					Exa context object
-- @param job_name				Job name of the Autopilot training run
-- @param endpoint_name			The name of endpoint to be created and deployed. It is also the name of the UDF to be created.
-- @param schema_name			The name of schema where PredictionUDF gets created
-- @param instance_type			EC2 instance type to deploy this Model to
-- @param instance_count		The initial number of instances to run in endpoint
-- @param aws_s3_connection		The name of the connection object with the AWS credentials
-- @param aws_region			The name of aws region
--
function main(
		exa, job_name, endpoint_name, schema_name,
		instance_type, instance_count, aws_s3_connection, aws_region)
	local script_schema_name = exa.meta.script_schema

	if not validate_input.is_autopilot_endpoint_name_valid(endpoint_name) then
		local error_obj = exaerror.create("E-SME-11",
				"Invalid endpoint name " ..job_name
		):add_mitigations("The name of endpoint should match the following pattern: ^[a-zA-Z0-9]{0,62}")
		_G.global_env.error(tostring(error_obj))
	end

	local endpoint_problem_type = deploy_autopilot_endpoint(
			script_schema_name, job_name, endpoint_name, instance_type,
			instance_count, aws_s3_connection, aws_region)

	local endpoint_conn = require('endpoint_connection_handler')
	local model_conn_name = endpoint_conn.update_model_connection_object(
			aws_s3_connection, aws_region, endpoint_name, 'deployed')

	local install_prediction_udf = require('install_autopilot_prediction_udf')
	install_prediction_udf.main(job_name, endpoint_problem_type,
			script_schema_name, endpoint_name, schema_name, model_conn_name)
end

main(exa, job_name, endpoint_name, schema_name, instance_type, instance_count, aws_s3_connection, aws_region)
/






