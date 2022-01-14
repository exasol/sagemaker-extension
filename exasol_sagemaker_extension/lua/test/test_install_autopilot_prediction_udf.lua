local luaunit = require("luaunit")
local mockagne = require("mockagne")
local install_autopilot_prediction_udf = require(
		"install_autopilot_prediction_udf")


test_install_autopilot_prediction_udf = {}


local function mock_pquery_create(exa_mock, query_str, params, result)
    mockagne.when(exa_mock.pquery(query_str, params)).thenAnswer(true, result)
end

local function mock_error_return_nil(exa_mock)
    mockagne.when(exa_mock.error()).thenAnswer(nil)
end


function  test_install_autopilot_prediction_udf.setUp()
    exa_mock = mockagne.getMock()
    _G.global_env = exa_mock
    mock_error_return_nil(exa_mock)
end



function test_install_autopilot_prediction_udf.test_split()
	local str = 'AA,BB,CC;DD'
	local splitted = str:split(',')
	luaunit.assertEquals(#splitted, 3)
	luaunit.assertEquals(splitted[1], 'AA')
end


function test_install_autopilot_prediction_udf.test_get_udf_params()
	local target_col = 'COL_5'
	local endpoint_problem_type = 'Regression'
	local input_params, output_params = {}, {}
	local n_columns = 5
	for i=1, n_columns do
		input_params[#input_params+1] = 'COL_' .. tostring(i)
		output_params[#output_params+1] = 'CHAR(' .. tostring(i) .. ')'
	end
	local metadata_row = {{
			target_col,
			table.concat(input_params, ';'),
			table.concat(output_params, ';')
	}}

	local res_input_params, res_output_params =
	install_autopilot_prediction_udf.get_udf_params(metadata_row, endpoint_problem_type)

	luaunit.assertEquals(#res_input_params, n_columns-1)
	luaunit.assertEquals(#res_output_params, n_columns)
	luaunit.assertEquals(res_input_params[1], 'COL_1 CHAR(1)')
	luaunit.assertEquals(res_output_params[#res_output_params],
			'PREDICTIONS DOUBLE')

end


function test_install_autopilot_prediction_udf.test_install_udf()
	local schema = 'schema'
	local endpoint_name = 'endpoint_name'
	local model_conn_name = 'model_conn_name'
	local input_params = {'COL_1 CHAR(1)', 'COL_2 CHAR(2)'}
	local output_params = {'COL_1 CHAR(1)', 'COL_2 CHAR(2)', 'OUTPUT FLOAT'}

	local query =
	"CREATE OR REPLACE PYTHON3_SME SET SCRIPT "
		.. schema .. ".\"" .. endpoint_name .. "\""
		.. "(" .. table.concat(input_params, ',') .. ")"
		.. "EMITS (" .. table.concat(output_params, ',') .. ") AS\n"
	.. "from exasol_sagemaker_extension.autopilot_prediction_udf import AutopilotPredictionUDF\n"
	.. "udf = AutopilotPredictionUDF(exa, '" .. model_conn_name .. "')\ndef run(ctx):\n\tudf.run(ctx)\n/"

	mock_pquery_create(exa_mock, query, nil)
	local result = install_autopilot_prediction_udf.install_udf(
			schema,
			endpoint_name,
			model_conn_name,
			input_params,
			output_params
	)
	luaunit.assertEquals(result, nil)

end

os.exit(luaunit.LuaUnit.run())