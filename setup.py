# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['exasol_sagemaker_extension']

package_data = \
{'': ['*']}

install_requires = [
    'requests==2.26.0',
    'pandas>=1.1.0,<2.0.0',
    'scikit-learn>=0.24.1,<0.25.0'
]

setup_kwargs = {
    'name': 'exasol_sagemaker_extension',
    'version': '0.1.0',
    'description': 'SageMaker Integration',
    'long_description': '',
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