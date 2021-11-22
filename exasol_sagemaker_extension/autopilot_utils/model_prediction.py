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

    def predict(self, df: pd.DataFrame) -> list:
        prediction = self._predictor.predict(
            df.to_csv(sep=",", header=False, index=False))

        return list(map(lambda x: x[0], prediction))
