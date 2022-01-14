import os
import json
import pandas as pd
from typing import Type
from exasol_sagemaker_extension.autopilot_utils.model_prediction import \
    AutopilotPrediction


class AutopilotPredictionUDF:
    def __init__(self, exa, model_connection_name,
                 prediction_class: Type[AutopilotPrediction] =
                 AutopilotPrediction):
        self.exa = exa
        self.model_connection_name = model_connection_name
        self.prediction_class = prediction_class

    def run(self, ctx):
        model_connection = self.exa.get_connection(self.model_connection_name)
        endpoint_info_json = json.loads(model_connection.address)
        batch_size = endpoint_info_json["batch_size"]

        if endpoint_info_json['status'] == 'deployed':
            aws_s3_conn_obj = self.exa.get_connection(
                endpoint_info_json['aws_s3_connection'])

            os.environ["AWS_DEFAULT_REGION"] = endpoint_info_json['aws_region']
            os.environ["AWS_ACCESS_KEY_ID"] = aws_s3_conn_obj.user
            os.environ["AWS_SECRET_ACCESS_KEY"] = aws_s3_conn_obj.password

            py_type = self.exa.meta.output_columns[-1].type
            prediction_class_obj = self.prediction_class(
                endpoint_info_json['endpoint_name'])
            while True:
                data_df = ctx.get_dataframe(batch_size)
                if data_df is None:
                    break
                pred_df = prediction_class_obj.predict(data_df)
                pred_df["predictions"] = \
                    pred_df["predictions"].astype(py_type)
                data_df = pd.concat([data_df, pred_df], axis=1, sort=False)
                ctx.emit(data_df)
        else:
            raise Exception("The status of endpoint ({endpoint}) is "
                            "'{status}', not 'deployed'. Therefore, "
                            "the prediction can not be performed.".
                            format(endpoint=endpoint_info_json['endpoint_name'],
                                   status=endpoint_info_json['status']))
