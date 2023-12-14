import logging
import click
from exasol_sagemaker_extension.deployment.deploy_cli import main as scripts_deployer_main
from exasol_sagemaker_extension.deployment.language_container_deployer_cli \
    import language_container_deployer_main, slc_parameter_formatters, CustomizableParameters
from exasol_sagemaker_extension.deployment.sme_language_container_deployer import SmeLanguageContainerDeployer


@click.group()
def main():
    pass


slc_parameter_formatters.set_formatter(CustomizableParameters.container_url,
                                       SmeLanguageContainerDeployer.SLC_URL_FORMATTER)
slc_parameter_formatters.set_formatter(CustomizableParameters.container_name,
                                       SmeLanguageContainerDeployer.SLC_NAME)

main.add_command(scripts_deployer_main)
main.add_command(language_container_deployer_main)


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(module)s  - %(message)s',
        level=logging.DEBUG)

    main()
