FROM exasol/script-language-container:python-3.7-minimal-EXASOL-6.2.0-release_62ACSVRND4XHWTZ56ATSZD4P7UGZMBBZVIO66MOQZHY5UMCSTEJA

COPY release/dist /project
RUN pip install /project/*.whl


RUN mkdir -p /build_info/actual_installed_packages/release && \
    /scripts/list_installed_scripts/list_installed_apt.sh > /build_info/actual_installed_packages/release/apt_get_packages && \
    /scripts/list_installed_scripts/list_installed_pip.sh python3.7 > /build_info/actual_installed_packages/release/python3_pip_packages
