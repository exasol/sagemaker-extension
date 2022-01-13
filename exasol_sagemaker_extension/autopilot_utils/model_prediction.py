import pandas as pd
from sagemaker.deserializers import CSVDeserializer
from sagemaker.predictor import Predictor
from sagemaker.serializers import CSVSerializer


class AutopilotPrediction:
    """
    This class is responsible for making prediction from a given Autopilot job
    """
    def __init__(self, endpoint_name: str):
        self._predictor = Predictor(endpoint_name)
        self._predictor.serializer = CSVSerializer()
        self._predictor.deserializer = CSVDeserializer()

    def predict(self, df: pd.DataFrame) -> pd.DataFrame:
        # make prediction
        predictions = self._predictor.predict(
            df.to_csv(sep=",", header=False, index=False))

        # create dataframe from predictions
        prediction_df = pd.DataFrame(
            [pred[0] for pred in predictions], columns=["predictions"])

        # add prediction probability for classification problems
        if len(predictions[0]) > 1:
            prediction_df["probability"] = [pred[1] for pred in predictions]

            # order columns, the last column must be "predictions"
            prediction_df = prediction_df[["probability", "predictions"]]

        return prediction_df
