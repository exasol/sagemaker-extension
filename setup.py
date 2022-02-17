# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['exasol_sagemaker_extension',
 'exasol_sagemaker_extension.autopilot_utils',
 'exasol_sagemaker_extension.deployment']

package_data = \
{'': ['*'],
 'exasol_sagemaker_extension': ['lua/src/*',
                                'lua/test/*',
                                'resources/lua/outputs/*',
                                'resources/lua/templates/*',
                                'resources/sql/*',
                                'resources/udf/*']}

install_requires = \
['boto>=2.49.0,<3.0.0',
 'click>=8.0.3,<9.0.0',
 'importlib-resources>=5.2.0,<6.0.0',
 'localstack-client>=1.25,<2.0',
 'pandas>=1.1.3,<2.0.0',
 'pyexasol>=0.20.0,<0.21.0',
 'sagemaker>=2.59.1,<3.0.0']

setup_kwargs = {
    'name': 'exasol-sagemaker-extension',
    'version': '0.3.0',
    'description': 'Exasol SageMaker Integration',
    'long_description': '# SageMaker Extension\n\nThis project provides a Python library that trains data stored in Exasol using AWS SageMaker.\n\n\n## Table of Contents\n\n### Information for Users\n\n* [User Guide](doc/user_guide/user_guide.md)\n* [Tutorial](https://github.com/exasol/data-science-examples/blob/main/tutorials/machine-learning/sagemaker-extension/tutorial.md)\n* [Changelog](doc/changes/changelog.md)\n\n### Information for Contributors\n\n\n* [System Requirement Specification](doc/system_requirements.md)\n* [Design](doc/design.md)\n* [Dependencies](doc/dependencies.md)',
    'author': 'Umit Buyuksahin',
    'author_email': 'umit.buyuksahin@exasol.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/exasol/sagemaker-extension',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.2,<4.0',
}


setup(**setup_kwargs)
