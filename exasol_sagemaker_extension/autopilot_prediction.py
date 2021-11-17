import os
import ast
import json
from typing import Callable
from exasol_sagemaker_extension.autopilot_utils.model_prediction import \
    AutopilotPrediction


class AutopilotPredictionUDF:
    def __init__(self, exa, model_connection_name,
                 prediction_method: Callable = AutopilotPrediction.predict):
        self.exa = exa
        self.model_connection_name = model_connection_name
        self.prediction_method = prediction_method

    def run(self, ctx):
        model_connection = self.exa.get_connection(self.model_connection_name)
        endpoint_info_json = json.loads(model_connection.address)

        if endpoint_info_json['status'] == 'deployed':
            aws_s3_conn_obj = self.exa.get_connection(
                endpoint_info_json['aws_s3_connection'])

            os.environ["AWS_DEFAULT_REGION"] = endpoint_info_json['aws_region']
            os.environ["AWS_ACCESS_KEY_ID"] = aws_s3_conn_obj.user
            os.environ["AWS_SECRET_ACCESS_KEY"] = aws_s3_conn_obj.password

            data_df = ctx.get_dataframe(num_rows='all')
            pred = self.prediction_method(
                endpoint_info_json['endpoint_name'], data_df)

            type = self.exa.meta.output_columns[-1].type
            data_df["predictions"] = [type(ast.literal_eval(i)) for i in pred]
            ctx.emit(data_df)
        else:
            raise Exception("The status of endpoint ({endpoint}) is "
                            "'{status}', not 'deployed'. Therefore, "
                            "the prediction can not be performed.".
                            format(endpoint=endpoint_info_json['endpoint_name'],
                                   status=endpoint_info_json['status']))
