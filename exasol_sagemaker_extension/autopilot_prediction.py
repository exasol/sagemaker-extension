import os
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

    def __parse_model_connection(self):
        model_connection = self.exa.get_connection(self.model_connection_name)
        endpoint_info_json = json.loads(model_connection.password)
        name = endpoint_info_json['name']
        status = endpoint_info_json['status']
        return name, status == 'deployed'

    def run(self, ctx):
        os.environ["AWS_DEFAULT_REGION"] = ""
        os.environ["AWS_ACCESS_KEY_ID"] = ""
        os.environ["AWS_SECRET_ACCESS_KEY"] = ""

        endpoint_name, is_running = self.__parse_model_connection()
        if is_running:
            data_df = ctx.get_dataframe()
            pred = self.prediction_method(endpoint_name, data_df)
            data_df["predictions"] = pred
            ctx.emit(data_df)
        else:
            print("ERROR TODO")  # TODO
