# Developer Guide


In this developer guide we explain how you can build and run this project.



## Building the Project

### 1. Build the Python Package
This project needs python interpreter Python 3.6 or above installed on the 
development machine. In addition, in order to build python packages you need to 
have >= [poetry](https://python-poetry.org/) 1.1.6 package manager. Then you can 
install and build as follows:
```bash
poetry install
poetry build
```

### 2. Deploy Lua Scripts
While deploying the project using python cli command, you can use `--develop` 
option to state how to install all necessary Lua scripts. 

```buildoutcfg
python -m exasol_sagemaker_extension.deployment.deploy_cli \
    --host <DB_HOST> \ 
    --port <DB_PORT> \
    --user <DB_USER> \
    --pass <PASS> \
    --schema <SCHEMA>
    --develop
```
#### 2.1. Use pre-prepared Lua scripts 
This deployment uses all the necessary scripts of the project which are already 
prepared in the project package. The `--develop` option is not used in this 
deployment.

#### 2.2. Generate Lua scripts from scratch
In this setup, Lua scripts are built and packaged from scratch. Therefore, this 
deployment needs Lua interpreter Lua 5.1 or above and some Lua dependencies 
installed on the development machine.

In order to be able to install the Lua dependencies, [LuaRocks](https://luarocks.org/) 
package manager is required. You can install luarocks as follows:
```bash
sudo apt-get install luarocks
```

You can install the Lua dependencies in the home directory of the project
using the following command:
```bash
luarocks install --only-deps *.rockspec
```

Note that, these scripts are regenerated from scratch at each commit, 
by the help of the `regenerate_scripts.py` script executed in the `pre-commit` 
hook script.

Please run the `./githooks/install.sh` script which installs the Github hooks 
after cloning the project. This makes the necessary githooks available in your 
development environment.

## Running the Tests

### 1. Lua Tests
In order to run all Lua tests you can execute the following command in the project:
```bash
poetry run poe lua-tests
```
This command runs the script `./scripts/lua_tests.sh` and not only tests all Lua 
scripts but also performs static code analysis.

### 2. Python Tests
Python tests consist of unit tests and integration tests. In the integration 
tests [LocalStack](https://localstack.cloud/) AWS framework is used to provide 
AWS environment. The AWS S3 integration is tested by placing Exasol database and 
Localstack emulator on the same network. The integration test environment 
is created with the following script:
```bash
./scripts/setup_integration_test.sh 
```

To run all the tests in the project use:
```bash
poetry run pytest tests
```

### 3. AWS Tets
The AWS tests are gathered under the `tests/ci-tests` directory. These test use 
the real AWS services. Therefore, you must set AWS credentials in the OS 
environment in order to use  these tests in development machine. 
```commandline
export AWS_ACCESS_KEY_ID=<AWS_ACCESS_KEY_ID>
export AWS_SECRET_ACCESS_KEY=<AWS_SECRET_ACCESS_KEY>
export AWS_REGION=<AWS_REGION>
export AWS_ROLE=<AWS_ROLE>
```
After that, you can run them as follows:
```bash
poetry run pytest tests/ci_tests
```

In order for these tests to run in the Github Workflow, the commit 
message must contain the following statement `[run aws tests]`. For example:
```bash
git commit -m "[run aws tests]"
```

Please note that, every commit that does not contain this statement does not run 
the `ci-tests`; as a result of that not all the tests can be validated. In 
order not to miss this situation, we deliberately get GitHub-workflows failed. 
Only when all tests including `ci-tests` are validated, then the workflows will 
be successful. 

## Conclusion
In the `.github/workflows` directory you can find the GitHub actions that 
make up the installing, building and testing steps for this project. This 
guide details these steps and actions.
