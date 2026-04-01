import boto3
import pandas as pd


class AutopilotPrediction:
    """
    This class is responsible for making prediction from a given Autopilot job
    """
    def __init__(self, endpoint_name: str):
        self._endpoint_name = endpoint_name
        self._sm_runtime = boto3.client("sagemaker-runtime")

    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        csv_data = df.to_csv(sep=",", header=False, index=False)

        # make prediction
        response = self._sm_runtime.invoke_endpoint(
            EndpointName=self._endpoint_name,
            ContentType="text/csv",
            Accept="text/csv",
            Body=csv_data
        )
        predictions = [
            row.split(",")
            for row in response["Body"].read().decode("utf-8").strip().splitlines()
        ]

        # create dataframe from predictions
        prediction_df = pd.DataFrame(
            [pred[0] for pred in predictions], columns=["predictions"])

        # add prediction probability for classification problems
        if len(predictions[0]) > 1:
            prediction_df["probability"] = [pred[1] for pred in predictions]

            # order columns, the last column must be "predictions"
            prediction_df = prediction_df[["probability", "predictions"]]

        return prediction_df
