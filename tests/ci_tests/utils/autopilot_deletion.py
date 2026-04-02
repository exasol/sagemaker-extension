import os
import boto3

class AutopilotTestDeletion:
    @staticmethod
    def delete_endpoint_via_database(endpoint_name, setup_params, db_conn, aws_conn_name):
        query_deletion = "EXECUTE SCRIPT " \
                         "{schema}.SME_DELETE_SAGEMAKER_AUTOPILOT_ENDPOINT(" \
                         "'{endpoint_name}', '{aws_conn_name}', '{aws_region}')". \
            format(schema=setup_params.schema_name,
                   endpoint_name=endpoint_name,
                   aws_conn_name=aws_conn_name,
                   aws_region=os.environ["AWS_REGION"])

        db_conn.execute(query_deletion)

    @staticmethod
    def delete_endpoint_via_api(endpoint_name):
        sm_client = boto3.client("sagemaker")

        endpoint_desc = sm_client.describe_endpoint(EndpointName=endpoint_name)
        config_name = endpoint_desc["EndpointConfigName"]
        config_desc = sm_client.describe_endpoint_config(
            EndpointConfigName=config_name)
        model_names = [
            v["ModelName"] for v in config_desc["ProductionVariants"]]

        sm_client.delete_endpoint(EndpointName=endpoint_name)
        sm_client.delete_endpoint_config(EndpointConfigName=config_name)
        for model_name in model_names:
            sm_client.delete_model(ModelName=model_name)
