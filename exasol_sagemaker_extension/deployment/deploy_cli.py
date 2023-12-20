import click
import logging
from exasol_sagemaker_extension.deployment.deploy_create_statements \
    import DeployCreateStatements


@click.command()
@click.option('--host', type=str, required=True, help="db host address")
@click.option('--port', type=str, required=True, help="db host port")
@click.option('--user', type=str, required=True, help="db user name")
@click.option('--pass', 'pwd', required=True, help="db user password")
@click.option('--schema', type=str, required=True, help="schema name")
@click.option('--print', 'verbose', type=bool, required=False,
              is_flag=True, help="print out statements")
@click.option('--develop', type=bool, required=False,
              is_flag=True, help="generate and execute the scripts")
def main(host: str, port: str, user: str, pwd: str, schema: str,
         verbose: bool = False, develop: bool = False):

    logging.basicConfig(format='%(asctime)s - %(module)s  - %(message)s',
                        level=logging.DEBUG)

    DeployCreateStatements.create_and_run(
        db_host=host,
        db_port=port,
        db_user=user,
        db_pass=pwd,
        schema=schema,
        to_print=verbose,
        develop=develop
    )


if __name__ == "__main__":
    main()

