import sys
import logging
import argparse
from exasol_sagemaker_extension.deployment.deploy_create_statements \
    import DeployCreateStatements


def main(args):
    parser = argparse.ArgumentParser(
        description="deploy the Sagemaker Extension")
    parser.add_argument("--host", help="db host address", required=True)
    parser.add_argument("--port", help="db host port", required=True)
    parser.add_argument("--user", help="db user name", required=True)
    parser.add_argument("--pass", help="db user password", required=True)
    parser.add_argument("--schema", help="schema name", required=True)
    parser.add_argument("--print", help="print out statements",
                        required=False, action="store_true")

    args = vars(parser.parse_args(args))
    deployment = DeployCreateStatements(
        db_host=args['host'],
        db_port=args['port'],
        db_user=args['user'],
        db_pass=args['pass'],
        schema=args['schema'],
        to_print=args['print'])
    deployment.run()


if __name__ == "__main__":
    logging.basicConfig(
        format='%(asctime)s - %(module)s  - %(message)s',
        level=logging.DEBUG)

    main(sys.argv[1:])

