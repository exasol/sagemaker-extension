import logging
from exasol_sagemaker_extension.deployment.deploy_create_statements \
    import DeployCreateStatements


def generate_scripts():
    """
    Generate CREATE sql statements from scratch and saves them.
    """
    logging.basicConfig(
        format='%(asctime)s - %(module)s  - %(message)s',
        level=logging.DEBUG)

    DeployCreateStatements.create_statements()


if __name__ == "__main__":
    generate_scripts()
