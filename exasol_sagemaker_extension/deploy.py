import logging
import click
from exasol.python_extension_common.cli.std_options import (
    StdParams, StdTags, select_std_options, ParameterFormatters)
from exasol.python_extension_common.cli.language_container_deployer_cli import (
    LanguageContainerDeployerCli)

from exasol_sagemaker_extension.deployment.sme_language_container_deployer import (
    SmeLanguageContainerDeployer)
from exasol_sagemaker_extension.deployment.deploy_create_statements import (
    DeployCreateStatements)

CONTAINER_URL_ARG = 'container_url'
CONTAINER_NAME_ARG = 'container_name'

ver_formatter = ParameterFormatters()
ver_formatter.set_formatter(CONTAINER_URL_ARG, SmeLanguageContainerDeployer.SLC_URL_FORMATTER)
ver_formatter.set_formatter(CONTAINER_NAME_ARG, SmeLanguageContainerDeployer.SLC_NAME)
formatters = {StdParams.version: ver_formatter}

opts = select_std_options([StdTags.DB, StdTags.BFS, StdTags.SLC],
                          exclude=StdParams.language_alias, formatters=formatters)
opts.append(click.Option(['--to-print/--no-to-print'], type=bool, default=False))
opts.append(click.Option(['--develop/--no-develop'], type=bool, default=False))
opts.append(click.Option(['--deploy-slc/--no-deploy-slc'], type=bool, default=True))
opts.append(click.Option(['--deploy-scripts/--no-deploy-scripts'], type=bool, default=True))


def deploy(deploy_slc: bool, deploy_scripts: bool,  **kwargs):

    if deploy_slc:
        slc_deployer = LanguageContainerDeployerCli(
            container_url_arg=CONTAINER_URL_ARG,
            container_name_arg=CONTAINER_NAME_ARG)

        extra_params = {StdParams.language_alias.name: 'PYTHON3_SME'}
        slc_deployer(**kwargs, **extra_params)

    if deploy_scripts:
        DeployCreateStatements.create_and_run(**kwargs)


deploy_command = click.Command(None, params=opts, callback=deploy)


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(module)s  - %(message)s',
        level=logging.DEBUG)

    deploy_command()
