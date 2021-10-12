import json
from exasol_udf_mock_python.connection import Connection


def extract_credentials(conn_obj: Connection):
    """
    Parse the password part of a given Exasol Connection object and
    extract aws session key and aws session token credentials

    :param Connection conn_obj: Exasol Connection object
    :return (str, str):  aws session key and  aws session token
    """

    credential_data = conn_obj.password
    try:
        credential_data = json.loads(credential_data)
    except Exception as e:
        print("String could not be converted to json :%s" % credential_data)

    if isinstance(credential_data, dict):
        secret_key, session_token = credential_data.get("secret_key"), \
                                    credential_data.get("session_token")
    else:
        secret_key, session_token = credential_data, None

    return secret_key, session_token
