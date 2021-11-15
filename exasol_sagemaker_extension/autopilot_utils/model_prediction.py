import pandas as pd
from sagemaker.deserializers import CSVDeserializer
from sagemaker.predictor import Predictor
from sagemaker.serializers import CSVSerializer


class AutopilotPrediction:
    """
    This class is responsible for making prediction from a given Autopilot job
    """

    @staticmethod
    def predict(endpoint_name: str, df: pd.DataFrame) -> list:
        predictor = Predictor(endpoint_name)

        predictor.serializer = CSVSerializer()
        predictor.deserializer = CSVDeserializer()
        prediction = predictor.predict(
            df.to_csv(sep=",", header=False, index=False))

        return prediction[0]
