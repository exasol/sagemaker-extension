from __future__ import annotations
from typing import Any
from collections import namedtuple

POLLING_INTERVAL = 5 * 60  # seconds
TIMEOUT = 90 * 60  # seconds

ModelSetupParams = namedtuple("ModelSetupParams", [
    "model_type", "schema_name", "table_name", "target_col",
    "data", "aws_output_path", "batch_size"])

reg_model_setup_params = ModelSetupParams(
    model_type='reg',
    schema_name="reg_schema",
    table_name="reg_table",
    target_col="output_col",
    data=[f"({i * 1.1}, {i * 1.2}, {i * 10})" for i in range(1, 1000)],
    aws_output_path="reg_path",
    batch_size=10
)

cls_model_setup_params = ModelSetupParams(
    model_type='cls',
    schema_name="cls_schema",
    table_name="cls_table",
    target_col="output_col",
    data=[f"({i * 1.1}, {i * 1.2}, {i % 2})" for i in range(1, 1000)],
    aws_output_path="cls_path",
    batch_size=10
)


def get_deploy_arg_list(deploy_params: dict[str, Any], schema: str) -> list[Any]:
    """
    Creates a CLI parameter list to be used when calling the script deployment
    command (see deployment/deploy_cli.py).
    """
    args_list: list[Any] = []
    for param_name, param_value in deploy_params.items():
        args_list.append(f'--{param_name.replace("_", "-")}')
        args_list.append(param_value)
    args_list.extend(["--schema", schema])
    # We validate the server certificate in SaaS, but not in the Docker DB
    if "saas_url" in deploy_params:
        args_list.append("--use-ssl-cert-validation")
    else:
        args_list.append("--no-use-ssl-cert-validation")
    return args_list
