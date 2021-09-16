# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['exasol_sagemaker_extension']

package_data = \
{'': ['*'], 'exasol_sagemaker_extension': ['lua/*']}

install_requires = \
['boto>=2.49.0,<3.0.0', 'pandas==1.1.0', 'sagemaker>=2.59.1,<3.0.0']

setup_kwargs = {
    'name': 'exasol-sagemaker-extension',
    'version': '0.1.0',
    'description': 'Exasol SageMaker Integration',
    'long_description': '# SageMaker Extension\n\nThis project provides a Python library that trains data stored in Exasol using AWS SageMaker.\n\n\n## Table of Contents\n\n### Information for Users\n\n* [User Guide](doc/user_guide/user_guide.md)\n* [Changelog](doc/changes/changelog.md)\n\n### Information for Contributors\n\n\n* [System Requirement Specification](doc/system_requirements.md)\n* [Design](doc/design.md)\n* [Dependencies](doc/dependencies.md)',
    'author': 'Umit Buyuksahin',
    'author_email': 'umit.buyuksahin@exasol.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/exasol/sagemaker-extension',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.1,<4.0',
}


setup(**setup_kwargs)
