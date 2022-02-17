import click
import logging
from exasol_sagemaker_extension.deployment.deploy_create_statements \
    import DeployCreateStatements


@click.command()
@click.option('--host', type=str, required=True, help="db host address")
@click.option('--port', type=str, required=True, help="db host port")
@click.option('--user', type=str, required=True, help="db user name")
@click.option('--pass', 'pass_', required=True, help="db user password")
@click.option('--schema', type=str, required=True, help="schema name")
@click.option('--print', 'print_', type=bool, required=False,
              is_flag=True, help="print out statements")
@click.option('--develop', type=bool, required=False,
              is_flag=True, help="generate and execute the scripts")
def main(host: str, port: str, user: str, pass_: str, schema: str,
         print_: bool = False, develop: bool = False):

    logging.basicConfig(format='%(asctime)s - %(module)s  - %(message)s',
                        level=logging.DEBUG)

    deployment = DeployCreateStatements(
        db_host=host,
        db_port=port,
        db_user=user,
        db_pass=pass_,
        schema=schema,
        to_print=print_,
        develop=develop
    )
    deployment.run()


if __name__ == "__main__":
    main()

